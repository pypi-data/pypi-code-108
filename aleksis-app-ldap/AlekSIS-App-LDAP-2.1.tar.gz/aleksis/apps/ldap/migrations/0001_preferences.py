from django.db import migrations

from aleksis.apps.ldap.util.ldap_sync import setting_name_from_field
from aleksis.core.models import Person

_preference_suffixes = ["", "_re", "_replace"]


def _setting_name_old(model, field):
    part_1 = model._meta.label_lower.replace(".", "_").replace("__", "_")
    return f"additional_field_{part_1}_{field.name}".replace("__", "_")


def _migrate_preferences(apps, schema_editor):
    SitePreferenceModel = apps.get_model("core", "SitePreferenceModel")

    for field in Person.syncable_fields():
        old_setting_name = _setting_name_old(Person, field)
        setting_name = setting_name_from_field(Person, field)
        for suffix in _preference_suffixes:
            old_pref_name = old_setting_name + suffix
            new_pref_name = setting_name + suffix
            SitePreferenceModel.objects.filter(section="ldap", name=old_pref_name).update(name=new_pref_name)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0001_initial"),
        ("sites", "0002_alter_domain_unique"),
    ]

    operations = [migrations.RunPython(_migrate_preferences)]
