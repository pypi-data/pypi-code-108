import typing as ty

from django.contrib import admin
from django.contrib.admin.sites import site

from jnt_django_toolbox.admin.views.content_type_autocomplete import (
    ContentTypeAutocompleteView,
)


def get_model_admin(model) -> ty.Optional[admin.ModelAdmin]:
    return site._registry.get(model)


class BaseContentTypeAdmin(admin.ModelAdmin):
    """Base content type admin."""

    search_fields = ("model",)

    def has_add_permission(self, request):
        """Check has add permissions."""
        return False

    def has_change_permission(self, request, obj=None):
        """Check has change permissions."""
        return False

    def has_view_or_change_permission(self, request, obj=None):
        """Check has view or change permissions."""
        return False

    def has_view_permission(self, request, obj=None):
        """Check has view permissions."""
        return True

    def get_model_perms(self, request):
        """Return a dict of all perms for this model."""
        return {}

    def autocomplete_view(self, request):
        """Content type autocomplete view."""
        return ContentTypeAutocompleteView.as_view(model_admin=self)(request)

    def autocomplete_queryset(self, request, queryset):
        queryset = super().autocomplete_queryset(request, queryset)

        ids = []
        for content_type in queryset:
            model_class = content_type.model_class()

            if get_model_admin(model_class):
                ids.append(content_type.pk)

        return queryset.filter(id__in=ids)

    def autocomplete_item_data(self, instance, request):
        item_data = super().autocomplete_item_data(instance, request)

        model = instance.model_class()

        related_obj = None

        for related_object in model._meta.related_objects:
            model_admin = get_model_admin(related_object.related_model)
            if model_admin:
                related_obj = related_object
                break

        if not related_obj:
            return item_data

        item_data.update(
            {
                "app_label": related_obj.related_model._meta.app_label,
                "model": related_obj.related_model._meta.model_name,
                "field_name": related_obj.remote_field.name,
                "field_placeholder": model._meta.verbose_name.title(),
            }
        )

        return item_data
