from django.utils.deprecation import MiddlewareMixin
from .models import Cart


class CartMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key

        if request.user.is_authenticated:
            request.cart, _ = Cart.objects.get_or_create(user=request.user)
            session_cart = Cart.objects.filter(session_key=session_key).exclude(user=request.user).first()
            if session_cart:
                request.cart.merge_from(session_cart)
        else:
            request.cart, _ = Cart.objects.get_or_create(session_key=session_key)

        return None
