from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    """
    Same behaviour as Django's default UserManager, except that a user
    created via `createsuperuser` (management command) is always given
    the SUPER_ADMIN role, since that command is how the very first
    admin account gets created.
    """

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', 'SUPER_ADMIN')
        return super().create_superuser(username, email, password, **extra_fields)
