import random
import string
import json
import pytz
from PIL import Image
from django.core.files.images import get_image_dimensions
from django.core.exceptions import ValidationError
from django.core.validators import validate_image_file_extension
from datetime import datetime
import datetime
from django.db.models.functions import TruncMonth
from django.template.loader import get_template
from xhtml2pdf import pisa
from openpyxl import Workbook
from django.http import HttpResponse
from django.db.models import Count
from calendar import month_abbr
from decimal import Decimal
from datetime import date
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
from myadmin.models import BlockedUser,MyProducts,ProductImages,Variant, Color,CategoryOffer,ProductOffer
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import inlineformset_factory
from myadmin.forms import CategoryForm
from django.views.decorators.http import require_POST
from users.models import Order, OrderStatus,MyCoupons,OrderItem,Referral
from datetime import datetime
from datetime import timedelta
from django.db.models import Sum

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
            category=form.save()

            # new_offer_percentage = request.POST.get('new_offer_percentage')
            # new_offer_start_date = request.POST.get('new_offer_start_date')
            # new_offer_end_date = request.POST.get('new_offer_end_date')

            # if new_offer_percentage and new_offer_start_date and new_offer_end_date:
            #     CategoryOffer.objects.create(
            #         category=category,
            #         discount_percentage=new_offer_percentage,
            #         start_date=new_offer_start_date,
            #         end_date=new_offer_end_date
            #     )
            try:
                category_offer=CategoryOffer.objects.get(category=category)
            except:
                category_offer=CategoryOffer.objects.create(category=category,discount_percentage=0)



            return redirect('category_list')


    else:
        form = CategoryForm()
    return render(request, 'myadmin/add_category.html', {'form': form})





def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    category_offer = get_object_or_404(CategoryOffer, category=category)
    if request.method == 'POST':
        form = CategoryForm(request.POST,request.FILES, instance=category )
        # discount_percentage = request.POST.get('new_offer_percentage', 0)
        # new_offer_start_date = request.POST.get('new_offer_start_date', date.today())
        # new_offer_end_date = request.POST.get('new_offer_end_date', date.today())

        # try:
        #     start_date = date.fromisoformat(new_offer_start_date)
        #     end_date = date.fromisoformat(new_offer_end_date)
        # except ValueError:
        #     return render(request, 'myadmin/edit_category.html', {'form': form, 'category': category, 'category_offer': category_offer, 'error': 'Invalid date format.'})

        # print(start_date , end_date)
        # print(end_date < start_date)
        # print(date.today())
        # print(start_date < date.today())

        # if end_date < start_date:
        #     messages.warning(request,"Error date !")
        #     return render(request, 'myadmin/edit_category.html', {'form': form, 'category': category, 'category_offer': category_offer, 'error': 'End date should be after the start date.'})

        # if start_date < date.today():
        #     messages.warning(request,"Error date !")
        #     return render(request, 'myadmin/edit_category.html', {'form': form, 'category': category, 'category_offer': category_offer, 'error': 'Start date should be today or in the future.'})

        # if end_date < date.today():
        #     messages.warning(request,"Error date !")
        #     return render(request, 'myadmin/edit_category.html', {'form': form, 'category': category, 'category_offer': category_offer, 'error': 'End date should be today or in the future.'})

        if form.is_valid():
            form.save()

            # if discount_percentage:
            #     category_offer.discount_percentage = discount_percentage
            # if start_date:
            #     category_offer.start_date = start_date
            # if end_date:
            #     category_offer.end_date = end_date

            # category_offer.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'myadmin/edit_category.html', {'form': form, 'category': category, 'category_offer':category_offer })

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

