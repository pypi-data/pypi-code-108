from collections import OrderedDict

from material import Layout, Row


class PreferenceLayout(Layout):
    """django-material Layout object for managing preferences."""

    def __init__(self, form_base_class, section=None):
        """
        Create Layout object for the given form_base_class.

        :param form_base_class: A Form class used as the base. Must have a ``registry` attribute
        :param section: A section where the layout builder will load preferences
        """
        registry = form_base_class.registry
        if section:
            # Try to use section param
            preferences_obj = registry.preferences(section=section)
        else:
            # display all preferences in the form
            preferences_obj = registry.preferences()

        rows = OrderedDict()

        for preference in preferences_obj:
            row_name = preference.get("row", preference.identifier())
            rows.setdefault(row_name, [])
            rows[row_name].append(preference.identifier())

        rows_material = []
        for fields in rows.values():
            rows_material.append(Row(*fields))
        super().__init__(*rows_material)
