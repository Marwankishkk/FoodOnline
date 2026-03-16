from django.urls import path

from accounts.views import vendorDashboard

from . import views

urlpatterns = [
    # Vendor Dashboard
    path('',vendorDashboard,name='vendorDashboard'),
    # Vendor Profile
    path('profile/ ',views.vprofile,name='vprofile'),
    # Menu Builder
    path('menu-builder/',views.menu_builder,name='menu_builder'),
    # Food Items by Category
    path('menu-builder/category/<int:pk>/',views.fooditems_by_category,name='fooditems_by_category'),
    # Menu Builder crud
    path('menu-builder/add-category/',views.add_category,name='add_category'),
    path('menu-builder/edit-category/<int:pk>/',views.edit_category,name='edit_category'),
    path('menu-builder/delete-category/<int:pk>/',views.delete_category,name='delete_category'),
    # Food Items crud
    path('menu-builder/fooditems/add/',views.add_food,name='add_food'),
    path('menu-builder/fooditems/edit/<int:pk>/',views.edit_food,name='edit_food'),
    path('menu-builder/fooditems/delete/<int:pk>/',views.delete_food,name='delete_food'),
    # Opening Hours
    path('opening-hours/',views.opening_hours,name='opening_hours'),
    path('opening-hours/add/',views.add_opening_hours,name='add_opening_hour'),
    path('opening-hours/remove/<int:pk>/',views.remove_opening_hours,name='remove_opening_hour'),
    # My Orders
    path('my_orders/',views.vendor_my_orders,name='vendor_my_orders'),
    path('order_detail/<int:order_number>/',views.vendor_order_detail,name='vendor_order_detail'),
]