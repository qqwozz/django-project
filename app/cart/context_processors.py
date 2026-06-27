def cart_processor(request):
    cart = getattr(request, 'cart', None)
    if cart is None:
        return {
            'cart_total_items': 0,
            'cart_subtotal': 0,
        }

    return {
        'cart_total_items': cart.total_items,
        'cart_subtotal': cart.subtotal,
    }
