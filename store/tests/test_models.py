"""
Unit tests for all store models.
Tests cover: creation, relationships, constraints, choices, and string representations.
"""
from django.test import TestCase
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import date, timedelta
from store.models import (
    Customer, Addresses, DiscountRate, Membership,
    Products, ProductImages,
    Basket, Orders, OrderItems, Places, GiftCards, Favourite,
    Store, Inventory, ProductInventory, OrderRef
)


# --- CUSTOMER ---
class CustomerModelTests(TestCase):
    def test_create_customer(self):
        c = Customer.objects.create(
            first_name="John",
            last_name="Doe",
            DOB=date(1990, 1, 1),
            gender="Male",
            email_address="john@example.com",
            password="hashed123"
        )
        self.assertEqual(c.first_name, "John")
        self.assertEqual(str(c), "John Doe")

    def test_customer_email_unique(self):
        Customer.objects.create(
            first_name="John", last_name="Doe", DOB=date(1990,1,1),
            gender="Male", email_address="john@example.com", password="pw"
        )
        with self.assertRaises(IntegrityError):
            Customer.objects.create(
                first_name="Jane", last_name="Doe", DOB=date(1990,1,1),
                gender="Female", email_address="john@example.com", password="pw"
            )

    def test_customer_middle_name_optional(self):
        c = Customer.objects.create(
            first_name="Jane", last_name="Smith", DOB=date(1995,5,15),
            gender="Female", email_address="jane@example.com", password="pw",
            middle_name="Anne"
        )
        self.assertEqual(c.middle_name, "Anne")
        c2 = Customer.objects.create(
            first_name="Bob", last_name="Jones", DOB=date(1985,3,10),
            gender="Male", email_address="bob@example.com", password="pw"
        )
        self.assertIsNone(c2.middle_name)

    def test_customer_phone_number(self):
        c = Customer.objects.create(
            first_name="Jane", last_name="Smith", DOB=date(1995,5,15),
            gender="Female", email_address="jane@example.com", password="pw",
            phone_number="+44 7911 123456"
        )
        self.assertEqual(c.phone_number, "+44 7911 123456")


# --- ADDRESSES ---
class AddressesModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Bob", last_name="Builder", DOB=date(1980,4,4),
            gender="Male", email_address="bob@example.com", password="pw"
        )

    def test_create_address(self):
        addr = Addresses.objects.create(
            customer=self.customer,
            house="123 Main St",
            street_name="Main Street",
            town_city="Springfield",
            county="Shelby",
            postcode="12345",
            country="US",
            state="IL"
        )
        self.assertEqual(addr.house, "123 Main St")
        self.assertEqual(addr.country, "US")
        self.assertEqual(addr.state, "IL")

    def test_address_fields_nullable(self):
        addr = Addresses.objects.create(
            customer=self.customer,
            house="456 Oak Ave",
            street_name="Oak Avenue",
            town_city="Metropolis",
            county=None,
            postcode=None,
            country="GB"
        )
        self.assertIsNone(addr.county)
        self.assertIsNone(addr.postcode)

    def test_address_cascade_delete(self):
        addr = Addresses.objects.create(
            customer=self.customer, house="1", street_name="St", town_city="City",
            county="C", postcode="000", country="US"
        )
        self.customer.delete()
        self.assertFalse(Addresses.objects.filter(pk=addr.address_id).exists())


# --- DISCOUNT_RATE ---
class DiscountRateModelTests(TestCase):
    def test_create_discount_rate(self):
        dr = DiscountRate.objects.create(member_type="Standard", discount_rate=10.0)
        self.assertEqual(dr.member_type, "Standard")
        self.assertEqual(dr.discount_rate, 10.0)
        self.assertEqual(str(dr), "Standard")

    def test_discount_rate_primary_key(self):
        DiscountRate.objects.create(member_type="Premium", discount_rate=15.0)
        dr = DiscountRate.objects.get(pk="Premium")
        self.assertEqual(dr.discount_rate, 15.0)


# --- MEMBERSHIP ---
class MembershipModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Charlie", last_name="Brown", DOB=date(1993,3,3),
            gender="Male", email_address="charlie@example.com", password="pw"
        )
        self.discount = DiscountRate.objects.create(member_type="Standard", discount_rate=10.0)

    def test_create_membership(self):
        mem = Membership.objects.create(
            customer=self.customer,
            member_type=self.discount,
            end_date=date(2026, 12, 31)
        )
        self.assertEqual(mem.customer, self.customer)
        self.assertEqual(mem.member_type, self.discount)
        self.assertEqual(str(mem), f"{self.customer} — None")

    def test_membership_one_to_one(self):
        Membership.objects.create(customer=self.customer, member_type=self.discount)
        with self.assertRaises(IntegrityError):
            Membership.objects.create(customer=self.customer, member_type=self.discount)


