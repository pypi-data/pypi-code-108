from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField

from mycarehub.clients.models import ClientType
from mycarehub.common.models.common_models import Facility
from mycarehub.users.models import GenderChoices


def validate_date_past(value):
    if not isinstance(value, date):
        raise ValidationError(
            _("%(value)s is not a date"),
            params={"value": value},
        )

    if value > timezone.now().date():
        raise ValidationError(
            _("%(value)s is a date that is in the future"),
            params={"value": value},
        )


def get_facility_choices():
    choices = []
    for facility in Facility.objects.all():
        choices.append((facility.name, facility.name))

    return choices


class ClientRegistrationForm(forms.Form):
    """
    This form is used in a HTML UI and via a Django REST Framework serializer
    to register new clients.
    """

    facility = forms.ChoiceField(
        required=True,
        choices=get_facility_choices,
        label="Client's Facility/Clinic",
        help_text="The client's currently assigned facility/clinic",
    )

    client_type = forms.ChoiceField(
        required=True,
        choices=ClientType.choices,
        label="Client Type e.g PMTCT",
        help_text="The client's current care classification",
    )

    name = forms.CharField(
        required=True,
        max_length=255,
        label="Name",
        help_text="The client's full name i.e family, given and other names, on one row",
    )

    gender = forms.ChoiceField(
        required=True,
        choices=GenderChoices.choices,
        label="Gender",
        help_text="Pick the client's gender from the drop-down list",
    )

    date_of_birth = forms.DateField(
        required=True,
        label="Date of birth",
        help_text="Select the client's date of birth",
        validators=[
            validate_date_past,
        ],
    )

    phone_number = PhoneNumberField(
        required=True,
        label="Phone Number",
        help_text="The client's phone number",
    )

    enrollment_date = forms.DateField(
        required=True,
        label="Enrollment date",
        help_text="When the client was first enrolled in care",
        validators=[
            validate_date_past,
        ],
    )

    ccc_number = forms.IntegerField(
        required=True,
        label="CCC Number",
        help_text="Comprehensive Care Clinic Number, to be used as the primary identifier",
    )

    counselled = forms.BooleanField(
        required=True,
        label="Client Counselled?",
        help_text="Whether the client has been counselled",
    )
