from django.contrib import admin

from jnt_django_toolbox.admin.mixins import (
    AutocompleteAdminMixin,
    ClickableLinksAdminMixin,
)


class BaseModelAdmin(
    ClickableLinksAdminMixin,
    AutocompleteAdminMixin,
    admin.ModelAdmin,
):
    """Base model admin."""
