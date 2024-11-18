from django.db import models
from django.conf import settings  # Để sử dụng settings.AUTH_USER_MODEL
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


# creat Customer Profile
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(User, auto_now=True)
    phone = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=200, blank=True)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    zipcode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.user.username

#Create a user Profile by default when user signs up
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
    
# Automate the profile thing
post_save.connect(create_profile, sender=User)


#Create a shipping by default when user signs up
def create_shipping(sender, instance, created, **kwargs):
    if created:
        user_shipping = ShippingAddress(user=instance)
        user_shipping.save()
    
# Automate the profile thing
post_save.connect(create_shipping, sender=User)

class PaymentType(models.Model):
    payment_type_name = models.CharField(max_length=50)

    def __str__(self):
        return self.payment_type_name



class Discount(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='uploads/category/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductBrand(models.Model):
    product_brand_name = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='uploads/brand/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_brand_name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, default='Mô tả sản phẩm')
    product_brand = models.ForeignKey(ProductBrand, on_delete=models.SET_NULL, null=True)
    product_category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=11, decimal_places=2)
    stock = models.IntegerField()
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    image_url = models.ImageField(upload_to='uploads/product/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class ProductReview(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.quantity}"


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shipping_full_name = models.CharField(max_length=255)
    shipping_email = models.CharField(max_length=255)
    shipping_address1 = models.CharField(max_length=255)
    shipping_address2 = models.CharField(max_length=255, null=True, blank=True)
    shipping_city = models.CharField(max_length=255)
    shipping_state = models.CharField(max_length=255, null=True, blank=True)
    shipping_zipcode = models.CharField(max_length=255, null=True, blank=True)
    shipping_country = models.CharField(max_length=255)


    class Meta:
        verbose_name_plural = "Shipping Address"
    
    def __str__(self):
        return f'Shipping Address - {str(self.id)}'


class Order(models.Model):
    id = models.CharField(max_length=50, primary_key=True)  # Khóa chính
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=250, default="Unknow")
    email = models.EmailField(default="example@example.com")
    shipping_address = models.TextField(max_length=15000, default="Hcm")
    amount_paid = models.DecimalField(max_digits=20, decimal_places=2)
    date_ordered = models.DateTimeField(auto_now_add=True)
    shipped = models.BooleanField(default=False)
    date_shipped = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f'Order - {self.order_id}'

@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    if instance.pk:  # Kiểm tra nếu đối tượng đã có pk (nghĩa là đang update)
        try:
            obj = sender._default_manager.get(pk=instance.pk)
            if obj and obj.shipped != instance.shipped and instance.shipped:
                instance.date_shipped = timezone.now()
        except sender.DoesNotExist:
            pass  # Bỏ qua nếu không tìm thấy order


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=20, decimal_places = 2)



    def __str__(self):
        return f'Order Item - {str(self.id)}'
    
class Payment_VNPay(models.Model):
    order_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    amount = models.FloatField(default = 8.0, null = True, blank = True)
    order_desc = models.CharField(max_length=255, null=True, blank = True) 
    vnp_TransactionNo = models.CharField(max_length=255, null = True, blank = True)
    vnp_ResponseCode = models.CharField(max_length=255, null = True, blank =True)





