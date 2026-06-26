#!/usr/bin/env python3
"""
Management command to seed the database with Fragrantica fragrance data.

Downloads the sample dataset from the FragDB GitHub repository and populates:
- FragranceNote (86 notes)
- FragranceAccord (32 accords)
- Brand (9 brands)
- Perfumer (15 perfumers)
- Products (10 fragrances with full enrichment data)
- ProductNotes, ProductAccords, ProductPerfumers, ProductVotes, ProductImages

Usage:
    python manage.py seed_fragrantica
    python manage.py seed_fragrantica --full  # TODO: support full 132K dataset
"""

import csv
import io
import re
import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from store.models import (
    Products, Brand, FragranceNote, FragranceAccord,
    ProductNote, ProductAccord, Perfumer, ProductPerfumer,
    ProductVote, ProductImages, SimilarProduct, Region, ProductVariant
)

# Fragrantica gender mapping: dataset value -> our display value
GENDER_MAP = {
    'gender_for_women': 'Woman',
    'gender_for_men': 'Man',
    'gender_for_women_and_men': 'Unisex',
}

# Fragrantica strength mapping
STRENGTH_MAP = {
    'edp': 'Eau de Parfum',
    'edt': 'Eau de Toilette',
    'parfum': 'Parfum',
    'cologne': 'Eau de Cologne',
    'oil': 'Perfume Oil',
    'mist': 'Body Mist',
    'hair mist': 'Hair Mist',
}

RAW_BASE = "https://raw.githubusercontent.com/FragDB/fragrance-database/main/samples"


def download_csv(filename):
    """Download a pipe-delimited CSV from the FragDB repo."""
    url = f"{RAW_BASE}/{filename}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    reader = csv.DictReader(io.StringIO(resp.text), delimiter='|')
    return list(reader)


def parse_brand(brand_str):
    """Parse 'Mugler;b92' -> (name, fragrantica_brand_id)."""
    parts = brand_str.split(';')
    name = parts[0].strip()
    bf_id = int(parts[1]) if len(parts) > 1 and parts[1].strip().isdigit() else None
    return name, bf_id


def parse_rating(rating_str):
    """Parse '3.55;34253' -> (avg, count)."""
    parts = rating_str.split(';')
    avg = float(parts[0]) if parts[0] else None
    count = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None
    return avg, count


def parse_accords(accords_str):
    """Parse 'a75:100;a59:63' -> [(accord_id, percent), ...]."""
    result = []
    for part in accords_str.split(';'):
        if ':' in part:
            aid, pct = part.split(':')
            # Strip 'a' prefix from accord ID
            aid_num = int(aid.replace('a', '')) if aid.replace('a', '').isdigit() else None
            if aid_num is not None:
                result.append((aid_num, float(pct)))
    return result


def parse_notes_pyramid(pyramid_str):
    """Parse 'top(n2025,0.95,3.65;n138,0.84,...)middle(...)base(...)' -> [(layer, note_id, opacity, weight), ...]."""
    result = []
    # Match each layer block
    layer_pattern = re.compile(r'(top|middle|base)\(([^)]*)\)', re.IGNORECASE)
    for match in layer_pattern.finditer(pyramid_str):
        layer = match.group(1).lower()
        notes_str = match.group(2)
        # Parse individual notes: n2025,0.95,3.65
        for note_part in notes_str.split(';'):
            note_part = note_part.strip()
            if not note_part:
                continue
            parts = note_part.split(',')
            if len(parts) >= 3:
                note_id_str = parts[0].strip()
                # Strip 'n' prefix
                note_id = int(note_id_str.replace('n', '')) if note_id_str.replace('n', '').isdigit() else None
                if note_id is not None:
                    try:
                        opacity = float(parts[1])
                        weight = float(parts[2])
                    except (ValueError, IndexError):
                        opacity = 1.0
                        weight = 1.0
                    result.append((layer, note_id, opacity, weight))
    return result


def parse_perfumers(perfumers_str):
    """Parse 'Olivier Cresp;p39;Yves de Chiris;p158' -> [(name, id), ...]."""
    result = []
    parts = perfumers_str.split(';')
    i = 0
    while i < len(parts):
        name = parts[i].strip()
        pf_id = None
        if i + 1 < len(parts):
            id_str = parts[i + 1].strip()
            pf_id = int(id_str.replace('p', '')) if id_str.replace('p', '').isdigit() else None
        if name:
            result.append((name, pf_id))
        i += 2
    return result


def parse_votes(vote_str):
    """Parse 'like_love:12200:35.65;like_like:8600:25.06' -> [(label, count, percent), ...]."""
    result = []
    for part in vote_str.split(';'):
        if ':' in part:
            segments = part.split(':')
            if len(segments) >= 3:
                label = segments[0].strip()
                try:
                    count = int(segments[1])
                    percent = float(segments[2])
                except (ValueError, IndexError):
                    continue
                result.append((label, count, percent))
    return result


