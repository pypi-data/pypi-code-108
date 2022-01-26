from django import forms
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators.form_validator import FormValidator

from ..models import DrugRefillDm
from .drug_refill_mixins import DrugRefillFormValidatorMixin


class DrugRefillDmFormValidator(
    DrugRefillFormValidatorMixin, CrfFormValidatorMixin, FormValidator
):
    def clean(self):
        self.drug_refill_clean()


class DrugRefillDmForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = DrugRefillDmFormValidator

    class Meta:
        model = DrugRefillDm
        fields = "__all__"
