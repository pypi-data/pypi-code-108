from django import forms
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators.form_validator import FormValidator

from ..models import DrugRefillChol
from .drug_refill_mixins import DrugRefillFormValidatorMixin


class DrugRefillCholFormValidator(
    DrugRefillFormValidatorMixin, CrfFormValidatorMixin, FormValidator
):
    pass


class DrugRefillCholForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = DrugRefillCholFormValidator

    class Meta:
        model = DrugRefillChol
        fields = "__all__"
