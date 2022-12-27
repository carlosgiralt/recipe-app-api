from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework.authtoken.models import Token as BaseToken


class Token(BaseToken):
    """Token model that extends from `rest_framework.Token` model.
    Set the `user` field to allow multiple tokens per user.
    """

    key = models.CharField(
        _("Key"),
        max_length=40,
        db_index=True,
        unique=True,
    )
    user = models.ForeignKey(
        get_user_model(),
        related_name="auth_tokens",
        on_delete=models.CASCADE,
        verbose_name=_("User"),
    )