def is_valid_image(file):
    try:

        width, height = get_image_dimensions(file)

        if width is not None and height is not None and isinstance(width, int) and isinstance(height, int):
            return width > 0 and height > 0
        else:
            return False
    except ValidationError:
        return False



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

        if not product_name:
            messages.error(request, 'Please provide a product name.')
            return render(request, 'myadmin/edit_product.html', {'product': product, 'variants': variants, 'images': images, 'category': category})


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
            if not color_name:
                messages.error(request, 'Please provide a color name for all variants.')
                return render(request, 'myadmin/edit_product.html', {'product': product, 'variants': variants, 'images': images, 'category': category})

            if not quantity.isdigit() or int(quantity) <= 0:
                messages.error(request, 'Please provide a valid quantity for all variants.')
                return render(request, 'myadmin/edit_product.html', {'product': product, 'variants': variants, 'images': images, 'category': category})
            
            if float(price) <= 0:
                messages.error(request, 'Please provide a valid price for all variants.')
                return render(request, 'myadmin/edit_product.html', {'product': product, 'variants': variants, 'images': images, 'category': category})


            variant.color.name = color_name
            variant.quantity = quantity
            variant.stock_added = quantity
            variant.price = price
            variant.is_listed = is_listed
            variant.save()
            for image in images:
                image_field_name = f'image_{variant.id}_{image.id}'

                if request.FILES.get(image_field_name):
                    image.image = request.FILES[image_field_name]
                    new_image = request.FILES[image_field_name]
                    if not is_valid_image(new_image):
                        messages.error(request, 'Invalid image file format. Please upload a valid image file.')
                        return render(request, 'myadmin/edit_product.html', {'product': product, 'variants': variants, 'images': images, 'category': category})

                    image.save()


            new_image_field_name = f'new_image_{variant.id}'
            new_image = request.FILES.get(new_image_field_name)
            if new_image:
                if not is_valid_image(new_image):
                        messages.error(request, 'Invalid image file format. Please upload a valid image file.')
                        return render(request, 'myadmin/edit_product.html', {'product': product, 'variants': variants, 'images': images, 'category': category})

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
        if not color_name:
                messages.error(request, 'Please provide a color name for all variants.')
                return render(request, "myadmin/add_variants.html",context)

        if not quantity.isdigit() or int(quantity) <= 0:
                messages.error(request, 'Please provide a valid quantity for all variants.')
                return render(request, "myadmin/add_variants.html",context)
        if float(price) <= 0:
                messages.error(request, 'Please provide a valid price for all variants.')
                return render(request, "myadmin/add_variants.html",context)


        variant = Variant(color=color, product_id=product,stock_added=quantity, quantity=quantity, price=price, is_listed=is_listed)
        variant.save()
        for i in range(1, 5):
                image = request.FILES.get(f'image{i}')
                if image:
                        if not is_valid_image(image):
                            messages.error(request, 'Invalid image file format. Please upload a valid image file.')
                            return render(request, "myadmin/add_variants.html",context)

                        ProductImages.objects.create(product=product, color=color, image=image)

        return redirect('product_list')


    return render(request, "myadmin/add_variants.html",context)




def delete_product(request, product_id):
    product = get_object_or_404(MyProducts, id=product_id)
    product.delete()
    return redirect('product_list')

def add_product(request):
    categories = Category.objects.all()

    if request.method == "POST":
        # Extracting form data
        product_name = request.POST.get('name')
        product_description = request.POST.get('description')
        product_category = request.POST.get('category')

        color_name = request.POST.get('color')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        is_listed = request.POST.get('is_listed') == 'on'

        # Validations
        if not product_name or not product_description or not product_category or not color_name:
            messages.error(request, 'All fields are required.')
            return redirect('add_product')

        if not quantity.isdigit() or int(quantity) <= 0:
            messages.error(request, 'Please provide a valid quantity.')
            return redirect('add_product')

        if not price.replace('.', '').isdigit() or float(price) <= 0:
            messages.error(request, 'Please provide a valid price.')
            return redirect('add_product')

        # Create and save product, color, and variant
        product = MyProducts(name=product_name, description=product_description, category_id=product_category)
        product.save()

        color = Color.objects.create(name=color_name)
        variant = Variant(color=color, product_id=product, stock_added=quantity, quantity=quantity, price=price, is_listed=is_listed)
        variant.save()

        # Create ProductImages
        try:
            for i in range(1, 5):
                image = request.FILES.get(f'image{i}')
                if image:
                    if not is_valid_image(image):
                        messages.error(request, 'Invalid image file format. Please upload a valid image file.')
                        raise ValueError('Invalid image file format')

                    ProductImages.objects.create(product=product, color=color, image=image)

        except Exception as e:
            # Rollback: Delete the variant and product if an error occurs during image processing
            if variant.id:
                variant.delete()

            if product.id:
                product.delete()

            messages.error(request, f'Error processing images: {str(e)}')
            return render(request, 'myadmin/add_product.html', {'categories': categories})

        return redirect('product_list')

    else:
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
        discount_price = request.POST.get('discount_price')

        # Basic validation checks
        if not coupon_code or not name or not expiry_date or not min_purchase_amount or not discount_price:
            messages.error(request, 'All fields are required. Please fill in all the details.')
            return render(request, 'myadmin/Create_coupon.html')

        try:
            # Adjust the format to match the date-only input
            expiry_date = timezone.datetime.strptime(expiry_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, 'Invalid date format. Please use the YYYY-MM-DD format.')
            return render(request, 'myadmin/Create_coupon.html')
  
        if discount_price > min_purchase_amount:
            messages.warning(request,'Discount price should be less than or equal to the minimum purchase amount')
            return render(request, 'myadmin/Create_coupon.html')
        
        if expiry_date <= timezone.now().date():
            messages.error(request, 'Expiry date must be in the future.')
            return render(request, 'myadmin/Create_coupon.html')

        MyCoupons.objects.create(
            coupon_code=coupon_code,
            name=name,
            expiry_date=expiry_date,
            min_purchase_amount=min_purchase_amount,
            discount_price=discount_price
        )

        messages.success(request, 'Coupon created successfully!')
        return redirect('coupon_list')

    return render(request, 'myadmin/Create_coupon.html')

