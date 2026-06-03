from django.core.management.base import BaseCommand
from store.models import MembershipTier

class Command(BaseCommand):
    help = 'Seed default membership tiers'

    def handle(self, *args, **options):
        tiers = [
            {
                'name': 'Classic',
                'slug': 'classic',
                'description': 'Perfect for fragrance enthusiasts who want solid discounts without commitment.',
                'monthly_price': 4.99,
                'yearly_price': 47.90,
                'discount_rate': 10,
            },
            {
                'name': 'Elite',
                'slug': 'elite',
                'description': 'Our most popular tier. Maximum savings for the dedicated fragrance connoisseur.',
                'monthly_price': 9.99,
                'yearly_price': 95.90,
                'discount_rate': 20,
            },
            {
                'name': 'Scholar',
                'slug': 'scholar',
                'description': 'Exclusive perks and premium access. For those who demand the finest.',
                'monthly_price': 14.99,
                'yearly_price': 143.90,
                'discount_rate': 30,
            },
        ]

        for tier_data in tiers:
            tier, created = MembershipTier.objects.update_or_create(
                slug=tier_data['slug'],
                defaults=tier_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created tier: {tier.name}'))
            else:
                self.stdout.write(f'Updated tier: {tier.name}')

        self.stdout.write(self.style.SUCCESS('Membership tiers seeded successfully.'))
