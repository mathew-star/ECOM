from django.db import models
from django.db.models import Count, Sum, Case, When, IntegerField
from accounts.models import CustomUser
from myadmin.models import MyProducts,Variant,Color,ProductImages
from django.contrib.auth import get_user_model
from django.utils import timezone
import random
from calendar import month_abbr
from django.db.models import Count, Sum




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
            if self.variant.discount ==0:
                return self.variant.price * self.quantity
            else:
                return self.variant.discount_price * self.quantity
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




class MyCoupons(models.Model):
    coupon_code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_price = models.IntegerField()
    is_disabled = models.BooleanField(default=False)


    def is_valid(self):
        return not self.is_disabled and timezone.now() < self.expiry_date
    
    def save(self, *args, **kwargs):
        if not self.is_disabled and timezone.now().date() >= self.expiry_date:
            self.is_disabled = True

        super().save(*args, **kwargs)


class UserAppliedCoupon(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    coupon = models.ForeignKey(MyCoupons, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'coupon')



class OrderStatus(models.Model):
    STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Shipped', 'Shipped'),
    ('Delivered', 'Delivered'),
    ("Canceled",'Canceled'),
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
    coupon = models.ForeignKey(MyCoupons, on_delete=models.CASCADE,default='', null=True,blank=True)
    coupon_code = models.CharField(max_length=100,null=True, blank=True)
    coupon_price = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    order_address =models.ForeignKey(OrderAddress,on_delete=models.CASCADE,related_name='orderaddress',null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount= models.DecimalField(max_digits=5, decimal_places=2, default=0)
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
    
    # @classmethod
    # def get_daily_orders_chart_data(cls):
    #     today = timezone.now().date()
    #     daily_orders_data = cls.objects.filter(created_at__date=today) \
    #         .values('created_at__hour') \
    #         .annotate(
    #             orders_count=Count('id'),
    #             cancelled_orders_count=Sum(
    #                 Case(
    #                     When(order_status__status='Canceled', then=1),
    #                     default=0,
    #                     output_field=IntegerField()
    #                 )
    #             )
    #         )

    #     hourly_data = [{'hour': i, 'orders_count': 0, 'cancelled_orders_count': 0} for i in range(24)]

    #     for entry in daily_orders_data:
    #         hour = entry['created_at__hour']
    #         index = next((i for i, item in enumerate(hourly_data) if item["hour"] == hour), None)
    #         if index is not None:
    #             hourly_data[index]['orders_count'] = entry['orders_count']
    #             hourly_data[index]['cancelled_orders_count'] = entry['cancelled_orders_count']

    #     return hourly_data
        
    @classmethod
    def get_daily_orders_chart_data(cls):
        today = timezone.now().date()
        daily_orders_data = cls.objects.filter(created_at__date=today) \
            .values('created_at__day') \
            .annotate(
                orders_count=Count('id'),
                cancelled_orders_count=Sum(
                    Case(
                        When(order_status__status='Canceled', then=1),
                        default=0,
                        output_field=IntegerField()
                    )
                )
            )

        daily_data = [{'day': i, 'orders_count': 0, 'cancelled_orders_count': 0} for i in range(1, 32)]

        for entry in daily_orders_data:
            day = entry['created_at__day']
            index = next((i for i, item in enumerate(daily_data) if item["day"] == day), None)
            if index is not None:
                daily_data[index]['orders_count'] = entry['orders_count']
                daily_data[index]['cancelled_orders_count'] = entry['cancelled_orders_count']

        return daily_data

    @classmethod
    def get_daily_orders_count_today(cls):
        today = timezone.now().date()
        return cls.objects.filter(created_at__date=today).count()

    class Meta:
        ordering = ['-created_at', '-id']
        db_table = "Order"
    

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


class Return(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return #{self.id} - Order #{self.order.id}"
    

class Referral(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=12, blank=True)
    referred_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True, related_name='ref_by')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)