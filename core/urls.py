from django.urls import path
from . import views

urlpatterns = [
    # ── Home & Tenants ──────────────────────────────────────
    path('', views.home, name='home'),
    path('tenant/<slug:slug>/', views.tenant_detail, name='tenant_detail'),

    # ── Table / Location ────────────────────────────────────
    path('table/', views.table_select, name='table_select'),
    path('table/choose/', views.table_choose, name='table_choose'),
    path('table/scan/<uuid:token>/', views.table_scan, name='table_scan'),
    path('table/clear/', views.table_clear, name='table_clear'),
    path('table/qr/all/', views.table_qr_all, name='table_qr_all'),
    path('table/qr/download/<int:table_id>/', views.table_qr_download, name='table_qr_download'),

    # ── Cart ────────────────────────────────────────────────
    path('cart/', views.cart, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),

    # ── Order flow ──────────────────────────────────────────
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('payment/<int:order_id>/confirm/', views.confirm_payment, name='confirm_payment'),
    path('order/<int:order_id>/success/', views.order_success, name='order_success'),
    path('order/status/<str:order_number>/', views.order_status, name='order_status'),

    # ── Search ──────────────────────────────────────────────
    path('search/', views.search, name='search'),
    path('htmx/search/', views.htmx_search_products, name='htmx_search'),
]
