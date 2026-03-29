from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
import json
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
import uuid
from datetime import timedelta
from .models import Tenant, Product, Order, OrderItem, Payment, Category, ProductCategory


def home(request):
    categories = Category.objects.all()
    tenants = Tenant.objects.filter(is_open=True)
    featured_products = Product.objects.filter(is_featured=True, is_available=True).select_related('tenant')[:8]
    best_sellers = Product.objects.filter(is_best_seller=True, is_available=True).select_related('tenant')[:6]

    category_filter = request.GET.get('category')
    search_query = request.GET.get('q', '')

    if category_filter:
        tenants = tenants.filter(category__id=category_filter)
    if search_query:
        tenants = tenants.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    context = {
        'categories': categories,
        'tenants': tenants,
        'featured_products': featured_products,
        'best_sellers': best_sellers,
        'category_filter': category_filter,
        'search_query': search_query,
    }
    return render(request, 'core/home.html', context)


def tenant_detail(request, slug):
    tenant = get_object_or_404(Tenant, slug=slug)
    products = Product.objects.filter(tenant=tenant, is_available=True)
    product_categories = ProductCategory.objects.filter(tenant=tenant)

    category_filter = request.GET.get('cat')
    search_query = request.GET.get('q', '')

    if category_filter:
        products = products.filter(category__id=category_filter)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Group products by category
    categorized_products = {}
    for cat in product_categories:
        cat_products = products.filter(category=cat)
        if cat_products.exists():
            categorized_products[cat] = cat_products

    # Uncategorized products
    uncategorized = products.filter(category__isnull=True)
    if uncategorized.exists():
        categorized_products['Lainnya'] = uncategorized

    context = {
        'tenant': tenant,
        'products': products,
        'product_categories': product_categories,
        'categorized_products': categorized_products,
        'category_filter': category_filter,
        'search_query': search_query,
    }
    return render(request, 'core/tenant_detail.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(
        tenant=product.tenant,
        is_available=True
    ).exclude(pk=pk)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'core/product_detail.html', context)


@require_POST
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))
    notes = request.POST.get('notes', '')

    product = get_object_or_404(Product, pk=product_id)

    cart = request.session.get('cart', {})

    cart_key = str(product_id)
    if cart_key in cart:
        cart[cart_key]['quantity'] += quantity
    else:
        cart[cart_key] = {
            'product_id': product_id,
            'product_name': product.name,
            'tenant_id': product.tenant.id,
            'tenant_name': product.tenant.name,
            'tenant_slug': product.tenant.slug,
            'price': float(product.price),
            'quantity': quantity,
            'notes': notes,
            'image': product.image.url if product.image else '',
        }

    request.session['cart'] = cart
    request.session.modified = True

    cart_count = sum(item['quantity'] for item in cart.values())
    cart_total = sum(item['price'] * item['quantity'] for item in cart.values())

    if request.headers.get('HX-Request'):
        return HttpResponse(f'''
            <div class="flex items-center gap-2 text-green-600 font-semibold">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
                Ditambahkan ke keranjang!
            </div>
            <script>
                document.getElementById('cart-count').textContent = '{cart_count}';
                document.getElementById('cart-total-header').textContent = 'Rp {int(cart_total):,}'.replace(/,/g, '.');
                showCartNotification('{product.name}');
            </script>
        ''')

    return JsonResponse({'success': True, 'cart_count': cart_count, 'cart_total': cart_total})


@require_POST
def update_cart(request):
    product_id = str(request.POST.get('product_id'))
    action = request.POST.get('action')

    cart = request.session.get('cart', {})

    if product_id in cart:
        if action == 'increase':
            cart[product_id]['quantity'] += 1
        elif action == 'decrease':
            if cart[product_id]['quantity'] > 1:
                cart[product_id]['quantity'] -= 1
            else:
                del cart[product_id]
        elif action == 'remove':
            del cart[product_id]

    request.session['cart'] = cart
    request.session.modified = True

    cart_count = sum(item['quantity'] for item in cart.values())
    cart_total = sum(item['price'] * item['quantity'] for item in cart.values())

    if request.headers.get('HX-Request'):
        return render(request, 'core/partials/cart_items.html', {
            'cart': cart,
            'cart_count': cart_count,
            'cart_total': cart_total,
        })

    return redirect('cart')


