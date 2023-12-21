from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from myadmin.models import BlockedUser
from myadmin.models import Category,ProductImages,Products
from users.models import Address
from accounts.models import CustomUser
from django.contrib import messages
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
    for i in address:
        print(i.name)
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


@login_required
def add_address(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        pincode = request.POST.get('pincode')
        locality = request.POST.get('locality')
        address_text = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')

        existing_address = Address.objects.filter(
            user=request.user,
            name=name,
            phone=phone,
            pincode=pincode,
            locality=locality,
            address=address_text,
            city=city,
            state=state
        ).exists()

        if existing_address:
            messages.error(request, 'Address already exists for this user.')
            return render(request, 'users/add_address.html')


        new_address = Address(
            user=request.user,
            name=name,
            phone=phone,
            pincode=pincode,
            locality=locality,
            address=address_text,
            city=city,
            state=state
        )
        new_address.save()

        messages.success(request, 'Address added successfully.')
        return redirect('userprofile')

    return render(request, 'users/add_address.html')


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == 'POST':
        address.name = request.POST.get('name')
        address.phone = request.POST.get('phone')
        address.pincode = request.POST.get('pincode')
        address.locality = request.POST.get('locality')
        address.address = request.POST.get('address')
        address.city = request.POST.get('city')
        address.state = request.POST.get('state')

        if not all([address.name, address.phone, address.pincode, address.locality, address.address, address.city, address.state]):
            messages.error(request, 'Please fill in all the fields.')
            return render(request, 'users/edit_address.html', {'address': address})

        address.save()
        print(address.phone)
        messages.success(request, 'Address updated successfully.')
        return redirect('userprofile')

    return render(request, 'users/edit_address.html', {'address': address})

