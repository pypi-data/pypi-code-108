from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    EncounterInpatient, Ethnicity, FractureLowerBody,
    HipDysfunctionAndOsteoarthritisOutcomeScoreForJointReplacementHoosjr, HospiceCareAmbulatory,
    OfficeVisit, OncAdministrativeSex, OutpatientConsultation, Payer, Race)


class ClinicalQualityMeasure56v9(ClinicalQualityMeasure):
    """
    Functional Status Assessment for Total Hip Replacement

    Description: Percentage of patients 18 years of age and older who received an elective primary
    total hip arthroplasty (THA) and completed a functional status assessment within 90 days prior
    to the surgery and in the 270-365 days after the surgery

    Definition: None

    Rationale: Total hip arthroplasties (THAs) are common surgical procedures that address hip pain
    and functional impairment, primarily caused by osteoarthritis. Although THA is an effective
    procedure for addressing osteoarthritis for many patients, some people, particularly those with
    more severe preoperative pain and impairment, do not experience the improvements in pain,
    function, and quality of life expected from the procedure (Beswick et al., 2012; Fortin et al.,
    1999; Tilbury et al., 2016). In 2010, providers performed 326,100 THAs, with 95 percent of them
    in patients age 45 and older (Wolford, Palso, & Bercovitz, 2015). Although THAs were introduced
    as a procedure for older adults, the percentage of patients age 55 to 64 (29 percent) who had a
    THA in 2010 exceeded the percentage of patients age 75 and older (26 percent) who had a THA
    (Wolford, Palso, & Bercovitz, 2015). Kurtz et al. (2009) projected that patients younger than
    65 would account for 52 percent of THAs by 2030. This growth in hip surgeries for patients
    younger than 65 is significant because these patients often require more expensive joint
    arthroplasties that will better withstand the wear caused by physical activity (Bozic et al.,
    2006).

    This measure evaluates whether patients complete a patient-reported functional status
    assessment (FSA) before and after a THA. Measuring functional status for patients undergoing
    THA permits longitudinal assessment - from the patient's perspective - of the impact of
    surgical intervention on pain, physical function, as well as health-related quality of life
    (Rothrock, 2010).

    Guidance: The same functional status assessment (FSA) instrument must be used for the initial
    and follow-up assessment.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms56v9
    """

    title = 'Functional Status Assessment for Total Hip Replacement'

    identifiers = ['CMS56v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'American Association of Orthopaedic Surgeons, the American Joint Replacement Registry, The Hip Society, The Knee Society, & the American Association of Hip and Knee Surgeons. (2015). Patient-reported outcomes summit for total joint arthroplasty report. Retrieved from http://www.aahks.org/wp-content/uploads/2018/08/comment-letter-pro-summit-09082015.pdf',
        'Beswick, A. D., Wylde, V., Gooberman-Hill, R., et al. (2012). What proportion of patients report long-term pain after total hip or knee replacement for osteoarthritis? A systematic review of prospective studies in unselected patients. British Medical Journal Open, 2(1), 1-12.',
        'Bozic, K. J., Morsehed, S., Silverstein, M. D., et al. (2006). Use of cost-effectiveness analysis to evaluate new technologies in orthopaedics: The case of alternative bearing surfaces in total hip arthroplasty. Journal of Bone and Joint Surgery, American Volume, 88(4), 706-714.',
        'Fortin, P. R., Clarke, A. E., Joseph, L., et al. (1999). Outcomes of total hip and knee replacement preoperative functional status predicts outcomes at six months after surgery. American College of Rheumatology, 42(8), 1722-1728.',
        'Kurtz, S. M., Lau, E., Ong, K., et al. (2009). Future young patient demand for primary and revision joint arthroplasty: National projections from 2010 to 2030. Clinical Orthopaedics and Related Research, 467(10), 2606-2612.',
        'Rothrock, N. E., Hays, R. D., Spritzer, K., et al. (2010). Relative to the general U.S. population, chronic diseases are associated with poorer health-related quality of life as measured by the Patient-Reported Outcomes Measurement Information System (PROMIS). Journal of Clinical Epidemiology, 63(11), 1195-1204.',
        'Tilbury, C., Haanstra, T. M., Leichtenberg, C. S., et al. (2016). Unfulfilled expectations after total hip and knee arthroplasty surgery: There is a need for better preoperative patient information and education. Journal of Arthroplasty, 31(10), 2136-2145.',
        'Wolford, M. L., Palso, K., & Bercovitz, A. (2015, February). Hospitalization for total hip replacement among inpatients aged 45 and over: United States, 2000-2010. NCHS Data Brief No. 186. Hyattsville, MD: National Center for Health Statistics.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients 19 years of age and older who had a primary total hip
        arthroplasty (THA) in the year prior to the measurement period and who had an outpatient
        encounter during the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Patients with two or more fractures indicating trauma at the time of the total
        hip arthroplasty or patients with severe cognitive impairment that overlaps the measurement
        period.

        Exclude patients whose hospice care overlaps the measurement period.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients with patient-reported functional status assessment  results (i.e.,
        Veterans RAND 12-item health survey [VR-12], Patient-Reported Outcomes Measurement
        Information System [PROMIS]-10-Global Health, Hip Disability and Osteoarthritis Outcome
        Score [HOOS], HOOS Jr.) in the 90 days prior to or on the day of the primary THA procedure,
        and in the 270 - 365 days after the THA procedure

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: While there is no clinical guideline recommending that clinicians
        assess patients who are undergoing total hip replacements using patient-reported outcomes
        of function and pain, several clinical specialty societies support the use of a general
        health questionnaire and a disease-specific questionnaire for these patients. In
        particular, they recommend the Veterans RAND 12-item health survey (VR-12) or the Patient-
        Reported Outcomes Measurement Information System [PROMIS]-10-Global as the general health
        questionnaire and the Hip Disability and Osteoarthritis Outcome Score [HOOS], Jr. as the
        disease-specific questionnaire (American Association of Orthopaedic Surgeons, the American
        Joint Replacement Registry, The Hip Society, The Knee Society, & the American Association
        of Hip and Knee Surgeons, 2015).
        """
        pass
