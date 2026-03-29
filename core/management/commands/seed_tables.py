"""
Management command: seed_tables
Membuat Zone dan Table (meja) untuk FoodCourt.

Struktur:
  Zone 1 – Lantai 1 Indoor   : A1–A6, B1–B6  (12 meja)
  Zone 2 – Lantai 2 Indoor   : C1–C6, D1–D4  (10 meja)
  Zone 3 – Area Outdoor      : E1–E5, F1–F5   (10 meja)
  Zone 4 – VIP Room          : V1–V4          (4 meja)
Total: 36 meja, masing-masing dengan QR code unik.
"""

from django.core.management.base import BaseCommand
from core.models import Zone, Table


ZONES = [
    {
        'name': 'Lantai 1 – Indoor',
        'description': 'Area makan dalam ruangan, AC, nyaman untuk keluarga',
        'icon': '🏠',
        'color': 'blue',
        'order': 1,
        'tables': [
            # Row A
            {'number': 'A1', 'display_name': 'Meja A1', 'capacity': 4},
            {'number': 'A2', 'display_name': 'Meja A2', 'capacity': 4},
            {'number': 'A3', 'display_name': 'Meja A3', 'capacity': 4},
            {'number': 'A4', 'display_name': 'Meja A4', 'capacity': 6},
            {'number': 'A5', 'display_name': 'Meja A5', 'capacity': 6},
            {'number': 'A6', 'display_name': 'Meja A6', 'capacity': 2},
            # Row B
            {'number': 'B1', 'display_name': 'Meja B1', 'capacity': 4},
            {'number': 'B2', 'display_name': 'Meja B2', 'capacity': 4},
            {'number': 'B3', 'display_name': 'Meja B3', 'capacity': 4},
            {'number': 'B4', 'display_name': 'Meja B4', 'capacity': 8},
            {'number': 'B5', 'display_name': 'Meja B5', 'capacity': 8},
            {'number': 'B6', 'display_name': 'Meja B6', 'capacity': 2},
        ],
    },
    {
        'name': 'Lantai 2 – Indoor',
        'description': 'Pemandangan ke lantai 1, cocok untuk nongkrong & meeting',
        'icon': '🏢',
        'color': 'purple',
        'order': 2,
        'tables': [
            {'number': 'C1', 'display_name': 'Meja C1', 'capacity': 2},
            {'number': 'C2', 'display_name': 'Meja C2', 'capacity': 2},
            {'number': 'C3', 'display_name': 'Meja C3', 'capacity': 4},
            {'number': 'C4', 'display_name': 'Meja C4', 'capacity': 4},
            {'number': 'C5', 'display_name': 'Meja C5', 'capacity': 6},
            {'number': 'C6', 'display_name': 'Meja C6', 'capacity': 6},
            {'number': 'D1', 'display_name': 'Meja D1', 'capacity': 4},
            {'number': 'D2', 'display_name': 'Meja D2', 'capacity': 4},
            {'number': 'D3', 'display_name': 'Meja D3', 'capacity': 8},
            {'number': 'D4', 'display_name': 'Meja D4', 'capacity': 10},
        ],
    },
    {
        'name': 'Area Outdoor',
        'description': 'Semi-outdoor, taman hijau, angin sepoi-sepoi',
        'icon': '🌳',
        'color': 'green',
        'order': 3,
        'tables': [
            {'number': 'E1', 'display_name': 'Meja E1', 'capacity': 4},
            {'number': 'E2', 'display_name': 'Meja E2', 'capacity': 4},
            {'number': 'E3', 'display_name': 'Meja E3', 'capacity': 4},
            {'number': 'E4', 'display_name': 'Meja E4', 'capacity': 6},
            {'number': 'E5', 'display_name': 'Meja E5', 'capacity': 6},
            {'number': 'F1', 'display_name': 'Meja F1', 'capacity': 2},
            {'number': 'F2', 'display_name': 'Meja F2', 'capacity': 2},
            {'number': 'F3', 'display_name': 'Meja F3', 'capacity': 4},
            {'number': 'F4', 'display_name': 'Meja F4', 'capacity': 4},
            {'number': 'F5', 'display_name': 'Meja F5', 'capacity': 8},
        ],
    },
    {
        'name': 'Ruang VIP',
        'description': 'Ruangan private, cocok untuk acara & rapat',
        'icon': '👑',
        'color': 'yellow',
        'order': 4,
        'tables': [
            {'number': 'V1', 'display_name': 'VIP 1', 'capacity': 8},
            {'number': 'V2', 'display_name': 'VIP 2', 'capacity': 10},
            {'number': 'V3', 'display_name': 'VIP 3', 'capacity': 12},
            {'number': 'V4', 'display_name': 'VIP 4', 'capacity': 12},
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed Zone dan Table (meja) untuk FoodCourt'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Hapus semua zone/table sebelum seed ulang',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('🗑️  Menghapus data zone/table lama...')
            Table.objects.all().delete()
            Zone.objects.all().delete()

        total_zones = 0
        total_tables = 0

        for zone_data in ZONES:
            tables_data = zone_data.pop('tables')
            zone, created = Zone.objects.get_or_create(
                name=zone_data['name'],
                defaults=zone_data,
            )
            if created:
                total_zones += 1
                self.stdout.write(f'  ✅ Zone: {zone.icon} {zone.name}')
            else:
                # Update fields if already exists
                for k, v in zone_data.items():
                    setattr(zone, k, v)
                zone.save()
                self.stdout.write(f'  ↩️  Zone exists: {zone.name} (updated)')

            # Re-attach tables_data for iteration
            zone_data['tables'] = tables_data

            for tdata in tables_data:
                table, t_created = Table.objects.get_or_create(
                    zone=zone,
                    number=tdata['number'],
                    defaults={
                        'display_name': tdata['display_name'],
                        'capacity': tdata['capacity'],
                        'status': 'available',
                    },
                )
                if t_created:
                    total_tables += 1
                    self.stdout.write(
                        f'    🪑 {table.display_name} (kapasitas {table.capacity} org) — QR: {table.qr_token}'
                    )
                else:
                    self.stdout.write(f'    ↩️  {table.display_name} sudah ada, skip.')

        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 Selesai! {total_zones} zone dan {total_tables} meja berhasil dibuat.\n'
            f'   QR code otomatis ter-generate untuk setiap meja baru.\n'
            f'   Lihat daftar QR: /table/qr/all/\n'
            f'   Admin panel: /admin/core/table/'
        ))
