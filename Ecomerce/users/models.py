from django.db import models
from accounts.models import CustomUser
from myadmin.models import MyProducts,Variant,Color,ProductImages
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



    
  

