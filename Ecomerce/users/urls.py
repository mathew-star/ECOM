from django.urls import path
from . import views
urlpatterns = [
    path('shop/',views.shop,name="shop"),
    path('c_shop/<str:category>/', views.c_shop, name='c_shop'),
    path('product/<int:product_id>/', views.single_product, name='single_product'),
    path('userprofile/', views.userprofile, name='userprofile'),
    path('search/',views.search_product,name="search"),
    path('search_products/', views.shop_search_products, name='search_products'),
    path('search_products/<str:category>/', views.shop_search_products, name='category_search_products'),
    path('edituser/<int:user_id>/', views.edituser, name='edituser'),
    path('add_address/', views.add_address, name='add_address'),
    path('checkout_address/',views.checkout_address,name="checkout_address"),
    path('remove_address/<int:address_id>/',views.remove_address,name="remove_address"),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
    path('get_product_details/<int:colorid>/', views.get_product_details, name='get_product_details'),
    path('get_stock_status/', views.get_stock_status, name='get_stock_status'),
    path('add_to_cart/', views.add_to_cart, name="add_to_cart"),
    path('cartitems_list/',views.cartitems_list,name="cartitems_list"),
    path('wishlist/',views.wishlist,name="wishlist"),
    path('remove_wishlist_item/<int:itemid>/',views.remove_wishlist_item,name="remove_wishlist_item"),
    path('add_to_wishlist/<int:product_id>/<int:variant_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/<int:variant_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('update_cart/<int:item_id>/<int:new_quantity>/', views.update_cart_quantity, name='update_cart'),
    path('remove_cart_item/<int:itemid>/',views.remove_cart_item,name="remove_cart_item"),
    path('cart_order/',views.cart_order,name="cart_order"),
    path('remove_cartorder_item/<int:itemid>/',views.remove_cart_item,name="remove_cartorder_item"),
    path('get_address_details/<int:address_id>/', views.get_address_details, name='get_address_details'),
    path('checkout/', views.checkout,name="checkout"),
    path('razorpay_initiate_payment/', views.initiate_razorpay_payment, name='razorpay_initiate_payment'),
    path('product_checkout/',views.product_checkout,name="product_checkout"),
    path('singleproduct_checkout/',views.singleproduct_checkout,name="singleproduct_checkout"),
    path('product_check/<int:product_id>/<int:color_id>/<int:variant_id>/<int:quantity>/', views.product_check, name="product_check"),
    path('user_orders/',views.user_orders, name="user_orders"),
    path('order_detail/<str:oid>/', views.order_detail,name="order_detail"),
    path('cancel_order/',views.cancel_order, name="cancel_order"),
    path('return/<str:order_id>/',views.o_return, name="o_return"),
    path('order_return/<str:order_id>/',views.order_return,name='order_return'),
    path('generate_invoice_pdf/<int:order_id>/', views.generate_invoice_pdf, name='generate_invoice_pdf'),

    path('wallet/',views.wallet,name="wallet"),
    path('get_coupon_discount/<int:coupon_id>/', views.get_coupon_discount, name='get_coupon_discount'),
]





    