from django.utils.translation import gettext_lazy as _

from dynamic_preferences.preferences import Section
from dynamic_preferences.types import BooleanPreference, ChoicePreference, StringPreference

from aleksis.core.registries import site_preferences_registry

ldap = Section("ldap", verbose_name=_("LDAP"))


@site_preferences_registry.register
class EnableLDAPSync(BooleanPreference):
    section = ldap
    name = "enable_sync"
    default = False
    required = False
    verbose_name = _("Enable LDAP sync")


@site_preferences_registry.register
class LDAPSyncCreateMissingPersons(BooleanPreference):
    section = ldap
    name = "create_missing_persons"
    default = True
    required = False
    verbose_name = _("Create missing persons for LDAP users")


@site_preferences_registry.register
class LDAPPersonSyncOnLogin(BooleanPreference):
    section = ldap
    name = "person_sync_on_login"
    default = True
    required = False
    verbose_name = _("Sync LDAP user with person on login")


@site_preferences_registry.register
class LDAPUserCreateOnRegister(BooleanPreference):
    section = ldap
    name = "user_create_on_register"
    default = True
    required = False
    verbose_name = _("Create LDAP user on registration")


@site_preferences_registry.register
class LDAPUserCreateRDNFields(StringPreference):
    section = ldap
    name = "user_create_rdn_fields"
    default = "uid"
    required = False
    verbose_name = _("Comma-separated list of RDN fields for new user entries")


@site_preferences_registry.register
class EnableLDAPGroupSync(BooleanPreference):
    section = ldap
    name = "enable_group_sync"
    default = True
    required = False
    verbose_name = _("Enable ldap group sync")


@site_preferences_registry.register
class LDAPGroupSyncFieldShortName(StringPreference):
    section = ldap
    name = "group_sync_field_short_name"
    default = "cn"
    required = False
    verbose_name = _("Field for short name of group")
    row = "ldap_group_sync_field_short_name"


@site_preferences_registry.register
class LDAPGroupSyncFieldShortNameRE(StringPreference):
    section = ldap
    name = "group_sync_field_short_name_re"
    default = ""
    required = False
    verbose_name = _("Regular expression to match LDAP value for group short name against")
    help_text = _("e.g. class_(?P<class>.*); separate multiple patterns by |")
    row = "ldap_group_sync_field_short_name"


@site_preferences_registry.register
class LDAPGroupSyncFieldShortNameReplace(StringPreference):
    section = ldap
    name = "group_sync_field_short_name_replace"
    default = ""
    required = False
    verbose_name = _("Replacement template to apply to group short name")
    help_text = _("e.g. \\g<class>; separate multiple templates by |")
    row = "ldap_group_sync_field_short_name"


@site_preferences_registry.register
class LDAPGroupSyncFieldName(StringPreference):
    section = ldap
    name = "group_sync_field_name"
    default = "cn"
    required = False
    verbose_name = _("Field for name of group")
    row = "ldap_group_sync_field_name"


@site_preferences_registry.register
class LDAPGroupSyncFieldNameRE(StringPreference):
    section = ldap
    name = "group_sync_field_name_re"
    default = ""
    required = False
    verbose_name = _("Regular expression to match LDAP value for group name against,")
    help_text = _("e.g. class_(?P<class>.*); separate multiple patterns by |")
    row = "ldap_group_sync_field_name"


@site_preferences_registry.register
class LDAPGroupSyncFieldNameReplace(StringPreference):
    section = ldap
    name = "group_sync_field_name_replace"
    default = ""
    required = False
    verbose_name = _("Replacement template to apply to group name")
    help_text = _("e.g. \\g<class>; separate multiple templates by |")
    row = "ldap_group_sync_field_name"


@site_preferences_registry.register
class LDAPGroupSyncOwnerAttr(StringPreference):
    section = ldap
    name = "group_sync_owner_attr"
    default = ""
    required = False
    verbose_name = _("LDAP field with dn of group owner")
    row = "ldap_group_sync_owner_attr"


@site_preferences_registry.register
class LDAPGroupSyncOwnerAttrType(ChoicePreference):
    section = ldap
    name = "group_sync_owner_attr_type"
    default = "dn"
    required = False
    verbose_name = _("LDAP sync matching fields")
    choices = [
        ("dn", _("Distinguished Name")),
        ("uid", _("UID")),
    ]
    row = "ldap_group_sync_owner_attr"


@site_preferences_registry.register
class LDAPMatchingMode(ChoicePreference):
    section = ldap
    name = "matching_mode"
    default = "AND"
    required = True
    verbose_name = _("LDAP sync matching mode")
    choices = [("AND", _("All fields must match")), ("OR", _("Any one field must match"))]


@site_preferences_registry.register
class EnableLDAPPasswordChange(BooleanPreference):
    section = ldap
    name = "enable_password_change"
    default = False
    required = False
    verbose_name = _("Change LDAP password on AlekSIS password change")


@site_preferences_registry.register
class AdminLDAPPasswordChange(BooleanPreference):
    section = ldap
    name = "admin_password_change"
    default = False
    required = False
    verbose_name = _("Use admin account (or auth account if unset) to change passwords")


@site_preferences_registry.register
class LDAPAdminDN(StringPreference):
    section = ldap
    name = "admin_dn"
    default = ""
    required = False
    verbose_name = _("DN of LDAP admin account (if other than LDAP auth account)")


@site_preferences_registry.register
class LDAPAdminPassword(StringPreference):
    section = ldap
    name = "admin_password"
    default = ""
    required = False
    verbose_name = _("Password of LDAP admin account (if other than LDAP auth account)")
