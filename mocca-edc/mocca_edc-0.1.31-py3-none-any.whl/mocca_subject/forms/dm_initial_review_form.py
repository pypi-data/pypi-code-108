from django import forms
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_dx_review.utils import (
    raise_if_both_ago_and_actual_date,
    raise_if_clinical_review_does_not_exist,
)
from edc_form_validators.form_validator import FormValidator
from edc_glucose.form_validators import GlucoseFormValidatorMixin
from edc_model.utils import estimated_date_from_ago

from ..constants import DRUGS, INSULIN
from ..models import DmInitialReview


class DmInitialReviewFormValidator(
    GlucoseFormValidatorMixin,
    CrfFormValidatorMixin,
    FormValidator,
):
    def clean(self):
        raise_if_clinical_review_does_not_exist(self.cleaned_data.get("subject_visit"))
        raise_if_both_ago_and_actual_date(cleaned_data=self.cleaned_data)
        self.required_if(
            DRUGS,
            INSULIN,
            field="managed_by",
            field_required="med_start_ago",
        )

        if self.cleaned_data.get("dx_ago") and self.cleaned_data.get("med_start_ago"):
            if (
                estimated_date_from_ago(data=self.cleaned_data, ago_field="dx_ago")
                - estimated_date_from_ago(data=self.cleaned_data, ago_field="med_start_ago")
            ).days > 1:
                raise forms.ValidationError(
                    {"med_start_ago": "Invalid. Cannot be before diagnosis."}
                )
        # self.required_if(YES, field="glucose_performed", field_required="glucose_date")
        # self.validate_glucose_test()


class DmInitialReviewForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = DmInitialReviewFormValidator

    class Meta:
        model = DmInitialReview
        fields = "__all__"
