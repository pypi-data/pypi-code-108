from django import forms
from edc_constants.constants import OTHER, YES
from edc_dx_review.utils import medications_exists_or_raise
from edc_visit_schedule.utils import is_baseline


class DrugRefillFormValidatorMixin:
    def drug_refill_clean(self) -> None:
        medications_exists_or_raise(self.cleaned_data.get("subject_visit"))
        if (
            self.cleaned_data.get("subject_visit")
            and is_baseline(self.cleaned_data.get("subject_visit"))
            and self.cleaned_data.get("rx_modified") == YES
        ):
            raise forms.ValidationError({"rx_modified": "Expected `No` at baseline."})

        self.m2m_other_specify(
            OTHER, m2m_field="modifications", field_other="modifications_other"
        )
        self.m2m_other_specify(
            OTHER,
            m2m_field="modification_reasons",
            field_other="modification_reasons_other",
        )
