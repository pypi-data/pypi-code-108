from django import forms
from edc_action_item.forms.action_item_form_mixin import ActionItemFormMixin
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_dx_review.utils import (
    raise_if_both_ago_and_actual_date,
    raise_if_clinical_review_does_not_exist,
)
from edc_form_validators.form_validator import FormValidator
from edc_model.utils import estimated_date_from_ago

from ..constants import DRUGS
from ..models import HtnInitialReview


class HtnInitialReviewFormValidator(
    CrfFormValidatorMixin,
    FormValidator,
):
    def clean(self):
        raise_if_clinical_review_does_not_exist(self.cleaned_data.get("subject_visit"))
        raise_if_both_ago_and_actual_date(cleaned_data=self.cleaned_data)
        self.required_if(DRUGS, field="managed_by", field_required="med_start_ago")
        if self.cleaned_data.get("med_start_ago") and self.cleaned_data.get("dx_ago"):
            if estimated_date_from_ago(
                data=self.cleaned_data, ago_field="med_start_ago"
            ) < estimated_date_from_ago(data=self.cleaned_data, ago_field="dx_ago"):
                raise forms.ValidationError(
                    {"med_start_ago": "Invalid. Cannot be before diagnosis."}
                )


class HtnInitialReviewForm(
    CrfModelFormMixin,
    ActionItemFormMixin,
    forms.ModelForm,
):
    form_validator_cls = HtnInitialReviewFormValidator

    class Meta:
        model = HtnInitialReview
        fields = "__all__"
