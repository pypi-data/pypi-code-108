from django import forms
from edc_constants.constants import YES
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_dx_review.utils import raise_if_clinical_review_does_not_exist
from edc_form_validators.form_validator import FormValidator

from ..models import ComplicationsFollowup


class ComplicationsFollowupFormValidators(CrfFormValidatorMixin, FormValidator):
    def clean(self):
        raise_if_clinical_review_does_not_exist(self.cleaned_data.get("subject_visit"))
        self.required_if(YES, field="stroke", field_required="stroke_date")
        self.required_if(YES, field="heart_attack", field_required="heart_attack_date")
        self.required_if(YES, field="renal_disease", field_required="renal_disease_date")
        self.required_if(YES, field="vision", field_required="vision_date")
        self.required_if(YES, field="numbness", field_required="numbness_date")
        self.required_if(YES, field="foot_ulcers", field_required="foot_ulcers_date")
        self.required_if(YES, field="complications", field_required="complications_other")


class ComplicationsFollowupForm(CrfModelFormMixin, forms.ModelForm):

    form_validator_cls = ComplicationsFollowupFormValidators

    class Meta:
        model = ComplicationsFollowup
        fields = "__all__"
