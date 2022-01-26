from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    EncounterInpatient, Ethnicity, HeartFailure, HospiceCareAmbulatory, OfficeVisit,
    OncAdministrativeSex, Payer, Race)


class ClinicalQualityMeasure90v10(ClinicalQualityMeasure):
    """
    Functional Status Assessments for Congestive Heart Failure

    Description: Percentage of patients 18 years of age and older with congestive heart failure who
    completed initial and follow-up patient-reported functional status assessments

    Definition: None

    Rationale: Patients living with congestive heart failure (CHF) often have poor functional
    status and health-related quality of life, which declines as the disease progresses (Allen et
    al., 2012). In addition, their care is often complicated by multiple comorbidities. To assist
    in managing these complex patients, the American College of Cardiology Foundation and American
    Heart Association recommend collecting initial and repeat assessments of a patient's function
    and ability to complete desired activities of daily living (Hunt et al., 2009). The American
    Heart Association has also released scientific statements emphasizing the collection of
    patient-reported health status (for example, functional limitations, symptom burden, quality of
    life) from CHF patients as an important means of establishing a dynamic conversation between
    patient and provider regarding care goals and the patient's priorities (Allen et al., 2012;
    Rumsfeld et al., 2013).

    Guidance: Initial functional status assessment (FSA) and encounter: The initial FSA is the
    first FSA that occurs two weeks before or during the first encounter in the first 185 days of
    the measurement year.

    Follow-up FSA: The follow-up FSA must be completed at least 30 days but no more than 180 days
    after the initial FSA.

    The same FSA instrument must be used for the initial and follow-up assessment.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms90v10
    """

    title = 'Functional Status Assessments for Congestive Heart Failure'

    identifiers = ['CMS90v10']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'Allen, L. A., Stevenson, L. W., Grady, K. L., et al. (2012). Decision making in advanced heart failure: A scientific statement from the American Heart Association. Circulation, 125(15), 1928-1952. doi: 10.1161/CIR.0b013e31824f2173',
        'American College of Cardiology Foundation & American Heart Association. (2013). Guideline for the management of heart failure: A report of the American College of Cardiology Foundation/American Heart Association Task Force on Practice Guidelines. Circulation, 128(16), e240-e327. doi: 10.1161/CIR.0b013e31829e8776',
        'Hunt, S. A., Abraham, W. T., Chin, M. H., et al. (2009). 2009 focused update incorporated into the ACC/AHA 2005 guidelines for the diagnosis and management of heart failure in adults. Circulation, 119(14), e391-e479. doi: 10.1161/CIRCULATIONAHA.109.192065',
        'Rumsfeld, J. S., Alexander, K. P., Goff, D. C., et al. (2013). Cardiovascular health: The importance of measuring patient-reported health status: A scientific statement from the American Heart Association. Circulation, 127(22), 2233-2249. doi: 10.1161/CIR.0b013e3182949a2e',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients 18 years of age and older who had two outpatient encounters
        during the measurement year and a diagnosis of congestive heart failure
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Exclude patients with severe cognitive impairment that overlaps the measurement
        period.

        Exclude patients whose hospice care overlaps the measurement period.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients with patient-reported functional status assessment  results (i.e.,
        Veterans RAND 12-item health survey [VR-12]; VR-36; Kansas City Cardiomyopathy
        Questionnaire [KCCQ]; KCCQ-12; Minnesota Living with Heart Failure Questionnaire [MLHFQ];
        Patient-Reported Outcomes Measurement Information System [PROMIS]-10 Global Health,
        PROMIS-29) present in the EHR two weeks before or during the initial FSA encounter and
        results for the follow-up FSA at least 30 days but no more than 180 days after the initial
        FSA

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: American College of Cardiology Foundation and American Heart
        Association (2013): While this guideline does not explicitly recommend the use of patient-
        reported functional status or quality of life assessments (such as the Kansas City
        Cardiomyopathy Questionnaire or Minnesota Living with Heart Failure Questionnaire), it does
        “refer to meaningful survival a state in which HRQOL [health-related quality of life] is
        satisfactory to the patient.” The guideline also includes quality of life assessments in
        its description of a detailed plan of care for patients with chronic heart failure.
        """
        pass
