from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
import json

from accounts import utils
from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile

from orders.models import Order, OrderedFood


@login_required(login_url='login')
@user_passes_test(utils.check_role_customer)
def cprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        user_form = UserInfoForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('cprofile')
        else:
            messages.error(request, 'Your profile has not been updated successfully!')
            print(user_form.errors)
            print(profile_form.errors)
            return redirect('cprofile')
            
    else:
        user_form = UserInfoForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    }
    return render(request, 'customers/cprofile.html', context)


@login_required(login_url='login')
@user_passes_test(utils.check_role_customer)
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'customers/my_orders.html', context)

@login_required(login_url='login')
@user_passes_test(utils.check_role_customer)
def order_detail(request, order_number):
    order = Order.objects.get(order_number=order_number)
    ordered_food = OrderedFood.objects.filter(order=order)
    subtotal = 0
    for item in ordered_food:
        subtotal += (item.price * item.quantity)
    
    tax_data = json.loads(order.tax_data)
    context = {
        'order': order,
        'subtotal': subtotal,
        'tax_data': tax_data,
    }
    return render(request, 'customers/order_detail.html', context)