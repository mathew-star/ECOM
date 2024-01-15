from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import  Wallet_user,Referral
from .utils import generate_referral_code
from accounts.models import  CustomUser
from myadmin.models import Variant

@receiver(post_save, sender=CustomUser)
def create_wallet(sender, instance, created, **kwargs):
 if created:
     Wallet_user.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def create_referral(sender, instance, created, **kwargs):
    if created:
        referral_code = generate_referral_code()
        Referral.objects.create(user=instance, code=referral_code)