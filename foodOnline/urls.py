from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from marketplace import views as marketplace_views

from . import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    # Home
    path('',views.home,name='home'),
    # Accounts
    path('',include('accounts.urls')),
    # Vendor
    path('vendor/',include('vendor.urls')),
    # Menu
    path('menu/',include('menu.urls')),
    path('marketplace/',include('marketplace.urls')),
    # Cart
    path('cart/',marketplace_views.cart,name='cart'),
    # Home Search
    path('home_search/',views.home_search,name='home_search'),

    path('orders/', include('orders.urls')),

    #checkout
    path('checkout/',marketplace_views.checkout,name='checkout'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
