from django.db.models import Q
from django.shortcuts import render

from menu.models import FoodItem
from vendor.models import Vendor


def home(request):
    vendors=Vendor.objects.filter(is_approved=True,user__is_active=True)
    context={
        'vendors':vendors,
    }
    return render(request, 'home.html', context)    

# def home_search(request):
#     keyword = request.GET.get('q')
#     vendors = []
#     food_items = []

#     if keyword:
#         vendors = Vendor.objects.filter(
#             Q(vendor_name__icontains=keyword) | Q(category__category_name__icontains=keyword)
#         ).distinct()

#         # Update FoodItem search as well (assuming it has a 'food_title' or similar)
#         # If FoodItem also uses a different field, check your models.py!
#         food_items = FoodItem.objects.filter(
#             Q(food_title__icontains=keyword) 
#         ).distinct()

#     context = {
#         'vendors': vendors,
#         'food_items': food_items,
#         'query': keyword,
#     }
#     return render(request, 'home.html', context)
def home_search(request):
    keyword = request.GET.get('q')
    vendors = []
    food_items = []

    if keyword:
        vendors = Vendor.objects.filter(vendor_name__icontains=keyword)
        food_items = FoodItem.objects.filter(food_title__icontains=keyword)

    context = {
        'vendors': vendors,
        'food_items': food_items,
        'query': keyword,
    }

    # If it's an HTMX request, only return the results snippet
    if request.headers.get('HX-Request'):
        return render(request, 'includes/search_results_partial.html', context)
    
    # Otherwise, return the full page
    return render(request, 'home.html', context)