# --- PRODUCTS ---
class ProductsModelTests(TestCase):
    def test_create_product(self):
        p = Products.objects.create(
            brand="Chanel",
            product_name="Coco Mademoiselle",
            description="A fresh oriental fragrance",
            price=120.00,
            gift=False
        )
        self.assertEqual(str(p), "Chanel - Coco Mademoiselle")
        self.assertEqual(p.price, 120.00)

    def test_product_gift_default(self):
        p = Products.objects.create(
            brand="Dior", product_name="Sauvage", description="Bold and fresh", price=80.0
        )
        self.assertFalse(p.gift)





# --- PRODUCT_IMAGES ---
class ProductImagesModelTests(TestCase):
    def setUp(self):
        self.product = Products.objects.create(
            brand="Tom Ford", product_name="Oud Wood", description="Luxury fragrance",
            price=200.00, gift=False
        )

    def test_create_product_image(self):
        img_url = "http://example.com/photo.jpg"
        img = ProductImages.objects.create(product=self.product, image_url=img_url)
        self.assertEqual(img.product, self.product)
        self.assertEqual(img.image_url, img_url)

    def test_product_image_cascade_delete(self):
        img = ProductImages.objects.create(product=self.product, image_url="http://example.com/photo.jpg")
        self.product.delete()
        self.assertFalse(ProductImages.objects.filter(pk=img.image_id).exists())


# --- BASKET ---
class BasketModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="David", last_name="Kim", DOB=date(1988,8,8),
            gender="Male", email_address="david@example.com", password="pw"
        )
        self.product = Products.objects.create(
            brand="Versace", product_name="Bright Crystal", description="Fresh floral",
            price=70.00, gift=False
        )
        self.variant = self.product.variants.first()

    def test_create_basket_item(self):
        item = Basket.objects.create(customer=self.customer, variant=self.variant, quantity=2)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(str(item), f"{self.customer} - {self.variant} x2")

    def test_basket_default_quantity(self):
        item = Basket.objects.create(customer=self.customer, variant=self.variant)
        self.assertEqual(item.quantity, 1)

    def test_basket_unique_together(self):
        Basket.objects.create(customer=self.customer, variant=self.variant, quantity=1)
        with self.assertRaises(IntegrityError):
            Basket.objects.create(customer=self.customer, variant=self.variant, quantity=3)

    def test_basket_cascade_delete_customer(self):
        item = Basket.objects.create(customer=self.customer, variant=self.variant)
        self.customer.delete()
        self.assertFalse(Basket.objects.filter(pk=item.id).exists())


# --- ORDERS ---
class OrdersModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Eve", last_name="Adams", DOB=date(1994,9,9),
            gender="Female", email_address="eve@example.com", password="pw"
        )
        self.gift_card = GiftCards.objects.create(
            customer=self.customer, amount=50.00,
            issue_date=date(2026,1,1), exp_date=date(2027,1,1), redeemed_status=False
        )

    def test_create_order(self):
        order = Orders.objects.create(
            gift_card=None,
            order_date=timezone.now(),
            order_status="Paid",
            order_type="Delivery",
            payment_method="Card",
            installment=False,
            total_payment=150.00
        )
        self.assertEqual(str(order), f"Order #{order.order_id}")

    def test_order_with_gift_card(self):
        order = Orders.objects.create(
            gift_card=self.gift_card,
            order_date=timezone.now(), order_status="Pending",
            order_type="Pickup", payment_method="Paypal",
            installment=False, total_payment=75.00
        )
        self.assertEqual(order.gift_card, self.gift_card)


# --- ORDER_ITEMS ---
class OrderItemsModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Frank", last_name="Wright", DOB=date(1985,5,20),
            gender="Male", email_address="frank@example.com", password="pw"
        )
        self.product = Products.objects.create(
            brand="Givenchy", product_name="L'Interdit", description="Mysterious",
            price=110.00, gift=False
        )
        self.variant = self.product.variants.first()
        self.order = Orders.objects.create(
            gift_card=None, order_date=timezone.now(), order_status="Pending",
            order_type="Delivery", payment_method="Card", installment=False, total_payment=110.00
        )

    def test_create_order_item(self):
        item = OrderItems.objects.create(
            order=self.order, variant=self.variant, quantity=1, price=110.00
        )
        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.price, 110.00)

    def test_order_item_unique_together(self):
        OrderItems.objects.create(order=self.order, variant=self.variant, quantity=1, price=50.00)
        with self.assertRaises(IntegrityError):
            OrderItems.objects.create(order=self.order, variant=self.variant, quantity=2, price=50.00)


