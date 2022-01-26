from django import forms
from edc_constants.constants import NOT_APPLICABLE, OTHER, STUDY_DEFINED_TIMEPOINT
from edc_form_validators import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin
from edc_visit_tracking.constants import MISSED_VISIT, SCHEDULED, UNSCHEDULED
from edc_visit_tracking.form_validators import VisitFormValidator

from ..models import SubjectVisit


class SubjectVisitFormValidator(VisitFormValidator):
    validate_missed_visit_reason = False

    def clean(self):
        super().clean()
        self.m2m_other_specify(
            OTHER,
            m2m_field="clinic_services",
            field_other="clinic_services_other",
        )

        self.validate__clinic_services()

        self.applicable_if(
            SCHEDULED, UNSCHEDULED, field="reason", field_applicable="info_source"
        )

    def validate__clinic_services(self):
        selections = self.get_m2m_selected("clinic_services")
        if (
            self.cleaned_data.get("appointment").visit_code_sequence == 0
            and self.cleaned_data.get("reason") != MISSED_VISIT
            and STUDY_DEFINED_TIMEPOINT not in selections
        ):
            raise forms.ValidationError({"clinic_services": "This is scheduled study visit."})
        elif (
            self.cleaned_data.get("appointment").visit_code_sequence != 0
            and self.cleaned_data.get("reason") != MISSED_VISIT
            and STUDY_DEFINED_TIMEPOINT in selections
        ):
            raise forms.ValidationError(
                {"clinic_services": "This is not a scheduled study visit."}
            )

        if self.cleaned_data.get("reason") == MISSED_VISIT:
            self.m2m_single_selection_if(NOT_APPLICABLE, m2m_field="clinic_services")

            self.m2m_selection_expected(
                m2m_field="clinic_services",
                response=NOT_APPLICABLE,
                error_msg=(
                    "Expected 'Not applicable' response (if this is a missed visit report)."
                ),
            )

        self.m2m_applicable_if_true(
            self.cleaned_data.get("reason") != MISSED_VISIT,
            m2m_field="clinic_services",
        )


class SubjectVisitForm(SiteModelFormMixin, FormValidatorMixin, forms.ModelForm):

    form_validator_cls = SubjectVisitFormValidator

    class Meta:
        model = SubjectVisit
        fields = "__all__"
