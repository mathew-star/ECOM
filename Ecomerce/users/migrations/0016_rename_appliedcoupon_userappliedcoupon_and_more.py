# Generated by Django 4.2.7 on 2024-01-07 15:06

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0015_coupon_order_coupon_appliedcoupon'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AppliedCoupon',
            new_name='UserAppliedCoupon',
        ),
        migrations.RenameModel(
            old_name='Coupon',
            new_name='UserCoupons',
        ),
    ]
