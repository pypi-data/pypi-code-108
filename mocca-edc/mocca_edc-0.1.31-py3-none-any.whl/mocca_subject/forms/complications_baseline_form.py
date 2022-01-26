from django import forms
from edc_constants.constants import YES
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators.form_validator import FormValidator
from edc_model.utils import estimated_date_from_ago, model_exists_or_raise
from edc_visit_schedule.utils import raise_if_not_baseline

from ..models import ClinicalReviewBaseline, ComplicationsBaseline


class ComplicationsBaselineFormValidator(CrfFormValidatorMixin, FormValidator):
    def clean(self):
        raise_if_not_baseline(self.cleaned_data.get("subject_visit"))
        model_exists_or_raise(
            self.cleaned_data.get("subject_visit"), model_cls=ClinicalReviewBaseline
        )
        self.required_if(YES, field="stroke", field_required="stroke_ago")
        estimated_date_from_ago(data=self.cleaned_data, ago_field="stroke_ago")
        self.required_if(YES, field="heart_attack", field_required="heart_attack_ago")
        estimated_date_from_ago(data=self.cleaned_data, ago_field="heart_attack_ago")
        self.required_if(YES, field="renal_disease", field_required="renal_disease_ago")
        estimated_date_from_ago(data=self.cleaned_data, ago_field="renal_disease_ago")
        self.required_if(YES, field="vision", field_required="vision_ago")
        estimated_date_from_ago(data=self.cleaned_data, ago_field="vision_ago")
        self.required_if(YES, field="numbness", field_required="numbness_ago")
        estimated_date_from_ago(data=self.cleaned_data, ago_field="numbness_ago")
        self.required_if(YES, field="foot_ulcers", field_required="foot_ulcers_ago")
        estimated_date_from_ago(data=self.cleaned_data, ago_field="foot_ulcers_ago")
        self.required_if(YES, field="complications", field_required="complications_other")


class ComplicationsBaselineForm(CrfModelFormMixin, forms.ModelForm):

    form_validator_cls = ComplicationsBaselineFormValidator

    class Meta:
        model = ComplicationsBaseline
        fields = "__all__"
