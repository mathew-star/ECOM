from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from myadmin.models import BlockedUser
from myadmin.models import Category,ProductImages,MyProducts, Variant, Color
from users.models import Address,cartitems,Order, OrderItem,OrderStatus
from accounts.models import CustomUser
from django.contrib import messages
from django.core import signing 
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned
from decimal import Decimal

def cart_count(request):
   if request.user.is_authenticated:
       bag_count = cartitems.objects.filter(user=request.user).count()
   else:
       bag_count = 0
   return {'bag_count': bag_count}

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


@login_required
def add_to_cart(request):
   print("in add cart")
   if request.method == 'POST':
       product_id = request.POST['product_id']
       color_id = request.POST['color_id']
       variant_id= request.POST['variant_id']
       user= request.user
       try:
           quantity= request.POST['quantity']
       except:
           quantity = 1
       print(product_id, color_id)
       product = MyProducts.objects.get(id=product_id)
       print("Product",product.name)
       color = get_object_or_404(Color, id=color_id)
       variant = get_object_or_404(Variant, product_id=product, color=color)
       c = cartitems.objects.create(user=user, product=product, color=color, variant=variant, quantity=quantity)

       return redirect('cartitems_list')
   else:
       return redirect('single_product',product_id=product.id)
   

@login_required
def update_cart_quantity(request, item_id, new_quantity):
    try:
        cart_item = cartitems.objects.get(id=item_id, user=request.user)
        cart_item.quantity = new_quantity
        cart_item.save()
        color_id= cart_item.color.id
        variant = Variant.objects.get(color_id=color_id)
        stock= variant.quantity - 2
        out_of_stock=None

        if int(cart_item.quantity) > stock:
            out_of_stock = True
            
        total_price = sum([item.total_price for item in cartitems.objects.filter(user=request.user)])
        bag_count = cartitems.objects.filter(user=request.user).count()

        response_data = {
            'success': True,
            'total_price': total_price,
            'bag_count': bag_count,
            'out_of_stock':out_of_stock
        }
    except cartitems.DoesNotExist:
        response_data = {'success': False}

    return JsonResponse(response_data)



@login_required
def cartitems_list(request):
   cart_items = cartitems.objects.filter(user=request.user)
   bag_count= cartitems.objects.filter(user=request.user).count()

   total_price = sum([item.total_price for item in cart_items])
   print(total_price)
   context={
       'cart_items': cart_items, 'total_price': total_price,
       'bag_count':bag_count
       
   }
   return render(request, "users/cart.html", context)

def remove_cart_item(request,itemid):
    cart_item = cartitems.objects.get(id=itemid)
    cart_item.delete()
    return redirect('cartitems_list')

def remove_cartorder_item(request, itemid):
    try:
        cart_item = cartitems.objects.get(id=itemid)
        cart_item.delete()
        messages.success(request, 'Item removed successfully')
    except cartitems.DoesNotExist:
        messages.error(request, 'Item not found')

    return redirect('cart_order')

def cart_order(request):
    user = request.user
    address= Address.objects.filter(user=user)
    cart_items = cartitems.objects.filter(user=request.user)
    bag_count= cartitems.objects.filter(user=request.user).count()
    first_address = address.first()

    total_price = sum([item.total_price for item in cart_items])
    context={
        'cart_items' : cart_items,
        'total_price':total_price,
        'address':address,
        'first_address':first_address
    }
    return render(request,"users/checkout.html",context)



