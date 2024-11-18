from django.shortcuts import get_object_or_404
from ..models import  Product
from decimal import Decimal

def get_products_all():
    products = Product.objects.all()
    products_arr = []
    for product in products:
        discount_percent = Decimal(product.discount.discount_percent) if product.discount else Decimal(0)
        discounted_price = product.price * (1 - (discount_percent / Decimal(100)))

        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'discounted_price': round(discounted_price, 2),
            'stock': product.stock,
            'image_url': product.image_url.url if product.image_url else None,
            'discount_id': product.discount.id if product.discount else None,
        }
        products_arr.append(product_data)
    return products_arr
def get_latest_products(limit):
    products = Product.objects.order_by('-created_at')[:limit]
    products_arr = []
    for product in products:
        discount_percent = Decimal(product.discount.discount_percent) if product.discount else Decimal(0)
        discounted_price = product.price * (1 - (discount_percent / Decimal(100)))

        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'discounted_price': round(discounted_price, 2),
            'stock': product.stock,
            'image_url': product.image_url.url if product.image_url else None,
            'discount_id': product.discount.id if product.discount else None,
        }
        products_arr.append(product_data)
    return products_arr

def get_deal_products(limit):
    products = Product.objects.filter(discount__isnull=False).order_by('-discount__discount_percent')[:limit]
    products_arr = []
    for product in products:
        discount_percent = Decimal(product.discount.discount_percent)
        discounted_price = product.price * (1 - (discount_percent / Decimal(100)))

        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'discounted_price': round(discounted_price, 2),
            'stock': product.stock,
            'image_url': product.image_url.url if product.image_url else None,
            'discount_id': product.discount.id,
        }
        products_arr.append(product_data)
    return products_arr
def get_product_by_id(product_id):
    product = get_object_or_404(Product, id=product_id)
    discount_percent = Decimal(product.discount.discount_percent) if product.discount else Decimal(0)
    discounted_price = product.price * (1 - (discount_percent / Decimal(100)))
    product_data ={
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'discounted_price': discounted_price,
        'stock': product.stock,
        'image_url': product.image_url.url if product.image_url else None,
        'discount_id': product.discount.id if product.discount else None,
        'created_at': product.created_at,
    }

    return product_data
def get_products_by_category(category_id):
    products = Product.objects.select_related('product_category')
    products = products.filter(product_category__id=category_id)
    products_arr = []
    for product in products:
        discount_percent = Decimal(product.discount.discount_percent) if product.discount else Decimal(0)
        discounted_price = product.price * (1 - (discount_percent / Decimal(100)))
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'discounted_price': round(discounted_price, 2),
            'stock': product.stock,
            'image_url': product.image_url.url if product.image_url else None,
            'discount_id': product.discount.id if product.discount else None,
        }
        products_arr.append(product_data)
    return  products_arr

def get_products_by_brand(brand_id):
    products = Product.objects.select_related('product_brand')
    products = products.filter(product_brand_id=brand_id)
    products_arr = []
    for product in products:
        discount_percent = Decimal(product.discount.discount_percent) if product.discount else Decimal(0)
        discounted_price = product.price * (1 - (discount_percent / Decimal(100)))
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'discounted_price': round(discounted_price, 2),
            'stock': product.stock,
            'image_url': product.image_url.url if product.image_url else None,
            'discount_id': product.discount.id if product.discount else None,
        }
        products_arr.append(product_data)
    return  products_arr
def get_products_by_brand_and_category(brand_id, category_id):
    products = Product.objects.select_related('product_brand', 'product_category')
    products =  products.filter(product_brand_id=brand_id, product_category_id=category_id)
    products_arr = []
    for product in products:
        discount_percent = Decimal(product.discount.discount_percent) if product.discount else Decimal(0)
        discounted_price = product.price * (1 - (discount_percent / Decimal(100)))
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'discounted_price': round(discounted_price, 2),
            'stock': product.stock,
            'image_url': product.image_url.url if product.image_url else None,
            'discount_id': product.discount.id if product.discount else None,
        }
        products_arr.append(product_data)
    return  products_arr
