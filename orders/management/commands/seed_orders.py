import random
import uuid

from django.core.management.base import BaseCommand, CommandError
from django_seed import Seed

from accounts.models import User
from menu.models import FoodItem
from orders.models import Order, OrderedFood, Payment


class _OrderPair:
    """Order model lists `user` before `payment`; pair one Payment per Order row."""

    def __init__(self):
        self._payment = None
        self._pool = None

    def _ensure_pool(self, inserted_entities):
        if self._pool is None:
            pks = inserted_entities.get(Payment) or []
            self._pool = list(pks)
            random.shuffle(self._pool)

    def user(self, inserted_entities):
        self._ensure_pool(inserted_entities)
        if not self._pool:
            raise CommandError("No Payment rows to attach to Order.")
        self._payment = Payment.objects.get(pk=self._pool.pop())
        return self._payment.user

    def payment(self, inserted_entities):
        return self._payment


class _OrderedFoodRow:
    """Tie line items to one Order; keep fooditem/quantity/price/amount consistent."""

    def __init__(self, fooditems):
        self._fooditems = fooditems
        self._order = None
        self._fi = None
        self._qty = None

    def order(self, inserted_entities):
        pks = inserted_entities.get(Order) or []
        if not pks:
            raise CommandError("No Order rows for OrderedFood.")
        self._order = Order.objects.get(pk=random.choice(pks))
        return self._order

    def payment(self, inserted_entities):
        return self._order.payment

    def user(self, inserted_entities):
        return self._order.user

    def fooditem(self, inserted_entities):
        self._fi = random.choice(self._fooditems)
        return self._fi

    def quantity(self, inserted_entities):
        self._qty = random.randint(1, 3)
        return self._qty

    def price(self, inserted_entities):
        return float(self._fi.price)

    def amount(self, inserted_entities):
        return self._qty * float(self._fi.price)


class Command(BaseCommand):
    help = (
        "Seed Payment, Order, and OrderedFood using existing users and food items. "
        "Run seed_accounts and seed_menu first."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--orders",
            type=int,
            default=10,
            help="How many payments and orders to create (default 10).",
        )
        parser.add_argument(
            "--lines",
            type=int,
            default=20,
            help="How many OrderedFood rows to create (default 20).",
        )

    def handle(self, *args, **options):
        n_orders = options["orders"]
        n_lines = options["lines"]

        users = list(User.objects.all())
        fooditems = list(FoodItem.objects.all())
        if not users:
            raise CommandError("No users. Run `python manage.py seed_accounts` first.")
        if not fooditems:
            raise CommandError("No food items. Run `python manage.py seed_menu` first.")

        def pick_user(_inserted_entities):
            return random.choice(users)

        def transaction_id(_inserted_entities):
            return f"txn-{uuid.uuid4().hex[:20]}"

        def order_number(_inserted_entities):
            return f"ORD-{uuid.uuid4().hex[:12].upper()}"

        order_pair = _OrderPair()
        of_row = _OrderedFoodRow(fooditems)

        seeder = Seed.seeder()

        seeder.add_entity(
            Payment,
            n_orders,
            {
                "user": pick_user,
                "transaction_id": transaction_id,
                "payment_method": lambda _x: "Paymob",
                "amount": lambda _x: "100",
                "status": lambda _x: "Completed",
            },
        )
        seeder.add_entity(
            Order,
            n_orders,
            {
                "user": order_pair.user,
                "payment": order_pair.payment,
                "order_number": order_number,
                "payment_method": lambda _x: "Paymob",
                "total": lambda _x: 100.0,
                "total_tax": lambda _x: 0.0,
                "status": lambda _x: "New",
            },
        )
        seeder.add_entity(
            OrderedFood,
            n_lines,
            {
                "order": of_row.order,
                "payment": of_row.payment,
                "user": of_row.user,
                "fooditem": of_row.fooditem,
                "quantity": of_row.quantity,
                "price": of_row.price,
                "amount": of_row.amount,
            },
        )

        self.stdout.write(
            self.style.NOTICE(
                f"Seeding {n_orders} payment(s)/order(s) and {n_lines} ordered line(s)"
            )
        )
        inserted = seeder.execute()

        for model, pks in inserted.items():
            for pk in pks:
                self.stdout.write(
                    f"Model {model.__name__} generated record with primary key {pk}"
                )