# --- PLACES ---
class PlacesModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Grace", last_name="Hopper", DOB=date(1906,12,9),
            gender="Female", email_address="grace@example.com", password="pw"
        )
        self.product = Products.objects.create(
            brand="Estée Lauder", product_name="Advanced Night Repair", description="Serum",
            price=95.00, gift=False
        )
        self.order = Orders.objects.create(
            gift_card=None, order_date=timezone.now(), order_status="Paid",
            order_type="Delivery", payment_method="Card", installment=False, total_payment=95.00
        )

    def test_create_place(self):
        place = Places.objects.create(customer=self.customer, product=self.product, order=self.order)
        self.assertEqual(place.customer, self.customer)
        self.assertEqual(place.product, self.product)
        self.assertEqual(place.order, self.order)

    def test_places_unique_together(self):
        Places.objects.create(customer=self.customer, product=self.product, order=self.order)
        with self.assertRaises(IntegrityError):
            Places.objects.create(customer=self.customer, product=self.product, order=self.order)


# --- GIFT_CARDS ---
class GiftCardsModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Henry", last_name="Ford", DOB=date(1863,7,30),
            gender="Male", email_address="henry@example.com", password="pw"
        )

    def test_create_gift_card(self):
        gc = GiftCards.objects.create(
            customer=self.customer,
            amount=100.00,
            issue_date=date(2026,1,1),
            exp_date=date(2027,1,1),
            redeemed_status=False
        )
        self.assertEqual(gc.amount, 100.00)
        self.assertFalse(gc.redeemed_status)
        self.assertEqual(str(gc), f"Gift Card #{gc.gift_card_num}")

    def test_gift_card_cascade_delete(self):
        gc = GiftCards.objects.create(
            customer=self.customer, amount=50.00,
            issue_date=date(2026,1,1), exp_date=date(2027,1,1), redeemed_status=False
        )
        self.customer.delete()
        self.assertFalse(GiftCards.objects.filter(pk=gc.gift_card_num).exists())


# --- FAVOURITE ---
class FavouriteModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Iris", last_name="Bloom", DOB=date(1996,4,12),
            gender="Female", email_address="iris@example.com", password="pw"
        )
        self.product = Products.objects.create(
            brand="Jo Malone", product_name="Peony & Blush Suede", description="Floral",
            price=130.00, gift=False
        )

    def test_create_favourite(self):
        fav = Favourite.objects.create(customer=self.customer, product=self.product)
        self.assertEqual(fav.customer, self.customer)
        self.assertEqual(fav.product, self.product)

    def test_favourite_unique_together(self):
        Favourite.objects.create(customer=self.customer, product=self.product)
        with self.assertRaises(IntegrityError):
            Favourite.objects.create(customer=self.customer, product=self.product)


# --- STORE ---
class StoreModelTests(TestCase):
    def test_create_store(self):
        store = Store.objects.create(branch_number="NYC001", address="123 5th Ave, NYC")
        self.assertEqual(store.branch_number, "NYC001")
        self.assertEqual(str(store), f"Store {store.store_id}")

    def test_store_fields_nullable(self):
        store = Store.objects.create()
        self.assertIsNone(store.branch_number)
        self.assertIsNone(store.address)


# --- INVENTORY ---
class InventoryModelTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create(branch_number="LA002", address="456 Sunset Blvd")
        self.product = Products.objects.create(
            brand="Lancôme", product_name="La Vie Est Belle", description="Floral",
            price=120.00, gift=False
        )

    def test_create_inventory(self):
        inv = Inventory.objects.create(
            store=self.store, product=self.product, quantity=50, restocking_threshold=10
        )
        self.assertEqual(inv.quantity, 50)
        self.assertEqual(inv.restocking_threshold, 10)

    def test_inventory_defaults(self):
        inv = Inventory.objects.create(store=self.store, product=self.product)
        self.assertEqual(inv.quantity, 0)
        self.assertEqual(inv.restocking_threshold, 10)
        self.assertIsNone(inv.last_restocking_date)

    def test_inventory_cascade_delete_store(self):
        inv = Inventory.objects.create(store=self.store, product=self.product)
        self.store.delete()
        self.assertFalse(Inventory.objects.filter(pk=inv.inventory_id).exists())

    def test_inventory_unique_together(self):
        Inventory.objects.create(store=self.store, product=self.product, quantity=10)
        with self.assertRaises(IntegrityError):
            Inventory.objects.create(store=self.store, product=self.product, quantity=20)


