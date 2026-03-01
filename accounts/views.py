from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserForm
from .models import User
from vendor.forms import VendorForm
from accounts.models import UserProfile
# Create your views here.
def registerUser(request):
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
            messages.success(request, 'Your account has been registered successfully!')
            return redirect('registerUser')
    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/registerUser.html', context)

def registerVendor(request):
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
            user_profile = UserProfile.objects.get(user=user)
            vendor.user_profile = user_profile
            vendor.save()
            messages.success(request, 'Your account has been registered successfully!')
            return redirect('registerVendor')
    else:
        vendor_form = VendorForm()
        user_form = UserForm()
    context = {
        'user_form': user_form,
        'vendor_form': vendor_form,
    }
    return render(request, 'accounts/registerVendor.html', context)
