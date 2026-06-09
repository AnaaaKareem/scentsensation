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
    ProductVote, ProductImages,
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
        for row in notes_data:
            nid = int(row['id'].replace('n', '')) if row['id'].replace('n', '').isdigit() else None
            if nid:
                note, _ = FragranceNote.objects.get_or_create(
                    note_id=nid,
                    defaults={
                        'name': row.get('name', ''),
                        'latin_name': row.get('latin_name', ''),
                        'group': row.get('group', ''),
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

        for row in fragrances_data:
            pid = int(row['pid']) if row['pid'].isdigit() else None
            if not pid:
                continue

            brand_name, bf_id = parse_brand(row.get('brand', ''))
            rating_avg, rating_count = parse_rating(row.get('rating', ''))
            gender_raw = row.get('gender', '')
            gender = GENDER_MAP.get(gender_raw, 'Unisex')

            # Get or create brand
            brand_obj = brand_map.get(bf_id) if bf_id else None

            product = Products.objects.create(
                brand=brand_name,
                product_name=row.get('name', ''),
                description=row.get('description', ''),
                price=0,  # Will be updated from Mazaya/Faces data later
                region='US',
                fragrantica_id=pid,
                fragrantica_url=row.get('url', ''),
                release_year=int(row['year']) if row.get('year', '').isdigit() else None,
                main_photo_url=row.get('main_photo', ''),
                rating_avg=rating_avg,
                rating_count=rating_count,
                reviews_count=int(row['reviews_count']) if row.get('reviews_count', '').isdigit() else None,
            )
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

        # Step 6: Summary
        self.stdout.write('\n[7/7] Summary:')
        self.stdout.write(f'  Products: {Products.objects.count()}')
        self.stdout.write(f'  ProductNotes: {ProductNote.objects.count()}')
        self.stdout.write(f'  ProductAccords: {ProductAccord.objects.count()}')
        self.stdout.write(f'  ProductPerfumers: {ProductPerfumer.objects.count()}')
        self.stdout.write(f'  ProductVotes: {ProductVote.objects.count()}')
        self.stdout.write(f'  ProductImages: {ProductImages.objects.count()}')
        self.stdout.write(f'  Brands: {Brand.objects.count()}')
        self.stdout.write(f'  FragranceNotes: {FragranceNote.objects.count()}')
        self.stdout.write(f'  FragranceAccords: {FragranceAccord.objects.count()}')
        self.stdout.write(f'  Perfumers: {Perfumer.objects.count()}')

        self.stdout.write(self.style.SUCCESS('\n=== Seeding Complete ==='))
