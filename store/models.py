"""
Database models for the ScentSensation fragrance store.
These models map to the existing PostgreSQL database schema.
"""

from django.db import models


class Customer(models.Model):
    objects = models.Manager()
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    DOB = models.DateField(db_column='DOB')
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    email_address = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        managed = True  # Let Django manage migrations
        db_table = 'CUSTOMER'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class PhoneNumbers(models.Model):
    objects = models.Manager()
    customer = models.ForeignKey(Customer, models.DO_NOTHING, related_name='phonenumbers', db_column='customer_id')
    phone_number = models.CharField(primary_key=True, max_length=20)

    class Meta:
        managed = True
        db_table = 'PHONE_NUMBERS'

    def __str__(self):
        return self.phone_number


class Addresses(models.Model):
    objects = models.Manager()
    address_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, models.DO_NOTHING, related_name='addresses', db_column='customer_id')
    house = models.CharField(max_length=100)
    street_name = models.CharField(max_length=100)
    town_city = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    postcode = models.CharField(max_length=20)
    country = models.CharField(
        max_length=50,
        choices=[
            ('England', 'England'),
            ('Scotland', 'Scotland'),
            ('Wales', 'Wales'),
            ('Northern Ireland', 'Northern Ireland')
        ]
    )

    class Meta:
        managed = True
        db_table = 'ADDRESSES'

    def __str__(self):
        return f"{self.house}, {self.street_name}, {self.town_city}"


class DiscountRate(models.Model):
    objects = models.Manager()
    member_type = models.CharField(primary_key=True, max_length=50,
                                   choices=[('Standard', 'Standard'), ('Premium', 'Premium'), ('Student', 'Student')])
    discount_rate = models.FloatField()

    class Meta:
        managed = True
        db_table = 'DISCOUNT_RATE'

    def __str__(self):
        return self.member_type


class Membership(models.Model):
    objects = models.Manager()
    member_id = models.AutoField(primary_key=True)
    customer = models.OneToOneField(Customer, models.DO_NOTHING, related_name='membership', db_column='customer_id')
    member_type = models.ForeignKey(DiscountRate, models.DO_NOTHING, db_column='member_type')
    end_ren_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'MEMBERSHIP'

    def __str__(self):
        return f"Membership for {self.customer}"


class Products(models.Model):
    objects = models.Manager()
    product_id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=50)
    product_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    gift = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'PRODUCTS'

    def __str__(self):
        return f"{self.brand} - {self.product_name}"


class PersonalFragrances(models.Model):
    objects = models.Manager()
    product = models.OneToOneField(Products, models.DO_NOTHING, primary_key=True, related_name='personal_fragrance', db_column='product_id')
    size = models.CharField(max_length=20)
    fragrance_family = models.CharField(
        max_length=50,
        choices=[
            ('Floral', 'Floral'),
            ('Oriental', 'Oriental'),
            ('Woody', 'Woody'),
            ('Fresh', 'Fresh'),
            ('Citrus', 'Citrus'),
            ('Chypre', 'Chypre')
        ]
    )
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    strength = models.CharField(
        max_length=20,
        choices=[
            ('Eau de Parfum', 'Eau de Parfum'),
            ('Eau de Toilette', 'Eau de Toilette'),
            ('Parfum', 'Parfum')
        ]
    )
    engraving = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'PERSONAL_FRAGRANCES'
        unique_together = (('product', 'size'),)

    def __str__(self):
        return f"{self.product} - {self.size}"


class HomeFragrances(models.Model):
    objects = models.Manager()
    product = models.OneToOneField(Products, models.DO_NOTHING, primary_key=True, related_name='home_fragrance', db_column='product_id')
    product_type = models.CharField(
        max_length=50,
        choices=[
            ('Scent Diffuser', 'Scent Diffuser'),
            ('Air Freshener', 'Air Freshener'),
            ('Scented Candles', 'Scented Candles'),
            ('Room Sprays', 'Room Sprays'),
            ('Reed Diffusers', 'Reed Diffusers')
        ]
    )
    bundle = models.BooleanField()

    class Meta:
        managed = True
        db_table = 'HOME_FRAGRANCES'

    def __str__(self):
        return f"{self.product} - {self.product_type}"


class ProductImages(models.Model):
    objects = models.Manager()
    image_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.DO_NOTHING, related_name='product_images', db_column='product_id')
    image = models.TextField()  # base64 encoded image data

    class Meta:
        managed = True
        db_table = 'PRODUCT_IMAGES'

    def __str__(self):
        return f"Image for {self.product}"


class Basket(models.Model):
    objects = models.Manager()
    customer = models.ForeignKey(Customer, models.DO_NOTHING, related_name='baskets', db_column='customer_id')
    product = models.ForeignKey(Products, models.DO_NOTHING, related_name='basket_items', db_column='product_id')
    quantity = models.IntegerField(default=1)

    class Meta:
        managed = True
        db_table = 'BASKET'
        unique_together = (('customer', 'product'),)

    def __str__(self):
        return f"{self.customer} - {self.product} x{self.quantity}"


