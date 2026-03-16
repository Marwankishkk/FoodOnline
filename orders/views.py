import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from accounts.models import User
from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart, Tax
from menu.models import FoodItem
from orders.services.fawaterk import FawaterkClient
from orders.services.paymob import PaymobClient


from .forms import OrderForm
from .models import Order, Payment, OrderedFood
from .utils import generate_order_number
from accounts.utils import send_notification


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    get_tax=Tax.objects.filter(is_active=True)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace') 
    subtotal = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax_total']
    grand_total = get_cart_amounts(request)['grand_total']
    vendors_ids = []
    for i in cart_items:
        if i.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(i.fooditem.vendor.id)
    
    total_data = {}
    tax_dict = {}
    k = {}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendors_ids)
        v_id = fooditem.vendor.id
        if v_id in k:
            subtotal = k[v_id]
            subtotal += (fooditem.price * i.quantity)
            k[v_id] = subtotal
        else:
            subtotal = (fooditem.price * i.quantity)
            k[v_id] = subtotal
        for tax in get_tax:
            tax_type = tax.tax_type
            tax_percentage = tax.tax_percentage
            tax_amount = round((tax_percentage * subtotal)/100, 2)
            tax_dict.update({tax_type: {str(tax_percentage) : str(tax_amount)}})
        if i.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(i.fooditem.vendor.id)  
        fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendors_ids)
        total_data.update({fooditem.vendor.id: {str(subtotal): str(tax_dict)}})

    
    
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
           
            existing_order = (
                Order.objects.filter(
                    user=request.user,
                    is_ordered=False,
                    status='New',
                    
                )
                .order_by('-created_at')
                .first()
            )
            if existing_order:
                
                if existing_order.payment_method != request.POST['payment_method']:
                    existing_order.payment_method = request.POST['payment_method']
                    existing_order.save()
                    messages.success(request, 'Finish unpaid order')
                existing_order.first_name = form.cleaned_data['first_name']
                existing_order.last_name = form.cleaned_data['last_name']
                existing_order.phone = form.cleaned_data['phone']
                existing_order.email = form.cleaned_data['email']
                existing_order.address = form.cleaned_data['address']
                existing_order.country = form.cleaned_data['country']
                existing_order.state = form.cleaned_data['state']
                existing_order.city = form.cleaned_data['city']
                existing_order.user = request.user
                existing_order.total = grand_total
                existing_order.total_data = json.dumps(total_data)
                existing_order.tax_data = json.dumps(tax_dict, cls=DecimalEncoder)
                existing_order.total_tax = total_tax
                existing_order.payment_method = request.POST['payment_method']
                existing_order.save()
                existing_order.order_number = generate_order_number(existing_order.id)
                existing_order.vendors.add(*vendors_ids)
                existing_order.save()
                payment = Payment()
                payment.user = request.user
                payment.payment_method = request.POST['payment_method']
                payment.amount = grand_total
                payment.status = 'Pending'
                payment.save()
                existing_order.payment = payment
                existing_order.save()
                order = existing_order
            
            else:
                order = Order()
                order.first_name = form.cleaned_data['first_name']
                order.last_name = form.cleaned_data['last_name']
                order.phone = form.cleaned_data['phone']
                order.email = form.cleaned_data['email']
                order.address = form.cleaned_data['address']
                order.country = form.cleaned_data['country']
                order.state = form.cleaned_data['state']
                order.city = form.cleaned_data['city']
                order.user = request.user
                order.total = grand_total
                order.tax_data = json.dumps(tax_dict, cls=DecimalEncoder)
                order.total_data = json.dumps(total_data)
                order.total_tax = total_tax
                order.payment_method = request.POST['payment_method']
                order.save()
                order.order_number = generate_order_number(order.id)
                order.vendors.add(*vendors_ids)
                order.save()
                payment = Payment()
                payment.user = request.user
                payment.transaction_id = order.order_number
                payment.payment_method = request.POST['payment_method']
                payment.amount = grand_total
                payment.status = 'Pending'
                payment.save()
                order.payment = payment
                order.save()

           
            
           
            context = {
                'order': order,
                'cart_items': cart_items,
            }
            return render(request, 'orders/place_order.html', context)

        else:
            print(form.errors)
    return render(request, 'orders/place_order.html')

def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = 'Cancelled'
    order.save()
    return redirect('marketplace')

