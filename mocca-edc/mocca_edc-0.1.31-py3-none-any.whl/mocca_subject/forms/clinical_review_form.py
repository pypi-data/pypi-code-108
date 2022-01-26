from django import forms
from edc_constants.constants import NO, YES
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_dx.form_validators import DiagnosisFormValidatorMixin
from edc_dx_review.utils import requires_clinical_review_at_baseline
from edc_form_validators.form_validator import FormValidator

from ..models import ClinicalReview


class ClinicalReviewFormValidator(
    DiagnosisFormValidatorMixin, CrfFormValidatorMixin, FormValidator
):
    def clean(self):
        requires_clinical_review_at_baseline(self.cleaned_data.get("subject_visit"))

        diagnoses = self.get_diagnoses()

        for cond, label in [
            ("htn", "hypertension"),
            ("dm", "diabetes"),
            ("hiv", "HIV"),
            ("chol", "High Cholesterol"),
        ]:
            self.applicable_if_not_diagnosed(
                diagnoses=diagnoses,
                prefix=cond,
                field_applicable=f"{cond}_test",
                label=label,
            )
            self.required_if(YES, field=f"{cond}_test", field_required=f"{cond}_test_date")
            self.required_if(YES, field=f"{cond}_test", field_required=f"{cond}_reason")
            self.applicable_if(YES, field=f"{cond}_test", field_applicable=f"{cond}_dx")

        self.required_if(
            YES,
            field="health_insurance",
            field_required="health_insurance_monthly_pay",
            field_required_evaluate_as_int=True,
        )
        self.required_if(
            YES,
            field="patient_club",
            field_required="patient_club_monthly_pay",
            field_required_evaluate_as_int=True,
        )

    def raise_if_dx_and_applicable(self, clinic, cond):
        if self.subject_screening.clinic_type in [clinic] and self.cleaned_data.get(
            f"{cond}_test"
        ) in [YES, NO]:
            raise forms.ValidationError(
                {
                    f"{cond}_test": (
                        f"Not applicable. Patient was recruited from the {cond.title} clinic."
                    ),
                }
            )


class ClinicalReviewForm(CrfModelFormMixin, forms.ModelForm):

    form_validator_cls = ClinicalReviewFormValidator

    class Meta:
        model = ClinicalReview
        fields = "__all__"
