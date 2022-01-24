def test_all_settigns_registered():
    """Tests for regressions of preferences not being registered.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/592
    """

    from dynamic_preferences.types import BasePreferenceType

    from aleksis.core import preferences
    from aleksis.core.preferences import person_preferences_registry, site_preferences_registry

    for obj in preferences.__dict__.values():
        if not isinstance(obj, BasePreferenceType):
            continue

        in_site_reg = site_preferences_registry.get(obj.section.name, {}).get(obj.name, None) is obj
        in_person_reg = (
            person_preferences_registry.get(obj.section.name, {}).get(obj.name, None) is obj
        )

        assert in_site_reg != in_person_reg


def test_custom_managers_return_correct_qs():
    """Tests that custom managers' get_queryset methods return the expected qs.

    https://edugit.org/AlekSIS/official/AlekSIS-Core/-/issues/594
    """

    from aleksis.core import managers

    def _check_get_queryset(Manager, QuerySet):
        assert isinstance(Manager.from_queryset(QuerySet)().get_queryset(), QuerySet)

    _check_get_queryset(managers.GroupManager, managers.GroupQuerySet)
