from django.urls import path
from . import views
urlpatterns = [
    path('shop/',views.shop,name="shop"),
    path('product/<int:product_id>/', views.single_product, name='single_product'),
    path('userprofile/', views.userprofile, name='userprofile'),
    path('edituser/<int:user_id>/', views.edituser, name='edituser'),
    path('add_address/', views.add_address, name='add_address'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('get_product_details/<int:colorid>/', views.get_product_details, name='get_product_details'),
    path('get_stock_status/', views.get_stock_status, name='get_stock_status'),
]
    