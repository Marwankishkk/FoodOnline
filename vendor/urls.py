from django.urls import path
from . import views
from accounts.views import vendorDashboard 
urlpatterns = [
    path('',vendorDashboard,name='vendorDashboard'),
    path('profile/ ',views.vprofile,name='vprofile'),
]