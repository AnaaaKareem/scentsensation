"""
Integration tests: complete user journeys and multi-step workflows.
Tests cover: signup → browse → basket → checkout → payment, as well as edge interactions.
"""
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from unittest.mock import patch, MagicMock
from django.utils import timezone
from django.core import mail
from datetime import date, timedelta, datetime

from store.models import (
    Customer, Addresses, DiscountRate, Membership, MembershipTier,
    Products, ProductImages, Basket,
    Orders, OrderItems, Places, GiftCards, Favourite, Store, Inventory,
    ProductInventory, OrderRef
)
from django.contrib.auth.hashers import make_password
from django.conf import settings

# Import BaseViewTestCase to inherit common test setup (customer, discount rates)
from .test_views import BaseViewTestCase


class CompleteUserJourneyTests(BaseViewTestCase):
    """Test the full lifecycle from signup to order completion."""

    @patch('store.views.send_mail')
    @patch('store.views.stripe.checkout.Session.create')
    @patch('store.views.stripe.checkout.Session.retrieve')
    def test_complete_purchase_flow(self, mock_retrieve, mock_session_create, mock_send_mail):
        # --- Arrange ---
        # Mock Stripe
        mock_checkout_session = MagicMock()
        mock_checkout_session.url = 'https://stripe.com/checkout/mock'
        mock_session_create.return_value = mock_checkout_session

        mock_paid_session = MagicMock()
        mock_paid_session.payment_status = 'paid'
        metadata = {
            'customer_id': str(self.customer.customer_id),
            'subtotal': '100.00',
            'discount': '0.00',
            'total': '100.00',
            'fulfilment': 'Delivery',
            'payment_method': 'Card'
        }
        mock_paid_session.metadata.to_dict.return_value = metadata
        mock_retrieve.return_value = mock_paid_session

        product = Products.objects.create(
            brand='TestCo', product_name='FragranceX', description='Nice scent',
            price=50.00, gift=False
        )
        session = self.client.session
        session['customer_id'] = self.customer.customer_id
        session.save()

        # --- Act step 1: Add to basket ---
        response = self.client.post(
            reverse('store'),
            {'add_basket': '', 'product_id': product.product_id, 'quantity': 2},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        basket = Basket.objects.get(customer=self.customer, variant__product=product)
        self.assertEqual(basket.quantity, 2)

        # --- Act step 2: View basket ---
        response = self.client.get(reverse('basket'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'FragranceX')

        # --- Act step 3: Checkout initiation ---
        response = self.client.post(reverse('checkout'), {
            'fulfilment': 'Delivery',
            'payment_method': 'Card'
        }, follow=False)
        self.assertRedirects(response, 'https://stripe.com/checkout/mock', fetch_redirect_response=False)

        # --- Act step 4: Payment success callback ---
        response = self.client.get(reverse('payment_success') + '?session_id=test_session_123')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/payment_success.html')
        self.assertContains(response, 'Order Number')
        self.assertContains(response, '#1')
        # Verify order created
        order = Orders.objects.filter(places__customer=self.customer).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.order_status, 'Paid')
        self.assertEqual(order.order_type, 'Delivery')
        self.assertEqual(order.payment_method, 'Card')
        self.assertEqual(order.total_payment, 100.00)
        # Verify order items
        item = OrderItems.objects.get(order=order)
        self.assertEqual(item.product, product)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, 50.00)
        # Verify basket cleared
        self.assertFalse(Basket.objects.filter(customer=self.customer).exists())
        # Verify email sent
        mock_send_mail.assert_called()
        # Verify Places record
        self.assertTrue(Places.objects.filter(customer=self.customer, product=product, order=order).exists())

    @patch('store.views.send_mail')
    @patch('store.views.stripe.checkout.Session.create')
    @patch('store.views.stripe.Coupon.create')
    def test_checkout_with_membership_discount_journey(self, mock_coupon, mock_session_create, mock_send_mail):
        # Setup membership discount
        mock_session = MagicMock()
        mock_session.url = 'https://stripe.test'
        mock_session_create.return_value = mock_session
        mock_coupon.return_value = MagicMock()

        tier = MembershipTier.objects.get(slug='Standard')
        Membership.objects.create(customer=self.customer, tier=tier, is_active=True)
        product = Products.objects.create(
            brand='Brand', product_name='Item', description='Desc', price=100.00, gift=False
        )
        Basket.objects.create(customer=self.customer, variant=product.variants.first(), quantity=1)
        session = self.client.session
        session['customer_id'] = self.customer.customer_id
        session.save()

        response = self.client.post(reverse('checkout'), {'fulfilment': 'Delivery', 'payment_method': 'Card'})
        self.assertRedirects(response, 'https://stripe.test', fetch_redirect_response=False)
        call_kwargs = mock_session_create.call_args[1]
        # Stripe line_items should reflect discount via coupon
        self.assertIn('discounts', call_kwargs)
        # Ensure coupon created
        self.assertGreater(len(call_kwargs['discounts']), 0)

    def test_basket_increment_and_decrement_flow(self):
        product1 = Products.objects.create(brand='B1', product_name='P1', description='D', price=10.0, gift=False)
        product2 = Products.objects.create(brand='B2', product_name='P2', description='D', price=20.0, gift=False)
        session = self.client.session
        session['customer_id'] = self.customer.customer_id
        session.save()

        # Add product1 qty 1
        self.client.post(reverse('add_quantity', kwargs={'variant_id': product1.variants.first().variant_id}))
        item = Basket.objects.get(customer=self.customer, variant__product=product1)
        self.assertEqual(item.quantity, 1)

        # Increment
        self.client.post(reverse('add_quantity', kwargs={'variant_id': product1.variants.first().variant_id}))
        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

        # Decrement
        self.client.post(reverse('remove_quantity', kwargs={'variant_id': product1.variants.first().variant_id}))
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

        # Decrement to 0 deletes
        self.client.post(reverse('remove_quantity', kwargs={'variant_id': product1.variants.first().variant_id}))
        self.assertFalse(Basket.objects.filter(variant__product=product1).exists())

        # Add second product
        self.client.post(reverse('add_quantity', kwargs={'variant_id': product2.variants.first().variant_id}))
        self.assertTrue(Basket.objects.filter(customer=self.customer, variant__product=product2).exists())

    def test_account_update_and_delete_flow(self):
        session = self.client.session
        session['customer_id'] = self.customer.customer_id
        session.save()

        # GET account loads data
        response = self.client.get(reverse('account'))
        self.assertContains(response, 'John')  # BaseViewTestCase first_name

        # POST update
        response = self.client.post(reverse('account'), {
            'update': '',
            'first_name': 'Updated',
            'last_name': 'Name',
            'email_address': 'updated@example.com',
            'phone_numbers': '555-8888'
        }, follow=True)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, 'Updated')
        self.assertEqual(self.customer.phone_number, '555-8888')

        # POST delete
        response = self.client.post(reverse('account'), {'delete': ''}, follow=True)
        self.assertFalse(Customer.objects.filter(pk=self.customer.pk).exists())
        self.assertNotIn('customer_id', self.client.session)



