"""
Database models for the ScentSensation fragrance store.
These models map to the existing PostgreSQL database schema.
"""

from django.db import models
import pycountry


def get_country_choices():
    """Generate country choices from pycountry."""
    return [(c.alpha_2, c.name) for c in pycountry.countries]


def get_us_state_choices():
    return [
        ('', 'Select state'),
        ('AL', 'Alabama'), ('AK', 'Alaska'),
        ('AZ', 'Arizona'), ('AR', 'Arkansas'),
        ('CA', 'California'), ('CO', 'Colorado'),
        ('CT', 'Connecticut'), ('DE', 'Delaware'),
        ('FL', 'Florida'), ('GA', 'Georgia'),
        ('HI', 'Hawaii'), ('ID', 'Idaho'),
        ('IL', 'Illinois'), ('IN', 'Indiana'),
        ('IA', 'Iowa'), ('KS', 'Kansas'),
        ('KY', 'Kentucky'), ('LA', 'Louisiana'),
        ('ME', 'Maine'), ('MD', 'Maryland'),
        ('MA', 'Massachusetts'), ('MI', 'Michigan'),
        ('MN', 'Minnesota'), ('MS', 'Mississippi'),
        ('MO', 'Missouri'), ('MT', 'Montana'),
        ('NE', 'Nebraska'), ('NV', 'Nevada'),
        ('NH', 'New Hampshire'), ('NJ', 'New Jersey'),
        ('NM', 'New Mexico'), ('NY', 'New York'),
        ('NC', 'North Carolina'), ('ND', 'North Dakota'),
        ('OH', 'Ohio'), ('OK', 'Oklahoma'),
        ('OR', 'Oregon'), ('PA', 'Pennsylvania'),
        ('RI', 'Rhode Island'),
        ('SC', 'South Carolina'), ('SD', 'South Dakota'),
        ('TN', 'Tennessee'), ('TX', 'Texas'),
        ('UT', 'Utah'), ('VT', 'Vermont'),
        ('VA', 'Virginia'), ('WA', 'Washington'),
        ('WV', 'West Virginia'), ('WI', 'Wisconsin'),
        ('WY', 'Wyoming'), ('DC', 'District of Columbia'),
    ]


def get_uk_country_choices():
    return [
        ('ENG', 'England'), ('SCT', 'Scotland'),
        ('WLS', 'Wales'), ('NIR', 'Northern Ireland'),
    ]


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
    customer = models.ForeignKey(Customer, models.CASCADE, related_name='phonenumbers', db_column='customer_id')
    phone_number = models.CharField(primary_key=True, max_length=20)

    class Meta:
        managed = True
        db_table = 'PHONE_NUMBERS'

    def __str__(self):
        return self.phone_number


class Addresses(models.Model):
    objects = models.Manager()
    address_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, models.CASCADE, related_name='addresses', db_column='customer_id')
    house = models.CharField(max_length=100)
    street_name = models.CharField(max_length=100)
    town_city = models.CharField(max_length=50)
    county = models.CharField(max_length=50, blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=2, choices=get_country_choices())
    state = models.CharField(max_length=2, choices=get_us_state_choices(), blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'ADDRESSES'

    def __str__(self):
        return f"{self.house}, {self.street_name}, {self.town_city}"


class DiscountRate(models.Model):
    objects = models.Manager()
    member_type = models.CharField(primary_key=True, max_length=50)
    discount_rate = models.FloatField(default=0)

    class Meta:
        managed = True
        db_table = 'DISCOUNT_RATE'

    def __str__(self):
        return self.member_type


class MembershipTier(models.Model):
    objects = models.Manager()
    tier_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, help_text="Display name: Classic, Elite, Scholar")
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    monthly_price = models.DecimalField(max_digits=8, decimal_places=2)
    yearly_price = models.DecimalField(max_digits=8, decimal_places=2)
    discount_rate = models.FloatField(default=0, help_text="Percentage discount on product prices")
    stripe_monthly_price_id = models.CharField(max_length=100, blank=True)
    stripe_yearly_price_id = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'MEMBERSHIP_TIER'
        ordering = ['monthly_price']

    def __str__(self):
        return self.name

    @property
    def yearly_monthly_equivalent(self):
        if self.yearly_price and self.monthly_price:
            return round(float(self.yearly_price) / 12, 2)
        return 0

    @property
    def yearly_savings_percent(self):
        if self.monthly_price and self.yearly_price:
            yearly_cost = float(self.monthly_price) * 12
            if yearly_cost > 0:
                return round((1 - float(self.yearly_price) / yearly_cost) * 100, 1)
        return 0


