import random
import string
from django.shortcuts import render, redirect,get_object_or_404
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate,logout
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import CustomUser
from myadmin.models import BlockedUser,MyProducts,ProductImages,Variant, Color
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import inlineformset_factory
from myadmin.forms import CategoryForm
from django.views.decorators.http import require_POST
from users.models import Order, OrderStatus,MyCoupons


from django.apps import apps
Category = apps.get_model('myadmin', 'Category')

# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def adminlogin(request):
    user = None

    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('adminhome')
    
    if request.method == 'POST':
        
        
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:  # Use the specific exception
            messages.warning(request, f"Admin with {email} does not exist")

        if user is not None:
            auth_user = authenticate(request, username=email, password=password)

            if auth_user:
                if auth_user.is_superuser:
                    login(request, user)
                    return redirect('adminhome')
                else:
                    messages.warning(request, 'You do not have permission to access this page!')
            else:
                messages.warning(request, "Invalid password")
    print("not post")
    return render(request, 'myadmin/adminlogin.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def adminlogout(request):
    if not request.user.is_authenticated:
        return redirect('adminlogin')
    messages.success(request, 'You have been successfully logged out.')
    logout(request)
    return redirect('adminlogin')


def adminhome(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request, 'myadmin/adminhome.html')
    return redirect('adminlogin')
    

def user_management_view(request):
    if request.user.is_superuser == False:
        return redirect( 'home')
    if not request.user.is_superuser:
        return render(request, 'users/userhome.html')
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        user = CustomUser.objects.get(id=user_id)  # Use your custom user model

        if action == 'Block':
            
            if not BlockedUser.objects.filter(user=user).exists():
                BlockedUser.objects.create(user=user)
                user.is_active = False  

        elif action == 'Unblock':
            
            blocked_user = BlockedUser.objects.filter(user=user).first()
            if blocked_user:
                blocked_user.delete()
                user.is_active = True  

        elif action == 'Edit':
            
            return redirect('edit_user', user_id=user_id)

        user.save() 
        return redirect('user_management_view')  

    users = CustomUser.objects.all()  # Use your custom user model
    return render(request, 'myadmin/user_management.html', {'users': users})


def edit_user_view(request, user_id):
        user = CustomUser.objects.get(id=user_id)
        if request.user.is_authenticated and request.user.is_superuser:
                return render(request, 'myadmin/adminhome.html')
        if request.method == 'POST':
            user.name = request.POST.get('name')
            user.email = request.POST.get('email')
            user.phone_number = request.POST.get('phone_number')
            user.save()
            return redirect('user_management_view')
        return render(request, 'myadmin/edituser.html', {'user': user})


def category_list(request):
    if request.user.is_superuser == False:
        return redirect( 'home')
    categories = Category.objects.all()
    return render(request, 'myadmin/category_list.html', {'categories': categories})

def add_category(request):
    if not request.user.is_superuser:
        return render(request, 'users/userhome.html')
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'myadmin/add_category.html', {'form': form})





def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'myadmin/edit_category.html', {'form': form, 'category': category})

def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category.delete()
    return redirect('category_list')



def toggle_category_listing(request, category_id):
    category = Category.objects.get(id=category_id)
    category.is_listed = not category.is_listed
    category.save()
    return redirect('category_list')


def toggle_product_listing(request, category_id):
    p = MyProducts.objects.get(id=category_id)
    p.is_listed = not p.is_listed
    p.save()
    return redirect('product_list')


def product_list(request):
    
    if request.user.is_superuser == False:
        return redirect( 'home')
    products = MyProducts.objects.all()
    context={'products': products
            
    }
    return render(request, 'myadmin/product_list.html', context)

def edit_product(request, product_id):
    
    category=Category.objects.all()
    product = get_object_or_404(MyProducts, id=product_id)
    variants = Variant.objects.filter(product_id=product)
    images = ProductImages.objects.filter(product=product)
    for i in images:
        print(i.image.url)

    if request.method == "POST":
        product_name = request.POST.get('name')
        product_description = request.POST.get('description')
        product_category = request.POST.get('category')
        product_is_listed = request.POST.get('is_listed') == 'on'

        product.name = product_name
        product.description = product_description
        product.category_id = product_category
        product.is_listed = product_is_listed
        product.save()

        for variant in variants:
            color_name = request.POST.get(f'color_{variant.id}')
            quantity = request.POST.get(f'quantity_{variant.id}')
            price = request.POST.get(f'price_{variant.id}')
            is_listed = request.POST.get(f'is_listed_{variant.id}') == 'on'

            variant.color.name = color_name
            variant.quantity = quantity
            variant.price = price
            variant.is_listed = is_listed
            variant.save()
            for image in images:
                image_field_name = f'image_{variant.id}_{image.id}'

                print(variant.color.name)
                if request.FILES.get(image_field_name):
                    print(request.FILES.get(image_field_name))
                    print("in var im")
                    image.image = request.FILES[image_field_name]
                    image.save()

            new_image_field_name = f'new_image_{variant.id}'
            new_image = request.FILES.get(new_image_field_name)
            if new_image:
                ProductImages.objects.create(product=product, color=variant.color, image=new_image)

        return redirect('product_list')

    return render(request, 'myadmin/edit_product.html', {'product': product, 'variants': variants, 'images': images,'category':category})

