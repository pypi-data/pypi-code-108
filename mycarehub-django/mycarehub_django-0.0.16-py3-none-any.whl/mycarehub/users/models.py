import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db.models import (
    PROTECT,
    BooleanField,
    CharField,
    ForeignKey,
    JSONField,
    TextChoices,
    TextField,
    UUIDField,
)
from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import DateField, DateTimeField, IntegerField
from django.db.utils import ProgrammingError
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.snippets.models import register_snippet

DEFAULT_ORG_CODE = 1


class UserTypes(TextChoices):
    CLIENT = "CLIENT", _("Client")
    STAFF = "STAFF", _("Staff")


class GenderChoices(TextChoices):
    MALE = "MALE", _("Male")
    FEMALE = "FEMALE", _("Female")


class FlavourChoices(TextChoices):
    PRO = "PRO", _("PRO")
    CONSUMER = "CONSUMER", _("CONSUMER")


def default_organisation():
    try:
        from mycarehub.common.models import Organisation  # intentional late import

        org, _ = Organisation.objects.get_or_create(
            code=DEFAULT_ORG_CODE,
            id=settings.DEFAULT_ORG_ID,
            defaults={
                "organisation_name": settings.ORGANISATION_NAME,
                "email_address": settings.ORGANISATION_EMAIL,
                "phone_number": settings.ORGANISATION_PHONE,
            },
        )
        return org.pk
    except (ProgrammingError, Exception):  # pragma: nocover
        # this will occur during initial migrations on a clean db
        return uuid.UUID(settings.DEFAULT_ORG_ID)


@register_snippet
class TermsOfService(Model):
    text = TextField()
    valid_from = DateTimeField(default=timezone.now)
    valid_to = DateTimeField(null=True, blank=True)
    active = BooleanField(default=True)
    created = DateTimeField(default=timezone.now)
    created_by = UUIDField(null=True, blank=True)
    updated = DateTimeField(default=timezone.now)
    updated_by = UUIDField(null=True, blank=True)
    deleted_at = DateTimeField(null=True, blank=True)


class User(AbstractUser):
    """Default user model."""

    id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    #: First and last name do not cover name patterns around the globe
    # this should be used as the display name
    name = CharField(_("Name of User"), blank=True, max_length=255)
    middle_name = TextField(blank=True)
    handle = TextField(blank=True)  # @handle

    last_successful_login = DateTimeField(null=True, blank=True)
    last_failed_login = DateTimeField(null=True, blank=True)
    next_allowed_login = DateTimeField(default=timezone.now)
    failed_login_count = IntegerField(default=0)
    accepted_terms_of_service = ForeignKey(
        TermsOfService, null=True, blank=True, on_delete=PROTECT
    )
    push_tokens = ArrayField(
        CharField(max_length=256),
        null=True,
        blank=True,
    )
    gender = CharField(choices=GenderChoices.choices, max_length=16, null=True, blank=True)
    date_of_birth = DateField(null=True, blank=True)
    user_type = CharField(choices=UserTypes.choices, max_length=32, null=True, blank=True)

    is_approved = BooleanField(
        default=False,
        help_text="When true, the user is able to log in to the main website (and vice versa)",
    )
    approval_notified = BooleanField(
        default=False,
        help_text="When true, the user has been notified that their account is approved",
    )
    phone = PhoneNumberField(null=True, blank=True)
    organisation = ForeignKey(
        "common.Organisation",
        on_delete=PROTECT,
        default=default_organisation,
    )
    flavour = CharField(choices=FlavourChoices.choices, max_length=32, null=True)
    terms_accepted = BooleanField(default=False, null=False)
    avatar = TextField(blank=True, null=True)
    is_suspended = BooleanField(
        default=False,
    )
    pin_change_required = BooleanField(default=True, blank=True, null=True)
    has_set_pin = BooleanField(default=False, blank=True, null=True)
    is_phone_verified = BooleanField(default=False, blank=True, null=True)
    has_set_security_questions = BooleanField(default=False, blank=True, null=True)

    @property
    def permissions(self):
        perms = set(
            [
                f"{perm.content_type.app_label}.{perm.codename}"
                for perm in self.user_permissions.all()
            ]
        )
        groups = self.groups.all()
        for group in groups:
            group_perms = set(
                [
                    f"{perm.content_type.app_label}.{perm.codename}"
                    for perm in group.permissions.all()
                ]
            )
            perms = perms | group_perms
        return ",\n".join(list(perms))

    @property
    def gps(self):
        groups = [gp.name for gp in self.groups.all()]
        return ",".join(groups) or "-"

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})

    def __str__(self):
        username = self.get_username()
        return f"{self.name} ({username})" if self.name else username

    class Meta(AbstractUser.Meta):
        permissions = [
            ("can_view_dashboard", "Can View Dashboard"),
            ("can_view_about", "Can View About Page"),
            ("can_export_data", "Can Export Data"),
            ("can_import_data", "Can Import Data"),
            ("system_administration", "System Administration"),
            ("community_management", "Community Management"),
            ("content_management", "Content Management"),
            ("client_management", "Client Management"),
        ]


class UserPIN(Model):
    """
    UserPIN stores a user's PINs - including historical/invalid ones.
    """

    user = ForeignKey(User, on_delete=PROTECT)
    hashed_pin = TextField()
    salt = TextField(null=True)
    valid_from = DateTimeField(default=timezone.now)
    valid_to = DateTimeField(default=timezone.now)
    user_type = CharField(choices=UserTypes.choices, max_length=32, null=True, blank=True)
    active = BooleanField(default=True)
    created = DateTimeField(default=timezone.now)
    created_by = UUIDField(null=True, blank=True)
    updated = DateTimeField(default=timezone.now)
    updated_by = UUIDField(null=True, blank=True)
    deleted_at = DateTimeField(null=True, blank=True)
    flavour = CharField(choices=FlavourChoices.choices, max_length=32, null=True)

    class Meta:
        index_together = (
            "user",
            "user_type",
        )


class Metric(Model):
    class MetricType(TextChoices):
        ENGAGEMENT = "ENGAGEMENT", _("Engagement Metrics")
        CONTENT = "CONTENT", _("Content Metrics")
        SYSTEM = "SYSTEM", _("System Metrics")

    timestamp = DateTimeField(default=timezone.now)
    payload = JSONField()
    user = ForeignKey(User, on_delete=PROTECT)
    metric_type = CharField(choices=MetricType.choices, max_length=32)
    active = BooleanField(default=True)
    created = DateTimeField(default=timezone.now)
    created_by = UUIDField(null=True, blank=True)
    updated = DateTimeField(default=timezone.now)
    updated_by = UUIDField(null=True, blank=True)
    deleted_at = DateTimeField(null=True, blank=True)


class UserOTP(Model):
    """
    UserOTP stores a user's OTP
    """

    user = ForeignKey(User, on_delete=CASCADE)
    is_valid = BooleanField()
    generated_at = DateTimeField(default=timezone.now)
    valid_until = DateTimeField(null=True, blank=True)
    channel = CharField(max_length=10)
    flavour = CharField(choices=FlavourChoices.choices, max_length=32, null=True)
    phonenumber = TextField()
    otp = CharField(max_length=8)
    created = DateTimeField(default=timezone.now)
    created_by = UUIDField(null=True, blank=True)
    updated = DateTimeField(default=timezone.now)
    updated_by = UUIDField(null=True, blank=True)
    deleted_at = DateTimeField(null=True, blank=True)
