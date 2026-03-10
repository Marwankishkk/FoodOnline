from django.urls import path, include
from . import views
urlpatterns = [
    #User Authentication
    path('',views.myAccount,name='myAccount'),
    path('registerUser/',views.registerUser,name='registerUser'),
    path('registerVendor/',views.registerVendor,name='registerVendor'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    # Dashboard
    path('customerDashboard/',views.customerDashboard,name='customerDashboard'),
    path('vendorDashboard/',views.vendorDashboard,name='vendorDashboard'),

    path('myAccount/',views.myAccount,name='myAccount'),
    # Activation
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),

   #  Password
    path('forgot_password/',views.forgot_password,name='forgot_password'),
    path('reset_password_validate/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate'),
    path('reset_password/',views.reset_password,name='reset_password'),
   # Vendor URLs
   path('vendor/',include('vendor.urls')),
   path('customer/',include('customers.urls')),
   ]