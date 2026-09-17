from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create or update the initial production Teacher."


    def handle(self, *args, **options):
        User = get_user_model()

        username = settings.INITIAL_TEACHER_USERNAME.strip()
        email = settings.INITIAL_TEACHER_EMAIL.strip()
        first_name = settings.INITIAL_TEACHER_FIRST_NAME.strip()
        last_name = settings.INITIAL_TEACHER_LAST_NAME.strip()
        password = settings.INITIAL_TEACHER_PASSWORD

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "Initial Teacher credentials are not configured. "
                    "Skipping creation."
                )
            )
            return

        user = User.objects.filter(username=username).first()

        if user:
            user.role = User.Role.TEACHER
            user.is_staff = False
            user.is_superuser = False

            if email:
                user.email = email

            if first_name:
                user.first_name = first_name

            if last_name:
                user.last_name = last_name

            # Make sure the production PIN/password is correct.
            user.set_password(password)

            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"Teacher '{username}' already exists. "
                    "Account verified and password updated."
                )
            )

            return

        user = User.objects.create_user(
            username=username,
            email=email or "",
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        user.role = User.Role.TEACHER
        user.is_staff = False
        user.is_superuser = False
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Initial Teacher '{user.username}' "
                "created successfully."
            )
        )