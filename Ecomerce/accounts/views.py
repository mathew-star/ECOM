from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts import form
from django.contrib import messages
from django.urls import reverse ,reverse_lazy
from django.contrib.auth import login as auth_login,authenticate,logout as auth_logout
from accounts.form import CustomUserCreationForm
from accounts.models import CustomUser
from myadmin.models import BlockedUser
from myadmin.models import Category,MyProducts,ProductImages, Variant
from users.models import cartitems
from django.core import signing 
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
import pyotp
import jwt
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import JsonResponse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View



class PasswordResetTokenGeneratorExtended(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) + str(user.is_active)
        )
def password_reset_request(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = CustomUser.objects.get(email=email)

        # Generate token
        token_generator = PasswordResetTokenGeneratorExtended()
        token = token_generator.make_token(user)

        # Create JWT token
        expiration_time = datetime.utcnow() + timedelta(days=1)
        token_payload = {
            'user_id': user.id,
            'exp': expiration_time,
        }
        jwt_token = jwt.encode(token_payload, settings.JWT_SECRET_KEY, algorithm='HS256')

        # Send email with reset link
        reset_url = f'{settings.BASE_URL}/reset/{urlsafe_base64_encode(force_bytes(user.pk))}/{jwt_token}'
        send_mail(
            'Password Reset',
            f'Click the link to reset your password: {reset_url}',
            'mjunni99@gmail.com',
            [user.email],
            fail_silently=False,
        )

        messages.success(request,"Email has been sent to your email address")
    return render(request, 'accounts/password_reset_request.html')



def password_reset_confirm(request, uidb64, token):
    try:
        user_id = str(urlsafe_base64_decode(uidb64), 'utf-8')
        user = get_object_or_404(CustomUser, id=user_id)
        jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
    except (TypeError, ValueError, OverflowError, jwt.ExpiredSignatureError):
        messages.warning(request,"Invalid test link...Go to login")

    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.success(request,"Password reset sucessfull")

        # Set the new password
        user.set_password(new_password)
        user.save()

        messages.success(request, 'Password reset successfully.')
    return render(request, 'accounts/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})





def send_otp_email(user):
   secret_key = pyotp.random_base32()
   totp = pyotp.TOTP(secret_key, digits=6, interval=120)
   otp = totp.now()
   user.otp_secret_key = secret_key
   user.otp = otp
   user.save()

   subject = 'OTP Verification'
   message = f'Your OTP for email verification is: {otp}'
   from_email = 'mjunni99@gmail.com'
   to_email = user.email

   send_mail(subject, message, from_email, [to_email])

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def signup(request):
    print(request.user.is_authenticated)
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate user until OTP verification
            user.save()

            # Invalidate any existing OTP for the user
            user.otp = None
            user.save()

            send_otp_email(user)

            messages.success(request, 'Account created successfully. Please check your email for OTP verification.')
            return redirect('verify_otp', user_id=user.id)
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/usignup.html', {'form': form})

@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def login(request):
    user = None  # Initialize user variable
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            messages.warning(request, f"User with {email} does not exist")

        if user is not None:
            blocked_user = BlockedUser.objects.filter(user=user).first()
            if user.is_active == False:
                messages.error(request, "Account has been deactivated.")

            if blocked_user:
                messages.warning(request, "User is blocked by admin.")

            else:
                authenticated_user = authenticate(request, email=email, password=password)
                
                if authenticated_user is not None:
                    auth_login(request, authenticated_user)
                    return redirect("home")
                else:
                    messages.warning(request, "Invalid password")
        else:
            messages.warning(request, "User doesn't exist, Create an account")

    return render(request, 'accounts/ulogin.html', {'user': user})



@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('signup')


@cache_control(no_cache=True, must_revalidate=True, no_store=False)
def verify_otp(request, user_id):
    user = CustomUser.objects.get(id=user_id)

    if request.method == 'POST':
        entered_otp = int(''.join(request.POST.getlist('otp')).strip())
        if entered_otp == '':
            messages.error(request, 'Please enter all OTP digits.')
            return render(request, 'accounts/otp.html', {'user': user})
        print(user.otp)
        print(entered_otp)
        if entered_otp == user.otp:
            user.is_active = True
            user.save()
            auth_login(request, user)
            messages.success(request, 'OTP verified successfully. You are now logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect OTP. Please try again.')

    return render(request, 'accounts/otp.html', {'user': user})


def resend_otp(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    
    # Invalidate any existing OTP for the user
    user.otp = None
    user.save()

    send_otp_email(user)

    messages.success(request, 'OTP resent successfully. Please check your email for the new OTP.')
    return redirect('verify_otp', user_id=user.id)


def home(request):
    if request.user.is_authenticated == False and request.user.is_active == False:
        return redirect('signup')
    
    categories= Category.objects.all()
    products= MyProducts.objects.all()

    first_variant_prices = {}

    # Fetch the first variant price for each product
    for product in products:
        first_variant = Variant.objects.filter(product_id=product).first()
        if first_variant:
            first_variant_prices[product.id] = first_variant.price
    context = {
         'categories':categories,
        'products': products,
        'first_variant':first_variant,
    }

    images= ProductImages.objects.all()
    return render(request,'users/userhome.html',context)

    