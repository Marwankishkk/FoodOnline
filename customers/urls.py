from django.urls import path

from . import views

urlpatterns = [
    path('',views.customerDashboard,name='customerDashboard'),
    path('profile/ ',views.cprofile,name='cprofile'),
    
]