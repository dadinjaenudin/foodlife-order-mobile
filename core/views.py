from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import json
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64
import uuid
from datetime import timedelta
from .models import (
    Tenant, Product, Order, OrderItem, Payment,
    Category, ProductCategory, Zone, Table,
)


# ─────────────────────────────────────────────
#  HELPER: session table state
# ─────────────────────────────────────────────

def _get_table_session(request):
    """Return dict with current table/order-type from session."""
    return request.session.get('table_session', {
        'order_type': None,      # 'dine_in' | 'pickup'
        'table_id': None,
        'table_number': None,
        'table_display': None,
        'zone_name': None,
    })


def _set_table_session(request, order_type, table=None):
    data = {
        'order_type': order_type,
        'table_id': table.id if table else None,
        'table_number': table.number if table else None,
        'table_display': table.display_name if table else None,
        'zone_name': table.zone.name if table else None,
    }
    request.session['table_session'] = data
    request.session.modified = True
    return data


def _clear_table_session(request):
    request.session.pop('table_session', None)
    request.session.modified = True


# ─────────────────────────────────────────────
#  TABLE LANDING — triggered saat buka app
# ─────────────────────────────────────────────

def table_select(request):
    """Halaman pilih meja atau pickup sebelum mulai order."""
    zones = Zone.objects.filter(is_active=True).prefetch_related('tables')
    table_session = _get_table_session(request)
    next_url = request.GET.get('next', '/')

    context = {
        'zones': zones,
        'table_session': table_session,
        'next_url': next_url,
    }
    return render(request, 'core/table_select.html', context)


@require_POST
def table_choose(request):
    """POST: user memilih meja atau pickup mode."""
    order_type = request.POST.get('order_type')  # 'dine_in' | 'pickup'
    table_id = request.POST.get('table_id')
    next_url = request.POST.get('next', '/')

    if order_type == 'pickup':
        _set_table_session(request, 'pickup')
        return redirect(next_url)

    if order_type == 'dine_in' and table_id:
        table = get_object_or_404(Table, pk=table_id, is_active=True)
        if table.status == 'unavailable':
            messages.error(request, f'Maaf, {table.display_name} tidak tersedia.')
            return redirect(f'/table/?next={next_url}')
        _set_table_session(request, 'dine_in', table)
        return redirect(next_url)

    messages.error(request, 'Pilih meja atau mode pickup terlebih dahulu.')
    return redirect(f'/table/?next={next_url}')


def table_scan(request, token):
    """
    URL yang di-embed di QR code masing-masing meja.
    Langsung set session & redirect ke home.
    """
    table = get_object_or_404(Table, qr_token=token, is_active=True)

    if table.status == 'unavailable':
        return render(request, 'core/table_unavailable.html', {'table': table})

    _set_table_session(request, 'dine_in', table)
    messages.success(request, f'Selamat datang di {table.display_name}! Silakan mulai pesan.')
    return redirect('home')


def table_clear(request):
    """Clear table session — ganti meja."""
    next_url = request.GET.get('next', '/table/')
    _clear_table_session(request)
    return redirect(next_url)


# ─────────────────────────────────────────────
#  ADMIN: QR code download per meja
# ─────────────────────────────────────────────

def table_qr_download(request, table_id):
    """Download QR code PNG untuk satu meja (untuk dicetak)."""
    table = get_object_or_404(Table, pk=table_id)
    if table.qr_code:
        with open(table.qr_code.path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='image/png')
            fname = f"QR_Meja_{table.zone.name}_{table.number}.png"
            response['Content-Disposition'] = f'attachment; filename="{fname}"'
            return response
    return HttpResponse('QR not found', status=404)


def table_qr_all(request):
    """Halaman daftar semua QR code meja — untuk admin print."""
    zones = Zone.objects.filter(is_active=True).prefetch_related('tables')
    return render(request, 'core/table_qr_all.html', {'zones': zones})


# ─────────────────────────────────────────────
#  HOME
# ─────────────────────────────────────────────

def home(request):
    table_session = _get_table_session(request)

    # Jika belum pilih meja/pickup, tunda redirect (biarkan browse dulu,
    # cukup tampilkan banner pilih meja di header)
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
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    context = {
        'categories': categories,
        'tenants': tenants,
        'featured_products': featured_products,
        'best_sellers': best_sellers,
        'category_filter': category_filter,
        'search_query': search_query,
        'table_session': table_session,
    }
    return render(request, 'core/home.html', context)


# ─────────────────────────────────────────────
#  TENANT DETAIL
# ─────────────────────────────────────────────

def tenant_detail(request, slug):
    tenant = get_object_or_404(Tenant, slug=slug)
    products = Product.objects.filter(tenant=tenant, is_available=True)
    product_categories = ProductCategory.objects.filter(tenant=tenant)
    table_session = _get_table_session(request)

    category_filter = request.GET.get('cat')
    search_query = request.GET.get('q', '')

    if category_filter:
        products = products.filter(category__id=category_filter)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    categorized_products = {}
    for cat in product_categories:
        cat_products = products.filter(category=cat)
        if cat_products.exists():
            categorized_products[cat] = cat_products
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
        'table_session': table_session,
    }
    return render(request, 'core/tenant_detail.html', context)


