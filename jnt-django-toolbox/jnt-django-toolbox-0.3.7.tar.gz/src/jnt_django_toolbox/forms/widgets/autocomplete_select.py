from unittest.mock import MagicMock

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS
from django.contrib.admin.widgets import (
    AutocompleteSelect as BaseAutocompleteSelect,
)
from django.contrib.admin.widgets import (
    AutocompleteSelectMultiple as BaseAutocompleteSelectMultiple,
)
from django.db import models
from django.utils.translation import get_language

from jnt_django_toolbox.admin.helpers.widgets import render_autocomplete_badge


class AdminAutocompleteError(Exception):
    def __init__(self, model):
        message = "Related objects for '{0}' not found. Can't create autocomplete widget.".format(
            model._meta.object_name,
        )
        super().__init__(message)


class AutocompleteMixin:
    """Autocomplete mixin."""

    def __init__(self, field, *args, **kwargs):
        """Init autocomplete mixin."""
        if isinstance(field, type) and issubclass(field, models.Model):
            related_objects = field._meta.related_objects
            if related_objects:
                field = related_objects[0].remote_field
            else:
                field = _fake_field(field)

        self._query_params = kwargs.pop("query_params", {})
        super().__init__(field, *args, **kwargs)

    @property
    def media(self):
        """Media."""
        extra = "" if settings.DEBUG else ".min"
        i18n_name = SELECT2_TRANSLATIONS.get(get_language())
        i18n_file = (
            ("admin/js/vendor/select2/i18n/{0}.js".format(i18n_name),)
            if i18n_name
            else ()
        )
        return forms.Media(
            js=(
                "admin/js/vendor/jquery/jquery{0}.js".format(extra),
                "admin/js/vendor/select2/select2.full{0}.js".format(extra),
            )
            + i18n_file
            + (
                "admin/js/jquery.init.js",
                "jnt_django_toolbox/js/widgets/autocomplete.js",
            ),
            css={
                "screen": (
                    "admin/css/vendor/select2/select2{0}.css".format(extra),
                    "admin/css/autocomplete.css",
                ),
            },
        )

    def build_attrs(self, base_attrs, extra_attrs=None):
        widget_attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        for attr, attr_value in self._query_params.items():
            widget_attrs["data-autocomplete--{0}".format(attr)] = attr_value
        return widget_attrs


class AutocompleteSelect(AutocompleteMixin, BaseAutocompleteSelect):
    """Autocomplete select widget."""


class AutocompleteSelectMultiple(
    AutocompleteMixin, BaseAutocompleteSelectMultiple
):
    """Autocomplete select multiple widget."""

    def optgroups(self, name, value, attr=None):
        """Return a list of optgroups for this widget."""
        original_label_from_instance = self.choices.field.label_from_instance

        self.choices.field.label_from_instance = render_autocomplete_badge

        option_groups = super().optgroups(name, value, attr=attr)

        self.choices.field.label_from_instance = original_label_from_instance

        return option_groups


def _fake_field(model: models.Model):
    """Fake field factory."""
    mock_field = MagicMock()
    mock_field.model = model
    mock_field.name = ""
    mock_field.remote_field.model = model
    mock_field.remote_field.field_name = "id"
    return mock_field