class Orders(models.Model):
    objects = models.Manager()
    order_id = models.AutoField(primary_key=True)
    gift_card = models.ForeignKey('GiftCards', models.DO_NOTHING, blank=True, null=True, db_column='gift_card_num', related_name='orders')
    order_date = models.DateTimeField()
    order_status = models.CharField(max_length=50)
    order_type = models.CharField(max_length=50, choices=[('Delivery', 'Delivery'), ('Pickup', 'Pickup')])
    payment_method = models.CharField(max_length=50, choices=[('Card', 'Card'), ('Paypal', 'Paypal')])
    installment = models.BooleanField(default=False)
    total_payment = models.FloatField()

    class Meta:
        managed = True
        db_table = 'ORDERS'

    def __str__(self):
        return f"Order #{self.order_id}"


class OrderItems(models.Model):
    objects = models.Manager()
    order = models.ForeignKey(Orders, models.DO_NOTHING, related_name='items', db_column='order_id')
    product = models.ForeignKey(Products, models.DO_NOTHING, db_column='product_id')
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'ORDER_ITEMS'
        unique_together = (('order', 'product'),)

    def __str__(self):
        return f"Item {self.product} in Order #{self.order.order_id}"


class Places(models.Model):
    objects = models.Manager()
    customer = models.ForeignKey(Customer, models.DO_NOTHING, db_column='customer_id')
    product = models.ForeignKey(Products, models.DO_NOTHING, db_column='product_id')
    order = models.ForeignKey(Orders, models.DO_NOTHING, db_column='order_id')

    class Meta:
        managed = True
        db_table = 'PLACES'
        unique_together = (('customer', 'product', 'order'),)

    def __str__(self):
        return f"Place: {self.customer} bought {self.product} in Order #{self.order.order_id}"


class GiftCards(models.Model):
    objects = models.Manager()
    gift_card_num = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, models.DO_NOTHING, related_name='gift_cards', db_column='customer_id')
    amount = models.FloatField()
    issue_date = models.DateField()
    exp_date = models.DateField()
    redeemed_status = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'GIFT_CARDS'

    def __str__(self):
        return f"Gift Card #{self.gift_card_num}"


class Favourite(models.Model):
    objects = models.Manager()
    customer = models.ForeignKey(Customer, models.DO_NOTHING, db_column='customer_id')
    product = models.ForeignKey(Products, models.DO_NOTHING, db_column='product_id')

    class Meta:
        managed = True
        db_table = 'FAVOURITE'
        unique_together = (('customer', 'product'),)

    def __str__(self):
        return f"{self.customer} favorites {self.product}"


class Store(models.Model):
    objects = models.Manager()
    store_id = models.AutoField(primary_key=True)
    branch_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'STORE'

    def __str__(self):
        return f"Store {self.store_id}"


class Inventory(models.Model):
    objects = models.Manager()
    inventory_id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, models.DO_NOTHING, related_name='inventory', db_column='store_id')
    product = models.ForeignKey(Products, models.DO_NOTHING, related_name='inventory_items', db_column='product_id')
    quantity = models.IntegerField(default=0)
    restocking_threshold = models.IntegerField(default=10)
    last_restocking_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'INVENTORY'

    def __str__(self):
        return f"Inventory: {self.product} at {self.store}"


class ProductInventory(models.Model):
    objects = models.Manager()
    inventory = models.ForeignKey(Inventory, models.DO_NOTHING, db_column='inventory_id')
    product = models.ForeignKey(Products, models.DO_NOTHING, db_column='product_id')

    class Meta:
        managed = True
        db_table = 'PRODUCT_INVENTORY'
        unique_together = (('inventory', 'product'),)

    def __str__(self):
        return f"Product {self.product} in Inventory {self.inventory}"


class Instalments(models.Model):
    objects = models.Manager()
    order = models.ForeignKey(Orders, models.DO_NOTHING, db_column='order_id')
    instalment_number = models.IntegerField()
    instalment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pay_due = models.DateField(blank=True, null=True)
    payment_status = models.CharField(
        max_length=50,
        default='Pending',
        choices=[('Pending', 'Pending'), ('Paid', 'Paid'), ('Late', 'Late')]
    )

    class Meta:
        managed = True
        db_table = 'INSTALMENTS'
        unique_together = (('order', 'instalment_number'),)

    def __str__(self):
        return f"Instalment {self.instalment_number} for Order #{self.order.order_id}"


class OrderRef(models.Model):
    objects = models.Manager()
    order = models.ForeignKey(Orders, models.DO_NOTHING, db_column='order_id')
    product = models.ForeignKey(Products, models.DO_NOTHING, db_column='product_id')

    class Meta:
        managed = True
        db_table = 'ORDER_REF'
        unique_together = (('order', 'product'),)

    def __str__(self):
        return f"OrderRef: Order #{self.order.order_id} - {self.product}"
