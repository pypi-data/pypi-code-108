from edc_adverse_event.form_validator_mixins import (
    RequiresDeathReportFormValidatorMixin,
)
from edc_consent.constants import CONSENT_WITHDRAWAL
from edc_constants.constants import DEAD, OTHER
from edc_form_validators import FormValidator
from edc_ltfu.constants import LOST_TO_FOLLOWUP
from edc_ltfu.forms import LtfuFormValidatorMixin
from edc_ltfu.utils import get_ltfu_model_name
from edc_offstudy.constants import OTHER_RX_DISCONTINUATION


class EndOfStudyFormValidator(
    LtfuFormValidatorMixin, RequiresDeathReportFormValidatorMixin, FormValidator
):

    offschedule_reason_field = "offschedule_reason"
    loss_to_followup_model = get_ltfu_model_name()
    loss_to_followup_date_field = "ltfu_date"
    loss_to_followup_reason = LOST_TO_FOLLOWUP

    def clean(self):

        self.validate_ltfu()

        self.validate_death_report_if_deceased()

        if self.cleaned_data.get("offschedule_reason"):
            if self.cleaned_data.get("offschedule_reason").name != OTHER:
                self.validate_other_specify(
                    field="offschedule_reason",
                    other_specify_field="other_offschedule_reason",
                    other_stored_value=OTHER_RX_DISCONTINUATION,
                )

            if self.cleaned_data.get("offschedule_reason").name != OTHER_RX_DISCONTINUATION:
                self.validate_other_specify(
                    field="offschedule_reason",
                    other_specify_field="other_offschedule_reason",
                    other_stored_value=OTHER,
                )

        self.required_if(DEAD, field="offschedule_reason", field_required="death_date")

        self.required_if(
            CONSENT_WITHDRAWAL,
            field="offschedule_reason",
            field_required="consent_withdrawal_reason",
        )

        self.required_if(
            "included_in_error",
            field="offschedule_reason",
            field_required="included_in_error",
        )

        self.required_if(
            "included_in_error",
            field="offschedule_reason",
            field_required="included_in_error_date",
        )
