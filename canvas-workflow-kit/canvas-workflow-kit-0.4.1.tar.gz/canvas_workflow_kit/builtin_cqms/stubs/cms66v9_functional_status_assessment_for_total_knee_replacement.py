from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    EncounterInpatient, Ethnicity, FractureLowerBody, HospiceCareAmbulatory,
    KneeInjuryAndOsteoarthritisOutcomeScoreForJointReplacementKoosjr, OfficeVisit,
    OncAdministrativeSex, OutpatientConsultation, Payer, Race)


class ClinicalQualityMeasure66v9(ClinicalQualityMeasure):
    """
    Functional Status Assessment for Total Knee Replacement

    Description: Percentage of patients 18 years of age and older who received an elective primary
    total knee arthroplasty (TKA) and completed a functional status assessment within 90 days prior
    to the surgery and in the 270-365 days after the surgery

    Definition: None

    Rationale: Total knee arthroplasties (TKAs) are common surgical procedures for addressing knee
    pain and functional impairment, primarily caused by osteoarthritis. From 2008 to 2010, TKAs
    were the most common procedure for adults age 45 and older. From 2000 to 2010, physicians
    performed 5.2 million TKAs, with 693,400 procedures performed in 2010 alone (Williams, Wolford,
    & Bercovitz, 2015). Although TKAs were introduced as a procedure for older adults, the mean age
    of patients undergoing TKA is decreasing. In 2010, the mean age for those undergoing TKA was
    66.2, a 3.9 percent decrease from 68.9 in 2000. Kurtz et al. (2009) projected that patients
    younger than 65 would account for 55 percent of TKAs by 2030. This growth in knee surgeries for
    younger patients is significant because they often require more expensive joint arthroplasties
    that will better withstand wear caused by physical activity (Bozic et al., 2006).

    This measure evaluates whether patients complete a patient-reported functional status
    assessment (FSA) before and after a TKA. Measuring functional status for patients undergoing
    total knee replacement permits longitudinal assessment - from the patient's perspective - of
    the impact of surgical intervention on pain, physical function, as well as health-related
    quality of life (Rothrock et al., 2010).

    Guidance: The same functional status assessment (FSA) instrument must be used for the initial
    and follow-up assessment.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms66v9
    """

    title = 'Functional Status Assessment for Total Knee Replacement'

    identifiers = ['CMS66v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'American Association of Orthopaedic Surgeons, the American Joint Replacement Registry, The Hip Society, The Knee Society, & the American Association of Hip and Knee Surgeons. (2015). Patient-reported outcomes summit for total joint arthroplasty report. Retrieved from http://www.aahks.org/wp-content/uploads/2018/08/comment-letter-pro-summit-09082015.pdf',
        'Bozic, K. J., Morsehed, S., Silverstein, M. D., et al. (2006). Use of cost-effectiveness analysis to evaluate new technologies in orthopaedics: The case of alternative bearing surfaces in total hip arthroplasty. Journal of Bone and Joint Surgery, American Volume, 88(4), 706-714.',
        'Kurtz, S. M., Lau, E., Ong, K., et al. (2009). Future young patient demand for primary and revision joint arthroplasty: National projections from 2010 to 2030. Clinical Orthopaedics and Related Research, 467(10), 2606-2612.',
        'Rothrock, N. E., Hays, R. D., Spritzer, K., et al. (2010). Relative to the general U.S. population, chronic diseases are associated with poorer health-related quality of life as measured by the Patient-Reported Outcomes Measurement Information System (PROMIS). Journal of Clinical Epidemiology, 63(11), 1195-1204.',
        'Williams, S. N., Wolford, M. L., & Bercovitz, A. (2015). Hospitalization for total knee replacement among inpatients aged 45 and over: United States, 2000-2010. NCHS Data Brief No. 210. Hyattsville, MD: National Center for Health Statistics.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients 19 years of age and older who had a primary total knee
        arthroplasty (TKA) in the year prior to the measurement period and who had an outpatient
        encounter during the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Patients with two or more fractures indicating trauma at the time of the total
        knee arthroplasty or patients with severe cognitive impairment that overlaps the
        measurement period.

        Exclude patients whose hospice care overlaps the measurement period.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients with patient-reported functional status assessment results (i.e.,
        Veterans RAND 12-item health survey [VR-12], Patient-Reported Outcomes Measurement
        Information System [PROMIS]-10 Global Health, Knee Injury and Osteoarthritis Outcome Score
        [KOOS], KOOS Jr.) in the 90 days prior to or on the day of the primary TKA procedure, and
        in the 270 - 365 days after the TKA procedure

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: While there is no clinical guideline recommending that clinicians
        assess patients who are undergoing total knee replacements using patient-reported outcomes
        of function and pain, several clinical specialty societies support the use of a general
        health questionnaire and a disease-specific questionnaire for these patients. In
        particular, they recommend the Veterans RAND 12-item health survey (VR-12) or the Patient-
        Reported Outcomes Measurement Information System [PROMIS]-10-Global as the general health
        questionnaire and the Knee Injury and Osteoarthritis Outcome Score [KOOS], Jr. as the
        disease-specific questionnaire (American Association of Orthopaedic Surgeons, the American
        Joint Replacement Registry, The Hip Society, The Knee Society, & the American Association
        of Hip and Knee Surgeons, 2015).
        """
        pass
