from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from decimal import Decimal
from .models import Variant

@receiver(post_save, sender=Variant)
def update_discount_price(sender, instance, created, **kwargs):
    if created:
        if instance.discount == 0:
            instance.discount_price = instance.get_discount()
            instance.save()
