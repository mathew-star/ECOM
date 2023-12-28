from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate,logout
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from accounts.models import CustomUser
from myadmin.models import BlockedUser,MyProducts,ProductImages,Variant, Color, Size
from django.shortcuts import render, get_object_or_404, redirect
from django.forms import inlineformset_factory
from myadmin.forms import CategoryForm,ProductForm, ColorForm, VariantFormSet, ImageFormSet


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
    size=Size.objects.all()
    products = MyProducts.objects.all()
    size= Size.objects.all()
    context={'products': products,
             'size': size
    }
    return render(request, 'myadmin/product_list.html', context)


def edit_product(request, product_id):
    categories = Category.objects.all()
    product = MyProducts.objects.get(id=product_id)
    v=Variant.objects.get(product_id_id=product_id)
    print(v.size)

    if request.method == 'POST':
        print("in edit")
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.category = Category.objects.get(id=request.POST['category'])
        product.save()

        for i in range(1, 5):
            image = request.FILES.get(f'image{i}')
            if image:
                ProductImages.objects.create(product=product, image=image)

        return redirect('product_list')

    return render(request, 'myadmin/edit_product.html', {'categories': categories, 'product': product})

def delete_product(request, product_id):
    product = get_object_or_404(MyProducts, id=product_id)
    product.delete()
    return redirect('product_list')

def add_product(request):
    if request.method == "POST":
        product_name = request.POST.get('name')
        product_description = request.POST.get('description')
        product_category = request.POST.get('category')
        v_color = request.POST.get('color')
        color = Color.objects.create(name=v_color)
        print(color.id)
        product = MyProducts(name=product_name, description=product_description, category_id=product_category)
        product.save()
        print( product_name,    v_color  )
       # Get the variants and images from the form
        

        variants = []
       
        
        for i in range(4):
            try:
                size_id = request.POST.get(f'size-{i}') 
                quantity = request.POST.get(f'variant-{i}-quantity')
                price = request.POST.get(f'variant-{i}-price')
                print("variants", size_id, quantity)

                if quantity is not None:
                    size_instance = Size.objects.get(id=size_id)
                    variants.append((size_instance.id, quantity, price))

            except Exception as e:
                print("Exception in variants loop:", e)
                break

        for i in range(1, 5):
                image = request.FILES.get(f'image{i}')
                if image:
                    ProductImages.objects.create(product=product, color_id=color.id, image=image)

        for variant in variants:
                size_id, quantity, price = variant
                print("In for var", size_id, quantity, price)
                variant_obj = Variant(color_id=color.id, size_id=size_id, product_id=product, quantity=quantity, price=price)
                variant_obj.save()

        return redirect('product_list')
    else:
        # Render the form for GET requests
        categories = Category.objects.all()
        sizes = Size.objects.all()
        return render(request, 'myadmin/add_product.html', {'categories': categories, 'sizes': sizes})