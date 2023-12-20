from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from myadmin.models import BlockedUser
from myadmin.models import Category,ProductImages,Products
from users.models import Address
from accounts.models import CustomUser
from django.core import signing 
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required

def single_product(request,product_id):
    product = get_object_or_404(Products, pk=product_id)

    return render(request, 'users/singleproduct.html', {'product': product})
def shop(request):
    if request.user.is_authenticated == False:
        return redirect('signup')
    
    products= Products.objects.all()
    images= ProductImages.objects.all()
    return render(request,'users/shop.html',{'products':products,'images':images})

    
@login_required
def userprofile(request):
    user = request.user
    address= Address.objects.filter(user=user)
    
    context = {'user': user, 'address':address}
    return render(request, 'users/userprofile.html', context)

def edituser(request, user_id):
    user = get_object_or_404(CustomUser, pk=user_id)

    if request.user != user:
        return redirect('login')


    if request.method == 'POST':
        print("in edit")
        user.name = request.POST['name']
        user.email = request.POST['email']
        user.phone_number = request.POST['phone number']
        user.save()
    return redirect('userprofile')

def add_address(request):
    pass
def edit_address(request):
    pass
