import re
from decimal import Decimal
from pathlib import Path

from django.core.management.base import BaseCommand

from stock.models import Brand, RollingStock

DATA_DIR = Path(__file__).resolve().parents[4] / 'rolling-stock'
TSV_FILE = DATA_DIR / 'frateschi' / 'rodante.tsv'
DCC_FILE = DATA_DIR / 'locomotivas-dcc.md'


def parse_price(raw):
    """Parse 'R$ 55,99' -> Decimal('55.99')"""
    cleaned = re.sub(r'[R$\s]', '', raw).replace(',', '.')
    return Decimal(cleaned)


def parse_tsv(path):
    records = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            parts = line.rstrip('\n').split('\t')
            if len(parts) < 4:
                continue
            type_code, code, description, qty, *price_parts = parts
            price_raw = price_parts[0] if price_parts else ''
            records.append({
                'type': type_code.strip(),
                'brand_name': 'Frateschi',
                'code': code.strip(),
                'description': description.strip(),
                'quantity': int(qty.strip()),
                'unit_price': parse_price(price_raw) if price_raw.strip() else None,
            })
    return records


def parse_dcc_md(path):
    records = []
    in_table = False
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if '| DCC ID |' in line:
                in_table = True
                continue
            if in_table and line.startswith('|:') or (in_table and '---' in line):
                continue
            if in_table and line.startswith('|'):
                cells = [c.strip() for c in line.strip('|').split('|')]
                if len(cells) < 7:
                    continue
                _, dcc_id, brand_name, model_raw, era, acquired, prototype = cells[:7]
                url_match = re.match(r'\[(.+?)\]\((.+?)\)', model_raw)
                if url_match:
                    code, product_url = url_match.group(1), url_match.group(2)
                else:
                    code, product_url = model_raw, ''
                records.append({
                    'type': 'L',
                    'brand_name': brand_name.strip(),
                    'code': code.strip(),
                    'description': prototype.strip(),
                    'dcc_address': int(dcc_id.strip()) if dcc_id.strip().isdigit() else None,
                    'era': era.strip(),
                    'acquired': acquired.strip(),
                    'prototype': prototype.strip(),
                    'product_url': product_url.strip(),
                })
    return records


class Command(BaseCommand):
    help = 'Import rolling stock data from rodante.tsv and locomotivas-dcc.md'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Preview without writing')

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        tsv_records = parse_tsv(TSV_FILE)
        dcc_records = parse_dcc_md(DCC_FILE)
        all_records = tsv_records + dcc_records

        brand_names = {r['brand_name'] for r in all_records}
        brands = {}
        for name in sorted(brand_names):
            if not dry_run:
                brand, created = Brand.objects.get_or_create(name=name)
                brands[name] = brand
                if created:
                    self.stdout.write(f'  Created brand: {name}')
            else:
                brands[name] = name

        created_count = skipped_count = 0
        for r in all_records:
            brand = brands[r['brand_name']]
            exists = (
                not dry_run
                and RollingStock.objects.filter(
                    code=r['code'],
                    brand=brand,
                    unit_price=r.get('unit_price'),
                ).exists()
            )
            if exists:
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(
                    f"  [{r['type']}] {r['brand_name']} {r['code']} — {r['description']}"
                )
            else:
                RollingStock.objects.create(
                    type=r['type'],
                    brand=brand,
                    code=r['code'],
                    description=r.get('description', ''),
                    quantity=r.get('quantity', 1),
                    unit_price=r.get('unit_price'),
                    era=r.get('era', ''),
                    dcc_address=r.get('dcc_address'),
                    acquired=r.get('acquired', ''),
                    prototype=r.get('prototype', ''),
                    product_url=r.get('product_url', ''),
                )
            created_count += 1

        action = 'Would create' if dry_run else 'Created'
        self.stdout.write(
            self.style.SUCCESS(
                f'{action} {created_count} records ({skipped_count} skipped as duplicates)'
            )
        )
