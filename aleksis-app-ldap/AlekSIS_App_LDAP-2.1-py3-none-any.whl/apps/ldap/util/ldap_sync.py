import io
import logging
import re
from hashlib import shake_256

from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.db import DataError, IntegrityError, transaction
from django.db.models import Q, fields
from django.db.models.fields.files import FileField
from django.utils.text import slugify
from django.utils.translation import gettext as _

from dynamic_preferences.types import MultipleChoicePreference, StringPreference
from magic import Magic
from tqdm import tqdm

from aleksis.core.registries import site_preferences_registry
from aleksis.core.util.core_helpers import get_site_preferences

logger = logging.getLogger(__name__)

TQDM_DEFAULTS = {
    "disable": None,
    "unit": "obj",
    "dynamic_ncols": True,
}


def setting_name_from_field(model, field):
    """Generate a setting name from a model field."""
    name = f"additional_field_{model._meta.label_lower}_{field.name}"
    name_hash = shake_256(name.encode()).hexdigest(5)
    cleaned_name = re.sub(r"[\._]+", "_", name)
    return f"{cleaned_name}{name_hash}"


def ldap_field_to_filename(dn, fieldname):
    """Generate a reproducible filename from a DN and a field name."""
    return f"{slugify(dn)}__{slugify(fieldname)}"


def from_ldap(value, field, dn, ldap_field, instance=None):
    """Convert an LDAP value to the Python type of the target field.

    This conversion is prone to error because LDAP deliberately breaks
    standards to cope with ASN.1 limitations.
    """
    from ldapdb.models.fields import datetime_from_ldap  # noqa

    # Pre-convert DateTimeField and DateField due to ISO 8601 limitations in RFC 4517
    if isinstance(field, (fields.DateField, fields.DateTimeField)):
        # Be opportunistic, but keep old value if conversion fails
        value = datetime_from_ldap(value) or value
    elif isinstance(field, FileField) and instance is not None:
        content = File(io.BytesIO(value))

        basename = ldap_field_to_filename(dn, ldap_field)
        if ldap_field == "jpegphoto":
            extension = "jpeg"
        else:
            extension = Magic(extension=True).from_buffer(content).split("/")[0]
        name = f"{basename}.{extension}"

        # Pre-save field file instance
        fieldfile = getattr(instance, field.attname)
        fieldfile.save(name, content)

        return fieldfile

    # Finally, use field's conversion method as default
    return field.to_python(value)


def update_dynamic_preferences():
    """Auto-generate sync field settings from models."""
    from ..preferences import ldap as section_ldap  # noqa

    Person = apps.get_model("core", "Person")
    for model in (Person,):
        # Collect fields that are matchable
        for field in model.syncable_fields():
            setting_name = setting_name_from_field(model, field)

            @site_preferences_registry.register
            class _GeneratedPreference(StringPreference):
                section = section_ldap
                name = setting_name
                verbose_name = _(f"LDAP field for '{field.verbose_name}' on {model._meta.label}")
                required = False
                default = ""
                row = setting_name

            @site_preferences_registry.register
            class _GeneratedPreferenceRe(StringPreference):
                section = section_ldap
                name = setting_name + "_re"
                verbose_name = _(
                    f"Regular expression to match LDAP value for"
                    f" '{field.verbose_name}' on {model._meta.verbose_name} against"
                )
                required = False
                default = ""
                row = setting_name

            @site_preferences_registry.register
            class _GeneratedPreferenceReplace(StringPreference):
                section = section_ldap
                name = setting_name + "_replace"
                verbose_name = _(
                    f"Replacement template to apply to '{field.verbose_name}'"
                    f" on {model._meta.verbose_name}"
                )
                required = False
                default = ""
                row = setting_name

    @site_preferences_registry.register
    class LDAPMatchingFields(MultipleChoicePreference):
        section = section_ldap
        name = "matching_fields"
        default = []
        required = False
        verbose_name = _("LDAP sync matching fields")
        choices = [(field.name, field.name) for field in Person.syncable_fields()]


def apply_templates(value, patterns, templates, separator="|"):
    """Regex-replace patterns in value in order."""
    if isinstance(patterns, str):
        patterns = patterns.split(separator)
    if isinstance(templates, str):
        templates = templates.split(separator)

    for pattern, template in zip(patterns, templates):
        if not pattern or not template:
            continue

        match = re.fullmatch(pattern, value)
        if match:
            value = match.expand(template)

    return value


