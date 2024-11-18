from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .services.cart import sync_cart_from_session_to_user

@receiver(user_logged_in)
def sync_cart_on_login(sender, request, user, **kwargs):
    sync_cart_from_session_to_user(request)