def coupon_list(request):
    coupons = MyCoupons.objects.all()
    for i in coupons:
        print(i.coupon_code ,i.is_valid())
    return render(request,'myadmin/Coupon_list.html',{'coupons':coupons })


@csrf_exempt
def generate_coupon_code(request):
    if request.method == 'GET':

        coupon_code = generate_unique_coupon_code()
        print(coupon_code)

        return JsonResponse({'coupon_code': coupon_code})
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
def generate_unique_coupon_code():

    code_length = 8
    characters = string.ascii_letters + string.digits
    coupon_code = ''.join(random.choice(characters) for i in range(code_length))
    
    while MyCoupons.objects.filter(coupon_code=coupon_code).exists():
        coupon_code = ''.join(random.choice(characters) for i in range(code_length))

    return coupon_code


def admin_order_detail(request, oid):
    order = get_object_or_404(Order, order_id=oid)
    order_items = OrderItem.objects.filter(order=order)
    context={
        'order': order,
        'order_items': order_items,
    }
    return render(request, "myadmin/admin_orderview.html",context)


def productoffer(request):
    products = MyProducts.objects.all()
    variants= Variant.objects.all()
    return render(request , "myadmin/productoffer.html",{'products':products,'variants':variants})
def categoryoffer(request):
    cat = CategoryOffer.objects.all()
    category = Category.objects.all()
    variants= Variant.objects.all()
    return render(request , "myadmin/categoryoffer.html",{'category':cat, 'variants':variants})

def addoffer(request):
    if request.method == "POST":
        variant_id = request.POST.get('variant_id')
        discount = request.POST.get('discount')
        variant = get_object_or_404(Variant, id=variant_id)
    
        try:
            discount_percentage = float(discount)
            if 0 <= discount_percentage <= 70:
                variant.discount = discount_percentage
                variant.discount_price = variant.get_discount()
                variant.save()
                messages.success(request, "Offer added successfully")
                return redirect('productoffer')
            else:
                messages.error(request, "Invalid Discount Percentage")
                return redirect('productoffer')
        except ValueError:
            messages.error(request, "Invalid discount percentage")
            return redirect('productoffer')
    else:
        messages.error(request, "Invalid request method")
        return redirect('productoffer')    


def add_category_offer(request):
    if request.method == "POST":
        category_id = request.POST.get('category_id')
        print(category_id)
        discount = request.POST.get('discount')  
        category = Category.objects.get(id=category_id)
        variants = Variant.objects.filter(product_id__category=category)
        categoryoffer=CategoryOffer.objects.get(category=category)

        try:
            discount = Decimal(discount)
            if 0 <= discount <= 70:
                for variant in variants:
                    variant.discount = discount
                    variant.discount_price = variant.get_discount()
                    variant.save()

                categoryoffer.discount_percentage = discount
                categoryoffer.save()
                messages.success(request, "Offer added successfully")
                return redirect('productoffer')
            
            else:
                messages.error(request, "Invalid Discount Percentage")
                return redirect('productoffer')
        except ValueError:
            messages.error(request, "Invalid Discount Percentage")
            return redirect( 'productoffer')



