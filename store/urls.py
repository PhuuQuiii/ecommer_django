from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    path('updatePassword/', views.updatePassword, name='updatePassword'),
    path('profile/', views.profile, name='profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('category/', views.category, name='category'),
    path('blog/', views.blog, name='blog'),
    path('add-cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('confirmation/', views.confirmation, name='confirmation'),
    path('elements/', views.elements, name='elements'),
    path('single-blog/', views.single_blog, name='single-blog'),
    path('single-product/', views.single_product, name='single-product'),
    path('tracking/', views.tracking, name='tracking'),
    path('contact/', views.contact, name='contact'),
    path('cart/remove/<int:product_id>/', views.deleteCart, name='delete_cart_item'),
    path('search/', views.product_search, name='product_search'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('billing_info/', views.billing_info, name='billing_info'),
    path('process_order/', views.process_order, name='process_order'),
    path('shipped_dash/', views.shipped_dash, name='shipped_dash'),
    path('not_shipped_dash/', views.not_shipped_dash, name='not_shipped_dash'),
    path('orders/<int:pk>', views.orders, name='orders'),
    path('ship_order/<int:pk>', views.shipped, name='ship_order'),
    path('unShip_order/<int:pk>', views.unShipped, name='unShip_order'),
    path('forgetPassword/', views.forgetPassword, name='forgetPassword'),


    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    
    path('pay', views.index, name='index'),
    path('payment', views.payment, name='payment'),
    path('payment_ipn', views.payment_ipn, name='payment_ipn'),
    path('payment_return', views.payment_return, name='payment_return'),
    path('query', views.query, name='query'),
    path('refund', views.refund, name='refund'),
    path('userOrders/', views.user_orders, name='user_orders'),


]

