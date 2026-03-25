# Manual testing steps

## Environment

1. Activate the virtual environment (if you use one).
2. From the project root, run `python manage.py migrate`.
3. Optional: load demo data in this order:
   - `python manage.py seed_accounts --number=15`
   - `python manage.py seed_vendors --number=5`
   - `python manage.py seed_menu --categories=5 --items=10`
   - `python manage.py seed_marketplace --taxes=3 --carts=15`
   - `python manage.py seed_orders --orders=10 --lines=20`

Seeded users have unknown passwords. For a known login, either run `python manage.py createsuperuser` or set a password in the shell with `User.objects.get(email="...").set_password("...")` and save.

## Run the server

```bash
python manage.py runserver
```

Use `http://127.0.0.1:8000/` unless you bind another host or port.

## Smoke checks

1. Open the home page. Confirm it loads without a 500 error.
2. Open `/admin/`, log in with a superuser, and confirm models list data when seeds were applied.
3. Register a new account or log in with a user whose password you set.
4. Browse vendors or menu pages (URLs depend on your `urls.py` and templates).
5. Add items to the cart, open the cart, and proceed to checkout.
6. Place an order using a payment method you can complete in your environment.

## Payment integrations

-  Fawaterk need valid API key and configuration in `.env`. If keys are missing or wrong, checkout or AJAX payment endpoints may return 400 or error JSON.
- Fawaterk callback and redirect URLs in `orders/services/fawaterk.py` must match your public base URL (for example ngrok in development). Update them when your tunnel URL changes.


