from django.contrib import admin
from django.contrib.auth.models import User
from .models import (
    PaymentType,
    Discount,
    ProductCategory,
    ProductBrand,
    Product,
    ProductReview,
    ShoppingCart,
    ShippingAddress,
    Order,
    OrderItem,
    Profile, 
    Payment_VNPay

)

# Đăng ký các model hiện có
admin.site.register(PaymentType)
admin.site.register(Payment_VNPay)
admin.site.register(Discount)
admin.site.register(ProductCategory)
admin.site.register(ProductBrand)
admin.site.register(Product)
admin.site.register(ProductReview)
admin.site.register(ShoppingCart)
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Profile)

# Mix profile info and user info
class ProfileInline(admin.StackedInline):
    model = Profile

# Extend User Model
class UserAdmin(admin.ModelAdmin):
    model = User
    field = ["username", "first_name", "last_name", "email"]
    inlines = [ProfileInline]

class OrderItemInline(admin.StackedInline):
    model =  OrderItem
    extra = 0
# Extend our model order
class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    field = ["user, full_name", "email", "shipping_address", "amount_paid", "date_ordered", "shipped", "date_shipped"]
    inlines = [OrderItemInline]

# Unregister the old way
admin.site.unregister(User)

# Re-Register the new way
admin.site.register(User, UserAdmin)

# Unregister order model
admin.site.unregister(Order)
# Re-Register our order and Orderadmin
admin.site.register(Order, OrderAdmin)
