from django.contrib import admin
from .models import Cart, Tax
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
# Register your models here.

class AdminCart(admin.ModelAdmin):
    list_display = ('user', 'fooditem', 'quantity', 'created_at', 'updated_at')
    
admin.site.register(Cart, AdminCart)

class AdminTax(admin.ModelAdmin):
    list_display = ('tax_type', 'tax_percentage', 'is_active')
admin.site.register(Tax, AdminTax)