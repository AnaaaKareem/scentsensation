from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from unittest.mock import patch, MagicMock
from datetime import date
from store.models import (
    Customer, Products, PersonalFragrances, HomeFragrances, ProductImages,
    Orders, OrderItems, MembershipTier, Membership, DiscountRate, Store, Inventory
)

class AdminPortalTests(TestCase):
    def setUp(self):
        # Create standard admin user data in DB
        self.password = "adminpass"
        self.admin_email = "admin@example.com"
        
        # Create mock data for dashboard stats
        self.product = Products.objects.create(
            brand="Chanel",
            product_name="No. 5",
            description="Classic scent",
            price=150.00,
            gift=False
        )
        self.store = Store.objects.create(name="London branch", address="Bond St")

    def test_admin_login_page_renders(self):
        response = self.client.get(reverse('admin_login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/admin/admin_login.html')

    @patch('store.views_admin.get_supabase_client')
    def test_admin_login_success(self, mock_get_supabase):
        # Mock Supabase authentication response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.user.id = "mock-admin-id"
        mock_response.user.email = self.admin_email
        mock_response.user.user_metadata = {"is_admin": True}
        mock_client.auth.sign_in_with_password.return_value = mock_response
        mock_get_supabase.return_value = mock_client

        response = self.client.post(reverse('admin_login'), {
            'email': self.admin_email,
            'password': self.password
        })

        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertEqual(self.client.session['admin_user_id'], 'mock-admin-id')
        self.assertEqual(self.client.session['admin_email'], self.admin_email)

    @patch('store.views_admin.get_supabase_client')
    def test_admin_login_failure(self, mock_get_supabase):
        # Mock Supabase raising authentication exception
        mock_client = MagicMock()
        mock_client.auth.sign_in_with_password.side_effect = Exception("Invalid login credentials")
        mock_get_supabase.return_value = mock_client

        response = self.client.post(reverse('admin_login'), {
            'email': 'wrong@admin.com',
            'password': 'wrong'
        })

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/admin/admin_login.html')
        # Session shouldn't have admin credentials
        self.assertNotIn('admin_user_id', self.client.session)

    def test_admin_logout(self):
        # Set session
        session = self.client.session
        session['admin_user_id'] = 'mock-admin-id'
        session.save()

        response = self.client.get(reverse('admin_logout'))
        self.assertRedirects(response, reverse('admin_login'))
        self.assertNotIn('admin_user_id', self.client.session)

    def test_dashboard_redirects_if_not_authenticated(self):
        response = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response, reverse('admin_login'))

    def test_dashboard_authenticated_loads(self):
        session = self.client.session
        session['admin_user_id'] = 'mock-admin-id'
        session['admin_email'] = self.admin_email
        session.save()

        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/admin/admin_dashboard.html')
        self.assertIn('total_products', response.context)

    def test_tier_save_new(self):
        session = self.client.session
        session['admin_user_id'] = 'mock-admin-id'
        session.save()

        response = self.client.post(reverse('tier_save'), {
            'name': 'Gold Elite',
            'monthly_price': '19.99',
            'yearly_price': '199.99',
            'discount_rate': '15',
            'description': 'Premium status',
            'is_active': 'true'
        })

        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertTrue(MembershipTier.objects.filter(name='Gold Elite').exists())
        self.assertTrue(DiscountRate.objects.filter(member_type='Gold Elite').exists())

    def test_tier_toggle(self):
        tier = MembershipTier.objects.create(
            name='Temporary',
            slug='temporary',
            monthly_price=5.00,
            yearly_price=50.00,
            discount_rate=5,
            is_active=True
        )
        session = self.client.session
        session['admin_user_id'] = 'mock-admin-id'
        session.save()

        response = self.client.get(reverse('tier_toggle', kwargs={'tier_id': tier.tier_id}))
        self.assertRedirects(response, reverse('admin_dashboard'))
        tier.refresh_from_db()
        self.assertFalse(tier.is_active)

    def test_add_product_personal(self):
        session = self.client.session
        session['admin_user_id'] = 'mock-admin-id'
        session.save()

        response = self.client.post(reverse('add_product'), {
            'brand': 'Gucci',
            'product_name': 'Bloom',
            'description': 'A beautiful floral scent',
            'price': '95.00',
            'region': 'UK',
            'category': 'Personal',
            'personal_size': '100ml',
            'personal_family': 'Floral',
            'personal_gender': 'Female',
            'personal_strength': 'Eau de Parfum'
        })

        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertTrue(Products.objects.filter(product_name='Bloom').exists())
        prod = Products.objects.get(product_name='Bloom')
        self.assertTrue(PersonalFragrances.objects.filter(product=prod).exists())

    def test_add_product_home(self):
        session = self.client.session
        session['admin_user_id'] = 'mock-admin-id'
        session.save()

        response = self.client.post(reverse('add_product'), {
            'brand': 'Yankee Candle',
            'product_name': 'Home Sweet Home',
            'description': 'Warm cozy candle',
            'price': '22.50',
            'region': 'US',
            'category': 'Home',
            'home_type': 'Scented Candles',
            'home_bundle': 'on'
        })

        self.assertRedirects(response, reverse('admin_dashboard'))
        self.assertTrue(Products.objects.filter(product_name='Home Sweet Home').exists())
        prod = Products.objects.get(product_name='Home Sweet Home')
        self.assertTrue(HomeFragrances.objects.filter(product=prod).exists())

    def test_manage_inventory_update(self):
        inv = Inventory.objects.create(store=self.store, product=self.product, quantity=5, restocking_threshold=2)
        session = self.client.session
        session['admin_user_id'] = 'mock-admin-id'
        session.save()

        response = self.client.post(reverse('manage_inventory') + f"?store_id={self.store.store_id}", {
            'action': 'update',
            'inventory_id': inv.inventory_id,
            'quantity': '20',
            'threshold': '5'
        })

        self.assertRedirects(response, reverse('manage_inventory') + f"?store_id={self.store.store_id}")
        inv.refresh_from_db()
        self.assertEqual(inv.quantity, 20)
        self.assertEqual(inv.restocking_threshold, 5)

    def test_view_customers(self):
        Customer.objects.create(
            first_name="Alice", last_name="Wonder", DOB=date(1995, 1, 1),
            gender="Female", email_address="alice@admin-test.com", password="pw"
        )
        session = self.client.session
        session['admin_user_id'] = 'mock-admin-id'
        session.save()

        response = self.client.get(reverse('view_customers') + "?q=Alice")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/admin/view_customers.html')
        self.assertIn('customers', response.context)
        self.assertEqual(len(response.context['customers']), 1)

    def test_export_reports(self):
        session = self.client.session
        session['admin_user_id'] = 'mock-admin-id'
        session.save()

        response = self.client.get(reverse('export_reports'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'store/admin/export_reports.html')
        self.assertIn('daily_sales', response.context)
