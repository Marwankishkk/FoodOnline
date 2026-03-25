import random

from django.core.management.base import BaseCommand, CommandError
from django_seed import Seed

from accounts.models import User
from marketplace.models import Cart, Tax
from menu.models import FoodItem


class Command(BaseCommand):
    help = (
        "Seed Tax rows and Cart rows using existing users and food items. "
        "Run seed_accounts and seed_menu first."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--taxes",
            type=int,
            default=3,
            help="How many Tax rows to create (default 3).",
        )
        parser.add_argument(
            "--carts",
            type=int,
            default=15,
            help="How many Cart rows to create (default 15).",
        )

    def handle(self, *args, **options):
        n_tax = options["taxes"]
        n_carts = options["carts"]

        users = list(User.objects.all())
        items = list(FoodItem.objects.all())
        if not users:
            raise CommandError("No users. Run `python manage.py seed_accounts` first.")
        if not items:
            raise CommandError("No food items. Run `python manage.py seed_menu` first.")

        def pick_user(_inserted_entities):
            return random.choice(users)

        def pick_fooditem(_inserted_entities):
            return random.choice(items)

        seeder = Seed.seeder()
        seeder.add_entity(Tax, n_tax)
        seeder.add_entity(
            Cart,
            n_carts,
            {
                "user": pick_user,
                "fooditem": pick_fooditem,
            },
        )

        self.stdout.write(
            self.style.NOTICE(
                f"Seeding {n_tax} tax(es) and {n_carts} cart line(s) "
                f"({len(users)} user(s), {len(items)} food item(s))"
            )
        )
        inserted = seeder.execute()

        for model, pks in inserted.items():
            for pk in pks:
                self.stdout.write(
                    f"Model {model.__name__} generated record with primary key {pk}"
                )
