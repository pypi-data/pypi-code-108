# flake8: noqa
from canvas_workflow_kit import events
from canvas_workflow_kit.protocol import ClinicalQualityMeasure
from canvas_workflow_kit.recommendation import ImmunizationRecommendation  # noqa

# context + prompting is huge win (for dignity); e.g. had this vaccine 11 months ago, he's now due
# for pneuomax 23; prevent need to look back in the chart; more trust == more utility
#


class PneuomoniaVaccinationStatusForOlderAdultsProtocol(ClinicalQualityMeasure):
    """
    https://ecqi.healthit.gov/ep/ecqms-2018-performance-period/pneumococcal-vaccination-status-older-adults

    Description: Percentage of patients 65 years of age and older who have ever received a
    pneumococcal vaccine.

    Initial population and denominator: Patients 65 years of age and older with a visit during the
    measurement period.

    Numerator: Patients who have ever received a pneumococcal vaccination.

    Guidance: It is recommended that patients 65 years of age or older receive one pneumococcal
    vaccination in their lifetime.

    The CDC flowchart specifies additional guidance used for narrative generation:

        https://www.cdc.gov/vaccines/vpd/pneumo/downloads/pneumo-vaccine-timing.pdf
    """

    # this protocol was created before an overhaul and needs finishing to work
    @classmethod
    def enabled(cls):
        return False

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    # where does the action go? in this case will it be a Recommendation?

    # request from clientside JS, e.g. for preventative services; figure out a way to serialize and
    # ship to client; include command & parameters (e.g. immunize, CVX 33)
    # need URLs/views for this

    # 'conceptually a protocol is a recommendation'
    # 'not enough for us to just report on whether you've had one of these vaccines; we'll give you
    # specific advice & tell you why'

    # ontologies to use? e.g. CVX 33/CVX 133
    # andrew: use CVX
    # look up value set for these; these will come from VSAC; in cases where there isn't one we can
    # create our own with the same structure
    # pneumococcal_vaccines = ['PCV13', 'PPSV23']
    pneumococcal_vaccines = ['CVX33', 'CVX133']

    # TODO Recommendations can have >1 action (more than one way to resolve a Recommendation)
    # TODO Add Predicate class for rich "debugging"?
    # TODO action-oriented 'tell me what to do view' vs. inverted 'tell me why' view
    # TODO look through dignity pcp/interop/customers/dignityhealth/...
    # https://github.com/canvas-medical/pcp/tree/master/pcp/interop/customers/dignityhealth/allscripts_touchworks/automata
    # TODO soup to nuts on 'kiddo' example

    @staticmethod
    def condition_names(conditions):
        return ', '.join(condition.name for condition in conditions)

    def recommendations(self):
        pvc13 = self.has_vaccine('PVC13')
        ppsv23 = self.has_vaccine('PPSV23')

        pvc13_age = pvc13.age_at_administration
        ppsv23_age = ppsv23.age_at_administration

        first_name = self.patient.first_name

        if pvc13_age >= 65 and ppsv23_age >= 65:
            return [{
                'type': 'up-to-date',
                'narrative': (
                    f'{first_name} received both PVC13 and PPSV23 after the age of 65 (they '
                    f'received PVC13 at {pvc13_age} and PPSV23 at {ppsv23_age}).')
            }]

        narratives = []

        compromised_conditions = (self.is_asplenic_or_immunocompromised() +
                                  self.is_immunocompetent_with_cochlear_implant_or_csf())
        competent_conditions = self.is_immunocompetent_with_condition()

        compromised_names = self.condition_names(compromised_conditions)
        competent_names = self.condition_names(competent_conditions)  # noqa

        # TODO this logic may have missing edge cases; needs to be verified with a test matrix that
        # follows the CDC flowcharts
        if compromised_conditions and not pvc13:
            narratives.append({
                'type': 'due',
                'action': 'vaccination',
                'code': 'PVC13',
                'narrative': (
                    'Patients 65 years or older with certain medical conditions should be '
                    'vaccinated with PVC13 only if they have not had a prior PVC13 vaccination. '
                    f'{first_name} has a qualifying condition ({compromised_names}) and has not '
                    'previously been vaccinated with PVC13.')
            })
        elif pvc13_age < 65:
            narratives.append({
                'type': 'due',
                'action': 'vaccination',
                'code': 'PVC13',
                'narrative': (
                    'Patients 65 years or older should receive a PVC13 vaccination regardless of '
                    'prior PVC13 vaccination status.')
            })

        # "PCV13 and PPSV23 should not be administered during the same office visit."
        # "When both are indicated, PCV13 should be given before PPSV23 whenever possible."
        if any(narrative.get('code') == 'PVC13' for narrative in narratives):
            return narratives

        if not ppsv23:
            if compromised_conditions and pvc13.administered.within('8 weeks'):
                narratives.append({
                    'type': 'up-to-date',
                    'narrative': (
                        f'{first_name} received PVC13 within the last 8 weeks. Because of '
                        f'their qualifying condition(s) ({compromised_names}) they must wait '
                        f"until {pvc13.administered.add('8 weeks')} to receive PPSV23.")
                })
            elif pvc13.administered.within('1 year'):
                narratives.append({
                    'type': 'up-to-date',
                    'narrative': (
                        f'{first_name} received PVC13 within the last year. They must wait '
                        f"until {pvc13.administered.add('1 year')} to receive PPSV23.")
                })
            else:
                narratives.append({
                    'type': 'due',
                    'action': 'vaccination',
                    'code': 'PPSV23',
                    'narrative': ('Patients 65 years or older should receive a PPSV23 vaccination '
                                  'regardless of prior PPSV23 vaccination status.')
                })
        elif ppsv23_age < 65:
            if ((compromised_conditions or competent_conditions) and
                    ppsv23.administered.within('5 years')):
                narratives.append({
                    'type': 'up-to-date',
                    'narrative': (
                        f'{first_name} received PPSV23 before they turned 65 but within the last '
                        f"5 years. They must wait until {ppsv23.administered.add('5 years')} to "
                        'receive PPSV23.')
                })

        return narratives

    def is_immunocompetent_with_condition(self):
        # TODO replace these with value sets (if available) or arrays
        return self.patient.has_any_condition([
            'alcoholism',
            # "Including congestive heart failure and cardiomyopathies"
            'chronic heart disease',
            'chronic liver disease',
            # "Including chronic obstructive pulmonary disease, emphysema, and asthma"
            'chronic lung disease',
            'smoker',
            'diabetes mellitus',
        ])

    def is_immunocompetent_with_cochlear_implant_or_csf(self):
        return self.patient.has_any_condition([
            'cochlear implant',
            'cerebrospinal fluid leak',
        ])

    def is_asplenic_or_immunocompromised(self):
        return self.patient.has_any_condition([
            # asplenias
            'congenital or acquired asplenia',
            'sickle cell disease',
            'other hemoglobinopathies',

            # immunocompromised
            'chronic renal failure',
            # "Includes B- (humoral) or T-lymphocyte deficiency, complement deficiencies
            #  (particularly C1, C2, C3, and C4 deficiencies), and phagocytic disorders (excluding
            #  chronic granulomatous disease)"
            'congenital or acquired immunodeficiencies',
            'generalized malignancy',
            'HIV infection',
            'Hodgkin disease',
            # "Diseases requiring treatment with immunosuppressive drugs, including long-term
            #  systemic corticosteroids and radiation therapy"
            'latrogenic immunosupression',
            'Leukemia',
            'multiple myeloma',
            'nephrotic syndrome',
            'solid organ transplant',
        ])

    # it would be great to be able to specify filters here in the same way that the Django ORM does
    # to avoid writing one test method for a single patient and one for reporting statistics on a
    # number of patients... 'point of care vs. reporting'
    #
    # for reporting also need to handle age during timeframe vs. age at report generation time
    def in_denominator(self):
        # TODO need to exclude patients on hospice care during the timeframe
        return self.patient.age >= 65 and self.patient.has_visit_within(self.timeframe)

    # for reporting need to check if they had pneumococcal_vaccines before the end of the reporting
    # period
    def in_numerator(self):
        return self.patient.vaccines_within(self.timeframe, self.pneumococcal_vaccines)
