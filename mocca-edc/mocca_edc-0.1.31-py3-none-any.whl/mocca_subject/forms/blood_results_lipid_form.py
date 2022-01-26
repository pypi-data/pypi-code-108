from django import forms
from edc_action_item.forms import ActionItemFormMixin
from edc_blood_results.form_validator_mixins import BloodResultsFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators import FormValidator

from mocca_labs.panels import lipids_panel

from ..models import BloodResultsLipid


class BloodResultsLipidFormValidator(BloodResultsFormValidatorMixin, FormValidator):
    panel = lipids_panel
    reportable_grades = []


class BloodResultsLipidForm(ActionItemFormMixin, CrfModelFormMixin, forms.ModelForm):

    form_validator_cls = BloodResultsLipidFormValidator

    class Meta:
        model = BloodResultsLipid
        fields = "__all__"
