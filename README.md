# Food Online

A Django web application for browsing restaurants, managing menus, shopping carts, and placing food orders. It supports customer and vendor flows, an admin site, and payment integrations (Fawaterk and Paymob-related configuration).


## What you need installed

- **Python** 3.12 or newer (match what your team uses; Django 6.x requires a supported Python version).
- **PostgreSQL** running locally (or reachable on your network). The project is configured to use PostgreSQL, not SQLite.
- **Git** to clone the repository.

Optional but common:

- A **virtual environment** for Python dependencies (recommended so project packages do not clash with system Python).

## Get the code and dependencies

1. Clone the repository and open the project folder in your terminal.

2. Create and activate a virtual environment (example for Unix-like systems):

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   On Windows, activation is usually `.venv\Scripts\activate`.

3. Install Python packages:

   ```bash
   pip install -r requirements.txt
   ```

## Environment variables (`.env`)

Configuration is loaded with `python-decouple` from a `.env` file in the **project root** (same folder as `manage.py`). **Do not commit real API keys or passwords to Git.** Keep `.env` local or use your team’s secret manager in production.

Create a `.env` file and set at least:

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Django secret key. Generate a new one for any shared or production deployment. |
| `DEBUG` | `True` for local development; must be `False` in production with care. |
| `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT` | PostgreSQL database connection. |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` | Outgoing email (for example password reset). |
| `PAYMOB_API_KEY`, `PAYMOB_INTEGRATION_ID`, `PAYMOB_IFRAME_ID` | Paymob-related integration (see `orders/services/paymob.py`). |
| `FAWATERK_API_KEY` | Fawaterk API key. |
| `FAWATERK_BASE_URL` | Public base URL for payment callbacks (in development this is often an **ngrok** URL so the payment provider can reach your machine). |

`foodOnline/settings.py` also references `CSRF_TRUSTED_ORIGINS` and payment URLs; when you use a new tunnel domain, update those settings to match your environment.

## Database setup

1. Create an empty PostgreSQL database and a user with access to it (names should match what you put in `.env`).

2. From the project root, apply migrations:

   ```bash
   python manage.py migrate
   ```

3. Create an admin user if you want to use `/admin/`:

   ```bash
   python manage.py createsuperuser
   ```

## Optional demo data

The project includes management commands to seed the database for testing. Run them **after** migrations, in order:

```bash
python manage.py seed_accounts --number=15
python manage.py seed_vendors --number=5
python manage.py seed_menu --categories=5 --items=10
python manage.py seed_marketplace --taxes=3 --carts=15
python manage.py seed_orders --orders=10 --lines=20
```

Seeded users do not have known passwords. For a login you control, use `createsuperuser` or set a password in the Django shell. More detail is in `docs/testing/steps.md`.

## Run the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser. The admin site is at `http://127.0.0.1:8000/admin/`.

## URL reference (all routes)

Base URL in development is usually `http://127.0.0.1:8000/`. All paths below are **relative to that origin** (no domain).

**How routing works here:** The main list lives in `foodOnline/urls.py`. Django walks patterns **from top to bottom** and uses the **first match**. The home page is registered as `path('', views.home)` before the accounts include, so `/` is the **home** view, not `myAccount` (accounts also defines an empty path; that route does not win for `/`).

**Source files:** `foodOnline/urls.py` (project), then each app’s `urls.py` as noted in each section.

---

### 1. Project shell (`foodOnline/urls.py`)

These routes are declared directly on the project URLconf.

| Path | URL name | Purpose |
|------|----------|---------|
| `/` | `home` | Home page |
| `/admin/` | (Django admin) | Admin site |
| `/cart/` | `cart` | Shopping cart (same view as marketplace cart) |
| `/checkout/` | `checkout` | Checkout |
| `/home_search/` | `home_search` | Home search |

The project also mounts the **`accounts`**, **`vendor`**, **`menu`**, **`marketplace`**, and **`orders`** includes (see below). User-uploaded files are served under **`/media/`** when `DEBUG` is on (see `foodOnline/urls.py` and `settings.MEDIA_URL`).

---

### 2. Accounts (`accounts/urls.py`)

Included with prefix `` (empty), so these paths are **at the site root**.

| Path | URL name | Purpose |
|------|----------|---------|
| `/registerUser/` | `registerUser` | Register as a customer user |
| `/registerVendor/` | `registerVendor` | Register as a vendor |
| `/login/` | `login` | Login |
| `/logout/` | `logout` | Logout |
| `/customerDashboard/` | `customerDashboard` | Customer dashboard |
| `/vendorDashboard/` | `vendorDashboard` | Vendor dashboard |
| `/myAccount/` | `myAccount` | My account |
| `/activate/<uidb64>/<token>/` | `activate` | Email activation link |
| `/forgot_password/` | `forgot_password` | Forgot password |
| `/reset_password_validate/<uidb64>/<token>/` | `reset_password_validate` | Validate reset token |
| `/reset_password/` | `reset_password` | Set new password |

