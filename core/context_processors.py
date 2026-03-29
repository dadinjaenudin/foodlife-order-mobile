def cart_processor(request):
    cart = request.session.get('cart', {})
    cart_count = sum(item['quantity'] for item in cart.values())
    cart_total = sum(item['price'] * item['quantity'] for item in cart.values())

    table_session = request.session.get('table_session', {})

    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
        'cart': cart,
        'table_session': table_session,
    }