def paymob_payment(request):
    paymob_order = PaymobClient()
    items=[]
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    try:
        order = Order.objects.exclude(status='Cancelled').get(user=request.user, is_ordered=False)        
    except Order.DoesNotExist:
        return redirect('marketplace')
    grand_total = get_cart_amounts(request)['grand_total']
    for item in cart_items:
        items.append({
            'name': item.fooditem.food_title,
            'description': item.fooditem.description,
            'quantity': item.quantity,
            'price_amount_cents': int(item.fooditem.price * 100),
        })
    token=paymob_order.create_order_and_payment_key(
        merchant_order_id=order.order_number,
        amount_cents=int(grand_total * 100),
        billing_data={
            'first_name': order.first_name,
            'last_name': order.last_name,
            'email': order.email,
            'street': order.address,
            'city': order.city,
            'building': 2,
            'floor': 1,
            'apartment': 1,
            'country': order.country,
            'email': order.email,
            'phone_number': order.phone,
        },

        
    )
    return HttpResponse(token['iframe_url'])

def fawaterk_payment(request):
    fawaterk_order = FawaterkClient()
    items = []
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    try:
        order = Order.objects.exclude(status='Cancelled').get(user=request.user, is_ordered=False)        
    except Order.DoesNotExist:
        return redirect('marketplace')
    amounts = get_cart_amounts(request)
    tax_total = Decimal(str(amounts['tax_total']))
    items_total = Decimal('0')
    for item in cart_items:
        price = round(Decimal(str(item.fooditem.price)), 2)
        qty = item.quantity
        items.append({
            'name': item.fooditem.food_title,
            'price': float(price),
            'quantity': qty,
        })
        items_total += price * qty
    if tax_total > 0:
        items.append({
            'name': 'Tax',
            'price': float(round(tax_total, 2)),
            'quantity': 1,
        })
        items_total += tax_total
    cart_total = round(items_total, 2)
    billing_data={
        'first_name': order.first_name,
        'last_name': order.last_name,
        'email': order.email,
        'phone': order.phone,
        'address': order.address,
        
    }
    payload = fawaterk_order.create_fawaterk_invoice(
        total=cart_total,
        billing_data=billing_data,
        cart_items=items,
    )
    if payload.get('status') == 'success':
        invoice_id = payload.get('data', {}).get('id') or payload.get('data', {}).get('invoice_id')
        if invoice_id is not None:
            order.payment.transaction_id = str(invoice_id)
            order.payment.save()
        return JsonResponse({
            'status': 'success',
            'redirect_url': payload['data']['payment_data']['redirectTo']
        })
    else:
        return JsonResponse({
            'status': 'error',
            'message': payload.get('message')
        }, status=400)


@login_required(login_url='login')
def fawaterk_success(request):   
    order = Order.objects.get(user=request.user, is_ordered=False)
    order.status = 'Accepted'
    order.is_ordered = True
    order.save()
    payment = Payment.objects.get(order=order)
    payment.status = 'Completed'
    payment.save()
    cart_items = Cart.objects.filter(user=request.user)
    ordered_food = OrderedFood.objects.filter(user=request.user, order=order)
    for item in cart_items:
        ordered_food = OrderedFood.objects.create(user=request.user, order=order, fooditem=item.fooditem,
        quantity=item.quantity, price=item.fooditem.price, amount=item.fooditem.price * item.quantity, payment=payment)
        ordered_food.save()
        item.delete()                        
    context = {
        'user': request.user,
        'order': order,
        'cart_items': cart_items,
    }
    send_notification(
        'Order Confirmed',
        'orders/emails/order_confirmed.html',
        context)

    for vendor in order.vendors.all():
        order_items = OrderedFood.objects.filter(order=order, fooditem__vendor=vendor)
        vendor_total = sum(item.amount for item in order_items)
        vendor_context = {
            'user': vendor.user,
            'order': order,
            'order_items': order_items,
            'vendor_total': vendor_total,
        }
        send_notification(
            'New order received #' + order.order_number,
            'orders/emails/order_received_vendor.html',
            vendor_context,
        )
    context = {'order': order}
    return render(request, 'orders/fawaterk_success.html', context)
@login_required(login_url='login')
def fawaterk_failed(request):
    return render(request, 'orders/fawaterk_failed.html')
