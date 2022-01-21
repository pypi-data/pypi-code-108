# type: ignore
from typing import cast

from canvas_workflow_kit import events, settings
from canvas_workflow_kit.protocol import (
    STATUS_DUE,
    STATUS_SATISFIED,
    ClinicalQualityMeasure,
    ExternallyAwareClinicalQualityMeasure,
    ProtocolResult
)


class CustomerScanHCCSuspectAlert(ExternallyAwareClinicalQualityMeasure, ClinicalQualityMeasure):
    """
    SCAN specific protocol that displays Suspect HCC data, if the patient has any.
    There is currently no action to take, so no recommendations are made.
    """

    class Meta:
        title = 'SCAN: HCC Suspect Alert'

        version = '2020-09-04v1'

        description = (
            'SCAN specific protocol that displays Suspect HCC data, if the patient has any. '
            'There is currently no action to take, so no recommendations are made.')
        information = 'https://docs.google.com/document/d/1NW4b3OT_yPeZy_oIKt_DCCeQ0egDaWFE/edit'

        identifiers = ['CustomerScanHCCSuspectAlertV1']

        types = ['CQM']

        responds_to_event_types = [
            events.HEALTH_MAINTENANCE,
        ]

        authors = [
            'SCAN',
        ]

        compute_on_change_types = [
            ClinicalQualityMeasure.CHANGE_PROTOCOL_OVERRIDE,
            ClinicalQualityMeasure.CHANGE_SUSPECT_HCC,
        ]

        funding_source = 'SCAN'

        references = ['Written by SCAN']

    @classmethod
    def enabled(cls) -> bool:
        return cast(bool, settings.IS_HEALTHCHEC)

    def in_initial_population(self) -> bool:
        return True

    def in_denominator(self) -> bool:
        """
        Denominator: Equals Initial Population

        Exclusions: None

        Exceptions: None
        """

        return self.in_initial_population()

    def in_numerator(self) -> bool:
        """
        Patient is in the numerator if they have no suspect hccs.
        """

        return len(self.patient.suspect_hccs) == 0

    def craft_satisfied_result(self):
        """
        Satisfied if in numerator. (See numerator description)
        """
        result = ProtocolResult()

        result.due_in = -1
        result.status = STATUS_SATISFIED

        result.add_narrative(f'{self.patient.first_name} does not have any Suspect HCC data.')

        return result

    def craft_unsatisfied_result(self):
        """
        Unsatisfied if not in the numerator.
        """
        result = ProtocolResult()

        result.due_in = -1
        result.status = STATUS_DUE

        previous_conditions = []
        hccs_implied_by_clinical_data = []

        for suspect_hcc in self.patient.suspect_hccs:
            if suspect_hcc['kind'] == 'previous_condition':
                previous_conditions.append(suspect_hcc)
            elif suspect_hcc['kind'] == 'implied_by_clinical_data':
                hccs_implied_by_clinical_data.append(suspect_hcc)

        if previous_conditions:
            previous_conditions_narrative = ('─────────────────────\n'
                                             'Previous conditions for consideration:\n')
            for suspect_hcc in previous_conditions:
                previous_conditions_narrative += f"    {suspect_hcc['previousCondition']}\n"
            result.add_narrative(previous_conditions_narrative)

        if hccs_implied_by_clinical_data:
            hccs_narrative = ('─────────────────────\nAI suspects for consideration:\n')
            for suspect_hcc in hccs_implied_by_clinical_data:
                hccs_narrative += f"\n    {suspect_hcc['hccDescription']}\n"
                for reason in suspect_hcc['reasons']:
                    hccs_narrative += f'        • {reason}\n'
            result.add_narrative(hccs_narrative)

        return result
