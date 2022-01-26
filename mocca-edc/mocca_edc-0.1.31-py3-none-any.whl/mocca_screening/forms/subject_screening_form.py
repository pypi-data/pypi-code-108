from django import forms
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import FEMALE, YES
from edc_form_validators import FormValidator, FormValidatorMixin
from edc_screening.modelform_mixins import AlreadyConsentedFormMixin

from ..models import MoccaRegister, SubjectScreening
from .care_status_form import CareStatusFormValidatorMixin


class SubjectScreeningFormValidator(CareStatusFormValidatorMixin, FormValidator):
    def clean(self) -> None:
        self.validate_is_mocca_participant()
        self.validate_consents_to_screen()
        self.validate_care_options()
        self.applicable_if(
            YES, field="screening_consent", field_applicable="willing_to_consent"
        )
        self.validate_pregnancy()
        self.applicable_if(
            YES,
            field="willing_to_consent",
            field_applicable="requires_acute_care",
            inverse=False,
        )
        self.validate_mocca_enrollment_data()
        return None

    def validate_is_mocca_participant(self) -> None:
        if self.cleaned_data.get("mocca_participant") != YES:
            raise forms.ValidationError(
                {
                    "mocca_participant": (
                        "Subject must have been a participant in the original MOCCA trial."
                    )
                }
            )
        return None

    def validate_consents_to_screen(self) -> None:
        if (
            not self.cleaned_data.get("screening_consent")
            or self.cleaned_data.get("screening_consent") != YES
        ):
            raise forms.ValidationError(
                {
                    "screening_consent": (
                        "You may NOT screen this subject without their verbal consent."
                    )
                }
            )
        return None

    def validate_pregnancy(self) -> None:
        if self.cleaned_data.get("mocca_register"):
            gender = self.cleaned_data.get("mocca_register").gender
        else:
            gender = self.instance.mocca_register.gender
        self.applicable_if_true(
            self.cleaned_data.get("willing_to_consent") == YES and gender == FEMALE,
            field_applicable="pregnant",
            inverse=False,
        )
        return None

    def validate_mocca_study_identifier_with_site(self) -> MoccaRegister:
        mocca_register = None
        mocca_register_cls = django_apps.get_model("mocca_screening.moccaregister")
        if self.cleaned_data.get("mocca_study_identifier") and self.cleaned_data.get(
            "mocca_site"
        ):
            mocca_study_identifier = self.cleaned_data.get("mocca_study_identifier")
            try:
                mocca_register = mocca_register_cls.objects.get(
                    mocca_study_identifier=mocca_study_identifier,
                )
            except ObjectDoesNotExist:
                raise forms.ValidationError(
                    {
                        "mocca_study_identifier": (
                            "Invalid MOCCA (original) study identifier. "
                            f"Got {mocca_study_identifier}"
                        )
                    }
                )
            else:
                if mocca_register.mocca_site != self.cleaned_data.get("mocca_site"):
                    expected_value = mocca_register.mocca_site
                    value = self.cleaned_data.get("mocca_site")
                    if expected_value != value:
                        raise forms.ValidationError(
                            {
                                "mocca_site": (
                                    f"Invalid MOCCA (original) site for given study "
                                    f"identifier. Got `{expected_value}` != `{value}` for "
                                    f"`{mocca_study_identifier}`"
                                )
                            }
                        )
        return mocca_register

    def validate_mocca_enrollment_data(self) -> None:
        """Raises an exception if either the birth year, gender or initials
        do not match the register record for the given
        `mocca_study_identifier`.
        """
        mocca_register = self.validate_mocca_study_identifier_with_site()
        if (
            mocca_register
            and self.cleaned_data.get("birth_year")
            and self.cleaned_data.get("initials")
        ):
            for attrname in ["initials", "gender", "birth_year"]:
                expected_value = getattr(mocca_register, attrname)
                value = self.cleaned_data.get(attrname)
                if expected_value != value:
                    label = attrname.replace("_", " ")
                    raise forms.ValidationError(
                        {
                            attrname: (
                                f"Invalid `{label}` for this MOCCA (original) study "
                                f"identifier. Got `{expected_value}` != `{value}` for "
                                f"`{mocca_register.mocca_study_identifier}`"
                            )
                        }
                    )

        if (
            self.cleaned_data.get("age_in_years")
            and self.cleaned_data.get("birth_year")
            and self.cleaned_data.get("report_datetime")
        ):
            expected_age = self.cleaned_data.get(
                "report_datetime"
            ).year - self.cleaned_data.get("birth_year")
            if abs(expected_age - self.cleaned_data.get("age_in_years")) > 1:
                raise forms.ValidationError(
                    {"age_in_years": "Does not make sense relative to birth year given"}
                )
        return None


class SubjectScreeningForm(AlreadyConsentedFormMixin, FormValidatorMixin, forms.ModelForm):
    form_validator_cls = SubjectScreeningFormValidator

    class Meta:
        model = SubjectScreening
        fields = "__all__"
