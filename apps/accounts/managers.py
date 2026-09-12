import uuid

from django.contrib.auth.models import UserManager as DjangoUserManager


class UserManager(DjangoUserManager):
    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email):
        return super().normalize_email(email).strip().lower()

    def _create_user(self, username, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        return super()._create_user(username or str(uuid.uuid4()), email, password, **extra_fields)

    def create_user(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, email, password=None, username=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")
        return self._create_user(username, email, password, **extra_fields)