def get_address_details(request, address_id):
    try:
        address = get_object_or_404(Address, pk=address_id)

        serialized_address = {
            'id': address.id,
            'name': address.name,
            'phone': address.phone,
            'pincode': address.pincode,
            'locality': address.locality,
            'address': address.address,
            'city': address.city,
            'state': address.state,
        }

        return JsonResponse(serialized_address)

    except Address.DoesNotExist:
        return JsonResponse({'error': 'Address not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

def singleproduct_checkout(request):
        
        if request.method == 'POST':
            product_id = request.POST['product_id']
            color_id = request.POST['color_id']
            variant_id= request.POST['variant_id']
            quantity= request.POST['quantity']
            print (quantity)
            user= request.user
        address= Address.objects.filter(user=user)
        first_address = address.first()
        product = MyProducts.objects.get(id=product_id)
        color = get_object_or_404(Color, id=color_id)
        images=ProductImages.objects.filter(color_id=color_id)
        variant = get_object_or_404(Variant, product_id=product, color=color)
        print(quantity)
        price = Decimal(variant.price)
        total_price = price * Decimal(quantity)

        
        context={
            'product':product,
            'images':images,
            'color':color,
            'variant':variant,
            'total_price':total_price,
            'quantity':quantity,
            'first_address':first_address,
            'address':address,

        }
        return render(request,"users/product_checkout.html",context)
        

def product_checkout(request):
    user = request.user
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        product_id = request.POST.get('product_id')
        variant_id = request.POST.get('varaint_id')
        total_price = request.POST.get('total_price')
        quantity = request.POST.get('quantity')
        quantity=int(quantity)
    print(quantity, total_price, address_id)
    selected_address = Address.objects.get(id=address_id)
    product=MyProducts.objects.get(id=product_id)
    variant=Variant.objects.get(id=variant_id)
    
    order = Order.objects.create(
        user=user,
        address=selected_address,
        total_price=total_price,
        order_status=OrderStatus.objects.get(status='Pending'),
        payment='COD' 
    )
    OrderItem.objects.create(order=order, variant=variant, quantity=quantity)

    variant.quantity -= quantity
    variant.save()

    return redirect('user_orders')


    
def checkout(request):
    user = request.user
    if request.method == 'POST':
        address_id = request.POST.get('address_id') 
    print(address_id)
    selected_address = Address.objects.get(id=address_id)
    cart_items = cartitems.objects.filter(user=request.user)
    total_price = sum([item.total_price for item in cart_items])


    order = Order.objects.create(
        user=user,
        address=selected_address,
        total_price=total_price,
        order_status=OrderStatus.objects.get(status='Pending'),
        payment='COD' 
    )

    for item in cart_items:
        OrderItem.objects.create(order=order, variant=item.variant, quantity=item.quantity)

        variant = get_object_or_404(Variant, id=item.variant.id)
        variant.quantity -= item.quantity
        variant.save()

    
    messages.success(request, 'Order placed successfully!')
    return redirect('user_orders')

def user_orders(request):
  cart_items = cartitems.objects.filter(user=request.user)
  cart_items.delete()
  user = CustomUser.objects.get(name=request.user.name)
  orders = Order.objects.filter(user=user)
  return render(request, 'users/user_orders.html', {'orders': orders})


def order_detail(request, oid):

    order = get_object_or_404(Order, order_id=oid)
    order_items = OrderItem.objects.filter(order=order)

    if order.order_status.status == 'Pending':
        progress_percentage = 0

    elif order.order_status.status == 'Shipped':
        progress_percentage = 50

    else:
        progress_percentage = 100

    context = {
        'order': order,
        'order_items': order_items,
        'progress_percentage': progress_percentage,
    }


    return render(request, 'users/order_details.html', context)

# def cancel_order(request, pk):
#     order = Order.objects.get(pk=pk)
#     for item in order.orderitem_set.all():
#         variant = item.product.variant
#         variant.quantity += item.quantity
#         variant.save()
#     order.delete()
#     return redirect('userprofile')

def cancel_order(request):
    if request.method == "POST":
        oid = request.POST.get('order_id')
        order = get_object_or_404(Order, id=oid)
        order_items = OrderItem.objects.filter(order=order)

        for item in order_items:
            variant = Variant.objects.get(id=item.variant.id)
            variant.quantity += item.quantity
            variant.save()

        order.order_status = OrderStatus.objects.get(status='Canceled')
        order.save()

        return redirect('user_orders')

