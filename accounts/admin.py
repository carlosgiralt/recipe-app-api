from django.contrib import admin

from .models import Token


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ("key", "user", "created")
    readonly_fields = ("key", "user", "created")
