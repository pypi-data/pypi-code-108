from django import forms
from edc_constants.constants import OTHER
from edc_form_validators import FormValidator, FormValidatorMixin

from ..models import SubjectRefusal


class SubjectRefusalScreeningFormValidator(FormValidator):
    def clean(self):
        self.required_if(OTHER, field="reason", field_required="other_reason")


class SubjectRefusalScreeningForm(FormValidatorMixin, forms.ModelForm):
    form_validator_cls = SubjectRefusalScreeningFormValidator

    class Meta:
        model = SubjectRefusal
        fields = "__all__"