# --- PRODUCT_INVENTORY ---
class ProductInventoryModelTests(TestCase):
    def setUp(self):
        self.store = Store.objects.create()
        self.product = Products.objects.create(
            brand="Dolce & Gabbana", product_name="The Only One", description="Floral",
            price=85.00, gift=False
        )
        self.inventory = Inventory.objects.create(store=self.store, product=self.product)

    def test_create_product_inventory(self):
        pi = ProductInventory.objects.create(inventory=self.inventory, product=self.product)
        self.assertEqual(pi.inventory, self.inventory)
        self.assertEqual(pi.product, self.product)

    def test_product_inventory_unique_together(self):
        ProductInventory.objects.create(inventory=self.inventory, product=self.product)
        with self.assertRaises(IntegrityError):
            ProductInventory.objects.create(inventory=self.inventory, product=self.product)


# --- ORDER_REF ---
class OrderRefModelTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Kate", last_name="Moss", DOB=date(1974,1,16),
            gender="Female", email_address="kate@example.com", password="pw"
        )
        self.product = Products.objects.create(
            brand="Chanel", product_name="No. 5", description="Iconic",
            price=150.00, gift=False
        )
        self.order = Orders.objects.create(
            gift_card=None, order_date=timezone.now(), order_status="Paid",
            order_type="Pickup", payment_method="Paypal", installment=False, total_payment=150.00
        )
        self.order_item = OrderItems.objects.create(
            order=self.order, variant=self.product.variants.first(), quantity=1, price=150.00
        )

    def test_create_order_ref(self):
        ref = OrderRef.objects.create(order=self.order, product=self.product)
        self.assertEqual(ref.order, self.order)
        self.assertEqual(ref.product, self.product)

    def test_order_ref_unique_together(self):
        OrderRef.objects.create(order=self.order, product=self.product)
        with self.assertRaises(IntegrityError):
            OrderRef.objects.create(order=self.order, product=self.product)


# --- Relationships & Cascade Tests ---
class RelationshipCascadeTests(TestCase):
    """Test all foreign key cascade behaviors across the schema."""

    def setUp(self):
        self.customer = Customer.objects.create(
            first_name="Liam", last_name="Neeson", DOB=date(1952,6,7),
            gender="Male", email_address="liam@example.com", password="pw"
        )
        self.product = Products.objects.create(
            brand="Prada", product_name="Luna Rossa", description="Sporty",
            price=65.00, gift=False
        )
        self.variant = self.product.variants.first()
        self.store = Store.objects.create()
        self.inventory = Inventory.objects.create(store=self.store, product=self.product)

    def test_customer_cascade_deletes_all_related(self):
        # Create related records
        Addresses.objects.create(
            customer=self.customer, house="1", street_name="Elm", town_city="Town",
            county="C", postcode="00000", country="US"
        )
        discount = DiscountRate.objects.create(member_type="Standard", discount_rate=10.0)
        Membership.objects.create(customer=self.customer, member_type=discount)
        GiftCards.objects.create(
            customer=self.customer, amount=25.00,
            issue_date=date(2026,1,1), exp_date=date(2027,1,1), redeemed_status=False
        )
        Basket.objects.create(customer=self.customer, variant=self.variant)
        Favourite.objects.create(customer=self.customer, product=self.product)

        # Delete customer
        self.customer.delete()

        # Verify cascades
        self.assertFalse(Addresses.objects.exists())
        self.assertFalse(Membership.objects.exists())
        self.assertFalse(GiftCards.objects.exists())
        self.assertFalse(Basket.objects.exists())
        self.assertFalse(Favourite.objects.exists())

    def test_product_cascade_deletes(self):
        # Create related records
        ProductImages.objects.create(product=self.product, image_url="http://example.com/photo.jpg")
        ProductInventory.objects.create(inventory=self.inventory, product=self.product)

        self.product.delete()

        self.assertFalse(ProductImages.objects.exists())
        self.assertFalse(ProductInventory.objects.exists())

    def test_order_cascade_deletes_items(self):
        order = Orders.objects.create(
            gift_card=None, order_date=timezone.now(), order_status="Completed",
            order_type="Delivery", payment_method="Card", installment=False, total_payment=100.00
        )
        OrderItems.objects.create(order=order, variant=self.variant, quantity=1, price=100.00)
        Places.objects.create(customer=self.customer, product=self.product, order=order)
        OrderRef.objects.create(order=order, product=self.product)

        order.delete()

        self.assertFalse(OrderItems.objects.exists())
        self.assertFalse(Places.objects.exists())
        self.assertFalse(OrderRef.objects.exists())