def get_ldap_value_for_field(model, field, attrs, dn, instance=None):
    """Get the value of a field in LDAP attributes.

    Looks at the site preference for sync fields to determine which LDAP field is
    associated with the model field, then gets this attribute and pythonises it.

    Raises KeyError if the desired field is not in the LDAP entry.
    Raises AttributeError if the requested field is not configured to be synced.
    """
    setting_name = "ldap__" + setting_name_from_field(model, field)

    # Try sync if preference for this field is non-empty
    ldap_field = get_site_preferences()[setting_name].lower()

    if not ldap_field:
        raise AttributeError(f"Field {field.name} not configured to be synced.")

    if ldap_field in attrs:
        value = attrs[ldap_field][0]

        # Apply regex replace from config
        patterns = get_site_preferences()[setting_name + "_re"]
        templates = get_site_preferences()[setting_name + "_replace"]
        value = apply_templates(value, patterns, templates)

        # Opportunistically convert LDAP string value to Python object
        value = from_ldap(value, field, dn, ldap_field, instance)

        return value
    else:
        raise KeyError(f"Field {ldap_field} not in attributes of {dn}")


@transaction.atomic
def ldap_create_user(sender, request, user, **kwargs):
    """Create a user in LDAP upon registration through allauth."""
    # Check if creation on registration is activated
    if not get_site_preferences()["ldap__user_create_on_register"]:
        return

    # Build attributes
    attrs = {attr: getattr(user, field) for field, attr in settings.AUTH_LDAP_USER_ATTR_MAP.items()}

    # Build DN for new object
    rdn_fields = get_site_preferences()["ldap__user_create_rdn_fields"]
    base_dn = settings.AUTH_LDAP_USER_SEARCH.base_dn
    rdn = "+".join([f"{rdn_field}={attrs[rdn_field][0]}" for rdn_field in rdn_fields])
    dn = f"{rdn},{base_dn}"


@transaction.atomic
def ldap_sync_user_on_login(sender, user, ldap_user, **kwargs):
    """Synchronise Person meta-data and groups from ldap_user on User update."""
    # Check if sync on login is activated
    if not get_site_preferences()["ldap__person_sync_on_login"]:
        return

    Person = apps.get_model("core", "Person")

    if get_site_preferences()["ldap__enable_sync"]:
        try:
            with transaction.atomic():
                person = ldap_sync_from_user(user, ldap_user.dn, ldap_user.attrs.data)
        except Person.DoesNotExist:
            logger.warn(f"No matching person for user {user.username}")
            return
        except Person.MultipleObjectsReturned:
            logger.error(f"More than one matching person for user {user.username}")
            return
        except (DataError, IntegrityError, KeyError, ValueError) as e:
            logger.error(f"Data error while synchronising user {user.username}:\n{e}")
            return

        if get_site_preferences()["ldap__enable_group_sync"]:
            # Get groups from LDAP
            groups = ldap_user._get_groups()
            group_infos = list(groups._get_group_infos())
            group_objects = ldap_sync_from_groups(group_infos)

            # Replace linked groups of logged-in user completely
            person.member_of.set(group_objects)
            logger.info(f"Replaced group memberships of {person}")

        try:
            person.save()
        except Exception as e:
            # Exceptions here are logged only because the synchronisation is optional
            # FIXME throw warning to user instead
            logger.error(f"Could not save person {person}:\n{e}")


