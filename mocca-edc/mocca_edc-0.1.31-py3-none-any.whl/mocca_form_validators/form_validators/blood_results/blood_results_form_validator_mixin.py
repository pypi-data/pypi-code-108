from edc_constants.constants import YES
from edc_form_validators.form_validator import FormValidator
from edc_lab.form_validators import CrfRequisitionFormValidatorMixin
from edc_reportable import ReportablesFormValidatorMixin
from edc_reportable.constants import GRADE3, GRADE4


class BloodResultsFormValidatorMixin(
    ReportablesFormValidatorMixin, CrfRequisitionFormValidatorMixin, FormValidator
):

    reportable_grades = [GRADE3, GRADE4]
    reference_list_name = "mocca"
    requisition_field = None
    assay_datetime_field = None
    field_names = []
    panels = []
    poc_panels = []

    @property
    def field_values(self):
        return [self.cleaned_data.get(f) is not None for f in [f for f in self.field_names]]

    @property
    def extra_options(self):
        return {}

    def clean(self):
        self.required_if_true(any(self.field_values), field_required=self.requisition_field)

        if self.cleaned_data.get("is_poc") and self.cleaned_data.get("is_poc") == YES:
            self.validate_requisition(
                self.requisition_field, self.assay_datetime_field, *self.poc_panels
            )
        else:
            self.validate_requisition(
                self.requisition_field, self.assay_datetime_field, *self.panels
            )

        # for field_name in self.field_names:
        #     self.validate_units_field(field_name)
        #     # self.validate_abnormal_field(field_name)
        #     # self.validate_reportable_field(field_name)

        self.validate_reportable_fields(
            reference_range_collection_name=self.reference_list_name, **self.extra_options
        )
