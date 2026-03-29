from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Category, Tenant, Product, ProductCategory, Order, OrderItem, Payment, Zone, Table


# ─────────────────────────────────────────────────────────────
#  CATEGORY
# ─────────────────────────────────────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']
    search_fields = ['name']


# ─────────────────────────────────────────────────────────────
#  ZONE
# ─────────────────────────────────────────────────────────────

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'description', 'color', 'order', 'is_active', 'table_count']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['order', 'name']

    def table_count(self, obj):
        count = obj.tables.filter(is_active=True).count()
        available = obj.tables.filter(is_active=True, status='available').count()
        occupied = count - available
        return format_html(
            '<span style="color:#16a34a;font-weight:700">{}</span> tersedia / '
            '<span style="color:#dc2626">{}</span> terisi / {} total',
            available, occupied, count
        )
    table_count.short_description = 'Meja'


# ─────────────────────────────────────────────────────────────
#  TABLE
# ─────────────────────────────────────────────────────────────

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = [
        'display_name', 'zone', 'number', 'capacity',
        'status_badge', 'is_active', 'qr_preview', 'qr_download_link',
    ]
    list_filter = ['zone', 'status', 'is_active', 'capacity']
    list_editable = ['is_active']
    search_fields = ['number', 'display_name', 'zone__name']
    ordering = ['zone__order', 'zone', 'number']
    readonly_fields = ['qr_code', 'qr_token', 'qr_preview', 'qr_download_link', 'created_at']

    fieldsets = (
        ('Informasi Meja', {
            'fields': ('zone', 'number', 'display_name', 'capacity', 'notes'),
        }),
        ('Status', {
            'fields': ('status', 'is_active'),
        }),
        ('QR Code', {
            'fields': ('qr_token', 'qr_code', 'qr_preview', 'qr_download_link'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def status_badge(self, obj):
        colors = {
            'available': '#16a34a',
            'occupied': '#dc2626',
            'reserved': '#d97706',
            'unavailable': '#9ca3af',
        }
        labels = {
            'available': '✅ Tersedia',
            'occupied': '🔴 Terisi',
            'reserved': '🟡 Dipesan',
            'unavailable': '⚫ N/A',
        }
        color = colors.get(obj.status, '#9ca3af')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="color:{};font-weight:700">{}</span>', color, label
        )
    status_badge.short_description = 'Status'

    def qr_preview(self, obj):
        if obj.qr_code:
            return format_html(
                '<img src="{}" style="width:80px;height:80px;border:2px solid #e5e7eb;border-radius:8px" />',
                obj.qr_code.url
            )
        return format_html('<span style="color:#9ca3af">Belum ada QR</span>')
    qr_preview.short_description = 'Preview QR'

    def qr_download_link(self, obj):
        if obj.pk:
            url = reverse('table_qr_download', args=[obj.pk])
            return format_html(
                '<a href="{}" target="_blank" style="color:#f97316;font-weight:700;text-decoration:underline">'
                '⬇️ Download QR PNG</a>', url
            )
        return '-'
    qr_download_link.short_description = 'Download QR'

    actions = ['regenerate_qr_codes', 'mark_available', 'mark_unavailable']

    def regenerate_qr_codes(self, request, queryset):
        count = 0
        for table in queryset:
            table.generate_qr_code()
            table.save(update_fields=['qr_code'])
            count += 1
        self.message_user(request, f'✅ QR code berhasil di-generate ulang untuk {count} meja.')
    regenerate_qr_codes.short_description = '🔄 Generate ulang QR code'

    def mark_available(self, request, queryset):
        count = queryset.update(status='available')
        self.message_user(request, f'✅ {count} meja ditandai tersedia.')
    mark_available.short_description = '✅ Tandai Tersedia'

    def mark_unavailable(self, request, queryset):
        count = queryset.update(status='unavailable')
        self.message_user(request, f'⚫ {count} meja ditandai tidak tersedia.')
    mark_unavailable.short_description = '⚫ Tandai Tidak Tersedia'


# ─────────────────────────────────────────────────────────────
#  TENANT & PRODUCT
# ─────────────────────────────────────────────────────────────

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'location', 'rating', 'is_open']
    list_filter = ['category', 'is_open']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_open']


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant']
    list_filter = ['tenant']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'tenant', 'price', 'is_available', 'is_featured', 'is_best_seller']
    list_filter = ['tenant', 'is_available', 'is_featured', 'is_best_seller', 'category']
    search_fields = ['name', 'description']
    list_editable = ['is_available', 'is_featured', 'is_best_seller']


# ─────────────────────────────────────────────────────────────
#  ORDER
# ─────────────────────────────────────────────────────────────

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'tenant', 'quantity', 'price', 'notes']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'customer_name', 'customer_phone',
        'order_type_badge', 'table_info', 'status_badge',
        'total_formatted', 'created_at',
    ]
    list_filter = ['status', 'order_type', 'table__zone', 'created_at']
    search_fields = ['order_number', 'customer_name', 'customer_phone', 'table_number']
    readonly_fields = ['order_number', 'session_key', 'created_at', 'updated_at']
    list_editable = []
    inlines = [OrderItemInline]
    ordering = ['-created_at']

    fieldsets = (
        ('Identitas Pelanggan', {
            'fields': ('customer_name', 'customer_phone', 'customer_email', 'notes'),
        }),
        ('Lokasi / Meja', {
            'fields': ('order_type', 'table', 'table_number'),
        }),
        ('Status & Total', {
            'fields': ('status', 'subtotal', 'service_fee', 'total'),
        }),
        ('Sistem', {
            'fields': ('order_number', 'session_key', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def order_type_badge(self, obj):
        if obj.order_type == 'dine_in':
            return format_html('<span style="color:#16a34a;font-weight:700">🪑 Dine In</span>')
        return format_html('<span style="color:#7c3aed;font-weight:700">🛍️ Pickup</span>')
    order_type_badge.short_description = 'Tipe'

    def table_info(self, obj):
        if obj.order_type == 'dine_in' and obj.table:
            return format_html(
                '<span style="font-weight:700">{} · {}</span>',
                obj.table.zone.name, obj.table.display_name
            )
        elif obj.order_type == 'pickup':
            return 'Ambil di kasir'
        return obj.table_number or '-'
    table_info.short_description = 'Meja / Lokasi'

    def status_badge(self, obj):
        colors = {
            'pending': '#d97706',
            'paid': '#2563eb',
            'processing': '#7c3aed',
            'ready': '#16a34a',
            'completed': '#15803d',
            'cancelled': '#dc2626',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="color:{};font-weight:700">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def total_formatted(self, obj):
        return f"Rp {int(obj.total):,}".replace(',', '.')
    total_formatted.short_description = 'Total'


# ─────────────────────────────────────────────────────────────
#  PAYMENT
# ─────────────────────────────────────────────────────────────

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_method', 'amount_formatted', 'status_badge', 'paid_at', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['order__order_number', 'transaction_id']
    readonly_fields = ['order', 'transaction_id', 'created_at']
    ordering = ['-created_at']

    def amount_formatted(self, obj):
        return f"Rp {int(obj.amount):,}".replace(',', '.')
    amount_formatted.short_description = 'Jumlah'

    def status_badge(self, obj):
        colors = {
            'pending': '#d97706',
            'success': '#16a34a',
            'failed': '#dc2626',
            'expired': '#9ca3af',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="color:{};font-weight:700">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


# ─────────────────────────────────────────────────────────────
#  Admin site customization
# ─────────────────────────────────────────────────────────────
admin.site.site_header = '🍜 FoodCourt Admin'
admin.site.site_title = 'FoodCourt'
admin.site.index_title = 'Kelola FoodCourt'
