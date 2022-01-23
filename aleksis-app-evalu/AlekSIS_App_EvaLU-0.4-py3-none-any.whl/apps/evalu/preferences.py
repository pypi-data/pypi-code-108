from django.utils.translation import gettext as _

from dynamic_preferences.preferences import Section
from dynamic_preferences.types import IntegerPreference, StringPreference

from aleksis.core.registries import site_preferences_registry

general = Section("evalu", verbose_name=_("EvaLU"))


@site_preferences_registry.register
class Place(StringPreference):
    """Place for legal consents."""

    section = general
    name = "place"
    default = ""
    verbose_name = _("Place (for legal consents)")


@site_preferences_registry.register
class MinimumNumberOfPersonsComparisonGroups(IntegerPreference):
    """Minimum number of persons needed for comparison groups."""

    section = general
    name = "number_of_persons_comparison_groups"
    default = 3
    verbose_name = _("Minimum number of persons needed for comparison groups")


@site_preferences_registry.register
class MinimumNumberOfResultsComparisonGroups(IntegerPreference):
    """Minimum number of results needed for comparison groups."""

    section = general
    name = "number_of_results_comparison_groups"
    default = 5
    verbose_name = _("Minimum number of results needed for comparison groups")


@site_preferences_registry.register
class MinimumNumberOfPersonsForResults(IntegerPreference):
    """Minimum number of persons needed for results."""

    section = general
    name = "number_of_persons_results"
    default = 5
    verbose_name = _("Minimum number of persons needed for results")