@transaction.atomic
def ldap_sync_from_user(user, dn, attrs):
    """Synchronise person information from a User object (with ldap_user) to Django."""
    Person = apps.get_model("core", "Person")

    # Check if there is an existing person connected to the user.
    if Person.objects.filter(user__username=user.username).exists():
        person = user.person
        created = False
        logger.info(f"Existing person {person} already linked to user {user.username}")
    # FIXME ALso account for existing person with DN here
    else:
        # Build filter criteria depending on config
        matches = {}
        defaults = {}

        # Match on all fields selected in preferences
        fields_map = {f.name: f for f in Person.syncable_fields()}
        for field_name in get_site_preferences()["ldap__matching_fields"]:
            try:
                value = get_ldap_value_for_field(Person, fields_map[field_name], attrs, dn)
            except KeyError:
                # Field is not set in LDAP, match on remaining fields
                continue

            matches[field_name] = value

        if not matches:
            raise KeyError(f"No matching fields found for {dn}")

        # Pre-fill all mandatory non-matching fields from User object
        for missing_key in ("first_name", "last_name", "email"):
            if missing_key not in matches:
                defaults[missing_key] = getattr(user, missing_key)

        q = Q()
        matching_mode = get_site_preferences()["ldap__matching_mode"]
        for field, value in matches.items():
            add_q = Q(**{field: value})
            if matching_mode == "AND":
                q = q & add_q
            elif matching_mode == "OR":
                q = q | add_q
            else:
                raise ValueError(f"Invalid setting for matching mode: {matching_mode}")

        try:
            person = Person.objects.get(q)
            created = False
        except Person.DoesNotExist:
            if get_site_preferences()["ldap__create_missing_persons"]:
                person = Person.objects.create(**matches, **defaults)
                created = True

        user.save()
        person.user = user
        status = "New" if created else "Existing"
        logger.info(f"{status} person {person} linked to user {user.username}")

    person.ldap_dn = dn.lower()
    if not created:
        person.first_name = user.first_name
        person.last_name = user.last_name
        person.email = user.email

    # Synchronise additional fields if enabled
    for field in Person.syncable_fields():
        try:
            value = get_ldap_value_for_field(Person, field, attrs, dn, person)
        except (AttributeError, KeyError):
            # A syncable field is not configured to sync or missing in LDAP
            continue

        setattr(person, field.name, value)
        logger.debug(f"Field {field.name} set to {value} for {person}")

    person.save()
    return person


@transaction.atomic
def ldap_sync_from_groups(group_infos):
    """Synchronise group information from LDAP results to Django."""
    Group = apps.get_model("core", "Group")
    SchoolTerm = apps.get_model("core", "SchoolTerm")

    # Get current school term
    school_term = SchoolTerm.current

    # Resolve Group objects from LDAP group objects
    ldap_groups = {}
    for ldap_group in tqdm(group_infos, desc="Parsing group infos", **TQDM_DEFAULTS):
        # Skip group if one of the name fields is missing
        # FIXME Throw exceptions and catch outside
        sync_field_short_name = get_site_preferences()["ldap__group_sync_field_short_name"]
        if sync_field_short_name not in ldap_group[1]:
            logger.error(
                f"LDAP group with DN {ldap_group[0]} does not have field {sync_field_short_name}"
            )
            continue

        sync_field_name = get_site_preferences()["ldap__group_sync_field_name"]
        if sync_field_name not in ldap_group[1]:
            logger.error(
                f"LDAP group with DN {ldap_group[0]} does not have field {sync_field_name}"
            )
            continue

        # Apply regex replace from config
        short_name = apply_templates(
            ldap_group[1][get_site_preferences()["ldap__group_sync_field_short_name"]][0],
            get_site_preferences()["ldap__group_sync_field_short_name_re"],
            get_site_preferences()["ldap__group_sync_field_short_name_replace"],
        )
        name = apply_templates(
            ldap_group[1][get_site_preferences()["ldap__group_sync_field_name"]][0],
            get_site_preferences()["ldap__group_sync_field_name_re"],
            get_site_preferences()["ldap__group_sync_field_name_replace"],
        )

        # Shorten names to fit into model fields
        short_name = short_name[: Group._meta.get_field("short_name").max_length]
        name = name[: Group._meta.get_field("name").max_length]

        ldap_groups[ldap_group[0].lower()] = {"short_name": short_name, "name": name}

    all_dns = set(ldap_groups.keys())

    # First, update all existing groups with known DNs
    existing = Group.objects.filter(ldap_dn__in=all_dns, school_term=school_term).select_related(
        None
    )
    existing_dns = set([v.ldap_dn for v in existing])
    for obj in existing:
        obj.name = ldap_groups[obj.ldap_dn]["name"]
        obj.short_name = ldap_groups[obj.ldap_dn]["short_name"]
    logger.info(f"Updating {len(existing)} Django groups")
    try:
        Group.objects.bulk_update(existing, ("name", "short_name"))
    except IntegrityError as e:
        logger.error(f"Integrity error while trying to import LDAP groups:\n{e}")
    else:
        logger.debug(f"Updated {len(existing)} Django groups")

    # Second, create all groups with unknown DNs
    nonexisting_dns = all_dns - existing_dns
    nonexisting = []
    for dn in nonexisting_dns:
        nonexisting.append(
            Group(
                ldap_dn=dn,
                name=ldap_groups[dn]["name"],
                short_name=ldap_groups[dn]["short_name"],
                school_term=school_term,
            )
        )
    logger.info(f"Creating {len(nonexisting)} Django groups")
    try:
        Group.objects.bulk_create(nonexisting)
    except IntegrityError as e:
        logger.error(f"Integrity error while trying to import LDAP groups:\n{e}")
    else:
        logger.debug(f"Created {len(nonexisting)} Django groups")

    # Return all groups ever touched
    return set(existing) | set(nonexisting)


