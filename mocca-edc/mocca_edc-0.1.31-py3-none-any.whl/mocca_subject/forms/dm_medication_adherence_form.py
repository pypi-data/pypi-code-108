from django import forms
from edc_adherence.form_validator_mixin import MedicationAdherenceFormValidatorMixin
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators.form_validator import FormValidator
from edc_model.widgets import SliderWidget

from ..models import DmMedicationAdherence


class DmMedicationAdherenceFormValidator(
    MedicationAdherenceFormValidatorMixin,
    CrfFormValidatorMixin,
    FormValidator,
):
    pass


class DmMedicationAdherenceForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = DmMedicationAdherenceFormValidator

    visual_score_slider = forms.CharField(
        label="Visual Score", widget=SliderWidget(attrs={"min": 0, "max": 100})
    )

    class Meta:
        model = DmMedicationAdherence
        fields = "__all__"
