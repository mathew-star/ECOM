
from django.db import models
from accounts.models import CustomUser
from colorfield.fields import ColorField
class BlockedUser(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='blocked_user')

    def __str__(self):
        return self.user.email


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='category/', blank=True)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class Color(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
class MyProducts(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category= models.ForeignKey(Category, on_delete=models.CASCADE)
    is_listed = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Variant(models.Model):
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    product_id = models.ForeignKey(MyProducts, on_delete=models.CASCADE, default=None)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_listed = models.BooleanField(default=True)


class ProductImages(models.Model):
    image = models.ImageField(upload_to='product_images/')
    product = models.ForeignKey(MyProducts, on_delete=models.CASCADE, default=None)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    
    def __str__(self):
        return f"{self.color.name}"

