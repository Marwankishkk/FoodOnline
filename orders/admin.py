from django.contrib import admin

from .models import Order, OrderedFood, Payment
class AdminPayment(admin.ModelAdmin):
    list_display = ('user', 'transaction_id', 'payment_method', 'amount', 'status', 'created_at')
class AdminOrder(admin.ModelAdmin):
    list_display = ('user', 'order_number', 'first_name', 'last_name', 'phone', 'email', 'address', 'country', 'state', 'city', 'pin_code', 'total', 'tax_data', 'total_tax', 'payment_method', 'status', 'is_ordered', 'created_at', 'updated_at')
class AdminOrderedFood(admin.ModelAdmin):
    list_display = ('order', 'user', 'fooditem', 'quantity', 'price', 'amount', 'created_at', 'updated_at')
admin.site.register(Payment, AdminPayment)
admin.site.register(Order, AdminOrder)
admin.site.register(OrderedFood, AdminOrderedFood)
