from django.urls import path

from . import views

urlpatterns = [
    path('profile/', views.cprofile, name='cprofile'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('order_detail/<int:order_number>/', views.order_detail, name='order_detail'),
]