**Note:** `accounts/urls.py` also defines `path('', views.myAccount, name='myAccount')`. Because `foodOnline/urls.py` registers `home` on `/` first, **`/` is not `myAccount`**.

---

### 3. Vendor area (`vendor/urls.py`)

Included **twice** in the project (under `foodOnline/urls.py` as `vendor/` and under `accounts/urls.py` as `vendor/`). The full path prefix is **`/vendor/`** in both cases.

| Path | URL name | Purpose |
|------|----------|---------|
| `/vendor/` | `vendorDashboard` | Vendor dashboard entry |
| `/vendor/profile/ ` | `vprofile` | Vendor profile (the path string in code ends with a space after `profile/`; see `vendor/urls.py`) |
| `/vendor/menu-builder/` | `menu_builder` | Menu builder |
| `/vendor/menu-builder/category/<int:pk>/` | `fooditems_by_category` | Food items for a category |
| `/vendor/menu-builder/add-category/` | `add_category` | Add category |
| `/vendor/menu-builder/edit-category/<int:pk>/` | `edit_category` | Edit category |
| `/vendor/menu-builder/delete-category/<int:pk>/` | `delete_category` | Delete category |
| `/vendor/menu-builder/fooditems/add/` | `add_food` | Add food item |
| `/vendor/menu-builder/fooditems/edit/<int:pk>/` | `edit_food` | Edit food item |
| `/vendor/menu-builder/fooditems/delete/<int:pk>/` | `delete_food` | Delete food item |
| `/vendor/opening-hours/` | `opening_hours` | Opening hours list |
| `/vendor/opening-hours/add/` | `add_opening_hour` | Add opening hour |
| `/vendor/opening-hours/remove/<int:pk>/` | `remove_opening_hour` | Remove opening hour |
| `/vendor/my_orders/` | `vendor_my_orders` | Vendor order list |
| `/vendor/order_detail/<int:order_number>/` | `vendor_order_detail` | Vendor order detail |

---

### 4. Customer area (`customers/urls.py`)

Included from `accounts/urls.py` under `customer/`. Prefix: **`/customer/`**.

| Path | URL name | Purpose |
|------|----------|---------|
| `/customer/profile/` | `cprofile` | Customer profile |
| `/customer/my_orders/` | `my_orders` | Customer order list |
| `/customer/order_detail/<int:order_number>/` | `order_detail` | Customer order detail |

---

### 5. Marketplace (`marketplace/urls.py`)

Included under `marketplace/`. Prefix: **`/marketplace/`**.

| Path | URL name | Purpose |
|------|----------|---------|
| `/marketplace/` | `marketplace` | Marketplace listing |
| `/marketplace/<slug:vendor_slug>/` | `vendor_detail` | Single vendor (restaurant) page |
| `/marketplace/cart/` | `cart` | Cart under marketplace URL namespace |
| `/marketplace/add_to_cart/<int:food_id>/` | `add_to_cart` | Add line to cart |
| `/marketplace/decrease_cart/<int:food_id>/` | `decrease_cart` | Decrease quantity |
| `/marketplace/delete_cart/<int:cart_id>/` | `delete_cart` | Remove cart row |

**Ordering note:** In `marketplace/urls.py`, the slug route is registered before `cart/`. A segment like `cart` could be interpreted as `vendor_slug` depending on the request path. For behavior details, read the view code and test in the browser.

---

### 6. Orders and payments (`orders/urls.py`)

Included under `orders/`. Prefix: **`/orders/`**.

| Path | URL name | Purpose |
|------|----------|---------|
| `/orders/place-order/` | `place_order` | Place order |
| `/orders/cancel-order/<int:order_id>/` | `cancel_order` | Cancel order |
| `/orders/paymob-payment/` | `paymob_payment` | Paymob payment flow |
| `/orders/fawaterk-payment/` | `fawaterk_payment` | Fawaterk payment flow |
| `/orders/fawaterk/webhook/` | `fawaterk_webhook` | Fawaterk webhook (server-to-server) |
| `/orders/fawaterk-success/` | `fawaterk_success` | Fawaterk success redirect |
| `/orders/fawaterk-failed/` | `fawaterk_failed` | Fawaterk failure redirect |

---

### 7. Menu app (`menu/urls.py`)

Included under `menu/` (`/menu/`). The file currently has **no** `path(...)` entries, so **no app routes** are defined there yet.

---

### Quick lookup by prefix

| Prefix | App / module |
|--------|----------------|
| `/` | Home, then accounts routes at root (see sections 1–2) |
| `/admin/` | Django admin |
| `/vendor/` | Vendor dashboards and tools |
| `/customer/` | Customer profile and orders |
| `/marketplace/` | Browse vendors, cart actions under this prefix |
| `/cart/` | Cart (root-level alias) |
| `/checkout/` | Checkout |
| `/orders/` | Orders and payment endpoints |
| `/menu/` | Reserved; no routes in `menu/urls.py` yet |
| `/media/` | User media (development-style serving via `static()`) |

