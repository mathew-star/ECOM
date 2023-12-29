from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from myadmin.models import BlockedUser
from myadmin.models import Category,ProductImages,MyProducts, Variant, Color
from users.models import Address
from accounts.models import CustomUser
from django.contrib import messages
from django.core import signing 
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned


def single_product(request,product_id):
    product = get_object_or_404(MyProducts, pk=product_id)
    variant = Variant.objects.filter(product_id=product_id)[0]
    images= ProductImages.objects.filter(color_id = variant.color.id)
    context={
        'product':product,
        'variant':variant,
        'images':images
    }

    return render(request, 'users/singleproduct.html', context)


# def get_product_images(request):
#     product_id = request.GET.get('product_id')
#     color = request.GET.get('color')

#     color_instance = get_object_or_404(Color, name=color)
#     product_images = ProductImages.objects.filter(product_id=product_id, color=color_instance)

#     data = {
#         'images': [{'image_url': img.image.url} for img in product_images],
#     }

#     return JsonResponse(data)




def get_product_details(request,colorid):
    print("reached")
    try:
        print("fetch")
        
        variant = Variant.objects.get(color_id=colorid)
        images= ProductImages.objects.filter(color_id=variant.color.id)
        images = [{'image': img.image.url} for img in images]

        data = {
            'variant': {
                'price': variant.price,
                'quantity': variant.quantity,
            },
            'images': images,
        }

        return JsonResponse(data)
    
    except Variant.DoesNotExist:
        return JsonResponse({'error': 'Variant not found'}, status=404)
    except ProductImages.DoesNotExist:
        return JsonResponse({'error': 'Product images not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  

def get_stock_status(request):
    color_id = request.GET.get('colorid')
    quantity = request.GET.get('quantity')
    print(color_id, quantity)
    variant = Variant.objects.get(color_id=color_id)
    print(variant.quantity)
    stock= variant.quantity - 2
    out_of_stock=None

    if int(quantity) > stock:
        print(True)
        out_of_stock = True

    data = {
        'outOfStock': out_of_stock,
    }

    return JsonResponse(data)

def shop(request):
    if request.user.is_authenticated == False:
        return redirect('signup')
    
    products= MyProducts.objects.all()
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

