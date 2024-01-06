from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import  Wallet_user
from accounts.models import  CustomUser

@receiver(post_save, sender=CustomUser)
def create_wallet(sender, instance, created, **kwargs):
 if created:
     Wallet_user.objects.create(user=instance)
