from django import forms
from edc_constants.constants import FORMER_SMOKER, YES
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators.form_validator import FormValidator
from edc_model.utils import estimated_date_from_ago
from edc_visit_schedule.utils import raise_if_not_baseline

from ..models import OtherBaselineData


class OtherBaselineDataFormValidator(CrfFormValidatorMixin, FormValidator):
    def clean(self):
        raise_if_not_baseline(self.cleaned_data.get("subject_visit"))

        self.required_if(
            FORMER_SMOKER, field="smoking_status", field_required="smoker_quit_ago"
        )
        estimated_date_from_ago(data=self.cleaned_data, ago_field="smoker_quit_ago")

        self.applicable_if(YES, field="alcohol", field_applicable="alcohol_consumption")

        self.validate_other_specify(
            field="employment_status", other_specify_field="employment_status_other"
        )


class OtherBaselineDataForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = OtherBaselineDataFormValidator

    class Meta:
        model = OtherBaselineData
        fields = "__all__"