def adminhome(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders_count_today = Order.get_daily_orders_count_today()
        cancelled_orders_count_today = Order.get_daily_orders_chart_data()
        categories = Category.objects.annotate(order_count=Count('myproducts__variant__orderitem__order__id'))

        high_demand_category = categories.order_by('-order_count').first()
        print(high_demand_category)

        payment_options = Order.objects.values('payment').annotate(order_count=Count('id'))

        high_demand_payment_option = payment_options.order_by('-order_count').first()
        try:
            p=payment_options[0]
            high_demand_payment_option=p['payment']
            payment_order_count = p['order_count']
        except:
            high_demand_payment_option=None
            payment_order_count=0



        today = datetime.today().date()
        start_of_month = today.replace(day=1)
        total_revenue_this_month = Order.objects.filter(created_at__date__gte=start_of_month).aggregate(total_revenue=Sum('total_price'))['total_revenue']

        total_sales_today = Order.objects.filter(created_at__date=today).count()


        daily_order_data = Order.get_daily_orders_chart_data()
        context = {
            "OCT": orders_count_today,
            "COCT": cancelled_orders_count_today,
            'daily_order_data': json.dumps(daily_order_data),
            'high_demand_category':high_demand_category,
            'high_demand_payment_option':high_demand_payment_option,
            'payment_order_count':payment_order_count,
            'total_revenue_this_month':total_revenue_this_month,
            'total_sales_today':total_sales_today,

        }

        return render(request, 'myadmin/adminhome.html', context)
    return redirect('adminlogin')




def charts(request):
    now = datetime.now()
    orders = Order.objects.filter(created_at__year=now.year).values('created_at__month').annotate(count=Count('id'))
    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    data = [orders.filter(created_at__month=i).aggregate(count=Count('id'))['count'] if orders.filter(created_at__month=i).exists() else 0 for i in range(1, 13)]

    return render(request, "myadmin/charts.html", {'labels': labels, 'data': data})



def order_chart(request):
    if request.method == 'POST':
        chart_type = request.POST.get('chart')
        if chart_type == 'monthly':
            return get_monthly_chart_data(request)
        elif chart_type == 'yearly':
            return get_yearly_chart_data(request)
    return render(request, "myadmin/charts.html")

def get_monthly_chart_data(request):
    now = datetime.now()
    orders = Order.objects.filter(created_at__year=now.year).values('created_at__month').annotate(count=Count('id'))
    labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    data = [orders.filter(created_at__month=i).aggregate(count=Count('id'))['count'] if orders.filter(created_at__month=i).exists() else 0 for i in range(1, 13)]

    return render(request, "myadmin/charts.html", {'labels': labels, 'data': data, 'chart_type': 'monthly'})

def get_yearly_chart_data(request):
    now = datetime.now()
    orders = Order.objects.filter(created_at__year=now.year).values('created_at__year').annotate(count=Count('id'))
    labels = [str(year['created_at__year']) for year in orders]
    data = [year['count'] for year in orders]

    return render(request, "myadmin/charts.html", {'labels': labels, 'data': data, 'chart_type': 'yearly'})



def sales(request):
    return render(request, "myadmin/salesreport.html")


def sales_table(request,format):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    print(start_date, end_date)
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)
    
    today = timezone.now().date()
    if start_date > today:
        messages.error(request,"Start date cannot be in the future")
        return redirect('sales')
    
    if end_date > today:
        messages.error(request,"End date cannot be in the future")
        return redirect('sales')
    

    if end_date < start_date:
        messages.error(request,"End date cannot be before start date")
        return redirect('sales')

    
    orders = Order.objects.filter(created_at__date__range=[start_date, end_date])

    return render(request, "myadmin/pdf_preview.html",{'orders':orders,'format':format,'start_date':start_date,'end_date':end_date})
    

def sales_report(request,format):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    print(start_date_str, end_date_str)
    print(type(start_date_str), type(end_date_str))
    
    try:
        start_date = datetime.strptime(start_date_str, '%b. %d, %Y').date()
        end_date = datetime.strptime(end_date_str, '%b. %d, %Y').date()
    except ValueError:
        return HttpResponse("Invalid date format", status=400)

        # Date validation
    today = timezone.now().date()

    if start_date > today:
        messages.error(request,"Start date cannot be in the future")
        return redirect('sales')
    
    if end_date > today:
        messages.error(request,"End date cannot be in the future")
        return redirect('sales')
    

    if end_date < start_date:
        messages.error(request,"End date cannot be before start date")
        return redirect('sales')


    if format == 'pdf':
        return generate_pdf(start_date, end_date)
    elif format == 'excel':
        return generate_excel(start_date, end_date)
    else:
        return HttpResponse("Invalid format", status=400)

def generate_pdf(start_date, end_date):
    orders = Order.objects.filter(created_at__date__range=[start_date, end_date])

    template_path = 'myadmin/admin_pdf_salesreport.html'
    context = {'orders': orders}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_{end_date}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response, encoding='UTF-8')
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response


def generate_excel(start_date, end_date):
   orders = Order.objects.filter(created_at__date__range=[start_date, end_date])

   response = HttpResponse(content_type='application/ms-excel')
   response['Content-Disposition'] = f'attachment; filename="sales_report_{start_date}_{end_date}.xlsx"'

   wb = Workbook()
   ws = wb.active
   ws.title = "Sales report"

   headers = ["Order ID", "Date", "Products", "User", "Price", "Quantity", "Payment"]
   ws.append(headers)

   for order in orders:

       created_at = order.created_at.astimezone(pytz.UTC).replace(tzinfo=None)

       product_names = ", ".join([item.variant.product_id.name for item in order.orderitem_set.all()])

       ws.append([
           f"ORD{order.id}",
           created_at,
           product_names,
           order.user.name,
           order.total_price,
           order.orderitem_set.aggregate(Sum('quantity'))['quantity__sum'],
           order.payment
       ])

   wb.save(response)
   return response


def referal(request):
    refer= Referral.objects.all()
    
    return render(request,"myadmin/referal.html", {'refer':refer})


def stock_report(request):
    products = MyProducts.objects.all()
    variants= Variant.objects.all()
    return render(request , "myadmin/stockreport.html",{'products':products,'variants':variants})