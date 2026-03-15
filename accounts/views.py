from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.utils.text import slugify

from accounts import utils
from accounts.utils import send_verification_email
from vendor.forms import VendorForm
from vendor.models import Vendor

from orders.models import Order

from .forms import UserForm
from .models import User, UserProfile


def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
            user.role = User.CUSTOMER
            user.save()
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, 'Your account has been registered successfully! Please wait for the activation email.')
            return redirect('registerUser')
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)

def registerVendor(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    if request.method == 'POST':
        vendor_form = VendorForm(request.POST, request.FILES)
        user_form = UserForm(request.POST)
        if vendor_form.is_valid() and user_form.is_valid():
            user_cleaned_data = user_form.cleaned_data
            vendor_cleaned_data = vendor_form.cleaned_data
            user = User.objects.create_user(
                first_name=user_cleaned_data['first_name'],
                last_name=user_cleaned_data['last_name'],
                username=user_cleaned_data['username'],
                email=user_cleaned_data['email'],
                password=user_cleaned_data['password'],
            )
            user.role = User.VENDOR
            user.save()
            vendor = vendor_form.save(commit=False)
            vendor.user = user
            vendor_name=vendor_form.cleaned_data['vendor_name']
            vendor.vendor_slug = slugify(vendor_name)+'-'+str(user.id)
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, 'Your account has been registered successfully! Please wait for the activation email.')
            return redirect('registerVendor')
    else:
        vendor_form = VendorForm()
        user_form = UserForm()
    context = {
        'user_form': user_form,
        'vendor_form': vendor_form,
    }
    return render(request, 'accounts/registerVendor.html', context)

def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(Exception, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account is activated successfully!')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('login')

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(request, email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    else:
        return render(request, 'accounts/login.html')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are now logged out.')
    return redirect('login')
    
@login_required(login_url='login')
@user_passes_test(utils.check_role_customer)
def customerDashboard(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    recent_orders = orders[:5]
    context = {
        'recent_orders': recent_orders,
        'orders_count': orders.count(),
    }
    return render(request, 'accounts/customerDashboard.html', context)

@login_required(login_url='login')
@user_passes_test(utils.check_role_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendorDashboard.html')

def myAccount(request):
    return redirect(utils.detectUser(request.user))

def forgot_password(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                mail_subject = 'Reset Your Password'
                email_template = 'accounts/emails/reset_password_email.html'
                send_verification_email(request, user, mail_subject, email_template)
                messages.success(request, 'Password reset email has been sent to your email address.')
                return redirect('forgot_password')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email address.')
                return redirect('forgot_password')
        else:
            messages.error(request, 'Please enter your email address.')
            return redirect('forgot_password')
    return render(request, 'accounts/forget_password.html')
def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(Exception, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        # Clear any existing session uid before setting a new one
        if 'uid' in request.session:
            del request.session['uid']
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('reset_password')  
    else:
        messages.error(request, 'Invalid or expired reset password link. Please request a new one.')
        return redirect('forgot_password')
def reset_password(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
    if 'uid' not in request.session:
        messages.error(request, 'Invalid reset password link. Please request a new password reset.')
        return redirect('forgot_password')
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        if not password or not confirm_password:
            messages.error(request, 'Please fill in all fields')
            return redirect('reset_password')
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('reset_password')
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long')
            return redirect('reset_password')
        try:
            uid = request.session.get('uid')
            user = User.objects.get(pk=uid)
            user.set_password(password)
            user.is_active = True
            user.save()
            del request.session['uid']
            messages.success(request, 'Password reset successfully. Please login with your new password.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Invalid user. Please request a new password reset.')
            if 'uid' in request.session:
                del request.session['uid']
            return redirect('forgot_password')
    return render(request, 'accounts/reset_password.html')