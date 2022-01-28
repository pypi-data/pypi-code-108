"""Custom registries for some preference containers."""

from dynamic_preferences.registries import PerInstancePreferenceRegistry


class SitePreferenceRegistry(PerInstancePreferenceRegistry):
    """Registry for preferences valid for a site."""

    pass


class PersonPreferenceRegistry(PerInstancePreferenceRegistry):
    """Registry for preferences valid for a person."""

    pass


class GroupPreferenceRegistry(PerInstancePreferenceRegistry):
    """Registry for preferences valid for members of a group."""

    pass


site_preferences_registry = SitePreferenceRegistry()
person_preferences_registry = PersonPreferenceRegistry()
group_preferences_registry = GroupPreferenceRegistry()
