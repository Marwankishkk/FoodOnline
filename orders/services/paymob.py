import requests
from decouple import config


class PaymobClient:
    def __init__(self):
        self.api_key = config('PAYMOB_API_KEY')
        self.integration_id = config('PAYMOB_INTEGRATION_ID')
        self.iframe_id = config('PAYMOB_IFRAME_ID')
        self.base_url = "https://accept.paymob.com/api"

    def _auth_token(self):
        resp = requests.post(f"{self.base_url}/auth/tokens", json={"api_key": self.api_key})
        resp.raise_for_status()
        return resp.json()["token"]

    def create_order_and_payment_key(self, *, merchant_order_id: str, amount_cents: int, billing_data: dict ) -> dict:
        token = self._auth_token()
        print(token)
        # 1) Create Paymob order
        order_resp = requests.post(
            f"{self.base_url}/ecommerce/orders",
            json={
                "auth_token": token,
                "delivery_needed": False,
                "amount_cents": amount_cents,
                "currency": "EGP",
                "merchant_order_id": merchant_order_id,
                "items":[],
            },
        )
        order_resp.raise_for_status()
        order_data = order_resp.json()
        paymob_order_id = order_data["id"]
        # 2) Create payment key
        payment_key_resp = requests.post(
            f"{self.base_url}/acceptance/payment_keys",
            json={
                "auth_token": token,
                "amount_cents": amount_cents,
                "expiration": 3600,
                "order_id": paymob_order_id,
                "billing_data": billing_data,
                "currency": "EGP",
                "integration_id": self.integration_id,
            },
        )
        print(payment_key_resp.json())
        payment_key_resp.raise_for_status()
        payment_key = payment_key_resp.json()["token"]
        # 3) Generate iframe URL
        iframe_url = f"https://accept.paymob.com/api/acceptance/iframes/{self.iframe_id}?payment_token={payment_key}"
        
        return {
            "paymob_order_id": paymob_order_id,
            "payment_key": payment_key,
            "iframe_url": iframe_url,
        }

    