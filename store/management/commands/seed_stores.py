from django.core.management.base import BaseCommand
from store.models import Store


class Command(BaseCommand):
    help = 'Seed placeholder store locations for pickup'

    def handle(self, *args, **options):
        stores = [
            {
                'name': 'Scent Sensation — Mayfair',
                'address': '14 New Bond Street, Mayfair, London W1S 3SX',
                'latitude': 51.5121,
                'longitude': -0.1441,
            },
            {
                'name': 'Scent Sensation — Chelsea',
                'address': '123 King\'s Road, Chelsea, London SW3 4RP',
                'latitude': 51.4875,
                'longitude': -0.1687,
            },
            {
                'name': 'Scent Sensation — Shoreditch',
                'address': '45 Shoreditch High Street, London E1 6PQ',
                'latitude': 51.5246,
                'longitude': -0.0770,
            },
            {
                'name': 'Scent Sensation — Notting Hill',
                'address': '78 Westbourne Grove, Notting Hill, London W11 2SB',
                'latitude': 51.5153,
                'longitude': -0.2050,
            },
            {
                'name': 'Scent Sensation — Canary Wharf',
                'address': '12 Canary Wharf, London E14 5AB',
                'latitude': 51.5054,
                'longitude': -0.0235,
            },
        ]

        created = 0
        for data in stores:
            store, was_created = Store.objects.get_or_create(
                name=data['name'],
                defaults={
                    'address': data['address'],
                    'latitude': data['latitude'],
                    'longitude': data['longitude'],
                }
            )
            if was_created:
                created += 1
                self.stdout.write(self.style.SUCCESS(f'Created: {store.name}'))
            else:
                self.stdout.write(f'Skipped (exists): {store.name}')

        self.stdout.write(self.style.SUCCESS(f'\nDone. Created {created} new store(s).'))
