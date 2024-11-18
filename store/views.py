from django.template import loader
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
import logging
import json
from.models import *
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from django.db import IntegrityError
from django.shortcuts import redirect, render
from decimal import Decimal
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login as auth_login


from .services.product import (
    get_latest_products,
    get_deal_products,
    get_product_by_id,
    get_products_by_category,
    get_products_by_brand,
    get_products_by_brand_and_category,
    get_products_all
)
from .services.cart import (
    add_cart_session,
    add_cart_user,
    update_cart_session,
    update_cart_user,
    countCart
)
from decimal import Decimal 
# from .forms import UserRegistrationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm, ShippingForm, PaymentForm
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
import hashlib
import hmac
import urllib
import urllib.parse
import urllib.request
import random
import requests
from datetime import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
# from django.utils.http import urlquote


from django.views.decorators.csrf import csrf_protect
from .account_tokens import account_activation_token
from django.core.mail import EmailMessage

from store.forms import PaymentForm
from store.vnpay import vnpay


def home(request):
    user_id = request.session.get('user_id')
    # user = User.objects.get(id=user_id)
    products_latest = get_latest_products(8)
    products_deal = get_deal_products(9) 
    context = {
        'products_latest': products_latest,
        'products_deal': products_deal,
    }
    return render(request, 'home.html', context)

    template = loader.get_template('home.html')
    return HttpResponse(template.render(context, request))
def contact(request):
    return render(request, 'contact.html', {})

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Kiểm tra xem username và password có được nhập không
        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return redirect('login')

        # Xác thực người dùng
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Kiểm tra nếu tài khoản bị vô hiệu hóa
            if not user.is_active:
                messages.error(request, "Your account has been disabled. Please contact support.")
                return redirect('login')

            # Đăng nhập thành công
            auth_login(request, user)
            # Lưu thông tin người dùng vào session
            request.session['user_id'] = user.id
            request.session['email'] = user.email
            messages.success(request, "You have logged in successfully!")
            
            # Lấy số lượng giỏ hàng và lưu vào session
            cart_count = countCart(request, user.id)
            request.session['cartCount'] = cart_count

            print("Session Data:", request.session.items())


            return redirect('home')
        
        else:
            # Nếu không tìm thấy người dùng với thông tin đã nhập
            messages.error(request, "Invalid username or password. Please try again.")
            return redirect('login')
    else:
        # Trả về trang đăng nhập cho request GET
        return render(request, 'login.html', {})

def user_logout(request):
    # logout(request)
    auth_logout(request)
    messages.success(request, ("You have been logged out ... Thanks"))
    return redirect('home')

def activate(request, uidb64, token):
    # User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        print(f"Error during user retrieval: {e}")
        user = None
        messages.error(request, f"Error during user retrieval: {str(e)}")
        
        
    # Nếu người dùng tồn tại và token hợp lệ, kích hoạt tài khoản
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        
        # Đăng nhập người dùng ngay lập tức sau khi kích hoạt
        auth_login(request, user)

        messages.success(request, "Account activated successfully! You can now log in.")
        return redirect('update_profile')
    else:
        messages.error(request, "The activation link is invalid!")
        return redirect('login')

def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user}, please go to your email inbox at {to_email} and click on \
            the received activation link to confirm and complete the registration. Note: Check your spam folder.')

    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')
        
@csrf_protect
def user_register(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        
        if form.is_valid():
            try:
                # Tạo người dùng và mã hóa mật khẩu
                user = form.save(commit=False)  # Chưa lưu vào database
                user.set_password(form.cleaned_data["password1"])  # Mã hóa mật khẩu
                user.is_active = False
                user.save()  # Lưu người dùng vào database với mật khẩu đã mã hóa
                
                activateEmail(request, user, form.cleaned_data.get('email'))
                
                
                # # Thông báo yêu cầu xác thực
                return redirect('register')

                
            except Exception as e:
                # Xử lý lỗi không mong muốn
                messages.error(request, f"An unexpected error occurred: {e}")
                return redirect('register')
                
        else:
            # Hiển thị lỗi cụ thể nếu form không hợp lệ
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            return redirect('register')
    
    else:
        form = SignUpForm()
    return render(request, 'register.html', {'form': form})

def updatePassword(request):
    if request.user.is_authenticated:
        current_user = request.user
        #Did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            # Is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, "Your Password Has Been Updated ")
                auth_login(request, current_user)
                return redirect('profile')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('updatePassword')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, "updatePassword.html", {'form':form})
    else:
        messages.success(request, "You Must Be Logged In To View Page. ")
        return redirect('home')

    

