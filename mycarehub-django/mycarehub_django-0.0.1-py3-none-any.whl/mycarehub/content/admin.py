from django.contrib import admin

from mycarehub.common.admin import BaseAdmin

from .models import Author


@admin.register(Author)
class AuthorAdmin(BaseAdmin):
    pass
