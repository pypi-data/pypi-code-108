from django import forms
from edc_constants.constants import YES
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators import FormValidator
from edc_glucose.utils import validate_glucose_as_millimoles_per_liter

from ..models import GlucoseFollowup


class GlucoseFollowupFormValidator(FormValidator):
    required_at_baseline = False

    def clean(self) -> None:
        self.applicable_if(YES, field="glucose_performed", field_applicable="glucose_fasted")
        self.required_if(YES, field="glucose_performed", field_required="glucose_date")
        self.required_if(YES, field="glucose_performed", field_required="glucose_value")
        self.required_if(YES, field="glucose_performed", field_required="glucose_quantifier")
        self.required_if(YES, field="glucose_performed", field_required="glucose_units")
        validate_glucose_as_millimoles_per_liter("glucose", self.cleaned_data)


class GlucoseFollowupForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = GlucoseFollowupFormValidator

    class Meta:
        model = GlucoseFollowup
        fields = "__all__"
