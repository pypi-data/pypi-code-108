from django import forms
from django.conf import settings
from edc_constants.constants import NOT_APPLICABLE
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_dx import Diagnoses
from edc_dx.diagnoses import InitialReviewRequired
from edc_form_validators.form_validator import FormValidator
from edc_model import model_exists_or_raise
from edc_utils import convert_php_dateformat
from edc_visit_schedule.utils import is_baseline

from ..models import ClinicalReview, ClinicalReviewBaseline, Medications


class MedicationsFormValidator(CrfFormValidatorMixin, FormValidator):
    def clean(self):
        if not is_baseline(self.cleaned_data.get("subject_visit")):
            model_exists_or_raise(
                self.cleaned_data.get("subject_visit"), model_cls=ClinicalReview
            )
        else:
            model_exists_or_raise(
                self.cleaned_data.get("subject_visit"),
                model_cls=ClinicalReviewBaseline,
                singleton=True,
            )
        self.validate_diagnosis_before_refill()

    def validate_diagnosis_before_refill(self):
        """Assert subject has been diagnosed for the condition
        for which they require a medication refill,
        including for the current timepoint."""

        diagnoses = Diagnoses(
            subject_identifier=self.subject_identifier,
            report_datetime=self.report_datetime,
            lte=True,
        )

        try:
            diagnoses.get_initial_reviews()
        except InitialReviewRequired as e:
            raise forms.ValidationError(e)

        options = []
        for prefix, label in settings.EDC_DX_LABELS.items():
            options.append(
                (
                    f"refill_{prefix}",
                    diagnoses.get_dx(prefix),
                    diagnoses.get_dx_date(prefix),
                    label,
                ),
            )

        for fld, dx, dx_date, label in options:
            if self.cleaned_data.get(fld) == NOT_APPLICABLE and dx:
                formatted_date = dx_date.strftime(convert_php_dateformat(settings.DATE_FORMAT))
                raise forms.ValidationError(
                    {
                        fld: (
                            f"Invalid. Subject was previously diagnosed with {label} "
                            f"on {formatted_date}. Expected YES/NO."
                        )
                    }
                )
            elif self.cleaned_data.get(fld) != NOT_APPLICABLE and not dx:
                raise forms.ValidationError(
                    {
                        fld: (
                            "Invalid. Subject has not been diagnosed with "
                            f"{label}. Expected N/A. See also the "
                            f"`{ClinicalReview._meta.verbose_name}` CRF."
                        )
                    }
                )


class MedicationsForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = MedicationsFormValidator

    class Meta:
        model = Medications
        fields = "__all__"