# ─────────────────────────────────────────────
#  CART
# ─────────────────────────────────────────────

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
                Ditambahkan!
            </div>
            <script>
                document.getElementById('cart-count').textContent = '{cart_count}';
                showCartNotification('{product.name}');
            </script>
        ''')
    return JsonResponse({'success': True, 'cart_count': cart_count})


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
        tenants_in_cart = _build_tenants_in_cart(cart)
        subtotal = sum(i['price'] * i['quantity'] for i in cart.values())
        return render(request, 'core/partials/cart_items.html', {
            'cart': cart,
            'tenants_in_cart': tenants_in_cart,
            'cart_count': cart_count,
            'cart_total': cart_total,
            'subtotal': subtotal,
            'service_fee': 2000,
            'total': subtotal + 2000,
        })
    return redirect('cart')


def _build_tenants_in_cart(cart):
    tenants_in_cart = {}
    for key, item in cart.items():
        tid = item['tenant_id']
        if tid not in tenants_in_cart:
            tenants_in_cart[tid] = {'tenant_name': item['tenant_name'], 'items': []}
        tenants_in_cart[tid]['items'].append({**item, 'key': key})
    return tenants_in_cart


def cart(request):
    cart = request.session.get('cart', {})
    tenants_in_cart = _build_tenants_in_cart(cart)
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    service_fee = 2000
    total = subtotal + service_fee
    table_session = _get_table_session(request)

    context = {
        'cart': cart,
        'tenants_in_cart': tenants_in_cart,
        'subtotal': subtotal,
        'service_fee': service_fee,
        'total': total,
        'table_session': table_session,
    }
    return render(request, 'core/cart.html', context)


# ─────────────────────────────────────────────
#  CHECKOUT  ← enforces table/pickup
# ─────────────────────────────────────────────

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('home')

    table_session = _get_table_session(request)
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    service_fee = 2000
    total = subtotal + service_fee

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        customer_email = request.POST.get('customer_email', '')
        notes = request.POST.get('notes', '')
        payment_method = request.POST.get('payment_method', 'qris')

        # Validate table/pickup from session (already set before checkout)
        order_type = table_session.get('order_type')
        table_id = table_session.get('table_id')

        if not order_type:
            messages.error(request, 'Pilih meja atau mode pickup terlebih dahulu.')
            return redirect(f'/table/?next=/checkout/')

        table_obj = None
        table_number_str = ''
        if order_type == 'dine_in' and table_id:
            try:
                table_obj = Table.objects.get(pk=table_id, is_active=True)
                table_number_str = table_obj.display_name
            except Table.DoesNotExist:
                messages.error(request, 'Meja tidak valid. Pilih ulang.')
                return redirect(f'/table/?next=/checkout/')
        elif order_type == 'pickup':
            table_number_str = 'Pickup'

        order = Order.objects.create(
            session_key=request.session.session_key or 'anon',
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            notes=notes,
            order_type=order_type,
            table=table_obj,
            table_number=table_number_str,
            subtotal=subtotal,
            service_fee=service_fee,
            total=total,
        )

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

        Payment.objects.create(
            order=order,
            payment_method=payment_method,
            amount=total,
            expired_at=timezone.now() + timedelta(minutes=15),
        )

        request.session['cart'] = {}
        request.session.modified = True

        return redirect('payment', order_id=order.id)

    context = {
        'cart': cart,
        'subtotal': subtotal,
        'service_fee': service_fee,
        'total': total,
        'table_session': table_session,
    }
    return render(request, 'core/checkout.html', context)


# ─────────────────────────────────────────────
#  PAYMENT
# ─────────────────────────────────────────────

def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    pay = get_object_or_404(Payment, order=order)

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
        'payment': pay,
        'qr_base64': qr_base64,
        'items': order.items.all().select_related('product', 'tenant'),
    }
    return render(request, 'core/payment.html', context)


@require_POST
def confirm_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    pay = get_object_or_404(Payment, order=order)

    pay.status = 'success'
    pay.paid_at = timezone.now()
    pay.transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"
    pay.save()

    order.status = 'paid'
    order.save()

    # Update table status to occupied
    if order.table:
        order.table.status = 'occupied'
        order.table.save(update_fields=['status'])

    return redirect('order_success', order_id=order.id)


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all().select_related('product', 'tenant')
    context = {'order': order, 'items': items}
    return render(request, 'core/order_success.html', context)


def order_status(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    items = order.items.all().select_related('product', 'tenant')
    context = {'order': order, 'items': items}
    return render(request, 'core/order_status.html', context)


# ─────────────────────────────────────────────
#  SEARCH
# ─────────────────────────────────────────────

def search(request):
    query = request.GET.get('q', '')
    products, tenants = [], []
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_available=True
        ).select_related('tenant')[:20]
        tenants = Tenant.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_open=True
        )[:10]

    context = {'query': query, 'products': products, 'tenants': tenants}
    return render(request, 'core/search.html', context)


def htmx_search_products(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return HttpResponse('')
    products = Product.objects.filter(Q(name__icontains=query), is_available=True).select_related('tenant')[:5]
    tenants = Tenant.objects.filter(Q(name__icontains=query), is_open=True)[:3]
    return render(request, 'core/partials/search_results.html', {
        'products': products, 'tenants': tenants, 'query': query,
    })
