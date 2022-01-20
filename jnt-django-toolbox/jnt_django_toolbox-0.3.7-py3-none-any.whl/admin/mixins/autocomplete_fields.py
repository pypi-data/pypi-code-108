from itertools import chain

from django.contrib.admin.checks import BaseModelAdminChecks
from django.contrib.admin.utils import flatten_fieldsets
from django.db.models import ForeignKey, ManyToManyField

from jnt_django_toolbox.admin.helpers.widgets import render_autocomplete_badge
from jnt_django_toolbox.forms.widgets import autocomplete_select


class AutocompleteWidgetsUpdateAdminMixin:
    """Update autocomplete widgets for models."""

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Get a form Field for a ForeignKey.

        Override only autocomplete widget.
        """
        if "widget" not in kwargs:
            if db_field.name in self.get_autocomplete_fields(request):
                kwargs["widget"] = autocomplete_select.AutocompleteSelect(
                    db_field,
                    self.admin_site,
                    using=kwargs.get("using"),
                )

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Get a form Field for a ManyToManyField.

        Override only autocomplete widget.
        """
        if not db_field.remote_field.through._meta.auto_created:
            return None

        if "widget" not in kwargs:
            autocomplete_fields = self.get_autocomplete_fields(request)
            if db_field.name in autocomplete_fields:
                kwargs[
                    "widget"
                ] = autocomplete_select.AutocompleteSelectMultiple(
                    db_field,
                    self.admin_site,
                    using=kwargs.get("using"),
                )

        return super().formfield_for_manytomany(db_field, request, **kwargs)


class AutocompleteFieldsAdminMixin(AutocompleteWidgetsUpdateAdminMixin):
    def get_autocomplete_fields(self, request):
        autocomplete_fields = super().get_autocomplete_fields(request)

        if autocomplete_fields:
            return autocomplete_fields

        admin_fields = self._get_admin_fields(request)
        relation_fields = self._get_relation_fields()

        if not admin_fields:
            return tuple(relation_fields)

        return tuple(set(admin_fields) & set(relation_fields))

    def autocomplete_queryset(self, request, queryset):
        if not queryset.ordered:
            queryset = queryset.order_by(*self.get_ordering(request))

        return queryset

    def autocomplete_item_data(self, instance, request):
        """Get present for autocomplete item."""
        return {
            "id": instance.pk
            if isinstance(instance.pk, int)
            else str(instance.pk),
            "text": str(instance),
            "__badge__": render_autocomplete_badge(instance),
        }

    def _get_relation_fields(self):
        return (
            field.name
            for field in self.model._meta.get_fields()
            if self._is_relation_field(field)
        )

    def _get_admin_fields(self, request):
        if self.fields:
            return self.get_fields(request)
        elif self.fieldsets:
            return flatten_fieldsets(self.get_fieldsets(request))

    def _is_relation_field(self, field):
        return isinstance(field, (ForeignKey, ManyToManyField)) and bool(
            self.admin_site._registry.get(field.remote_field.model)
        )

    def check(self, **kwargs):
        return [
            *super().check(**kwargs),
            *self._check_autocomplete_mixin(),
        ]

    def _check_autocomplete_mixin(self):
        if "autocomplete_fields" in self.__class__.__dict__.keys():
            return []

        check_autocomplete_fields_item = (
            BaseModelAdminChecks()._check_autocomplete_fields_item
        )

        return list(
            chain.from_iterable(
                [
                    check_autocomplete_fields_item(
                        self,
                        field_name,
                        "autocomplete_fields[{0}]".format(index),
                    )
                    for index, field_name in enumerate(
                        self.get_autocomplete_fields(None)
                    )
                ]
            )
        )
