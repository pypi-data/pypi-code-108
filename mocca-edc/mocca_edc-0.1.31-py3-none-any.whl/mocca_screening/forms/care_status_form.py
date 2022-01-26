from django import forms
from edc_constants.constants import NO, UNKNOWN, YES
from edc_form_validators import FormValidator, FormValidatorMixin

from mocca_screening.models import CareStatus

from ..constants import NO_INTERRUPTION, SOME_INTERRUPTION


class CareStatusFormValidatorMixin(FormValidator):
    def validate_care_options(self) -> None:
        self.required_if(NO, UNKNOWN, field="care", field_required="care_not_in_reason")
        self.applicable_if(YES, field="care", field_applicable="care_facility_location")
        self.applicable_if(YES, field="care", field_applicable="icc")
        self.applicable_if(NO, field="icc", field_applicable="icc_not_in_reason")
        self.required_if(
            SOME_INTERRUPTION,
            field="icc_since_mocca",
            field_required="icc_since_mocca_comment",
        )
        if (
            self.cleaned_data.get("icc_since_mocca") == NO
            and self.cleaned_data.get("icc") == YES
        ):
            raise forms.ValidationError(
                {"icc_since_mocca": "Invalid. Patient is currently receiving integrated care."}
            )
        if (
            self.cleaned_data.get("icc_since_mocca") == NO_INTERRUPTION
            and self.cleaned_data.get("icc") != YES
        ):
            raise forms.ValidationError(
                {
                    "icc_since_mocca": (
                        "Invalid. Patient is NOT currently receiving integrated care."
                    )
                }
            )
        return None


class CareStatusFormValidator(CareStatusFormValidatorMixin):
    pass


class CareStatusForm(FormValidatorMixin, forms.ModelForm):
    form_validator_cls = CareStatusFormValidator

    class Meta:
        model = CareStatus
        fields = "__all__"
