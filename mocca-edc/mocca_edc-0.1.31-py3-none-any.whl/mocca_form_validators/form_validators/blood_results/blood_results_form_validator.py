from edc_blood_results.form_validator_mixins import BloodResultsGluFormValidatorMixin
from edc_form_validators import FormValidator
from edc_lab_panel.panels import blood_glucose_panel, hba1c_panel

from mocca_labs.panels import lipids_panel

from .blood_results_form_validator_mixin import BloodResultsFormValidatorMixin


class BloodResultsGluFormValidator(
    BloodResultsGluFormValidatorMixin, BloodResultsFormValidatorMixin, FormValidator
):
    panel = blood_glucose_panel
    reportable_grades = []


class BloodResultsHba1cFormValidator(BloodResultsFormValidatorMixin, FormValidator):
    panels = hba1c_panel
    reportable_grades = []


class BloodResultsLipidFormValidator(BloodResultsFormValidatorMixin, FormValidator):
    panel = lipids_panel
    reportable_grades = []


# class BloodResultsGluFormValidator(BloodResultsFormValidatorMixin):
#
#     requisition_field = "glucose_requisition"
#     assay_datetime_field = "glucose_assay_datetime"
#     field_names = ["glucose", "fasting"]
#     panels = [blood_glucose_panel]
#     poc_panels = [blood_glucose_poc_panel]
#
#     @property
#     def extra_options(self):
#         if not self.cleaned_data.get("fasting"):
#             raise forms.ValidationError({"fasting": "This field is required."})
#         fasting = True if self.cleaned_data.get("fasting") == FASTING else False
#         return dict(fasting=fasting)


# class BloodResultsHba1cFormValidator(BloodResultsFormValidatorMixin):
#
#     requisition_field = "hba1c_requisition"
#     assay_datetime_field = "hba1c_assay_datetime"
#     field_names = ["hba1c"]
#     panels = [hba1c_panel]
#     poc_panels = [hba1c_poc_panel]
#
#     def validate_reportable_fields(self, **kwargs):
#         pass

#
# class BloodResultsLipidFormValidator(BloodResultsFormValidatorMixin):
#
#     requisition_field = "lipid_requisition"
#     assay_datetime_field = "lipid_assay_datetime"
#     field_names = ["ldl", "hdl", "trig", "chol"]
#     panels = [chemistry_lipids_panel]
#     reportable_grades = []