def profile(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()

            auth_login(request, current_user)
            messages.success(request, "User Has Been Updated!!")
            return redirect('home')
        return render(request, "profile.html", {'user_form': user_form})
    else:
        messages.error(request, "You Must Be Logged In To Access That Page!!")
        redirect('home')

def update_profile(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id=request.user.id)
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        if form.is_valid() or shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request, "Your Profile Has Been Updated!!")
            return redirect('home')
        return render(request, "update_profile.html", {'form': form, 'shipping_form': shipping_form})
    else:
        messages.error(request, "You Must Be Logged In To Access That Page!!")
        return redirect('home')


def blog(request):
    return render(request, 'blog.html', {})

def add_cart(request, product_id):
    if not request.user.is_authenticated:
        add_cart_session(request,  product_id)
        return redirect('cart')
    else:
        add_cart_user(request, product_id)
        return redirect('cart')

def update_cart(request):
    if not request.user.is_authenticated:
        update_cart_session(request)
        return redirect('cart')
    else:
        update_cart_user(request)
        return redirect('cart')
    return redirect('cart')
def cart(request):
    if not request.user.is_authenticated:
        cart = request.session.get('cart', {})
        products = []
        total_price = Decimal(0.0)

        for item_id, item_data in cart.items():
            product = get_product_by_id(item_id)
            item_total_price = Decimal(item_data['quantity'])
            total_price += Decimal(item_total_price) * product['discounted_price']
            products.append({
                'id': product['id'],
                'name': product['name'],
                'description': product['description'],
                'discounted_price': product['discounted_price'],
                'stock': product['stock'],
                'quantity': item_total_price,
                'total_price': total_price,
                'image_url': product['image_url'],
                'discount_id': product['discount_id'],
                'created_at': product['created_at'],
            })
        
        context = {
            'products': products,
        }
        return render(request, 'cart.html', context)
    else:
         cart_items = ShoppingCart.objects.filter(user=request.user)
         total_price = Decimal(0.0)  

         products =[]
         for item in cart_items:
            discount_percent = Decimal(item.product.discount.discount_percent) if item.product.discount else Decimal(0)
            discounted_price = item.product.price * (1 - (discount_percent / Decimal(100)))

            item_total_price = discounted_price * item.quantity 
            total_price += Decimal(item_total_price)
            product_data = {
                'id': item.product.id,
                'name': item.product.name,
                'description': item.product.description,
                'discounted_price': discounted_price,
                'stock': item.product.stock,
                'quantity': item.quantity,
                'total_price': total_price,
                'image_url': item.product.image_url.url if item.product.image_url else None,
                'discount_id': item.product.discount.id if item.product.discount else None,
                'created_at': item.product.created_at,
            }
            products.append(product_data)
         context = {
             'products': products,
         }
         return render(request, 'cart.html', context)

logger = logging.getLogger(__name__)
def category(request):
    categories = ProductCategory.objects.all()
    brands = ProductBrand.objects.all().annotate(product_count=Count('product'))

    category_id = request.GET.get('category', None) 
    brand_id = request.GET.get('brand', None)  

    if (category_id and brand_id):
        products = get_products_by_brand_and_category(brand_id,category_id)
    elif (category_id):
        products = get_products_by_category(category_id)
    elif (brand_id):
        products = get_products_by_brand(brand_id)
    else:
        products = get_products_all()
    
    products_deal = get_deal_products(9)
    sort_by = request.GET.get('sort', 'name')
    page_size = request.GET.get('page_size', 6)

    try:
        page_size = int(page_size)
        if page_size not in [6, 12, 24]:
            page_size = 6
    except ValueError:
        page_size = 6

    sorting_options = {
        'name': lambda x: x['name'],
        'name_desc': lambda x: x['name'],
        'discounted_price': lambda x: x['discounted_price'],
        'discounted_price_desc': lambda x: -x['discounted_price'],
    }

    sort_option = sorting_options.get(sort_by, lambda x: x['name'])
    reverse_sort = sort_by.endswith('_desc')

    products.sort(key=sort_option, reverse=reverse_sort)

    paginator = Paginator(products, page_size)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'categories': categories,
        'brands': brands,
        'products_deal': products_deal,
        'page_obj': page_obj,
        'page_size': page_size,
        'sort_by': sort_by,
    }

    return render(request, 'category.html', context)

