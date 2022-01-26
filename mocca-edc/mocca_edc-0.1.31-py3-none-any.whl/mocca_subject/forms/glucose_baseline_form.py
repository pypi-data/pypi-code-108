from django import forms
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_glucose.form_validators import GlucoseFormValidator as BaseGlucoseFormValidator

from ..models import GlucoseBaseline


class GlucoseFormValidator(BaseGlucoseFormValidator):
    required_at_baseline = True


class GlucoseBaselineForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = GlucoseFormValidator

    class Meta:
        model = GlucoseBaseline
        fields = "__all__"
