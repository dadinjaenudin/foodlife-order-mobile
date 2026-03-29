from django.db import models
from django.utils import timezone
import uuid
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='🍽️')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Zone(models.Model):
    """Zona/area di foodcourt: Lantai 1, Lantai 2, Outdoor, dll."""
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    icon = models.CharField(max_length=10, default='🏢')
    color = models.CharField(max_length=20, default='blue')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def available_tables(self):
        return self.tables.filter(is_active=True, status='available')

    def all_tables(self):
        return self.tables.filter(is_active=True)


class Table(models.Model):
    STATUS_CHOICES = [
        ('available', 'Tersedia'),
        ('occupied', 'Terisi'),
        ('reserved', 'Dipesan'),
        ('unavailable', 'Tidak Tersedia'),
    ]
    CAPACITY_CHOICES = [(i, f'{i} orang') for i in range(1, 13)]

    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='tables')
    number = models.CharField(max_length=10)          # e.g. "A1", "B3", "12"
    display_name = models.CharField(max_length=50)    # e.g. "Meja A1"
    capacity = models.IntegerField(choices=CAPACITY_CHOICES, default=4)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    is_active = models.BooleanField(default=True)
    qr_code = models.ImageField(upload_to='tables/qr/', blank=True, null=True)
    qr_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    notes = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['zone', 'number']
        unique_together = ['zone', 'number']

    def __str__(self):
        return f"{self.zone.name} - {self.display_name}"

    def get_qr_url(self):
        """URL yang akan di-encode di QR code"""
        return f"/table/scan/{self.qr_token}/"

    def generate_qr_code(self):
        """Generate dan simpan QR code image"""
        qr_data = f"FOODCOURT|TABLE|{self.qr_token}|{self.number}"
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#1f2937", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        filename = f"table_qr_{self.zone.name.lower().replace(' ', '_')}_{self.number}.png"
        self.qr_code.save(filename, ContentFile(buffer.read()), save=False)

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new or not self.qr_code:
            self.generate_qr_code()
            super().save(update_fields=['qr_code'])

    @property
    def status_color(self):
        return {
            'available': 'green',
            'occupied': 'red',
            'reserved': 'yellow',
            'unavailable': 'gray',
        }.get(self.status, 'gray')

    @property
    def capacity_icon(self):
        if self.capacity <= 2:
            return '👥'
        elif self.capacity <= 4:
            return '👨‍👩‍👧‍👦'
        elif self.capacity <= 6:
            return '🪑'
        else:
            return '🏟️'


class Tenant(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    logo = models.ImageField(upload_to='tenants/', blank=True, null=True)
    banner = models.ImageField(upload_to='tenants/banners/', blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.5)
    total_reviews = models.IntegerField(default=0)
    min_order = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    delivery_time = models.CharField(max_length=50, default='15-25 menit')
    is_open = models.BooleanField(default=True)
    location = models.CharField(max_length=200, default='Lantai 1')
    slug = models.SlugField(unique=True)
    color_theme = models.CharField(max_length=20, default='orange')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_products(self):
        return self.product_set.filter(is_available=True)


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Product Categories'

    def __str__(self):
        return f"{self.tenant.name} - {self.name}"


class Product(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_spicy = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    calories = models.IntegerField(default=0)
    stock = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tenant.name} - {self.name}"

    def formatted_price(self):
        return f"Rp {int(self.price):,}".replace(',', '.')


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('dine_in', 'Dine In'),
        ('pickup', 'Ambil Sendiri'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Menunggu Pembayaran'),
        ('paid', 'Sudah Dibayar'),
        ('processing', 'Sedang Diproses'),
        ('ready', 'Siap Diambil'),
        ('completed', 'Selesai'),
        ('cancelled', 'Dibatalkan'),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    session_key = models.CharField(max_length=40)
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.CharField(max_length=200, blank=True)

    # Table / Order type
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='dine_in')
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    table_number = models.CharField(max_length=20, blank=True)  # denormalized for display

    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    service_fee = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"FC{timezone.now().strftime('%Y%m%d%H%M%S')}"
        # Denormalize table number for easy display
        if self.table and not self.table_number:
            self.table_number = self.table.display_name
        super().save(*args, **kwargs)

    @property
    def order_type_display_icon(self):
        return '🪑' if self.order_type == 'dine_in' else '🛍️'

    @property
    def location_display(self):
        if self.order_type == 'dine_in' and self.table:
            return f"{self.table.zone.name} · {self.table.display_name}"
        elif self.order_type == 'pickup':
            return 'Ambil di Kasir / Counter'
        return self.table_number or '-'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    def subtotal(self):
        return self.price * self.quantity


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('qris', 'QRIS'),
        ('gopay', 'GoPay'),
        ('ovo', 'OVO'),
        ('dana', 'DANA'),
        ('shopeepay', 'ShopeePay'),
        ('linkaja', 'LinkAja'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Menunggu'),
        ('success', 'Berhasil'),
        ('failed', 'Gagal'),
        ('expired', 'Kadaluarsa'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    qris_image = models.ImageField(upload_to='qris/', blank=True, null=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.order.order_number} - {self.payment_method}"