@transaction.atomic
def mass_ldap_import():
    """Add utility code for mass import from ldap."""
    from django_auth_ldap.backend import LDAPBackend, _LDAPUser  # noqa

    Person = apps.get_model("core", "Person")

    # Abuse pre-configured search object as general LDAP interface
    backend = LDAPBackend()
    connection = _LDAPUser(backend, "").connection

    # Synchronise all groups first
    if get_site_preferences()["ldap__enable_group_sync"]:
        ldap_groups = backend.settings.GROUP_SEARCH.execute(connection)
        group_objects = ldap_sync_from_groups(ldap_groups)

        # Create lookup table as cache for later code
        group_dict = {obj.ldap_dn: obj for obj in group_objects}

    # Guess LDAP username field from user filter
    uid_field = re.search(
        r"([a-zA-Z]+)=%\(user\)s", backend.settings.USER_SEARCH.searches[0].filterstr
    ).group(1)

    # Synchronise user data for all found users
    ldap_users = backend.settings.USER_SEARCH.execute(connection, {"user": "*"}, escape=False)
    for dn, attrs in tqdm(ldap_users, desc="Sync. user infos", **TQDM_DEFAULTS):
        uid = attrs[uid_field][0]

        # Prepare an empty LDAPUser object with the target username
        ldap_user = _LDAPUser(backend, username=uid)

        # Get existing or new User object and pre-populate
        user, created = backend.get_or_build_user(uid, ldap_user)
        ldap_user._user = user
        ldap_user._attrs = attrs
        ldap_user._dn = dn
        ldap_user._populate_user_from_attributes()
        user.save()

        try:
            with transaction.atomic():
                person = ldap_sync_from_user(user, dn, attrs)
        except Person.DoesNotExist:
            logger.warn(f"No matching person for user {user.username}")
            continue
        except Person.MultipleObjectsReturned:
            logger.error(f"More than one matching person for user {user.username}")
            continue
        except (DataError, IntegrityError, KeyError, ValueError) as e:
            logger.error(f"Data error while synchronising user {user.username}:\n{e}")
            continue
        else:
            logger.info(f"Successfully imported user {uid}")

    # Synchronise group memberships now
    if get_site_preferences()["ldap__enable_group_sync"]:
        member_attr = getattr(backend.settings.GROUP_TYPE, "member_attr", "memberUid")
        owner_attr = get_site_preferences()["ldap__group_sync_owner_attr"]

        for ldap_group in tqdm(
            ldap_groups,
            desc="Sync. group members",
            total=len(ldap_groups),
            **TQDM_DEFAULTS,
        ):
            dn, attrs = ldap_group

            if dn not in group_dict:
                logger.warning(f"Skip {dn} because there are no groups with this dn.")
                continue

            group = group_dict[dn]

            ldap_members = [_.lower() for _ in attrs[member_attr]] if member_attr in attrs else []

            if member_attr.lower() == "memberuid":
                members = Person.objects.filter(user__username__in=ldap_members)
            else:
                members = Person.objects.filter(ldap_dn__in=ldap_members)

            if get_site_preferences()["ldap__group_sync_owner_attr"]:
                ldap_owners = [_.lower() for _ in attrs[owner_attr]] if owner_attr in attrs else []
                if get_site_preferences()["ldap__group_sync_owner_attr_type"] == "uid":
                    owners = Person.objects.filter(user__username__in=ldap_owners)
                elif get_site_preferences()["ldap__group_sync_owner_attr_type"] == "dn":
                    owners = Person.objects.filter(ldap_dn__in=ldap_owners)

            group.members.set(members)
            if get_site_preferences()["ldap__group_sync_owner_attr"]:
                group.owners.set(owners)
            group.save()
            logger.info(f"Set group members of group {group}")

    # Synchronise primary groups
    all_persons = set(Person.objects.all())
    for person in tqdm(all_persons, desc="Sync. primary groups", **TQDM_DEFAULTS):
        person.auto_select_primary_group()
    Person.objects.bulk_update(all_persons, ("primary_group",))

    logger.info("Commiting transaction; this can take some time.")