def checkout(request):
    if not request.user.is_authenticated:
        # Dành cho người dùng chưa đăng nhập
        cart = request.session.get('cart', {})
        products = []
        total_price = Decimal(0.0)

        for item_id, item_data in cart.items():
            product = get_product_by_id(item_id)
            item_quantity = item_data['quantity']
            item_total_price = Decimal(item_quantity) * product['discounted_price']
            total_price += item_total_price
            products.append({
                'id': product['id'],
                'name': product['name'],
                'description': product['description'],
                'discounted_price': product['discounted_price'],
                'stock': product['stock'],
                'quantity': item_quantity,
                'total_price': item_total_price,
                'image_url': product['image_url'],
                'discount_id': product['discount_id'],
                'created_at': product['created_at'],
            })

        # Khởi tạo form vận chuyển cho người dùng chưa đăng nhập
        shipping_form = ShippingForm(request.POST or None)

    else:
        # Dành cho người dùng đã đăng nhập
        cart_items = ShoppingCart.objects.filter(user=request.user)
        products = []
        total_price = Decimal(0.0)

        for item in cart_items:
            discount_percent = Decimal(item.product.discount.discount_percent) if item.product.discount else Decimal(0)
            discounted_price = item.product.price * (1 - (discount_percent / Decimal(100)))
            item_total_price = discounted_price * item.quantity
            total_price += item_total_price
            products.append({
                'id': item.product.id,
                'name': item.product.name,
                'description': item.product.description,
                'discounted_price': discounted_price,
                'stock': item.product.stock,
                'quantity': item.quantity,
                'total_price': item_total_price,
                'image_url': item.product.image_url.url if item.product.image_url else None,
                'discount_id': item.product.discount.id if item.product.discount else None,
                'created_at': item.product.created_at,
            })

        # Lấy địa chỉ giao hàng của người dùng và khởi tạo form
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

    context = {
        'products': products,
        'total_price': total_price,
        'shipping_form': shipping_form,
    }
    return render(request, 'checkout.html', context)

def confirmation(request):
    return render(request, 'confirmation.html', {})

def elements(request):
    return render(request, 'elements.html', {})

def single_blog(request):
    return render(request, 'single_blog.html', {})

def single_product(request):
    id = request.GET.get('id')
    product = get_product_by_id(id)
    products_deal = get_deal_products(9)

    context = {
        'product': product,
        'products_deal': products_deal,
    }
    return render(request, 'single_product.html', context)

def tracking(request):
    return render(request, 'tracking.html', {})

def deleteCart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not request.user.is_authenticated:
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
            request.session['cart'] = cart 
        return redirect('cart')
    else:
        try:
            shopping_cart = ShoppingCart.objects.get(user=request.user, product=product)
            shopping_cart.delete()  
        except ShoppingCart.DoesNotExist:
            pass 
        return redirect('cart')

def product_search(request):
    if request.method == "POST":
        query = request.POST['query']
        query = Product.objects.filter(name__icontains=query)
        if not query:
            messages.success(request, "Sản phẩm không tồn tại!")
            return render(request, "product_search.html", {})
        else:
            return render(request, "product_search.html", {'query': query})
    else:
        return render(request, "product_search.html", {})

def payment_success(request):
    return render(request, 'payment_success.html', {})

