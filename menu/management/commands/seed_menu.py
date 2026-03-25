import random
import uuid

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django_seed import Seed

from menu.models import Category, FoodItem
from vendor.models import Vendor

_MIN_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
)


class _FoodItemRow:
    """django-seed formats vendor before category; keep vendor for category picker."""

    def __init__(self, vendors):
        self._vendors = vendors
        self._vendor = None

    def vendor(self, _inserted_entities):
        self._vendor = random.choice(self._vendors)
        return self._vendor

    def category(self, inserted_entities):
        cat_pks = inserted_entities.get(Category) or []
        if cat_pks and self._vendor is not None:
            matching = [
                c
                for c in Category.objects.filter(pk__in=cat_pks)
                if c.vendor_id == self._vendor.id
            ]
            if matching:
                return random.choice(matching)
        qs = Category.objects.filter(vendor=self._vendor)
        if qs.exists():
            return random.choice(list(qs))
        qs = Category.objects.filter(vendor__in=self._vendors)
        if qs.exists():
            return random.choice(list(qs))
        raise CommandError(
            "No categories available for FoodItem; seed categories first or increase --categories."
        )


class Command(BaseCommand):
    help = (
        "Seed Category and FoodItem using existing vendors. "
        "Run `seed_vendors` first. Plain `seed menu` fails: Vendor lives in another app."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--categories",
            type=int,
            default=5,
            help="How many categories to create (default 5).",
        )
        parser.add_argument(
            "--items",
            type=int,
            default=10,
            help="How many food items to create (default 10).",
        )

    def handle(self, *args, **options):
        n_cat = options["categories"]
        n_items = options["items"]

        vendors = list(Vendor.objects.all())
        if not vendors:
            raise CommandError(
                "No vendors in the database. Run `python manage.py seed_vendors` first."
            )

        def pick_vendor(_inserted_entities):
            return random.choice(vendors)

        def food_image(_inserted_entities):
            return ContentFile(_MIN_PNG, name=f"food_{uuid.uuid4().hex}.png")

        row = _FoodItemRow(vendors)

        seeder = Seed.seeder()
        seeder.add_entity(Category, n_cat, {"vendor": pick_vendor})
        seeder.add_entity(
            FoodItem,
            n_items,
            {
                "vendor": row.vendor,
                "category": row.category,
                "image": food_image,
            },
        )

        self.stdout.write(
            self.style.NOTICE(
                f"Seeding {n_cat} categories and {n_items} food items "
                f"(using {len(vendors)} vendor(s))"
            )
        )
        inserted = seeder.execute()

        for model, pks in inserted.items():
            for pk in pks:
                self.stdout.write(
                    f"Model {model.__name__} generated record with primary key {pk}"
                )
