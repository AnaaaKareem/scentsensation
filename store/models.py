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
    phone_number = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        managed = True  # Let Django manage migrations
        db_table = 'CUSTOMER'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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


class Region(models.Model):
    region_code = models.CharField(max_length=2, primary_key=True)  # 'US', 'UK'
    name = models.CharField(max_length=50)
    currency_code = models.CharField(max_length=3)  # 'USD', 'GBP'
    currency_symbol = models.CharField(max_length=5)  # '$', '£'

    class Meta:
        managed = True
        db_table = 'REGION'

    def __str__(self):
        return f"{self.name} ({self.region_code})"


class ProductsManager(models.Manager):
    def create(self, **kwargs):
        price = kwargs.pop('price', None)
        region_code = kwargs.pop('region', 'US')
        
        product = super().create(**kwargs)
        
        if price is not None:
            region, _ = Region.objects.get_or_create(
                region_code=region_code,
                defaults={
                    'name': 'United States' if region_code == 'US' else 'United Kingdom',
                    'currency_code': 'USD' if region_code == 'US' else 'GBP',
                    'currency_symbol': '$' if region_code == 'US' else '£'
                }
            )
            ProductVariant.objects.get_or_create(
                product=product,
                size_ml=100,
                region=region,
                defaults={'price': price, 'stock': 100}
            )
        return product


class Products(models.Model):
    objects = ProductsManager()
    product_id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=50)
    product_name = models.CharField(max_length=100)
    description = models.TextField()
    gift = models.BooleanField(default=False)
    regions = models.ManyToManyField(Region, through='ProductVariant', related_name='products')

    # Fragrantica enrichment fields
    fragrantica_id = models.IntegerField(blank=True, null=True, unique=True, help_text="Fragrantica PID")
    fragrantica_url = models.CharField(max_length=500, blank=True)
    release_year = models.IntegerField(blank=True, null=True)
    main_photo_url = models.CharField(max_length=500, blank=True)
    rating_avg = models.FloatField(blank=True, null=True)
    rating_count = models.IntegerField(blank=True, null=True)
    reviews_count = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'PRODUCTS'

    def __str__(self):
        return f"{self.brand} - {self.product_name}"

    @property
    def price(self):
        variant = self.variants.first()
        return variant.price if variant else 0.00

    @property
    def region(self):
        variant = self.variants.first()
        return variant.region.region_code if variant else 'US'

    def is_out_of_stock_in_region(self, region_code):
        variants = self.variants.filter(region_id=region_code)
        if not variants.exists():
            return True
        return sum(v.stock for v in variants) <= 0


class ProductVariant(models.Model):
    variant_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.CASCADE, related_name='variants', db_column='product_id')
    size_ml = models.IntegerField()  # e.g. 50, 100, 150
    region = models.ForeignKey(Region, models.CASCADE, related_name='variants', db_column='region_code')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = 'PRODUCT_VARIANT'
        unique_together = (('product', 'size_ml', 'region'),)

    def __str__(self):
        return f"{self.product} - {self.size_ml}ml ({self.region.region_code}) (£/{self.price})"


class FragranceNote(models.Model):
    """Master list of fragrance notes from Fragrantica."""
    objects = models.Manager()
    note_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    latin_name = models.CharField(max_length=100, blank=True)
    group = models.CharField(max_length=50, blank=True, help_text="e.g. Woods and mosses, Flowers, Citrus")
    group_color = models.CharField(max_length=7, blank=True, default="#8B7355", help_text="Hex color for note group display")
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


class SimilarProduct(models.Model):
    """Similar/related products from Fragrantica (reminds_of field)."""
    objects = objects = models.Manager()
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.CASCADE, related_name='similar_products', db_column='product_id')
    similar_product = models.ForeignKey(Products, models.CASCADE, related_name='similar_to', db_column='similar_product_id')
    likes = models.IntegerField(default=0)
    dislikes = models.IntegerField(default=0)

    class Meta:
        managed = True
        db_table = 'SIMILAR_PRODUCT'
        unique_together = ('product', 'similar_product')

    def __str__(self):
        return f"{self.product.product_name} → {self.similar_product.product_name} ({self.likes} likes)"


class ProductImages(models.Model):
    objects = models.Manager()
    image_id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Products, models.CASCADE, related_name='product_images', db_column='product_id')
    image_url = models.CharField(max_length=500, blank=True)  # URL to image
    is_primary = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'PRODUCT_IMAGES'

    def __str__(self):
        return f"Image for {self.product}"


class Basket(models.Model):
    objects = models.Manager()
    customer = models.ForeignKey(Customer, models.CASCADE, related_name='baskets', db_column='customer_id')
    variant = models.ForeignKey('ProductVariant', models.CASCADE, related_name='basket_items', db_column='variant_id', null=True, blank=True)
    quantity = models.IntegerField(default=1)

    class Meta:
        managed = True
        db_table = 'BASKET'
        unique_together = (('customer', 'variant'),)

    def __str__(self):
        return f"{self.customer} - {self.variant} x{self.quantity}"

    @property
    def product(self):
        return self.variant.product if self.variant else None


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
    variant = models.ForeignKey('ProductVariant', models.CASCADE, db_column='variant_id', null=True, blank=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = True
        db_table = 'ORDER_ITEMS'
        unique_together = (('order', 'variant'),)

    def __str__(self):
        return f"Item {self.variant} in Order #{self.order.order_id}"

    @property
    def product(self):
        return self.variant.product if self.variant else None


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
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)
    customer = models.ForeignKey(Customer, models.CASCADE, related_name='gift_cards', db_column='customer_id', null=True, blank=True)
    amount = models.FloatField()
    issue_date = models.DateField(auto_now_add=True)
    exp_date = models.DateField(null=True, blank=True)
    redeemed_status = models.BooleanField(default=False)
    redeemed_at = models.DateTimeField(null=True, blank=True)
    redeemed_by = models.ForeignKey(Customer, models.SET_NULL, null=True, blank=True, related_name='redeemed_gift_cards')
    redemption_channel = models.CharField(max_length=10, choices=[('Online', 'Online'), ('Store', 'Store')], null=True, blank=True)
    redeemed_at_store = models.ForeignKey('Store', models.SET_NULL, null=True, blank=True, related_name='gift_card_redemptions')

    class Meta:
        managed = True
        db_table = 'GIFT_CARDS'

    def __str__(self):
        if self.code:
            return f"Promo Code: {self.code} (£{self.amount})"
        return f"Gift Card #{self.gift_card_num}"


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
        unique_together = (('store', 'product'),)

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


# Instalments model removed per request


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
