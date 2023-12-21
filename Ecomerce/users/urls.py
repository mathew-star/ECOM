from django.urls import path
from . import views
urlpatterns = [
    path('shop/',views.shop,name="shop"),
    path('product/<int:product_id>/', views.single_product, name='single_product'),
    path('userprofile/', views.userprofile, name='userprofile'),
    path('edituser/<int:user_id>/', views.edituser, name='edituser'),
    path('add_address/', views.add_address, name='add_address'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),

]
    