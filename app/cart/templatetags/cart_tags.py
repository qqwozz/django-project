from django import template
from cart.models import Cart


register = template.Library()


@register.simple_tag(takes_context=True)
def get_cart_count(context):
    request = context['request']
    cart = getattr(request, 'cart', None)
    if cart is None:
        return 0
    return cart.total_items


@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0