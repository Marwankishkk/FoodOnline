from django.urls import path

from . import views

urlpatterns = [
    path('place-order/',views.place_order,name='place_order'),
    path('cancel-order/<int:order_id>/',views.cancel_order,name='cancel_order'),
    path('paymob-payment/',views.paymob_payment,name='paymob_payment'),
    path('fawaterk-payment/',views.fawaterk_payment,name='fawaterk_payment'),
    path('fawaterk/webhook/', views.fawaterk_webhook, name='fawaterk_webhook'),
    path('fawaterk-success/',views.fawaterk_success,name='fawaterk_success'),
    path('fawaterk-failed/',views.fawaterk_failed,name='fawaterk_failed'),
]