class Membership(models.Model):
    objects = models.Manager()
    member_id = models.AutoField(primary_key=True)
    customer = models.OneToOneField(Customer, models.CASCADE, related_name='membership', db_column='customer_id')
    tier = models.ForeignKey(MembershipTier, models.SET_NULL, null=True, blank=True, related_name='subscriptions')
    member_type = models.ForeignKey(DiscountRate, models.SET_NULL, null=True, blank=True, db_column='member_type')
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    auto_renew = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'MEMBERSHIP'

    def __str__(self):
        tier_name = self.tier.name if self.tier else "None"
        return f"{self.customer} — {tier_name}"

    @property
    def is_current(self):
        from django.utils import timezone
        if not self.is_active or not self.end_date:
            return False
        return self.end_date >= timezone.now().date()


class Brand(models.Model):
    objects = models.Manager()
    brand_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        managed = True
        db_table = 'BRAND'
        ordering = ['name']

    def __str__(self):
        return self.name

    def product_count(self):
        return Products.objects.filter(brand=self.name).count()


class Products(models.Model):
    REGION_CHOICES = [
        ('US', 'United States'),
        ('UK', 'United Kingdom'),
        ('EU', 'European Union'),
    ]

    objects = models.Manager()
    product_id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=50)
    product_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()
    gift = models.BooleanField(default=False)
    region = models.CharField(max_length=2, choices=REGION_CHOICES, default='US')

    class Meta:
        managed = True
        db_table = 'PRODUCTS'

    def __str__(self):
        return f"{self.brand} - {self.product_name}"


class PersonalFragrances(models.Model):
    objects = models.Manager()
    product = models.OneToOneField(Products, models.CASCADE, primary_key=True, related_name='personal_fragrance', db_column='product_id')
    size = models.CharField(max_length=20)
    fragrance_family = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('Floral', 'Floral'),
            ('Oriental', 'Oriental'),
            ('Woody', 'Woody'),
            ('Fresh', 'Fresh'),
            ('Citrus', 'Citrus'),
            ('Chypre', 'Chypre'),
            ('Fougère', 'Fougère'),
            ('Leather', 'Leather'),
            ('Aromatic', 'Aromatic'),
            ('Gourmand', 'Gourmand'),
        ]
    )
    gender = models.CharField(
        max_length=20,
        choices=[
            ('Man', 'Man'),
            ('Woman', 'Woman'),
            ('Unisex', 'Unisex'),
        ],
        default='Unisex',
    )
    strength = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('Eau de Parfum', 'Eau de Parfum'),
            ('Eau de Toilette', 'Eau de Toilette'),
            ('Parfum', 'Parfum'),
            ('Eau de Cologne', 'Eau de Cologne'),
            ('Perfume Oil', 'Perfume Oil'),
            ('Body Mist', 'Body Mist'),
            ('Hair Mist', 'Hair Mist'),
        ]
    )
    engraving = models.CharField(max_length=100, blank=True, null=True)

    # Fragrantica enrichment fields
    fragrance_url = models.CharField(max_length=500, blank=True, help_text="Fragrantica page URL")
    release_year = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, help_text="HTML description from Fragrantica")
    rating_avg = models.FloatField(blank=True, null=True, help_text="Average rating (0-5)")
    rating_count = models.IntegerField(blank=True, null=True, help_text="Total number of ratings")
    reviews_count = models.IntegerField(blank=True, null=True, help_text="Total number of written reviews")
    main_photo_url = models.CharField(max_length=500, blank=True, help_text="Primary bottle image URL")

    class Meta:
        managed = True
        db_table = 'PERSONAL_FRAGRANCES'
        unique_together = (('product', 'size'),)

    def __str__(self):
        return f"{self.product} - {self.size}"


class HomeFragrances(models.Model):
    objects = models.Manager()
    product = models.OneToOneField(Products, models.CASCADE, primary_key=True, related_name='home_fragrance', db_column='product_id')
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


# ─── Fragrantica Enrichment Models ───────────────────────────────────────────

