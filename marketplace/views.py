from datetime import date, datetime
import pytz

from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import render, redirect

from accounts.models import UserProfile
from menu.models import Category, FoodItem
from orders.forms import OrderForm
from vendor.models import OpeningHour, Vendor

from .context_processors import get_cart_counter, get_cart_amounts
from .models import Cart

egypt_tz = pytz.timezone('Africa/Cairo')

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True,user__is_active=True)[:8]
    context = {
        'vendors': vendors,
    }   
    return render(request, 'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
    print("vendor_slug", vendor_slug)
    vendor = Vendor.objects.get(vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch('fooditems', queryset=FoodItem.objects.filter(is_available=True))
    )
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    today = date.today().isoweekday()
    custom_day = (today + 1) % 7 + 2
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=custom_day)
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', 'from_hour')

   
    context = {
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,
    }
    return render(request, 'marketplace/vendor_detail.html', context)

def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                # Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                    # Increase the cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                except:
                    chkCart = Cart.objects.create(user=request.user, fooditem=fooditem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the food to the cart', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
            except:
                print('This food does not exist!')
                return JsonResponse({'status': 'Failed', 'message': 'This food does not exist!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
        
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    subtotal = 0
    for item in cart_items:
        subtotal += item.quantity * item.fooditem.price
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
    }
    return render(request, 'marketplace/cart.html', context)
def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Check if the food item exists
            try:
                fooditem = FoodItem.objects.get(id=food_id)
                try:
                    chkCart = Cart.objects.get(user=request.user, fooditem=fooditem)
                # Check if the user has already added that food to the cart
                    if chkCart.quantity > 1:
                        chkCart.quantity -= 1
                        chkCart.save()
                        return JsonResponse({'status': 'Success', 'message': 'Decreased the cart quantity', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity, 'cart_amount': get_cart_amounts(request)})
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0    
                        return JsonResponse({'status': 'Success', 'message': 'Removed the item from the cart', 'cart_counter': get_cart_counter(request), 'qty': 0, 'cart_amount': get_cart_amounts(request)})
                except:
                    return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
                
            except:
                print("error")
                return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})
def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                cart_item = Cart.objects.get(id=cart_id)
                cart_item.delete()
                return JsonResponse({'status': 'Success', 'message': 'Removed the item from the cart', 'cart_counter': get_cart_counter(request), 'qty': 0, 'cart_amount': get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'You do not have this item in your cart!'})
        else:
            return JsonResponse({'status': 'Failed', 'message': 'Invalid request!'})
    else:
        return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})
    return redirect('cart')

@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        print('Cart is empty')
        return redirect('marketplace')
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }
    form = OrderForm(initial=default_values)
    context = {
        'form': form,
        'cart_items': cart_items,
    }
    return render(request, 'marketplace/checkout.html', context)