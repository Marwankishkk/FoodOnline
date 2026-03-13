import requests
from decouple import config


class FawaterkClient:
    def __init__(self):
        self.api_key = config('FAWATERK_API_KEY')
        self.base_url = "https://staging.fawaterk.com/api/v2/invoiceInitPay"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    def create_fawaterk_invoice(self, total, billing_data: dict,cart_items: list):
        
        payload = {
            "payment_method_id": 2, 
            "cartTotal": str(total),
            "currency": "EGP",
            "customer": billing_data,
            "cartItems": cart_items,
            "redirectionUrls": {
            "successUrl": "https://apathetic-disorientedly-shanice.ngrok-free.dev/orders/fawaterk-success/",
            "failUrl": "https://apathetic-disorientedly-shanice.ngrok-free.dev/orders/fawaterk-failed/",
        },
            "returnUrl": "https://apathetic-disorientedly-shanice.ngrok-free.dev/",
            "callbackUrl": "https://apathetic-disorientedly-shanice.ngrok-free.dev/orders/fawaterk-webhook/"
        }
        response = requests.post(f"{self.base_url}", json=payload, headers=self.headers)
        return response.json()