class FragranceNote(models.Model):
    """Master list of fragrance notes from Fragrantica."""
    objects = models.Manager()
    note_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    latin_name = models.CharField(max_length=100, blank=True)
    group = models.CharField(max_length=50, blank=True, help_text="e.g. Woods and mosses, Flowers, Citrus")
    odor_profile = models.TextField(blank=True)
    icon_url = models.CharField(max_length=500, blank=True)

    class Meta:
        managed = True
        db_table = 'FRAGRANCE_NOTE'
        ordering = ['name']

    def __str__(self):
        return self.name


class FragranceAccord(models.Model):
    """Master list of scent accords from Fragrantica."""
    objects = models.Manager()
    accord_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    bar_color = models.CharField(max_length=7, blank=True, help_text="Hex color for display")
    font_color = models.CharField(max_length=7, blank=True, default="#FFFFFF")

    class Meta:
        managed = True
        db_table = 'FRAGRANCE_ACCORD'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductNote(models.Model):
    """Notes pyramid for a product — links products to their fragrance notes by layer."""
    LAYER_CHOICES = [
        ('top', 'Top'),
        ('middle', 'Middle / Heart'),
        ('base', 'Base'),
    ]

    objects = models.Manager()
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.CASCADE, related_name='product_notes', db_column='product_id')
    note = models.ForeignKey(FragranceNote, models.CASCADE, related_name='product_usages')
    layer = models.CharField(max_length=10, choices=LAYER_CHOICES)
    opacity = models.FloatField(default=1.0, help_text="Visual prominence 0.0-1.0")
    weight = models.FloatField(default=1.0, help_text="Visual size on pyramid chart")

    class Meta:
        managed = True
        db_table = 'PRODUCT_NOTE'
        ordering = ['layer', '-opacity']

    def __str__(self):
        return f"{self.product} — {self.note} ({self.layer})"


class ProductAccord(models.Model):
    """Scent accords breakdown for a product with percentages."""
    objects = models.Manager()
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.CASCADE, related_name='product_accords', db_column='product_id')
    accord = models.ForeignKey(FragranceAccord, models.CASCADE, related_name='product_usages')
    percentage = models.FloatField(default=0, help_text="0-100 percentage")

    class Meta:
        managed = True
        db_table = 'PRODUCT_ACCORD'
        ordering = ['-percentage']

    def __str__(self):
        return f"{self.product} — {self.accord} ({self.percentage}%)"


class Perfumer(models.Model):
    """Perfumer (nose) profiles from Fragrantica."""
    objects = models.Manager()
    perfumer_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    photo_url = models.CharField(max_length=500, blank=True)
    company = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)

    class Meta:
        managed = True
        db_table = 'PERFUMER'
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductPerfumer(models.Model):
    """Links products to their perfumers."""
    objects = models.Manager()
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.CASCADE, related_name='product_perfumers', db_column='product_id')
    perfumer = models.ForeignKey(Perfumer, models.CASCADE, related_name='perfumer_products')

    class Meta:
        managed = True
        db_table = 'PRODUCT_PERFUMER'

    def __str__(self):
        return f"{self.product} by {self.perfumer}"


class ProductVote(models.Model):
    """Community voting data from Fragrantica (appreciation, longevity, sillage, season, etc.)."""
    VOTE_TYPE_CHOICES = [
        ('appreciation', 'Appreciation'),
        ('longevity', 'Longevity'),
        ('sillage', 'Sillage / Projection'),
        ('season', 'Season'),
        ('time_of_day', 'Time of Day'),
        ('price_value', 'Price Value'),
        ('gender_votes', 'Gender Votes'),
    ]

    objects = models.Manager()
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.CASCADE, related_name='product_votes', db_column='product_id')
    vote_type = models.CharField(max_length=20, choices=VOTE_TYPE_CHOICES)
    vote_label = models.CharField(max_length=50, help_text="e.g. love, like, moderate, strong, winter")
    votes_count = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)

    class Meta:
        managed = True
        db_table = 'PRODUCT_VOTE'
        ordering = ['vote_type', '-votes_count']

    def __str__(self):
        return f"{self.product} — {self.vote_type}: {self.vote_label} ({self.votes_count})"


class ProductImages(models.Model):
    objects = models.Manager()
    image_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.CASCADE, related_name='product_images', db_column='product_id')
    image = models.TextField()  # base64 encoded image data

    class Meta:
        managed = True
        db_table = 'PRODUCT_IMAGES'

    def __str__(self):
        return f"Image for {self.product}"


