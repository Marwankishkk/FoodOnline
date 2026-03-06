from django.urls import path
from . import views
from accounts.views import vendorDashboard 
urlpatterns = [
    path('',vendorDashboard,name='vendorDashboard'),
    path('profile/ ',views.vprofile,name='vprofile'),
    path('menu-builder/',views.menu_builder,name='menu_builder'),
    path('menu-builder/category/<int:pk>/',views.fooditems_by_category,name='fooditems_by_category'),
    path('menu-builder/add-category/',views.add_category,name='add_category'),
    path('menu-builder/edit-category/<int:pk>/',views.edit_category,name='edit_category'),
    path('menu-builder/delete-category/<int:pk>/',views.delete_category,name='delete_category'),
    path('menu-builder/fooditems/add/',views.add_food,name='add_food'),
    path('menu-builder/fooditems/edit/<int:pk>/',views.edit_food,name='edit_food'),
    path('menu-builder/fooditems/delete/<int:pk>/',views.delete_food,name='delete_food'),
]