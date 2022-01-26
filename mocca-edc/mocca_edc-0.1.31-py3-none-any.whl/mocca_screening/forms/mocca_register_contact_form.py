from django import forms
from edc_constants.constants import ALIVE, DEAD, UNKNOWN, YES
from edc_form_validators import FormValidator, FormValidatorMixin

from ..models import MoccaRegisterContact


class MoccaRegisterContactFormValidator(FormValidator):
    def clean(self):
        self.applicable_if(YES, field="answered", field_applicable="respondent")
        self.applicable_if(YES, field="answered", field_applicable="survival_status")
        self.not_required_if(
            UNKNOWN,
            ALIVE,
            field="survival_status",
            field_required="death_date",
            inverse=False,
        )
        self.applicable_if(
            ALIVE, field="survival_status", field_applicable="willing_to_attend"
        )
        self.applicable_if(ALIVE, field="survival_status", field_applicable="icc")
        self.required_if(YES, field="willing_to_attend", field_required="next_appt_date")
        if (
            self.cleaned_data.get("survival_status") == DEAD
            and self.cleaned_data.get("call_again") == YES
        ):
            raise forms.ValidationError({"call_again": "Invalid. Subject is deceased"})


class MoccaRegisterContactForm(FormValidatorMixin, forms.ModelForm):

    form_validator_cls = MoccaRegisterContactFormValidator

    class Meta:
        model = MoccaRegisterContact
        fields = [
            "answered",
            "respondent",
            "survival_status",
            "death_date",
            "willing_to_attend",
            "icc",
            "next_appt_date",
            "call_again",
            "report_datetime",
        ]
        labels = {"report_datetime": "Date", "answered": "Did someone answer?"}
