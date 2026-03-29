from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tenant/<slug:slug>/', views.tenant_detail, name='tenant_detail'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<int:order_id>/', views.payment, name='payment'),
    path('payment/<int:order_id>/confirm/', views.confirm_payment, name='confirm_payment'),
    path('order/<int:order_id>/success/', views.order_success, name='order_success'),
    path('order/status/<str:order_number>/', views.order_status, name='order_status'),
    path('search/', views.search, name='search'),
    path('htmx/search/', views.htmx_search_products, name='htmx_search'),
]
