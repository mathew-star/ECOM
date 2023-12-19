from django.urls import path
from . import views
urlpatterns = [
    path('',views.signup,name='signup'),
    path('home',views.home,name='home'),
    path('login',views.login,name='login'),
    path('logout/', views.logout, name='logout'),
    path('verify-otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('resend-otp/<int:user_id>/', views.resend_otp, name='resend_otp'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/done/', views.password_reset_request, name='password_reset_request'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_request, name='password_reset_complete'),

]



