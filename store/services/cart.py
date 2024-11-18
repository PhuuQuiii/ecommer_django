from django.shortcuts import get_object_or_404
from ..models import  *
from .product import (
    get_product_by_id,
)
from decimal import Decimal

def add_cart_session(request, product_id):
    product = get_product_by_id(product_id)
    quantity = request.GET.get('quantity', 1)
    
    try:
        quantity = int(quantity)
        if quantity <= 0:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        cart = {}

    if  str(product_id) in cart:
        cart[str(product_id)]['quantity'] += quantity
    else:
        cart[str(product_id)]  = {
            'quantity': quantity,
            'product_name': product['name'],
        }
    
    request.session['cart'] = cart

def add_cart_user(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = request.GET.get('quantity', 1)
    user = request.user

    try:
        quantity = int(quantity)
        if quantity <= 0:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1

    shopping_cart, created =  ShoppingCart.objects.get_or_create(user=user, product=product)
    if not created:
        shopping_cart.quantity += quantity
    else:
            shopping_cart.quantity = quantity
    shopping_cart.save()

def update_cart_session(request):
    if request.method == 'GET':
        cart_items = request.GET.getlist('cart')
        cart_data = request.session.get('cart', {})
        print(cart_items)
        print(request.session['cart'])

        for item in cart_items:
            product_id, quantity = item.split(',')
            quantity = int(quantity) 

            if product_id in cart_data:
                if quantity > 0:
                    cart_data[product_id]['quantity'] = quantity
                else:
                    del cart_data[product_id]
            else:
                cart_data[product_id] = {
                    'quantity': quantity,
                    'product_name': 'Unknown Product'
                }

        request.session['cart'] = cart_data

def update_cart_user(request):
    if request.method == 'GET':
        cart_items = request.GET.getlist('cart')
        user = request.user
        
        for item in cart_items:
            product_id, quantity = item.split(',')
            quantity = int(quantity)
            if (quantity > 0):
                shopping_cart = ShoppingCart.objects.get(user=user, product_id=product_id)
                shopping_cart.quantity = quantity
                shopping_cart.save()
            else:
                ShoppingCart.objects.filter(user=user, product_id=product_id).delete()

def sync_cart_from_session_to_user(request):
    user = request.user
    cart_session = request.session.get('cart', {})

    for product_id, item_data in cart_session.items():
        product = get_object_or_404(Product, id=product_id)
        quantity = item_data.get('quantity', 1)
        
        cart_item, created = ShoppingCart.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity  
            cart_item.save()

    request.session['cart'] = {}

def countCart(request, userId):
    if userId:
        count = ShoppingCart.objects.filter(user_id=userId).count()
    else:
        cart = request.storage.get('cartCount', {})
        count = len(cart)
    return count
