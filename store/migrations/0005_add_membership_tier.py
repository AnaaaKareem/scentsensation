import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_discountrate_valid_member_type'),
    ]

    operations = [
        # Create the new MembershipTier model
        migrations.CreateModel(
            name='MembershipTier',
            fields=[
                ('tier_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Display name: Classic, Elite, Scholar', max_length=50, unique=True)),
                ('slug', models.SlugField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True)),
                ('monthly_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('yearly_price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('discount_rate', models.FloatField(default=0, help_text='Percentage discount on product prices')),
                ('stripe_monthly_price_id', models.CharField(blank=True, max_length=100)),
                ('stripe_yearly_price_id', models.CharField(blank=True, max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'MEMBERSHIP_TIER',
                'ordering': ['monthly_price'],
            },
        ),

        # Remove the CheckConstraint from DiscountRate (no longer needed)
        migrations.RemoveConstraint(
            model_name='discountrate',
            name='valid_member_type',
        ),

        # Remove choices from DiscountRate.member_type
        migrations.AlterField(
            model_name='discountrate',
            name='member_type',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),

        # Add new fields to Membership
        migrations.AddField(
            model_name='membership',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='membership',
            name='start_date',
            field=models.DateField(auto_now_add=True, default=datetime.date(2026, 1, 1)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='membership',
            name='tier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriptions', to='store.membershiptier'),
        ),

        # Rename end_ren_date to end_date
        migrations.RenameField(
            model_name='membership',
            old_name='end_ren_date',
            new_name='end_date',
        ),
    ]
