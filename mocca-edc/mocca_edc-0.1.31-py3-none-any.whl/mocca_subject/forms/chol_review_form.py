from django import forms
from edc_constants.constants import NO
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_dx_review.utils import raise_if_clinical_review_does_not_exist
from edc_form_validators.form_validator import FormValidator

from ..models import CholReview


class CholReviewFormValidator(
    CrfFormValidatorMixin,
    FormValidator,
):
    def clean(self):
        raise_if_clinical_review_does_not_exist(self.cleaned_data.get("subject_visit"))
        self.validate_care_delivery()

    def validate_care_delivery(self) -> None:
        self.required_if(NO, field="care_delivery", field_required="care_delivery_other")


class CholReviewForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = CholReviewFormValidator

    class Meta:
        model = CholReview
        fields = "__all__"