def parse_similar(reminds_str):
    """Parse '12345:1200:648;67890:906:290' -> [(similar_fid, likes, dislikes), ...]."""
    result = []
    for part in reminds_str.split(';'):
        if ':' in part:
            segments = part.split(':')
            if len(segments) >= 3:
                try:
                    similar_fid = int(segments[0])
                    likes = int(segments[1])
                    dislikes = int(segments[2])
                    result.append((similar_fid, likes, dislikes))
                except (ValueError, IndexError):
                    continue
    return result


class Command(BaseCommand):
    help = 'Seed the database with Fragrantica fragrance data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Download and import the full 132K dataset (requires FragDB bundle)',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('=== Seeding Fragrantica Data ==='))

        # Step 1: Clear existing test data
        self.stdout.write('\n[1/7] Clearing existing test data...')
        ProductImages.objects.all().delete()
        ProductVote.objects.all().delete()
        ProductNote.objects.all().delete()
        ProductAccord.objects.all().delete()
        ProductPerfumer.objects.all().delete()
        Products.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('  Cleared all products and related data'))

        # Step 2: Load reference data (notes, accords)
        self.stdout.write('\n[2/7] Loading fragrance notes...')
        notes_data = download_csv('notes.csv')
        note_map = {}  # fragrantica_note_id -> FragranceNote

        # Color map for note groups
        GROUP_COLORS = {
            'Citrus smells': '#FFD700',
            'Flowers': '#FF69B4',
            'Woods and mosses': '#8B4513',
            'Spices': '#CD853F',
            'Sweets and gourmand smells': '#DDA0DD',
            'Fruits, vegetables and nuts': '#FF6347',
            'Resins and balsams': '#8B0000',
            'Mosses and': '#556B2F',
            'Aromatic herbs': '#228B22',
            'Leather': '#8B4513',
            'Tobacco': '#654321',
            'Musks and animalic': '#C0C0C0',
            'Marine and aquatic': '#4682B4',
            'Vanilla and sweet': '#F5DEB3',
            'Fresh and clean': '#87CEEB',
            'Green and herbal': '#6B8E23',
            'Powdery and soft': '#F0E68C',
            'Smoky and leathery': '#696969',
            'Floral notes': '#FF69B4',
            'Woody notes': '#8B4513',
            'Oriental and spicy': '#B22222',
            'Fresh citrus': '#FFD700',
            'Sweet gourmand': '#DDA0DD',
        }

        for row in notes_data:
            nid = int(row['id'].replace('n', '')) if row['id'].replace('n', '').isdigit() else None
            if nid:
                group = row.get('group', '')
                # Find matching color based on keywords in group name
                color = '#888888'
                group_lower = group.lower()
                if 'citrus' in group_lower: color = '#FFD700'
                elif 'flower' in group_lower: color = '#FF69B4'
                elif 'wood' in group_lower or 'moss' in group_lower: color = '#8B4513'
                elif 'spice' in group_lower: color = '#CD853F'
                elif 'sweet' in group_lower or 'gourmand' in group_lower or 'vanilla' in group_lower: color = '#DDA0DD'
                elif 'fruit' in group_lower or 'vegetable' in group_lower or 'nut' in group_lower: color = '#FF6347'
                elif 'resin' in group_lower or 'balsam' in group_lower: color = '#8B0000'
                elif 'leather' in group_lower: color = '#654321'
                elif 'tobacco' in group_lower: color = '#8B4513'
                elif 'musk' in group_lower or 'animal' in group_lower: color = '#A0A0A0'
                elif 'marine' in group_lower or 'aquatic' in group_lower: color = '#4682B4'
                elif 'fresh' in group_lower or 'clean' in group_lower: color = '#87CEEB'
                elif 'green' in group_lower or 'herb' in group_lower or 'fougere' in group_lower: color = '#6B8E23'
                elif 'powder' in group_lower: color = '#F0E68C'
                elif 'smok' in group_lower: color = '#696969'
                elif 'oriental' in group_lower: color = '#B22222'
                elif 'aromatic' in group_lower: color = '#228B22'
                elif 'amber' in group_lower: color = '#DAA520'
                elif 'musk' in group_lower: color = '#C0C0C0'
                note, _ = FragranceNote.objects.get_or_create(
                    note_id=nid,
                    defaults={
                        'name': row.get('name', ''),
                        'latin_name': row.get('latin_name', ''),
                        'group': group,
                        'group_color': color,
                        'odor_profile': row.get('odor_profile', ''),
                        'icon_url': row.get('main_icon', ''),
                    }
                )
                note_map[nid] = note
        self.stdout.write(self.style.SUCCESS(f'  Loaded {len(note_map)} notes'))

        self.stdout.write('\n[3/7] Loading fragrance accords...')
        accords_data = download_csv('accords.csv')
        accord_map = {}  # fragrantica_accord_id -> FragranceAccord
        for row in accords_data:
            aid = int(row['id'].replace('a', '')) if row['id'].replace('a', '').isdigit() else None
            if aid:
                accord, _ = FragranceAccord.objects.get_or_create(
                    accord_id=aid,
                    defaults={
                        'name': row.get('name', ''),
                        'bar_color': row.get('bar_color', ''),
                        'font_color': row.get('font_color', '#FFFFFF'),
                    }
                )
                accord_map[aid] = accord
        self.stdout.write(self.style.SUCCESS(f'  Loaded {len(accord_map)} accords'))

        # Step 3: Load brands
        self.stdout.write('\n[4/7] Loading brands...')
        brands_data = download_csv('brands.csv')
        brand_map = {}  # fragrantica_brand_id -> Brand
        for row in brands_data:
            bf_id = row.get('id', '').replace('b', '')
            name = row.get('name', '').strip()
            if name and bf_id.isdigit():
                brand, created = Brand.objects.get_or_create(
                    name=name,
                    defaults={
                        'slug': name.lower().replace(' ', '-').replace('&', 'and'),
                        'description': row.get('description', ''),
                    }
                )
                brand_map[int(bf_id)] = brand
        self.stdout.write(self.style.SUCCESS(f'  Loaded {len(brand_map)} brands'))

        # Step 4: Load perfumers
        self.stdout.write('\n[5/7] Loading perfumers...')
        perfumers_data = download_csv('perfumers.csv')
        perfumer_map = {}  # fragrantica_perfumer_id -> Perfumer
        for row in perfumers_data:
            pf_id = row.get('id', '').replace('p', '')
            name = row.get('name', '').strip()
            if name and pf_id.isdigit():
                perfumer, _ = Perfumer.objects.get_or_create(
                    perfumer_id=int(pf_id),
                    defaults={
                        'name': name,
                        'photo_url': row.get('photo_url', ''),
                        'company': row.get('company', ''),
                        'bio': row.get('biography', ''),
                    }
                )
                perfumer_map[int(pf_id)] = perfumer
        self.stdout.write(self.style.SUCCESS(f'  Loaded {len(perfumer_map)} perfumers'))

        # Step 5: Load fragrances
        self.stdout.write('\n[6/7] Loading fragrances...')
        fragrances_data = download_csv('fragrances.csv')
        product_map = {}  # fragrantica_pid -> Products

        # Price map (in USD) for known fragrances
        PRICE_MAP = {
            704: 120.0, 1825: 185.0, 16657: 95.0, 33519: 325.0, 17: 110.0,
            31623: 145.0, 430: 85.0, 3747: 75.0, 253: 65.0, 276: 55.0,
        }

        for row in fragrances_data:
            pid = int(row['pid']) if row['pid'].isdigit() else None
            if not pid:
                continue

            brand_name, bf_id = parse_brand(row.get('brand', ''))
            rating_avg, rating_count = parse_rating(row.get('rating', ''))

            # Get or create brand
            brand_obj = brand_map.get(bf_id) if bf_id else None

            # Create regions
            us_region, _ = Region.objects.get_or_create(
                region_code='US',
                defaults={'name': 'United States', 'currency_code': 'USD', 'currency_symbol': '$'}
            )
            uk_region, _ = Region.objects.get_or_create(
                region_code='UK',
                defaults={'name': 'United Kingdom', 'currency_code': 'GBP', 'currency_symbol': '£'}
            )

            product = Products.objects.create(
                brand=brand_name,
                product_name=row.get('name', ''),
                description=row.get('description', ''),
                fragrantica_id=pid,
                fragrantica_url=row.get('url', ''),
                release_year=int(row['year']) if row.get('year', '').isdigit() else None,
                main_photo_url=row.get('main_photo', ''),
                rating_avg=rating_avg,
                rating_count=rating_count,
                reviews_count=int(row['reviews_count']) if row.get('reviews_count', '').isdigit() else None,
            )

            base_price = PRICE_MAP.get(pid, 99.0)

            # Seed multiple variants for US and UK
            # US Variants
            ProductVariant.objects.get_or_create(product=product, size_ml=50, region=us_region, defaults={'price': base_price * 0.7, 'stock': 15})
            ProductVariant.objects.get_or_create(product=product, size_ml=100, region=us_region, defaults={'price': base_price, 'stock': 5})
            ProductVariant.objects.get_or_create(product=product, size_ml=150, region=us_region, defaults={'price': base_price * 1.3, 'stock': 0})

            # UK Variants
            ProductVariant.objects.get_or_create(product=product, size_ml=50, region=uk_region, defaults={'price': base_price * 0.6, 'stock': 22})
            ProductVariant.objects.get_or_create(product=product, size_ml=100, region=uk_region, defaults={'price': base_price * 0.9, 'stock': 18})
            ProductVariant.objects.get_or_create(product=product, size_ml=150, region=uk_region, defaults={'price': base_price * 1.2, 'stock': 40})
            product_map[pid] = product

            # Create ProductNotes (pyramid)
            notes_pyramid = parse_notes_pyramid(row.get('notes_pyramid', ''))
            for layer, note_id, opacity, weight in notes_pyramid:
                note_obj = note_map.get(note_id)
                if note_obj:
                    ProductNote.objects.create(
                        product=product,
                        note=note_obj,
                        layer=layer,
                        opacity=opacity,
                        weight=weight,
                    )

            # Create ProductAccords
            accords = parse_accords(row.get('accords', ''))
            for aid, pct in accords:
                accord_obj = accord_map.get(aid)
                if accord_obj:
                    ProductAccord.objects.create(
                        product=product,
                        accord=accord_obj,
                        percentage=pct,
                    )

            # Create ProductPerfumers
            perfumers = parse_perfumers(row.get('perfumers', ''))
            for pf_name, pf_id in perfumers:
                if pf_id and pf_id in perfumer_map:
                    ProductPerfumer.objects.create(
                        product=product,
                        perfumer=perfumer_map[pf_id],
                    )

            # Create ProductVotes (appreciation)
            for vote_type in ['appreciation', 'longevity', 'sillage', 'season', 'time_of_day', 'price_value', 'gender_votes']:
                vote_str = row.get(vote_type, '')
                if vote_str:
                    for label, count, percent in parse_votes(vote_str):
                        ProductVote.objects.create(
                            product=product,
                            vote_type=vote_type,
                            vote_label=label,
                            votes_count=count,
                            percentage=percent,
                        )

            # Create ProductImages from main_photo and user_photos
            main_photo = row.get('main_photo', '')
            if main_photo:
                ProductImages.objects.create(
                    product=product,
                    image_url=main_photo,
                    is_primary=True,
                )
            # User photos
            user_photos = row.get('user_photoes', '')
            if user_photos:
                for i, url in enumerate(user_photos.split(';')):
                    url = url.strip()
                    if url:
                        ProductImages.objects.create(
                            product=product,
                            image_url=url,
                            is_primary=False,
                        )

        self.stdout.write(self.style.SUCCESS(f'  Loaded {len(product_map)} fragrances'))

        # Step 6: Create similar product relationships
        self.stdout.write('\n[7/7] Creating similar product relationships...')
        similar_count = 0
        for row in fragrances_data:
            pid = int(row['pid']) if row['pid'].isdigit() else None
            if not pid or pid not in product_map:
                continue
            product = product_map[pid]
            reminds_str = row.get('reminds_of', '')
            if reminds_str:
                for similar_fid, likes, dislikes in parse_similar(reminds_str):
                    if similar_fid in product_map:
                        similar_product = product_map[similar_fid]
                        SimilarProduct.objects.get_or_create(
                            product=product,
                            similar_product=similar_product,
                            defaults={'likes': likes, 'dislikes': dislikes},
                        )
                        similar_count += 1
        self.stdout.write(self.style.SUCCESS(f'  Created {similar_count} similar product links'))

        # Step 7: Summary
        self.stdout.write('\n[8/8] Summary:')
        self.stdout.write(f'  Products: {Products.objects.count()}')
        self.stdout.write(f'  ProductNotes: {ProductNote.objects.count()}')
        self.stdout.write(f'  ProductAccords: {ProductAccord.objects.count()}')
        self.stdout.write(f'  ProductPerfumers: {ProductPerfumer.objects.count()}')
        self.stdout.write(f'  ProductVotes: {ProductVote.objects.count()}')
        self.stdout.write(f'  ProductImages: {ProductImages.objects.count()}')
        self.stdout.write(f'  SimilarProducts: {SimilarProduct.objects.count()}')
        self.stdout.write(f'  Brands: {Brand.objects.count()}')
        self.stdout.write(f'  FragranceNotes: {FragranceNote.objects.count()}')
        self.stdout.write(f'  FragranceAccords: {FragranceAccord.objects.count()}')
        self.stdout.write(f'  Perfumers: {Perfumer.objects.count()}')

        self.stdout.write(self.style.SUCCESS('\n=== Seeding Complete ==='))
