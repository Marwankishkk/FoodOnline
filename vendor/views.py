from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from accounts import utils
from accounts.forms import UserForm, UserProfileForm
from accounts.models import User, UserProfile
from accounts.utils import check_role_vendor
from menu.models import Category, FoodItem
from vendor.models import OpeningHour, Vendor

from .forms import CategoryForm, FoodItemForm, OpeningHourForm, VendorForm


@login_required(login_url='login')
@user_passes_test(utils.check_role_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance=profile)
        vendor_form = VendorForm(instance=vendor)
    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,
    }
    return render(request, 'vendor/vprofile.html', context)

@login_required(login_url='login')
@user_passes_test(utils.check_role_vendor)
def menu_builder(request):
    vendor = Vendor.objects.get(user=request.user)
    categories = Category.objects.filter(vendor=vendor)
    return render(request, 'vendor/menu_builder.html', {'categories': categories})

@login_required(login_url='login')
def fooditems_by_category(request, pk=None):
    vendor = Vendor.objects.get(user=request.user)
    category = get_object_or_404(Category, pk=pk)
    fooditems = FoodItem.objects.filter(category=category, vendor=vendor)
    context = {
        'fooditems': fooditems,
        'category': category,
    }   
    return render(request, 'vendor/fooditems_by_category.html', context)

@login_required(login_url='login')
@user_passes_test(utils.check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.vendor = Vendor.objects.get(user=request.user)
            # Generate unique slug from category name (required; DB has unique constraint)
            base_slug = slugify(category.category_name)
            slug = f"{base_slug}-{category.vendor.id}" if base_slug else f"category-{category.vendor.id}"
            category.slug = slug
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('menu_builder')
    else:
        form = CategoryForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context)

@login_required(login_url='login')
@user_passes_test(utils.check_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            base_slug = slugify(category.category_name)
            category.slug = f"{base_slug}-{category.vendor.id}" if base_slug else f"category-{category.vendor.id}"
            category.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('menu_builder')
    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'vendor/edit_category.html', context)

@login_required(login_url='login')
@user_passes_test(utils.check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category has been deleted successfully!')
    return redirect('menu_builder')


@login_required(login_url='login')
@user_passes_test(utils.check_role_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES)
        if form.is_valid():
            foodtitle = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = Vendor.objects.get(user=request.user)
            food.slug = slugify(foodtitle)
            form.save()
            messages.success(request, 'Food Item added successfully!')
            return redirect('fooditems_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodItemForm()
        # modify this form
        form.fields['category'].queryset = Category.objects.filter(vendor=Vendor.objects.get(user=request.user))
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_food.html', context)


@login_required(login_url='login')
@user_passes_test(utils.check_role_vendor)
def edit_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.vendor = Vendor.objects.get(user=request.user)
            food.slug = slugify(food_title)
            food.save()
            messages.success(request, 'Food item updated successfully!')
            return redirect('fooditems_by_category', food.category.id)
    else:
        
        form = FoodItemForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(vendor=Vendor.objects.get(user=request.user))
    context = {
        'form': form,
        'food': food,
    }
    return render(request, 'vendor/edit_food.html', context)

@login_required(login_url='login')
@user_passes_test(utils.check_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    food.delete()
    messages.success(request, 'Food item has been deleted successfully!')
    return redirect('fooditems_by_category', food.category.id)   

@login_required(login_url='login')
@user_passes_test(utils.check_role_vendor)
def opening_hours(request):
    opening_hours = OpeningHour.objects.filter(vendor=Vendor.objects.get(user=request.user))
    if request.method == 'POST':
        form = OpeningHourForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Opening hours updated successfully!')
            return redirect('opening_hours')
    else:
        form = OpeningHourForm()
    context = {
        'form': form,
        'opening_hours': opening_hours,
    }
    return render(request, 'vendor/opening_hours.html', context)

@login_required(login_url='login')
@user_passes_test(utils.check_role_vendor)
def add_opening_hours(request):
    # handle the data and save them inside the database
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')
            
            try:
                hour = OpeningHour.objects.create(vendor=Vendor.objects.get(user=request.user), day=day, from_hour=from_hour, to_hour=to_hour, is_closed=is_closed)
                if hour:
                    print('hour created: ', hour)
                    day = OpeningHour.objects.get(id=hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'is_closed': 'Closed'}
                    else:
                        response = {'status': 'success', 'id': hour.id, 'day': day.get_day_display(), 'from_hour': hour.from_hour, 'to_hour': hour.to_hour}
                return JsonResponse(response)
            except IntegrityError as e:
                response = {'status': 'failed', 'message': from_hour+'-'+to_hour+' already exists for this day!'}
                return JsonResponse(response)
        else:
            HttpResponse('Invalid request')

@login_required(login_url='login')
@user_passes_test(utils.check_role_vendor)
def remove_opening_hours(request, pk=None):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        hour = get_object_or_404(OpeningHour, pk=pk)
        hour_id = hour.id
        hour.delete()
        return JsonResponse({'status': 'success', 'id': hour_id})
    else:
        HttpResponse('Invalid request')
    return redirect('opening_hours')