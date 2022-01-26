from django import forms
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_phq9.forms import Phq9FormValidator

from ..models import PatientHealth


class PatientHealthForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = Phq9FormValidator

    class Meta:
        model = PatientHealth
        fields = "__all__"
