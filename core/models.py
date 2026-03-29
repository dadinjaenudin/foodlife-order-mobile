from django.db import models
from django.utils import timezone
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='🍽️')

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


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
    table_number = models.CharField(max_length=10, blank=True)
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
        super().save(*args, **kwargs)


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
