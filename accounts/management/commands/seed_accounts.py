from django.core.management.base import BaseCommand
from django_seed import Seed

from accounts.models import User, UserProfile


class Command(BaseCommand):
    help = (
        "Seed accounts.User with django-seed, then create one UserProfile per new user. "
        "Use this instead of `manage.py seed accounts`, which fails on the User↔UserProfile "
        "OneToOne (django-seed can exhaust user PKs across retries)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            type=int,
            default=10,
            help="How many User rows to create; one UserProfile is created per new user (default 10).",
        )

    def handle(self, *args, **options):
        number = options["number"]
        seeder = Seed.seeder()
        seeder.add_entity(User, number)

        self.stdout.write(self.style.NOTICE(f"Seeding {number} Users"))
        inserted = seeder.execute()

        user_pks = inserted.get(User, [])
        self.stdout.write(
            self.style.NOTICE(
                f"Ensuring UserProfile for {len(user_pks)} users "
                "(post_save usually creates these; get_or_create fills any gap)"
            )
        )

        for pk in user_pks:
            obj, created = UserProfile.objects.get_or_create(user_id=pk)
            if created:
                self.stdout.write(f"UserProfile pk={obj.pk} for user_id={pk} (created here)")
            else:
                self.stdout.write(f"UserProfile pk={obj.pk} for user_id={pk} (already present)")

        for pk in user_pks:
            self.stdout.write(f"Model User generated record with primary key {pk}")

