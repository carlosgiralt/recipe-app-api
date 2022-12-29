import typing as t
from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractUser,
    UserManager as BaseUserManager,
)
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(
        self, email: str, password: t.Optional[str] = None, **extra_fields
    ) -> "User":
        """Creates and saves a new user."""

        if not email:
            raise ValueError("Users must have an email address.")

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(
        self, email: str, password: str, **extra_fields
    ) -> "User":
        """Creates and saves a new super user."""
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

    def normalize_email(self, email: str) -> str:
        """Normalize the email address by lowercasing it."""
        return email.strip().lower()


MAX_EMAIL_LENGTH = 255


class User(AbstractUser):
    """Custom user model that supports using email instead of username."""

    email = models.EmailField(
        _("email address"),
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
    )

    objects: UserManager = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ()

    @property
    def username(self) -> str:
        return self.email


class Ingredient(models.Model):
    """Ingredient to be used for a recipe"""

    name = models.CharField(_("name"), max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """Tag to be used for a recipe"""

    name = models.CharField(_("name"), max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="tags",
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Recipe object"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)

    ingredients = models.ManyToManyField("Ingredient")
    tags = models.ManyToManyField("Tag")

    def __str__(self) -> str:
        return self.title
