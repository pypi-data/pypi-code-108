from django import forms
from edc_action_item.forms.action_item_form_mixin import ActionItemFormMixin
from edc_constants.constants import NO, OTHER, YES
from edc_crf.forms import CrfFormValidatorMixin
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_dx_review.utils import (
    raise_if_both_ago_and_actual_date,
    raise_if_clinical_review_does_not_exist,
)
from edc_form_validators import FormValidator
from edc_model.utils import estimated_date_from_ago

from ..models import HivInitialReview


class HivInitialReviewFormValidator(
    CrfFormValidatorMixin,
    FormValidator,
):
    def clean(self):
        super().clean()
        raise_if_clinical_review_does_not_exist(self.cleaned_data.get("subject_visit"))

        raise_if_both_ago_and_actual_date(cleaned_data=self.cleaned_data)

        self.applicable_if(YES, field="receives_care", field_applicable="clinic")

        self.required_if(OTHER, field="clinic", field_required="clinic_other")

        self.required_if(YES, field="receives_care", field_required="arv_initiated")

        self.validate_art_initiation_date()

        self.required_if(YES, field="arv_initiated", field_required="has_vl")
        self.validate_viral_load()

        self.required_if(YES, field="arv_initiated", field_required="has_cd4")
        self.validate_cd4()

    def validate_art_initiation_date(self):
        self.not_required_if(
            NO,
            field="arv_initiated",
            field_required="arv_initiation_ago",
            inverse=False,
        )
        self.not_required_if(
            NO,
            field="arv_initiated",
            field_required="arv_initiation_actual_date",
            inverse=False,
        )
        if self.cleaned_data.get("art_initiated") == YES and not (
            self.cleaned_data.get("arv_initiation_ago")
            or self.cleaned_data.get("arv_initiation_actual_date")
        ):
            raise forms.ValidationError(
                {"arv_initiation_actual_date": "This field is required (or the above)."}
            )

        raise_if_both_ago_and_actual_date(
            dx_ago=self.cleaned_data.get("arv_initiation_ago"),
            dx_date=self.cleaned_data.get("arv_initiation_actual_date"),
        )

        if self.arv_initiation_date and self.dx_date:
            if self.arv_initiation_date < self.dx_date:
                field = self.which_field(
                    ago_field="arv_initiation_ago",
                    date_field="arv_initiation_actual_date",
                )
                raise forms.ValidationError(
                    {field: "Invalid. Cannot start ART before HIV diagnosis."}
                )

    def validate_viral_load(self):
        self.required_if(YES, field="has_vl", field_required="vl")
        self.required_if(YES, field="has_vl", field_required="vl_quantifier")
        self.required_if(YES, field="has_vl", field_required="vl_date")
        if self.cleaned_data.get("vl_date") and self.dx_date:
            if self.cleaned_data.get("vl_date") < self.dx_date:
                raise forms.ValidationError(
                    {"vl_date": "Invalid. Cannot be before HIV diagnosis."}
                )

    def validate_cd4(self):
        self.required_if(YES, field="has_cd4", field_required="cd4")
        self.required_if(YES, field="has_cd4", field_required="cd4_date")
        if self.cleaned_data.get("cd4_date") and self.dx_date:
            if self.cleaned_data.get("cd4_date") < self.dx_date:
                raise forms.ValidationError(
                    {"cd4_date": "Invalid. Cannot be before HIV diagnosis."}
                )

    @property
    def dx_date(self):
        if self.cleaned_data.get("dx_ago"):
            return estimated_date_from_ago(data=self.cleaned_data, ago_field="dx_ago")
        return self.cleaned_data.get("dx_date")

    @property
    def arv_initiation_date(self):
        if self.cleaned_data.get("arv_initiation_ago"):
            return estimated_date_from_ago(
                data=self.cleaned_data, ago_field="arv_initiation_ago"
            )
        return self.cleaned_data.get("arv_initiation_actual_date")

    def which_field(self, ago_field=None, date_field=None):
        if self.cleaned_data.get(ago_field):
            return ago_field
        if self.cleaned_data.get(date_field):
            return date_field
        return None


class HivInitialReviewForm(
    CrfModelFormMixin,
    ActionItemFormMixin,
    forms.ModelForm,
):
    form_validator_cls = HivInitialReviewFormValidator

    class Meta:
        model = HivInitialReview
        fields = "__all__"