def billing_info(request):
    if request.POST:
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        # Regular or VIP user distinction
        if not request.user.is_authenticated:
            # For non-logged-in users
            cart = request.session.get('cart', {})
            products = []
            total_price = Decimal(0.0)

            for item_id, item_data in cart.items():
                product = get_product_by_id(item_id)
                item_quantity = item_data['quantity']
                item_total_price = Decimal(item_quantity) * product['discounted_price']
                total_price += item_total_price
                products.append({
                    'id': product['id'],
                    'name': product['name'],
                    'description': product['description'],
                    'discounted_price': product['discounted_price'],
                    'stock': product['stock'],
                    'quantity': item_quantity,
                    'total_price': item_total_price,
                    'image_url': product['image_url'],
                    'discount_id': product['discount_id'],
                    'created_at': product['created_at'],
                })

            # Non-logged-in user shipping form
            shipping_form = ShippingForm(request.POST or None)
            billing_form = PaymentForm()

        else:
            # For logged-in users
            cart_items = ShoppingCart.objects.filter(user=request.user)
            products = []
            total_price = Decimal(0.0)

            for item in cart_items:
                discount_percent = Decimal(item.product.discount.discount_percent) if item.product.discount else Decimal(0)
                discounted_price = item.product.price * (1 - (discount_percent / Decimal(100)))
                item_total_price = discounted_price * item.quantity
                total_price += item_total_price
                products.append({
                    'id': item.product.id,
                    'name': item.product.name,
                    'description': item.product.description,
                    'discounted_price': discounted_price,
                    'stock': item.product.stock,
                    'quantity': item.quantity,
                    'total_price': item_total_price,
                    'image_url': item.product.image_url.url if item.product.image_url else None,
                    'discount_id': item.product.discount.id if item.product.discount else None,
                    'created_at': item.product.created_at,
                })

            # Get user's shipping address and initialize form
            shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
            shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
            billing_form = PaymentForm()

        # Store order ID and total price in session
        order_id = datetime.now().strftime('%Y%m%d%H%M%S')
        request.session['order_id'] = order_id
        request.session['total_price'] = float(total_price)

        context = {
            'products': products,
            'total_price': total_price,
            'shipping_form': shipping_form,
            'shipping_info': request.POST,
            'billing_form': billing_form
        }
        return render(request, 'billing_info.html', context)
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def process_order(request): 
    if request.POST:
        order_id = request.session.get('order_id')
        
        if not order_id:
            messages.error(request, "Không tìm thấy mã đơn hàng.")
            return redirect('billing_info')
        
        # Kiểm tra giỏ hàng và tính tổng giá trị
        if not request.user.is_authenticated:
            cart = request.session.get('cart', {})
            products = []
            total_price = Decimal(0.0)

            for item_id, item_data in cart.items():
                product = get_product_by_id(item_id)
                if product is None:
                    print(f"Product with ID {item_id} not found.")
                    continue

                item_quantity = item_data['quantity']
                item_total_price = Decimal(item_quantity) * product['price']  # Sử dụng product['price']
                total_price += item_total_price
                products.append({
                    'id': product['id'],
                    'name': product['name'],
                    'price': product['price'],  # Bỏ discounted_price
                    'quantity': item_quantity,
                    'total_price': item_total_price,
                })
                print(f"Adding product {product['name']} to order with quantity {item_quantity}.")

        else:
            cart_items = ShoppingCart.objects.filter(user=request.user)
            products = []
            total_price = Decimal(0.0)

            for item in cart_items:
                item_total_price = item.product.price * item.quantity  # Sử dụng price
                total_price += item_total_price
                products.append({
                    'id': item.product.id,
                    'name': item.product.name,
                    'price': item.product.price,  # Bỏ discounted_price
                    'quantity': item.quantity,
                    'total_price': item_total_price,
                })
                print(f"Adding product {item.product.name} to order with quantity {item.quantity}.")

        my_shipping = request.session.get('my_shipping')
        if not my_shipping:
            messages.error(request, "Thông tin vận chuyển không có trong session.")
            return redirect('billing_info')

        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address = f"{my_shipping['shipping_address1']} {my_shipping['shipping_address2']}, {my_shipping['shipping_city']}, {my_shipping['shipping_state']}, {my_shipping['shipping_zipcode']}, {my_shipping['shipping_country']}"

        try:
            if request.user.is_authenticated:
                user = request.user
                create_order = Order(id=order_id, user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=total_price)
                create_order.save()
                print(f"Order created for user {user.username} with ID {order_id}.")
                
                for product in products:
                    OrderItem.objects.create(order=create_order, product_id=product['id'], user=user, quantity=product['quantity'], price=product['price'])
                    print(f"OrderItem created for product {product['name']} with quantity {product['quantity']}.")
                ShoppingCart.objects.filter(user=user).delete()

            else:
                create_order = Order(id=order_id, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=total_price)
                create_order.save()
                print(f"Order created for guest user with ID {order_id}.")

                for product in products:
                    OrderItem.objects.create(order=create_order, product_id=product['id'], quantity=product['quantity'], price=product['price'])
                    print(f"OrderItem created for product {product['name']} with quantity {product['quantity']}.")
                request.session.pop('cart', None)

            messages.success(request, "Order Placed!")
            return redirect('home')

        except IntegrityError as e:
            print(f"Error creating order or order item: {e}")
            messages.error(request, "Có lỗi xảy ra khi xử lý đơn hàng.")
            return redirect('billing_info')

    else:
        messages.error(request, "Access Denied")
        return redirect('home')


