"""
models.py — Custom user model for the banking simulator.

Why it exists:
    Django's default User model uses `username` as the primary identifier.
    Banking systems typically identify users by email. Swapping to a custom
    model NOW (before any migrations) means we never have to do a painful
    migration later. Django's docs explicitly recommend this approach.

What it does:
    - Defines CustomUser, which extends AbstractBaseUser + PermissionsMixin.
    - Uses email as the unique login credential (no username field).
    - Stores first_name and last_name for display on the dashboard.
    - Provides CustomUserManager with create_user() and create_superuser()
      helpers that Django's admin and auth system require.

How it connects:
    - settings.py declares AUTH_USER_MODEL = "accounts.CustomUser" so
      Django substitutes this model everywhere the auth system is used.
    - Future models (BankAccount, Transfer, Transaction) will use
      ForeignKey(settings.AUTH_USER_MODEL) to link back to this model —
      never ForeignKey(User) directly, which is the Django best practice.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Manager that replaces Django's default UserManager.

    Required because we removed `username` and use `email` instead.
    Django's built-in manager references `username`, so we must override.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with the given email and password."""
        if not email:
            raise ValueError("An email address is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)   # hashes the password — never stored plain
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser (for Django admin access)."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    The application's primary user model.

    Fields:
        email       — unique login credential; replaces `username`
        first_name  — displayed on the dashboard and future account pages
        last_name   — displayed on the dashboard and future account pages
        is_active   — soft-delete flag; False = account disabled, not deleted
        is_staff    — grants access to the Django admin interface
        date_joined — timestamp recorded at registration
    """

    email = models.EmailField(unique=True, verbose_name="Email address")
    first_name = models.CharField(max_length=150, verbose_name="First name")
    last_name = models.CharField(max_length=150, verbose_name="Last name")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    # Tell Django which field is the login credential
    USERNAME_FIELD = "email"

    # Fields prompted when running `createsuperuser` (beyond USERNAME_FIELD)
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def get_full_name(self):
        """Return 'First Last', used throughout templates and admin."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return just the first name, used in greeting messages."""
        return self.first_name

    def __str__(self):
        return self.email