class OrderHistoryTests(BaseViewTestCase):
    """Tests for order retrieval and display after purchase (implicit)."""

    @patch('store.views.stripe.checkout.Session.retrieve')
    @patch('store.views.send_mail')
    def test_order_items_linked_to_customer_and_product(self, mock_send_mail, mock_retrieve):
        mock_session = MagicMock()
        mock_session.payment_status = 'paid'
        mock_session.metadata.to_dict.return_value = {
            'customer_id': str(self.customer.customer_id),
            'subtotal': '50', 'discount': '0', 'total': '50',
            'fulfilment': 'Pickup', 'payment_method': 'Paypal'
        }
        mock_retrieve.return_value = mock_session

        product = Products.objects.create(
            brand='Hist', product_name='HistProd', description='H', price=50.0, gift=False
        )
        Basket.objects.create(customer=self.customer, variant=product.variants.first(), quantity=1)
        session = self.client.session
        session['customer_id'] = self.customer.customer_id
        session.save()

        response = self.client.get(reverse('payment_success') + '?session_id=abc')
        order = Orders.objects.get()
        order_items = OrderItems.objects.filter(order=order)
        self.assertEqual(order_items.count(), 1)
        self.assertEqual(order_items.first().product, product)
        self.assertEqual(order_items.first().price, 50.00)

        # Check Places table populated
        places = Places.objects.filter(customer=self.customer, product=product, order=order)
        self.assertTrue(places.exists())


# To run: python manage.py test store.tests.test_integration
# Focus: full-stack flows, session continuity, Stripe mocking.