def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        return render(request, "not_shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        return render(request, "shipped_dash.html", {"orders":orders})
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(id=pk)
        items = OrderItem.objects.filter(order=pk)
        return render(request, 'orders.html', {"order": order, "items": items})
    
    else:
        messages.success(request, "Access Denied")
        return redirect('home')

def shipped(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(id=pk)
        order.shipped = True
        order.save()
        messages.success(request, "Order ship success!")
        return redirect('not_shipped_dash')
    else:
        messages.warning(request, "Access Denied")
        return redirect('home')
    
def unShipped(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        order = Order.objects.get(id=pk)
        order.shipped = False
        order.save()
        messages.warning(request, "Order Unship success!")
        return redirect('shipped_dash')
    else:
        messages.warning(request, "Access Denied")
        return redirect('home')
    

def index(request):
    return render(request, "payment/index.html", {"title": "Danh sách demo"})


def hmacsha512(key, data):
    byteKey = key.encode('utf-8')
    byteData = data.encode('utf-8')
    return hmac.new(byteKey, byteData, hashlib.sha512).hexdigest()

def payment(request):
    if request.method == 'POST':
        # Get order ID and amount from session
        order_id = request.session.get('order_id')
        amount = request.session.get('total_price', 0)  # Đảm bảo giá trị mặc định là 0 nếu không có total_price
        
        form = PaymentForm(request.POST)
        if form.is_valid() and order_id and amount:
            order_type = form.cleaned_data['order_type']
            order_desc = form.cleaned_data['order_desc']
            bank_code = form.cleaned_data['bank_code']
            language = form.cleaned_data['language']
            ipaddr = get_client_ip(request)

            # Build URL for payment
            vnp = vnpay()
            vnp.requestData['vnp_Version'] = '2.1.0'
            vnp.requestData['vnp_Command'] = 'pay'
            vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
            vnp.requestData['vnp_Amount'] = int(amount) * 100  # Amount in cents
            vnp.requestData['vnp_CurrCode'] = 'VND'
            vnp.requestData['vnp_TxnRef'] = order_id
            vnp.requestData['vnp_OrderInfo'] = order_desc
            vnp.requestData['vnp_OrderType'] = order_type

            vnp.requestData['vnp_Locale'] = language if language else 'vn'
            if bank_code:
                vnp.requestData['vnp_BankCode'] = bank_code

            vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
            vnp.requestData['vnp_IpAddr'] = ipaddr
            vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL

            vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
            return redirect(vnpay_payment_url)
        else:
            print("Form input not valid or missing order details")
    else:
        # Truyền giá trị total_price vào context nếu người dùng truy cập trang thanh toán mà không có POST
        total_price = request.session.get('total_price', 0)
        return render(request, "payment/payment.html", {"title": "Thanh toán", "total_price": total_price})


def payment_ipn(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = inputData['vnp_Amount']
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Your code here
            firstTimeUpdate = True
            totalamount = True
            if totalamount:
                if firstTimeUpdate:
                    if vnp_ResponseCode == '00':
                        print('Payment Success. Your code implement here')
                    else:
                        print('Payment Error. Your code implement here')

                    # Return VNPAY: Merchant update success
                    result = JsonResponse({'RspCode': '00', 'Message': 'Confirm Success'})
                else:
                    # Already Update
                    result = JsonResponse({'RspCode': '02', 'Message': 'Order Already Update'})
            else:
                # invalid amount
                result = JsonResponse({'RspCode': '04', 'Message': 'invalid amount'})
        else:
            # Invalid Signature
            result = JsonResponse({'RspCode': '97', 'Message': 'Invalid Signature'})
    else:
        result = JsonResponse({'RspCode': '99', 'Message': 'Invalid request'})

    return result

def payment_return(request):
    inputData = request.GET
    if inputData:
        vnp = vnpay()  # Instantiate the vnpay object
        vnp.responseData = inputData.dict()
        order_id = inputData.get('vnp_TxnRef')
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_PayDate = inputData.get('vnp_PayDate')

        # Store the payment details in the database
        payment = Payment_VNPay.objects.create(
            order_id=order_id,
            amount=amount,
            order_desc=order_desc,
            vnp_TransactionNo=vnp_TransactionNo,
            vnp_ResponseCode=vnp_ResponseCode,
        )

        if not order_id:
            messages.error(request, "Không tìm thấy mã đơn hàng trong URL trả về.")
            return redirect('home')

        # Validate the response
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":
                my_shipping = request.session.get('my_shipping')
                if not my_shipping:
                    messages.error(request, "Thông tin vận chuyển không có trong session.")
                    return redirect('billing_info')

                full_name = my_shipping['shipping_full_name']
                email = my_shipping['shipping_email']
                shipping_address = f"{my_shipping['shipping_address1']} {my_shipping['shipping_address2']}, {my_shipping['shipping_city']}, {my_shipping['shipping_state']}, {my_shipping['shipping_zipcode']}, {my_shipping['shipping_country']}"

                try:
                    if request.user.is_authenticated:
                        user = request.user
                        order, created = Order.objects.update_or_create(
                            id=order_id,
                            defaults={
                                'user': user,
                                'full_name': full_name,
                                'email': email,
                                'shipping_address': shipping_address,
                                'amount_paid': amount
                            }
                        )
                        cart_items = ShoppingCart.objects.filter(user=user)
                        for item in cart_items:
                            discount_percent = Decimal(item.product.discount.discount_percent) if item.product.discount else Decimal(0)
                            discounted_price = item.product.price * (1 - (discount_percent / Decimal(100)))
                            OrderItem.objects.create(
                                order=order,
                                product=item.product,
                                quantity=item.quantity,
                                price=discounted_price,  # Save discounted price
                                user=user
                            )
                        ShoppingCart.objects.filter(user=user).delete()

                    else:
                        order = Order.objects.create(
                            id=order_id,
                            full_name=full_name,
                            email=email,
                            shipping_address=shipping_address,
                            amount_paid=amount
                        )
                        cart = request.session.get('cart', {})
                        for product_id, product_data in cart.items():
                            product = get_product_by_id(product_id)
                            if product:
                                discount_percent = Decimal(product['discount_percent']) if product['discount_percent'] else Decimal(0)
                                discounted_price = Decimal(product['price']) * (1 - (discount_percent / Decimal(100)))
                                OrderItem.objects.create(
                                    order=order,
                                    product_id=product_id,
                                    quantity=product_data['quantity'],
                                    price=discounted_price,  # Save discounted price
                                    user_id=None
                                )
                            else:
                                print(f"Sản phẩm với ID {product_id} không tồn tại.")
                        request.session.pop('cart', None)

                    request.session['cartCount'] = 0
                    user_email = request.user.email if request.user.is_authenticated else email
                    subject = "Xác nhận đơn hàng thành công"
                    message = f"""
                    Cảm ơn bạn đã đặt hàng!

                    Mã đơn hàng: {order_id}
                    Số tiền: {amount} VND
                    Thông tin: {order_desc}
                    Mã giao dịch: {vnp_TransactionNo}
                    Ngày thanh toán: {vnp_PayDate}

                    Đơn hàng của bạn đã được xác nhận và sẽ được xử lý sớm nhất.
                    """
                    if user_email:
                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            [user_email],
                            fail_silently=False,
                        )

                    return render(request, "payment/payment_return.html", {
                        "title": "Kết quả thanh toán",
                        "result": "Thành công",
                        "order_id": order_id,
                        "amount": amount,
                        "order_desc": order_desc,
                        "vnp_TransactionNo": vnp_TransactionNo,
                        "vnp_ResponseCode": vnp_ResponseCode
                    })

                except IntegrityError as e:
                    print(f"Error creating order or order item: {e}")
                    messages.error(request, "Đơn hàng đã tồn tại hoặc có lỗi xảy ra. Vui lòng thử lại.")
                    return redirect('billing_info')

            else:
                return render(request, "payment/payment_return.html", {
                    "title": "Kết quả thanh toán",
                    "result": "Lỗi",
                    "order_id": order_id,
                    "amount": amount,
                    "order_desc": order_desc
                })

        else:
            return render(request, "payment/payment_return.html", {
                "title": "Kết quả thanh toán",
                "result": "Sai checksum"
            })

    else:
        return render(request, "payment/payment_return.html", {
            "title": "Kết quả thanh toán",
            "result": ""
        })


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

n = random.randint(10**11, 10**12 - 1)
n_str = str(n)
while len(n_str) < 12:
    n_str = '0' + n_str


def query(request):
    if request.method == 'GET':
        return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_Version = '2.1.0'

    vnp_RequestId = n_str
    vnp_Command = 'querydr'
    vnp_TxnRef = request.POST['order_id']
    vnp_OrderInfo = 'kiem tra gd'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode,
        vnp_TxnRef, vnp_TransactionDate, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/query.html", {"title": "Kiểm tra kết quả giao dịch", "response_json": response_json})

def refund(request):
    if request.method == 'GET':
        return render(request, "payment/refund.html", {"title": "Hoàn tiền giao dịch"})

    url = settings.VNPAY_API_URL
    secret_key = settings.VNPAY_HASH_SECRET_KEY
    vnp_TmnCode = settings.VNPAY_TMN_CODE
    vnp_RequestId = n_str
    vnp_Version = '2.1.0'
    vnp_Command = 'refund'
    vnp_TransactionType = request.POST['TransactionType']
    vnp_TxnRef = request.POST['order_id']
    vnp_Amount = request.POST['amount']
    vnp_OrderInfo = request.POST['order_desc']
    vnp_TransactionNo = '0'
    vnp_TransactionDate = request.POST['trans_date']
    vnp_CreateDate = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp_CreateBy = 'user01'
    vnp_IpAddr = get_client_ip(request)

    hash_data = "|".join([
        vnp_RequestId, vnp_Version, vnp_Command, vnp_TmnCode, vnp_TransactionType, vnp_TxnRef,
        vnp_Amount, vnp_TransactionNo, vnp_TransactionDate, vnp_CreateBy, vnp_CreateDate,
        vnp_IpAddr, vnp_OrderInfo
    ])

    secure_hash = hmac.new(secret_key.encode(), hash_data.encode(), hashlib.sha512).hexdigest()

    data = {
        "vnp_RequestId": vnp_RequestId,
        "vnp_TmnCode": vnp_TmnCode,
        "vnp_Command": vnp_Command,
        "vnp_TxnRef": vnp_TxnRef,
        "vnp_Amount": vnp_Amount,
        "vnp_OrderInfo": vnp_OrderInfo,
        "vnp_TransactionDate": vnp_TransactionDate,
        "vnp_CreateDate": vnp_CreateDate,
        "vnp_IpAddr": vnp_IpAddr,
        "vnp_TransactionType": vnp_TransactionType,
        "vnp_TransactionNo": vnp_TransactionNo,
        "vnp_CreateBy": vnp_CreateBy,
        "vnp_Version": vnp_Version,
        "vnp_SecureHash": secure_hash
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        response_json = json.loads(response.text)
    else:
        response_json = {"error": f"Request failed with status code: {response.status_code}"}

    return render(request, "payment/refund.html", {"title": "Kết quả hoàn tiền giao dịch", "response_json": response_json})

def forgetPassword(request):
    return render(request, 'forgetPassword.html', {})
