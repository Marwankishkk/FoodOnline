from menu.models import FoodItem

from .models import Cart, Tax


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0
    return dict(cart_count=cart_count)

def get_cart_amounts(request):
    subtotal = 0
    tax_total = 0
    grand_total = 0
    tax_dict = {}
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        taxes = Tax.objects.filter(is_active=True)
        for item in cart_items:
            subtotal += item.quantity * item.fooditem.price
        for tax in taxes:
            tax_type = tax.tax_type
            tax_percentage = tax.tax_percentage
            tax_amount = round((subtotal * tax_percentage) / 100, 2)
            tax_dict[tax_type] = {str(tax_percentage): tax_amount}
            tax_total += tax_amount
            
        grand_total = subtotal + tax_total
    return dict(subtotal=subtotal, tax_dict=tax_dict, grand_total=grand_total,tax_total=tax_total)