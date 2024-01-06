from django.db import models
from accounts.models import CustomUser
from myadmin.models import MyProducts,Variant,Color,ProductImages
from django.contrib.auth import get_user_model
from django.utils import timezone
import random
class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, default='')
    pincode = models.CharField(max_length=7)
    locality = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.address}"
    
class cartitems(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(MyProducts, on_delete=models.CASCADE, default=None)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveSmallIntegerField()

    @property
    def total_price(self):
        if self.variant is not None:
            return self.variant.price * self.quantity
        else:
            return 0
    @property
    def product_images(self):
        if self.color:
            return ProductImages.objects.filter(product=self.product, color=self.color)
        return None


    
class whishlist(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    product = models.ForeignKey(MyProducts,on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, null=True, blank=True)
    added_date = models.DateTimeField(auto_now_add=True)



class OrderStatus(models.Model):
    STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
    ("Caneled",'Canceled'),
    ('Returned', 'Returned'),
    ('Paid', 'Paid')

    ]
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)

    def __str__(self):
        return self.status


class OrderAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, default='')
    pincode = models.CharField(max_length=7)
    locality = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.address}"


class Order(models.Model):
    ORDER_ID_PREFIX = "OID-"
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    order_address =models.ForeignKey(OrderAddress,on_delete=models.CASCADE,related_name='orderaddress',null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.SET_NULL, null=True)
    payment_status = models.CharField(max_length=10,default='Unpaid')
    payment = models.CharField(max_length=100)
    order_id = models.CharField(max_length=15, unique=True, editable=False)


    def save(self, *args, **kwargs):
        random_code = str(random.randint(1000, 9999))

        if not self.order_id:
            self.order_id = f"{self.ORDER_ID_PREFIX}{random_code}"
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at', '-id']
        db_table = "Order"

class OrderItem(models.Model):
   variant = models.ForeignKey(Variant, on_delete=models.CASCADE, default=None)
   order = models.ForeignKey(Order, on_delete=models.CASCADE)
   quantity = models.PositiveIntegerField(default=1)
  


class Wallet_user(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2,default = 0)
    payment_type = models.CharField(max_length = 100,null = True)
    user = models.OneToOneField(CustomUser, on_delete = models.CASCADE, related_name = 'wallet',null = True)

class WalletHistory(models.Model):
    TRANSACTION_CHOICES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)
    date = models.DateTimeField(auto_now_add=True)