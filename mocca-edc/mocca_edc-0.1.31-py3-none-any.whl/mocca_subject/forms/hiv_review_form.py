from django import forms
from edc_constants.constants import NO, YES
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_dx_review.utils import (
    art_initiation_date,
    raise_if_clinical_review_does_not_exist,
)
from edc_form_validators.form_validator import FormValidator

from ..models import HivReview


class HivReviewFormValidator(CrfFormValidatorMixin, FormValidator):
    def clean(self):
        raise_if_clinical_review_does_not_exist(self.cleaned_data.get("subject_visit"))
        self.validate_care_delivery()
        art_init_date = art_initiation_date(
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
        )
        self.applicable_if_true(
            not art_init_date,
            field_applicable="arv_initiated",
            applicable_msg="Subject was NOT previously reported as on ART.",
            not_applicable_msg="Subject was previously reported as on ART.",
        )
        self.required_if(
            YES, field="arv_initiated", field_required="arv_initiation_actual_date"
        )

    def validate_care_delivery(self) -> None:
        self.required_if(NO, field="care_delivery", field_required="care_delivery_other")


class HivReviewForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = HivReviewFormValidator

    class Meta:
        model = HivReview
        fields = "__all__"
