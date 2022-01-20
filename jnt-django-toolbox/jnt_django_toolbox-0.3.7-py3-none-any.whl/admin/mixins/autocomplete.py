from jnt_django_toolbox.admin.mixins import (
    AutocompleteChangelistFiltersAdminMixin,
    AutocompleteFieldsAdminMixin,
)


class AutocompleteAdminMixin(
    AutocompleteFieldsAdminMixin,
    AutocompleteChangelistFiltersAdminMixin,
):
    """Autocomplete model admin."""
