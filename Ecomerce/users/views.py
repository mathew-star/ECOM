from django.core.validators import validate_email, RegexValidator
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from datetime import date
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
from django.http import Http404
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from reportlab.pdfgen import canvas
from io import BytesIO
from myadmin.models import BlockedUser
from myadmin.models import Category,ProductImages,MyProducts, Variant, Color,CategoryOffer,ProductOffer
from users.models import Address,cartitems,Order, OrderItem,OrderStatus,whishlist,OrderAddress,Wallet_user, WalletHistory,Return,MyCoupons,UserAppliedCoupon,Referral
from accounts.models import CustomUser
from django.contrib import messages
from django.core import signing 
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.core.exceptions import MultipleObjectsReturned
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal, ROUND_DOWN
import razorpay
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO



def apply_category_offer(product, category_offers):
    if product.category.id in category_offers:
        offer_percentage = category_offers[product.category.id]
        if offer_percentage is not None:
            first_variant = product.variant_set.first()
            if first_variant:
                original_price = first_variant.price
                discounted_price = original_price - (original_price * (Decimal(offer_percentage) / 100))
                return {
                    'original_price': original_price,
                    'discounted_price': discounted_price,
                    'discount_percentage': offer_percentage
                }
    return None



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
    try:
        category_offer = CategoryOffer.objects.filter(category=product.category, end_date__gte=timezone.now().date()).first()
        Productofferprice = variant.price - (variant.price * (category_offer.discount_percentage / 100))
    except:
        Productofferprice=None
        category_offer=None

    if Productofferprice:
        context={
            'product':product,
            'variant':variant,
            'images':images,
            'category_offer':category_offer,
            'Productofferprice':Productofferprice,
        }
    else:
        context={
            'product':product,
            'variant':variant,
            'images':images,
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

def search_product(request):
  if request.method == "POST":
      query_name = request.POST.get('name', None)
      if query_name:
          results = MyProducts.objects.filter(name__icontains=query_name)
          if results:
              product = results[0]
              return redirect('single_product', product_id=product.pk)
          
  messages.warning(request,"No such product found !")  
  return redirect('home')


def shop_search_products(request):
    if request.method == 'GET':
        search_term = request.GET.get('search_term', '')
        products = MyProducts.objects.filter(name__icontains=search_term)
        
        
        product_list = []
        for product in products:
            # Get the first image for each product (you might want to adjust this logic)
            image = ProductImages.objects.filter(product=product).first()
            first_variant = Variant.objects.filter(product_id=product).first()
            if image:
                product_data = {

                    'id': product.id,
                    'name': product.name,
                    'image': image.image.url,
                    'price': first_variant.price
                }
                product_list.append(product_data)

        return JsonResponse({'products': product_list})
    
def category_search_products(request):
        if request.method == 'GET':
            search_term = request.GET.get('search_term', '')
            products = MyProducts.objects.filter(name__icontains=search_term)
            
        
        product_list = []
        for product in products:
            # Get the first image for each product (you might want to adjust this logic)
            image = ProductImages.objects.filter(product=product).first()
            first_variant = Variant.objects.filter(product_id=product).first()
            if image:
                product_data = {

                    'id': product.id,
                    'name': product.name,
                    'image': image.image.url,
                    'price': first_variant.price
                }
                product_list.append(product_data)

        return JsonResponse({'products': product_list})


def get_product_details(request,colorid):
    try:
        variant = Variant.objects.get(color_id=colorid)
        images= ProductImages.objects.filter(color_id=variant.color.id)
        images = [{'image': img.image.url} for img in images]
        data = {
            'variant': {
                'price': variant.price,
                'variant_id':variant.id,
                'color_id':colorid,
                'discount':variant.discount,
                'discount_price':variant.discount_price,
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
    sort_option = request.GET.get('sort', 'default')

    images = ProductImages.objects.all()  

    if sort_option == 'low_to_high':
        products = MyProducts.objects.all().order_by('variant__price').distinct()
    elif sort_option == 'high_to_low':
        products = MyProducts.objects.all().order_by('-variant__price').distinct()
    else:
        products = MyProducts.objects.all().distinct()

    first_variant_prices = {}

    for product in products:
        first_variant = Variant.objects.filter(product_id=product).first()
        if first_variant:
            first_variant_prices[product.id] = first_variant.price
    unique_products = {}
    for product in products:
        unique_products[product.id] = product

    unique_product_list = list(unique_products.values())


    return render(request,'users/shop.html',{'products':unique_product_list,'images':images,'first_variant':first_variant})




def c_shop(request, category):
    if request.user.is_authenticated == False:
        return redirect('signup')
    category= Category.objects.get(name=category)
    sort_option = request.GET.get('sort', 'default')

    if sort_option == 'low_to_high':
        products = MyProducts.objects.filter(category=category).order_by('variant__price')
    elif sort_option == 'high_to_low':
        products = MyProducts.objects.filter(category=category).order_by('-variant__price')
    else:
        products = MyProducts.objects.filter(category=category)

    unique_products = {}
    for product in products:
        unique_products[product.id] = product

    unique_product_list = list(unique_products.values())
        
    category = get_object_or_404(Category, name=category)
    products = MyProducts.objects.filter(category=category)
    images = ProductImages.objects.filter(product__in=products)
    category = get_object_or_404(Category, name=category)


    return render(request, 'users/shop.html', {'products': unique_product_list, 'category':category})


# def c_shop(request, category):
#     if request.user.is_authenticated == False:
#        return redirect('signup')

#     category = get_object_or_404(Category, name=category)
    
       
#     sort_option = request.GET.get('sort', 'default')

#     if sort_option == 'low_to_high':
#         products = MyProducts.objects.filter(category=category).order_by('variant__price')
#     elif sort_option == 'high_to_low':
#         products = MyProducts.objects.filter(category=category).order_by('-variant__price')
#     else:
#         products = MyProducts.objects.filter(category=category)

#     unique_products = {}
#     for product in products:
#         unique_products[product.id] = product

#     unique_product_list = list(unique_products.values())
   

#     return render(request, 'users/shop.html', {'products': unique_product_list, 'category':category})


@login_required
def userprofile(request):
    user = request.user
    referal_code=Referral.objects.get(user=user)
    address= Address.objects.filter(user=user)
    for i in address:
        print(i.name)
    context = {'user': user, 'address':address,'referal':referal_code}
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

        if not all([name, phone, pincode, locality, address_text, city, state]):
            messages.error(request, 'Please fill in all the fields.')
            return render(request, 'users/add_address.html')

        if not phone.isdigit():
            messages.error(request, 'Please enter a valid phone number.')
            return render(request, 'users/add_address.html')


        if not (pincode.isdigit() and len(pincode) == 6):
            messages.error(request, 'Please enter a valid 6-digit pin code.')
            return render(request, 'users/add_address.html')



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

def remove_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    return redirect('userprofile')


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

        if not address.phone.isdigit():
            messages.error(request, 'Please enter a valid phone number.')
            return render(request, 'users/edit_address.html', {'address': address})

        
        if not (address.pincode.isdigit() and len(address.pincode) == 6):
            messages.error(request, 'Please enter a valid 6-digit pin code.')
            return render(request, 'users/edit_address.html', {'address': address})


        address.save()
        print(address.phone)
        messages.success(request, 'Address updated successfully.')
        return redirect('userprofile')

    return render(request, 'users/edit_address.html', {'address': address})




def wishlist(request):
    w= whishlist.objects.all()
    context={'wishlist':w}
    return render(request,"users/wishlist.html",context)

def remove_wishlist_item(request,itemid):
    w = whishlist.objects.get(id=itemid)   
    w.delete()
    return redirect("wishlist") 



@login_required
def add_to_wishlist(request, product_id,variant_id):
    user = request.user
    product = get_object_or_404(MyProducts, id=product_id)
    variant = get_object_or_404(Variant, id=variant_id)
    wishlist_item, created = whishlist.objects.get_or_create(user=user, product=product,variant=variant,color=variant.color)

    if created:
        status = 'added'
    else:
        status = 'already_added'

    return JsonResponse({'status': status, 'message': f'Item {status.capitalize()} to wishlist'})


@login_required
@require_POST
def remove_from_wishlist(request, product_id,variant_id):
    user = request.user
    product = get_object_or_404(MyProducts, id=product_id)
    variant= get_object_or_404(Variant, id=variant_id)
    wishlist_item = whishlist.objects.filter(user=user, product=product,variant=variant).first()


    if wishlist_item:
        wishlist_item.delete()
        status = 'removed'
    else:
        status = 'not_in_wishlist'

    return JsonResponse({'status': status, 'message': f'Item {status.capitalize()} from wishlist'})


@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST['product_id']
        color_id = request.POST['color_id']
        variant_id = request.POST['variant_id']
        user = request.user

        try:
            quantity = int(request.POST['quantity'])
        except:
            quantity = 1

        try:
            existing_cart_item = cartitems.objects.get(user=user, product_id=product_id, color_id=color_id, variant_id=variant_id)

            existing_cart_item.quantity += quantity
            existing_cart_item.save()
        except cartitems.DoesNotExist:
            product = get_object_or_404(MyProducts, id=product_id)
            color = get_object_or_404(Color, id=color_id)
            variant = get_object_or_404(Variant, id=variant_id)
            if quantity > variant.quantity:
                messages.error(request,"The item out of stock !")
                return redirect('single_prodct',product_id)
            

            new_cart_item = cartitems.objects.create(user=user, product=product, color=color, variant=variant, quantity=quantity)

        return redirect('cartitems_list')
    else:
        return redirect('single_product', product_id=product.id)

@login_required
def update_cart_quantity(request, item_id, new_quantity):
    try:
        cart_item = cartitems.objects.get(id=item_id, user=request.user)
        cart_item.quantity = new_quantity
        cart_item.save()
        print(cart_item.quantity)
        color_id= cart_item.color.id
        variant = Variant.objects.get(color_id=color_id)
        stock= variant.quantity - 2
        out_of_stock=None

        if int(cart_item.quantity) > stock:
            out_of_stock = True
            
        total_price = sum([item.total_price for item in cartitems.objects.filter(user=request.user)])
        sub_total = sum([item.variant.price*item.quantity for item in cartitems.objects.filter(user=request.user)])
        discount = round(sum ((item.variant.price*item.quantity)*Decimal(item.variant.discount/100) for item in cartitems.objects.filter(user=request.user)),2)

        print(sub_total)
        bag_count = cartitems.objects.filter(user=request.user).count()

        response_data = {
            'success': True,
            'total_price': total_price,
            'sub_total': sub_total,
            'discount': discount,
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
   sub_total = sum (item.variant.price*item.quantity for item in cart_items)
   discount = round(sum (item.variant.price*Decimal(item.variant.discount/100) for item in cart_items),2)

   
   print(total_price)
   context={
       'cart_items': cart_items, 'total_price': total_price,
       'bag_count':bag_count,'sub_total':sub_total, 'discount':discount,
       
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
    
    
    try:
         user_wallet = Wallet_user.objects.get(user=user)
    except:
        pass
    
    address= Address.objects.filter(user=user)
    cart_items = cartitems.objects.filter(user=request.user)
    bag_count= cartitems.objects.filter(user=request.user).count()

    if bag_count == 0:
        messages.error(request,"No items in the cart !")
        return redirect('cartitems_list')

    first_address = address.first()
    for item in cart_items:
            print(item.quantity)
            print(item.variant.quantity)
            print(item.quantity>item.variant.quantity)
            if item.quantity>(item.variant.quantity-2):
                messages.error(request,f"{item.product.name} is Out of stock, decrease the quantity or come later ")
                return redirect('cartitems_list')
            if item.variant.quantity < 2:
                messages.error(request, f"Item '{item.product.name}' is out of stock.")
                return redirect('cartitems_list')
    

    total_price = sum([item.total_price for item in cart_items])


    today = date.today()
    valid_coupons = MyCoupons.objects.filter(
        Q(min_purchase_amount__lte=total_price) &
        Q(expiry_date__gte=today)
    )

    
    sub_total = sum (item.variant.price*item.quantity for item in cart_items)
    discount = round(sum (item.variant.price*Decimal(item.variant.discount/100) for item in cart_items),2)


    context={
        'cart_items' : cart_items,
        'total_price':total_price,
        'sub_total':sub_total,
        'discount':discount,
        'address':address,
        'first_address':first_address,
        'user_wallet':user_wallet,
        'valid_coupons':valid_coupons,
    }
    return render(request,"users/checkout.html",context)



def get_coupon_discount(request, coupon_id):
    try:
        coupon = MyCoupons.objects.get(id=coupon_id)

        if coupon.is_valid():
            return JsonResponse({'discount': coupon.discount_price})
        else:
            return JsonResponse({'error': 'Invalid coupon or expired'})
    except MyCoupons.DoesNotExist:
        return JsonResponse({'error': 'Coupon not found'})
    



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
    






@csrf_exempt
def initiate_razorpay_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            total_price_in_paisa = float(data.get('total_price', 0)) * 100
            user_id = data.get('user', '')
            address_id = data.get('address_id', '')


            if not isinstance(total_price_in_paisa, (int, float)):
                raise ValueError("Invalid totalPrice provided.")
            
            print(settings.RAZORPAY_KEY)
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))

            r_order = client.order.create({
                'amount': int(total_price_in_paisa),
                'currency': 'INR',
                'payment_capture': 1
            })


            return JsonResponse({'status': 'success', 'order_id': r_order['id'],'amount':r_order['amount'] })
        except Exception as e:
            # Log the error for debugging
            print("Error:", str(e))
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    
def product_check(request, product_id, color_id, variant_id, quantity):
        user =request.user
        try:
            user_wallet = Wallet_user.objects.get(user=user)
        except:
            pass

        address= Address.objects.filter(user=user)
        first_address = address.first()
        product = MyProducts.objects.get(id=product_id)
        color = get_object_or_404(Color, id=color_id)
        images=ProductImages.objects.filter(color_id=color_id)
        variant = get_object_or_404(Variant, product_id=product, color=color)
        print(quantity)

        if variant.discount == 0:
            price = Decimal(variant.price)
            total_price = price * Decimal(quantity)
            discount=0
        else:
            price = Decimal(variant.discount_price)
            total_price = price * Decimal(quantity)
            discount= round(variant.price * Decimal(variant.discount/100),2)

        today = date.today()
        valid_coupons = MyCoupons.objects.filter(
        Q(min_purchase_amount__lte=total_price) &
        Q(expiry_date__gte=today)
    )

        
        context={
            'product':product,
            'images':images,
            'color':color,
            'variant':variant,
            'discount':discount,
            'total_price':total_price,
            'quantity':quantity,
            'first_address':first_address,
            'address':address,
            'user_wallet':user_wallet,
            'valid_coupons':valid_coupons,

        }
        return render(request,"users/product_checkout.html",context)


def singleproduct_checkout(request):
        if request.method == 'POST':
            product_id = request.POST['product_id']
            color_id = request.POST['color_id']
            variant_id= request.POST['variant_id']
            quantity= request.POST['quantity']
            try:
                offerprice= request.POST['offer_price']
                offerpercentage= request.POST['offer_percentage']
            except:
                pass
   
         
        user = request.user
        

        try:
         user_wallet = Wallet_user.objects.get(user=user)
        except:
            pass

        address= Address.objects.filter(user=user)
        first_address = address.first()
        product = MyProducts.objects.get(id=product_id)
        color = get_object_or_404(Color, id=color_id)
        images=ProductImages.objects.filter(color_id=color_id)
        variant = get_object_or_404(Variant, product_id=product, color=color)

        try:
            category_offer= CategoryOffer.objects.get(category=product.category)
        except:
            pass
        
        if int(quantity) > variant.quantity:
            messages.error(request,'This item is out of stock, decrease the quantity !')
            return redirect('single_product',product_id=product_id)
        if variant.discount == 0:
            price = Decimal(variant.price)
            total_price = price * Decimal(quantity)
            discount=0
        else:
            price = Decimal(variant.discount_price)
            total_price = price * Decimal(quantity)
            discount= round(variant.price * Decimal(variant.discount/100),2)

        today = date.today()
        valid_coupons = MyCoupons.objects.filter(
        Q(min_purchase_amount__lte=total_price) &
        Q(expiry_date__gte=today)
    )
        print(valid_coupons)
        
        context={
            'product':product,
            'images':images,
            'color':color,
            'discount':discount,
            'variant':variant,
            'total_price':total_price,
            'quantity':quantity,
            'first_address':first_address,
            'address':address,
            'user_wallet':user_wallet,
            'valid_coupons':valid_coupons,

        }
        return render(request,"users/product_checkout.html",context)

        

def product_checkout(request):
    user = request.user
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        product_id = request.POST.get('product_id')
        variant_id = request.POST.get('varaint_id')
        color_id   = request.POST.get('color_id')
        total_price = request.POST.get('total_price')
        total_price = float(total_price)
        quantity = request.POST.get('quantity')
        payment= request.POST.get('selected_payment_option')
        coupon_code=request.POST.get('selected_coupon_code')
        

        

        
        if address_id:
            selected_address = Address.objects.get(id=address_id)
        else:
            messages.warning(request,"Add a Address")
            return redirect('product_check', product_id=product_id, color_id=color_id, variant_id=variant_id, quantity=quantity)


        quantity=int(quantity)
        total_price = round(total_price)
    
    try:
        w_user = Wallet_user.objects.get(user=user)
    except ObjectDoesNotExist:
        w_user = None

    if coupon_code:
        coupon=MyCoupons.objects.get(coupon_code=coupon_code)
        if coupon.is_disabled == False:
            total_price=total_price-coupon.discount_price
        else:
            messages.info(request,'This Coupon is not valid now!')
            return redirect('singleproduct_checkout')

    selected_address = Address.objects.get(id=address_id)
    product=MyProducts.objects.get(id=product_id)
    variant=Variant.objects.get(id=variant_id)
    if variant.discount != 0:
        discount= variant.price * Decimal(variant.discount/100)
    else:
        discount=0
    print(discount)

    
    existing_address = OrderAddress.objects.filter(
            user=user,
            name= selected_address.name,
            phone=selected_address.phone,
            pincode= selected_address.pincode,
            locality= selected_address.locality,
            address=selected_address.address,
            city= selected_address.city,
            state= selected_address.state 
        ).exists()
    if existing_address:
        address = OrderAddress.objects.get(
            user=user,
            name= selected_address.name,
            phone=selected_address.phone,
            pincode= selected_address.pincode,
            locality= selected_address.locality,
            address=selected_address.address,
            city= selected_address.city,
            state= selected_address.state 
        )
        order = Order.objects.create(
        user=user,
        order_address= address,
        total_price=total_price,
        discount= discount,
        order_status=OrderStatus.objects.get(status='Pending'),
        payment=payment
    )
    else:
        order_address= OrderAddress(
        user= user,
        name= selected_address.name,
        phone=selected_address.phone,
        pincode= selected_address.pincode,
        locality= selected_address.locality,
        address=selected_address.address,
        city= selected_address.city,
        state= selected_address.state 
         
    )
        order_address.save() 

        order = Order.objects.create(
            user=user,
            order_address=order_address,
            total_price=total_price,
            discount= discount,
            order_status=OrderStatus.objects.get(status='Pending'),
            payment=payment
        )   
        
    if coupon_code:
        order.coupon_code = coupon_code
        order.coupon_price = coupon.discount_price
        order.save()

    
    OrderItem.objects.create(order=order, variant=variant, quantity=quantity)
    variant.quantity -= quantity
    variant.save()


    if payment == 'Wallet' and w_user:
        if w_user.amount >= total_price:
    
                w_user.amount -= total_price
                w_user.save()

                WalletHistory.objects.create(
                    user=user,
                    amount=total_price,
                    transaction_type='debit'
                )
        else:
                messages.error(request, "Insufficient funds in your wallet.")
                return redirect('product_check', product_id=product_id, color_id=color_id, variant_id=variant_id, quantity=quantity)
        

    if payment == 'Online' or payment=='Wallet':
        order.payment_status = "Paid"
        order.save
        print(order.payment_status)

    o_items= OrderItem.objects.get(order=order)


    context={
        'order_items':o_items,
        'order':order,
    }
    
    return render(request , "users/order_confirm.html",context)


    
def checkout(request):

    user = request.user
    if request.method == 'POST':
        address_id = request.POST.get('address_id') 
        payment= request.POST.get('selected_payment_option')
        coupon_code=request.POST.get('selected_coupon_code')
    if address_id:
        selected_address = Address.objects.get(id=address_id)
    else:
        messages.warning(request,"Add a Address")
        return redirect('cart_order')
    
    try:
        w_user = Wallet_user.objects.get(user=user)
    except ObjectDoesNotExist:
        w_user = None

    cart_items = cartitems.objects.filter(user=request.user)
    total_price = sum([item.total_price for item in cart_items])
    discount=0
    for i in cart_items:
        if i.variant.discount != 0:
            discount += i.variant.price * Decimal(i.variant.discount/100)
        else:
            discount=0
    print(discount)
    
    if coupon_code:
        coupon=MyCoupons.objects.get(coupon_code=coupon_code)
        if coupon.is_disabled == False:
            total_price=total_price-coupon.discount_price
        else:
            messages.info(request,'This Coupon is not valid now!')
            return redirect('cart_order')

    existing_address = OrderAddress.objects.filter(
            user=user,
            name= selected_address.name,
            phone=selected_address.phone,
            pincode= selected_address.pincode,
            locality= selected_address.locality,
            address=selected_address.address,
            city= selected_address.city,
            state= selected_address.state 
        ).exists()
    if existing_address:
        address = OrderAddress.objects.get(
            user=user,
            name= selected_address.name,
            phone=selected_address.phone,
            pincode= selected_address.pincode,
            locality= selected_address.locality,
            address=selected_address.address,
            city= selected_address.city,
            state= selected_address.state 
        )
        order = Order.objects.create(
        user=user,
        order_address= address,
        total_price=total_price,
        discount=discount,
        order_status=OrderStatus.objects.get(status='Pending'),
        payment=payment 
    )
    else:
        order_address= OrderAddress(
        user= user,
        name= selected_address.name,
        phone=selected_address.phone,
        pincode= selected_address.pincode,
        locality= selected_address.locality,
        address=selected_address.address,
        city= selected_address.city,
        state= selected_address.state 
         
    )
        order_address.save() 

        order = Order.objects.create(
            user=user,
            order_address=order_address,
            total_price=total_price,
            discount=discount,
            order_status=OrderStatus.objects.get(status='Pending'),
            payment= payment
        )

    if coupon_code:
        order.coupon_code = coupon_code
        order.coupon_price = coupon.discount_price
        order.save()


    for item in cart_items:
        order_items= OrderItem.objects.create(order=order, variant=item.variant, quantity=item.quantity)
        variant = get_object_or_404(Variant, id=item.variant.id)
        variant.quantity -= item.quantity
        variant.save()
    
    if payment == 'Wallet' and w_user:
            if w_user.amount >= total_price:
                w_user.amount -= total_price
                w_user.save()

                WalletHistory.objects.create(
                    user=user,
                    amount=total_price,
                    transaction_type='debit'
                )
            else:
                messages.error(request, "Insufficient funds in your wallet.")
                return redirect('cart_order')

    if payment == 'Online' or payment=='Wallet':
        order.payment_status = "Paid"
        order.save

    o_items= OrderItem.objects.filter(order=order)
    context={
        'order_items':o_items,
        'order':order,
    }
    return render(request , "users/order_confirm.html",context)


def user_orders(request):
    cart_items = cartitems.objects.filter(user=request.user)
    cart_items.delete()
    orders_list = Order.objects.filter(user=request.user)

    orders_per_page = 3  

    paginator = Paginator(orders_list, orders_per_page)

    page = request.GET.get('page')

    try:

        orders = paginator.page(page)
    except PageNotAnInteger:

        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

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

def wallet(request):
    wallet_user = Wallet_user.objects.get(user=request.user)
    wallet_history = WalletHistory.objects.filter(user=request.user).order_by('-date') 
    print(wallet_user.amount)
    w_amount= wallet_user.amount
    context={' wallet_user':wallet_user,'wallet_history':wallet_history,'w_amount':w_amount}
    return render(request, "users/wallet.html",context)



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

        if order.payment == 'Wallet' or order.payment == 'Online':
            user_wallet = Wallet_user.objects.get(user=request.user)
            user_wallet.amount += order.total_price
            user_wallet.save()

            WalletHistory.objects.create(
                user=request.user,
                amount=order.total_price,
                transaction_type='credit',
            )

        return redirect('user_orders')



def o_return(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        order_items = OrderItem.objects.filter(order=order)

        context = {
            'order': order,
            'order_items': order_items,
        }

        return render(request, 'users/return.html', context)
    except Order.DoesNotExist:
        raise Http404("Order does not exist")
   
def order_return(request,order_id):
    order = get_object_or_404(Order, order_id=order_id)
    if request.method == "POST":
        reason= request.POST.get('return_reason')
        print(reason)
 
        re_turn= Return.objects.create(
            user=request.user,reason=reason,order=order
        )
        status = get_object_or_404(OrderStatus, status='Returned')
        order.order_status=status
        order.save()

        user_wallet = Wallet_user.objects.get(user=request.user)
        user_wallet.amount += order.total_price
        user_wallet.save()

        WalletHistory.objects.create(
                user=request.user,
                amount=order.total_price,
                transaction_type='credit',
            ) 

        return redirect("user_orders") 





def generate_invoice_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_date = order.created_at.strftime('%b. %d, %Y, %I:%M %p')
    buffer = BytesIO()
    pdf_title = f'Invoice'
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    body_style = styles['BodyText']

    story = []
    story.append(Paragraph(pdf_title, title_style)) 
    story.append(Spacer(1, 12))
    story.append(Paragraph("Order Number: {}".format(order.order_id), title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Order Date: {}".format(order_date), body_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Payment Method: {}".format(order.payment), body_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Coupon applied: {}".format(order.coupon_code), body_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Flat off: {}".format(order.coupon_price), body_style))
    story.append(Spacer(1, 12))
    if order.discount != 0:
        story.append(Paragraph("Discount: {} Rs".format(order.discount), body_style))
        story.append(Spacer(1, 12))
    story.append(Paragraph("Total Amount: {} Rs".format(order.total_price), body_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Shipping Address:", body_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Name: {}".format(order.order_address.name), body_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Phone: {}".format(order.order_address.phone), body_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Address: {}, {}, {}, {} - {}".format(order.order_address.address, order.order_address.locality, order.order_address.city, order.order_address.state, order.order_address.pincode), body_style))
    story.append(Spacer(1, 12))


    # Adding product information in a table
    data = [['Product Name', 'Quantity', 'Price', 'Total']]
    for item in order.orderitem_set.all():
        data.append([Paragraph(item.variant.product_id.name, body_style), item.quantity, item.variant.price * item.quantity, order.total_price])

    table = Table(data, colWidths=[250, 100, 50, 50])  # Adjust the column width for the product name
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))

    story.append(table)

    pdf.build(story)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=order_invoice_{order_id}.pdf'
    buffer.seek(0)
    response.write(buffer.read())

    return response