def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    subtotal = 0

    # Group by tenant
    tenants_in_cart = {}
    for key, item in cart.items():
        tenant_id = item['tenant_id']
        if tenant_id not in tenants_in_cart:
            tenants_in_cart[tenant_id] = {
                'tenant_name': item['tenant_name'],
                'items': []
            }
        tenants_in_cart[tenant_id]['items'].append({**item, 'key': key})
        subtotal += item['price'] * item['quantity']

    service_fee = 2000
    total = subtotal + service_fee

    context = {
        'cart': cart,
        'tenants_in_cart': tenants_in_cart,
        'subtotal': subtotal,
        'service_fee': service_fee,
        'total': total,
    }
    return render(request, 'core/cart.html', context)


def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')

    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    service_fee = 2000
    total = subtotal + service_fee

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')
        customer_email = request.POST.get('customer_email', '')
        table_number = request.POST.get('table_number', '')
        notes = request.POST.get('notes', '')
        payment_method = request.POST.get('payment_method', 'qris')

        # Create order
        order = Order.objects.create(
            session_key=request.session.session_key or 'anonymous',
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            table_number=table_number,
            notes=notes,
            subtotal=subtotal,
            service_fee=service_fee,
            total=total,
        )

        # Create order items
        for key, item in cart.items():
            product = Product.objects.get(pk=item['product_id'])
            tenant = Tenant.objects.get(pk=item['tenant_id'])
            OrderItem.objects.create(
                order=order,
                product=product,
                tenant=tenant,
                quantity=item['quantity'],
                price=item['price'],
                notes=item.get('notes', ''),
            )

        # Create payment
        payment = Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=total,
            expired_at=timezone.now() + timedelta(minutes=15),
        )

        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True

        return redirect('payment', order_id=order.id)

    context = {
        'cart': cart,
        'subtotal': subtotal,
        'service_fee': service_fee,
        'total': total,
    }
    return render(request, 'core/checkout.html', context)


def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payment = get_object_or_404(Payment, order=order)

    # Generate QR code for QRIS
    qr_data = f"QRIS|{order.order_number}|{int(order.total)}"
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    context = {
        'order': order,
        'payment': payment,
        'qr_base64': qr_base64,
        'items': order.items.all().select_related('product', 'tenant'),
    }
    return render(request, 'core/payment.html', context)


@require_POST
def confirm_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    payment = get_object_or_404(Payment, order=order)

    payment.status = 'success'
    payment.paid_at = timezone.now()
    payment.transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
    payment.save()

    order.status = 'paid'
    order.save()

    return redirect('order_success', order_id=order.id)


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all().select_related('product', 'tenant')

    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'core/order_success.html', context)


def order_status(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    items = order.items.all().select_related('product', 'tenant')
    context = {
        'order': order,
        'items': items,
    }
    return render(request, 'core/order_status.html', context)


def search(request):
    query = request.GET.get('q', '')
    products = []
    tenants = []

    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_available=True
        ).select_related('tenant')[:20]

        tenants = Tenant.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query),
            is_open=True
        )[:10]

    context = {
        'query': query,
        'products': products,
        'tenants': tenants,
    }
    return render(request, 'core/search.html', context)


def htmx_search_products(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return HttpResponse('')

    products = Product.objects.filter(
        Q(name__icontains=query),
        is_available=True
    ).select_related('tenant')[:5]

    tenants = Tenant.objects.filter(
        Q(name__icontains=query),
        is_open=True
    )[:3]

    return render(request, 'core/partials/search_results.html', {
        'products': products,
        'tenants': tenants,
        'query': query,
    })