class Basket(models.Model):
    objects = models.Manager()
    customer = models.ForeignKey(Customer, models.CASCADE, related_name='baskets', db_column='customer_id')
    product = models.ForeignKey(Products, models.CASCADE, related_name='basket_items', db_column='product_id')
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
    gift_card = models.ForeignKey('GiftCards', models.SET_NULL, blank=True, null=True, db_column='gift_card_num', related_name='orders')
    order_date = models.DateTimeField()
    order_status = models.CharField(max_length=50)
    order_type = models.CharField(max_length=50, choices=[('Delivery', 'Delivery'), ('Pickup', 'Pickup')])
    payment_method = models.CharField(max_length=50, choices=[('Card', 'Card'), ('Paypal', 'Paypal'), ('Cash', 'Cash')])
    installment = models.BooleanField(default=False)
    total_payment = models.FloatField()

    class Meta:
        managed = True
        db_table = 'ORDERS'

    def __str__(self):
        return f"Order #{self.order_id}"


class OrderItems(models.Model):
    objects = models.Manager()
    order = models.ForeignKey(Orders, models.CASCADE, related_name='items', db_column='order_id')
    product = models.ForeignKey(Products, models.CASCADE, db_column='product_id')
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
    customer = models.ForeignKey(Customer, models.CASCADE, db_column='customer_id')
    product = models.ForeignKey(Products, models.CASCADE, db_column='product_id')
    order = models.ForeignKey(Orders, models.CASCADE, db_column='order_id')

    class Meta:
        managed = True
        db_table = 'PLACES'
        unique_together = (('customer', 'product', 'order'),)

    def __str__(self):
        return f"Place: {self.customer} bought {self.product} in Order #{self.order.order_id}"


class GiftCards(models.Model):
    objects = models.Manager()
    gift_card_num = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, models.CASCADE, related_name='gift_cards', db_column='customer_id')
    amount = models.FloatField()
    issue_date = models.DateField()
    exp_date = models.DateField()
    redeemed_status = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'GIFT_CARDS'

    def __str__(self):
        return f"Gift Card #{self.gift_card_num}"


class PromoCode(models.Model):
    objects = models.Manager()
    promo_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    redeemed = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'PROMO_CODES'

    def __str__(self):
        return f"{self.code} (£{self.amount})"


class Favourite(models.Model):
    objects = models.Manager()
    customer = models.ForeignKey(Customer, models.CASCADE, db_column='customer_id')
    product = models.ForeignKey(Products, models.CASCADE, db_column='product_id')

    class Meta:
        managed = True
        db_table = 'FAVOURITE'
        unique_together = (('customer', 'product'),)

    def __str__(self):
        return f"{self.customer} favorites {self.product}"


class Wishlist(models.Model):
    objects = models.Manager()
    customer = models.ForeignKey(Customer, models.CASCADE, related_name='wishlist_items', db_column='customer_id')
    product = models.ForeignKey(Products, models.CASCADE, related_name='wishlisted_by', db_column='product_id')

    class Meta:
        managed = True
        db_table = 'WISHLIST'
        unique_together = (('customer', 'product'),)

    def __str__(self):
        return f"{self.customer} wishlists {self.product}"


class Store(models.Model):
    objects = models.Manager()
    store_id = models.AutoField(primary_key=True)
    branch_number = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'STORE'

    def __str__(self):
        return self.name or f"Store {self.store_id}"


class Inventory(models.Model):
    objects = models.Manager()
    inventory_id = models.AutoField(primary_key=True)
    store = models.ForeignKey(Store, models.CASCADE, related_name='inventory', db_column='store_id')
    product = models.ForeignKey(Products, models.CASCADE, related_name='inventory_items', db_column='product_id')
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
    inventory = models.ForeignKey(Inventory, models.CASCADE, db_column='inventory_id')
    product = models.ForeignKey(Products, models.CASCADE, db_column='product_id')

    class Meta:
        managed = True
        db_table = 'PRODUCT_INVENTORY'
        unique_together = (('inventory', 'product'),)

    def __str__(self):
        return f"Product {self.product} in Inventory {self.inventory}"


class Instalments(models.Model):
    objects = models.Manager()
    order = models.ForeignKey(Orders, models.CASCADE, db_column='order_id')
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
    order = models.ForeignKey(Orders, models.CASCADE, db_column='order_id')
    product = models.ForeignKey(Products, models.CASCADE, db_column='product_id')

    class Meta:
        managed = True
        db_table = 'ORDER_REF'
        unique_together = (('order', 'product'),)

    def __str__(self):
        return f"OrderRef: Order #{self.order.order_id} - {self.product}"