def add_variant(request, product_id):
    product = MyProducts.objects.get(id=product_id)

    color= Variant.objects.filter(product_id=product_id).values('color__name')
    p_colors=[]
    for i in color:
        for k,v in i.items():
            p_colors.append(v)

    context={'product': product,
             'color':p_colors
    }
    if request.method == "POST":
        color_name = request.POST.get('color')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        is_listed = request.POST.get('is_listed') == 'on'

        color= Color.objects.create(name=color_name)

        variant = Variant(color=color, product_id=product, quantity=quantity, price=price, is_listed=is_listed)
        variant.save()
        for i in range(1, 5):
                image = request.FILES.get(f'image{i}')
                if image:
                    ProductImages.objects.create(product=product, color=color, image=image)

        return redirect('product_list')


    return render(request, "myadmin/add_variants.html",context)




def delete_product(request, product_id):
    product = get_object_or_404(MyProducts, id=product_id)
    product.delete()
    return redirect('product_list')

def add_product(request):
    if request.method == "POST":
        product_name = request.POST.get('name')
        product_description = request.POST.get('description')
        product_category = request.POST.get('category')

        color_name = request.POST.get('color')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        is_listed = request.POST.get('is_listed') == 'on'

        product = MyProducts(name=product_name, description=product_description, category_id=product_category)
        product.save()

        color= Color.objects.create(name=color_name)

        variant = Variant(color=color, product_id=product, quantity=quantity, price=price, is_listed=is_listed)
        variant.save()

        for i in range(1, 5):
                image = request.FILES.get(f'image{i}')
                if image:
                    ProductImages.objects.create(product=product, color=color, image=image)

        return redirect('product_list')
    else:
        categories = Category.objects.all()
        return render(request, 'myadmin/add_product.html', {'categories': categories})
    

def admin_orders(request):
    orders = Order.objects.all()
    order_statuses = OrderStatus.objects.all()

    context = {
        'orders': orders,
        'order_statuses': order_statuses,
    }

    return render(request, 'myadmin/admin_orders.html', context)


def update_order_status(request, orderid):
   if request.method == "POST":
       print(request.POST)
       order_id = request.POST.get('order_id')
       order = get_object_or_404(Order, id=order_id)
       status_id = request.POST.get('status')
       status = get_object_or_404(OrderStatus, id=status_id)
       order.order_status = status
       order.save()
       return redirect('admin_orders')

   return render(request, 'admin_orders.html')


def add_new_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        name = request.POST.get('name')
        expiry_date = request.POST.get('expiry_date')
        min_purchase_amount = request.POST.get('min_purchase_amount')
        discount_percentage = request.POST.get('discount_percentage')

        # Validate and save the coupon
        try:
            expiry_date = timezone.datetime.strptime(expiry_date, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return render(request, 'myadmin/Create_coupon.html', {'error': 'Invalid date format'})

        MyCoupons.objects.create(
            coupon_code=coupon_code,
            name=name,
            expiry_date=expiry_date,
            min_purchase_amount=min_purchase_amount,
            discount_percentage=discount_percentage
        )

        return redirect('myadmin/coupon_list')
     
    return render(request,"myadmin/Create_coupon.html")

@csrf_exempt
def generate_coupon_code(request):
    if request.method == 'GET':
        coupon_code = generate_unique_coupon_code()

        return JsonResponse({'coupon_code': coupon_code})
    else:
        return JsonResponse({'error': 'Invalid request method'})

def generate_unique_coupon_code():
    code_length = 8
    characters = string.ascii_letters + string.digits
    coupon_code = ''.join(random.choice(characters) for i in range(code_length))
    
    while MyCoupons.objects.filter(code=coupon_code).exists():
        coupon_code = ''.join(random.choice(characters) for i in range(code_length))
    
    return coupon_code