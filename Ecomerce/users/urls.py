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
    path('add_to_cart/', views.add_to_cart, name="add_to_cart"),
    path('cartitems_list/',views.cartitems_list,name="cartitems_list"),
    path('update_cart/<int:item_id>/<int:new_quantity>/', views.update_cart_quantity, name='update_cart'),
    path('remove_cart_item/<int:itemid>/',views.remove_cart_item,name="remove_cart_item"),
    path(' cart_order/',views. cart_order,name=" cart_order"),
    path('remove_cartorder_item/<int:itemid>/',views.remove_cart_item,name="remove_cartorder_item"),
    path('get_address_details/<int:address_id>/', views.get_address_details, name='get_address_details'),
    path('checkout/', views.checkout,name="checkout"),
    path('user_orders/',views.user_orders, name="user_orders"),
    path('order_detail/<int:order_id>/', views.order_detail,name="order_details"),


]
    