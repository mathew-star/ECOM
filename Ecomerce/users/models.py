from django.db import models
from accounts.models import CustomUser
class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    phone = models.IntegerField(null=True,default=0)
    pincode = models.CharField(max_length=7)
    locality = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.address}"