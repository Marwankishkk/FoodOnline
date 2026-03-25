import uuid

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django_seed import Seed

from accounts.models import User
from vendor.models import Vendor

# 1×1 transparent PNG (valid image for ImageField)
_MIN_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
)


class Command(BaseCommand):
    help = (
        "Create vendor users and Vendor rows in one django-seed run. "
        "`manage.py seed vendor` alone cannot create User rows (wrong app), "
        "so Vendor.user stays empty and seeding fails."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            type=int,
            default=5,
            help="How many vendors to create (default 5).",
        )

    def handle(self, *args, **options):
        number = options["number"]
        seeder = Seed.seeder()

        def dummy_license(_inserted_entities):
            return ContentFile(_MIN_PNG, name=f"license_{uuid.uuid4().hex}.png")

        seeder.add_entity(
            User,
            number,
            {
                "role": lambda _x: User.VENDOR,
                "is_active": lambda _x: True,
            },
        )
        seeder.add_entity(
            Vendor,
            number,
            {
                "vendor_license": dummy_license,
            },
        )

        self.stdout.write(
            self.style.NOTICE(
                f"Seeding {number} vendor Users and {number} Vendors (User first, then Vendor)"
            )
        )
        inserted = seeder.execute()

        for model, pks in inserted.items():
            for pk in pks:
                self.stdout.write(
                    f"Model {model.__name__} generated record with primary key {pk}"
                )
