# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Addresses(models.Model):
    objects = models.Manager()
    address_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('Customer', models.DO_NOTHING, related_name='addresses')
    house = models.CharField(max_length=100)
    street_name = models.CharField(max_length=100)
    town_city = models.CharField(max_length=50)
    county = models.CharField(max_length=50)
    postcode = models.CharField(max_length=20)
    country = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'addresses'


class Basket(models.Model):
    objects = models.Manager()
    pk = models.CompositePrimaryKey('customer_id', 'product_id')
    customer = models.ForeignKey('Customer', models.DO_NOTHING, related_name='baskets')
    product = models.ForeignKey('Products', models.DO_NOTHING, related_name='basket_items')
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'basket'
        unique_together = (('customer', 'product'),)


class Customer(models.Model):
    objects = models.Manager()
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50)
    DOB = models.DateField(db_column='DOB')
    gender = models.CharField(max_length=10)
    email_address = models.CharField(max_length=100)
    password = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'customer'


class DiscountRate(models.Model):
    objects = models.Manager()
    member_type = models.CharField(primary_key=True, max_length=50)
    discount_rate = models.FloatField()

    class Meta:
        managed = False
        db_table = 'discount_rate'


class HomeFragrances(models.Model):
    objects = models.Manager()
    product = models.OneToOneField('Products', models.DO_NOTHING, primary_key=True, related_name='home_fragrance')
    product_type = models.CharField(max_length=50)
    bundle = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'home_fragrances'


class Membership(models.Model):
    objects = models.Manager()
    member_id = models.AutoField(primary_key=True)
    customer = models.OneToOneField('Customer', models.DO_NOTHING, related_name='membership')
    member_type = models.ForeignKey(DiscountRate, models.DO_NOTHING, db_column='member_type')
    end_ren_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'membership'


class OrderItems(models.Model):
    objects = models.Manager()
    pk = models.CompositePrimaryKey('order_id', 'product')
    order = models.ForeignKey('Orders', models.DO_NOTHING)
    product = models.ForeignKey('Products', models.DO_NOTHING, db_column='product_id')
    quantity = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'order_items'
        unique_together = (('order', 'product'),)


class Orders(models.Model):
    objects = models.Manager()
    order_id = models.AutoField(primary_key=True)
    order_date = models.DateField()
    order_time = models.TimeField()
    order_type = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'orders'


class PersonalFragrances(models.Model):
    objects = models.Manager()
    product = models.OneToOneField('Products', models.DO_NOTHING, primary_key=True, related_name='personal_fragrance')
    fragrance_family = models.CharField(max_length=50)
    gender = models.CharField(max_length=10)
    strength = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'personal_fragrances'


class PhoneNumbers(models.Model):
    objects = models.Manager()
    customer = models.ForeignKey(Customer, models.DO_NOTHING, related_name='phonenumbers')
    phone_number = models.CharField(primary_key=True, max_length=20)

    class Meta:
        managed = False
        db_table = 'phone_numbers'


class Places(models.Model):
    objects = models.Manager()
    pk = models.CompositePrimaryKey('customer_id', 'product_id', 'order_id')
    customer = models.ForeignKey(Customer, models.DO_NOTHING)
    product = models.ForeignKey('Products', models.DO_NOTHING)
    order = models.ForeignKey(Orders, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'places'
        unique_together = (('customer', 'product', 'order'),)


class ProductImages(models.Model):
    objects = models.Manager()
    image_id = models.AutoField(primary_key=True)
    product = models.ForeignKey('Products', models.DO_NOTHING, related_name='product_images')
    image = models.TextField()

    class Meta:
        managed = False
        db_table = 'product_images'


class Products(models.Model):
    objects = models.Manager()
    product_id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=50)
    product_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.FloatField()

    class Meta:
        managed = False
        db_table = 'products'