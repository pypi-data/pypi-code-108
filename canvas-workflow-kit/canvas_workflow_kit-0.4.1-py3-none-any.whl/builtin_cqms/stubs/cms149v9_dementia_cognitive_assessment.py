from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    BehavioralneuropsychAssessment, CareServicesInLongTermResidentialFacility, CognitiveAssessment,
    DementiaMentalDegenerations, Ethnicity, HomeHealthcareServices, NursingFacilityVisit,
    OccupationalTherapyEvaluation, OfficeVisit, OncAdministrativeSex, OutpatientConsultation,
    PatientProviderInteraction, Payer, PsychVisitDiagnosticEvaluation, PsychVisitPsychotherapy,
    Race, StandardizedToolsForAssessmentOfCognition)


class ClinicalQualityMeasure149v9(ClinicalQualityMeasure):
    """
    Dementia: Cognitive Assessment

    Description: Percentage of patients, regardless of age, with a diagnosis of dementia for whom
    an assessment of cognition is performed and the results reviewed at least once within a
    12-month period

    Definition: Cognition can be assessed by the clinician during the patient's clinical history.
    Cognition can also be assessed by direct examination of the patient using one of a number of
    instruments, including several originally developed and validated for screening purposes. This
    can also include, where appropriate, administration to a knowledgeable informant. Examples
    include, but are not limited to:
    -Blessed Orientation-Memory-Concentration Test (BOMC)
    -Montreal Cognitive Assessment (MoCA)
    -St. Louis University Mental Status Examination (SLUMS)
    -Mini-Mental State Examination (MMSE) [Note: The MMSE has not been well validated for non-
    Alzheimer's dementias]
    -Short Informant Questionnaire on Cognitive Decline in the Elderly (IQCODE)
    -Ascertain Dementia 8 (AD8) Questionnaire
    -Minimum Data Set (MDS) Brief Interview of Mental Status (BIMS) [Note: Validated for use with
    nursing home patients only]
    -Formal neuropsychological evaluation
    -Mini-Cog

    Rationale: An estimated 5.8 million of adults in the US were living with dementia in 2019.
    Dementia is often characterized by the gradual onset and continuing cognitive decline in one or
    more domains including memory, communication and language, ability to focus or pay attention,
    reasoning and judgment and visual perception (Alzheimer’s Association, 2019). Cognitive
    deterioration represents a major source of morbidity and mortality and poses a significant
    burden on affected individuals and their caregivers (Daviglus et al., 2010). Although cognitive
    deterioration follows a different course depending on the type of dementia, significant rates
    of decline have been reported. For example, one study found that the annual rate of decline for
    Alzheimer's disease patients was more than four times that of older adults with no cognitive
    impairment (Wilson et al., 2010). Nevertheless, measurable cognitive abilities remain
    throughout the course of dementia (American Psychiatric Association, 2007). Initial and ongoing
    assessments of cognition are fundamental to the proper management of patients with dementia.
    These assessments serve as the basis for identifying treatment goals, developing a treatment
    plan, monitoring the effects of treatment, and modifying treatment as appropriate.

    Guidance: Use of a standardized tool or instrument to assess cognition other than those listed
    will meet numerator performance. Standardized tools can be mapped to the concept "Intervention,
    Performed": "Cognitive Assessment" included in the numerator logic below.

    The requirement of two or more visits is to establish that the eligible professional or
    eligible clinician has an existing relationship with the patient.

    In recognition of the growing use of integrated and team-based care, the diagnosis of dementia
    and the assessment of cognitive function need not be performed by the same provider or
    clinician.

    The DSM-5 has replaced the term dementia with major neurocognitive disorder and mild
    neurocognitive disorder. For the purposes of this measure, the terms are equivalent.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms149v9
    """

    title = 'Dementia: Cognitive Assessment'

    identifiers = ['CMS149v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'Alzheimer’s Association. (2019). 2019 Alzheimer’s Disease Facts and Figures. Alzheimer’s & Dementia, 15(3), 321-387. Retrieved from https://alz.org/media/Documents/alzheimers-facts-and-figures-2019-r.pdf',
        'American Psychiatric Association, Work Group on Alzheimer’s Disease and Other Dementias. (2007). Practice Guideline for the Treatment of Patients with Alzheimer’s Disease and Other Dementias. Retrieved from https://psychiatryonline.org/pb/assets/raw/sitewide/practice_guidelines/guidelines/alzheimers.pdf',
        'American Psychiatric Association. (2016). Practice guideline on the use of antipsychotics to treat agitation or psychosis in patients with dementia. Retrieved from https://psychiatryonline.org/doi/pdf/10.1176/appi.books.9780890426807',
        'California Department of Public Health. (2017). California guidelines for Alzheimer’s disease management, 2017. Retrieved from https://www.cdph.ca.gov/Programs/CCDPHP/DCDIC/CDCB/CDPH%20Document%20Library/Alzheimers\'%20Disease%20Program/ALZ-CareGuidelines.pdf',
        'Daviglus M.L., Bell, C.C., Berrettini, W., Bowen, P.E., Connolly, E.S., Cox, N.J.,…Trevisan, M. (2010). National Institutes of Health State-of-the-Science Conference Statement: Preventing Alzheimer’s Disease and Cognitive Decline. NIH Consensus and State-of-the-Science Statements, 27(4), 1-24. Retrieved from https://consensus.nih.gov/2010/alzstatement.htm',
        'Fazio, S., Pace, D., Maslow, K., Zimmerman, S., & Kallmyer, B. (2018). Alzheimer’s Association Dementia Care Practice Recommendations. The Gerontologist, 58(S1), S1-S9. [Supplemental material]. Retrieved from the Alzheimer’s Association website: https://academic.oup.com/gerontologist/article/58/suppl_1/S1/4816759',
        'U.S. Department of Health and Human Services, Assistant Secretary for Planning and Evaluation, Office of Disability, Aging and Long-Term Care Policy. (2016). Examining models of dementia care: Final report. (ASPE Final Report No. 0212704.017.000.001). Retrieved from https://aspe.hhs.gov/system/files/pdf/257216/ExamDCMod.pdf',
        'Wilson, R. S., Aggarwal, N. T., Barnes, L. L., Mendes de Leon, C.F., Herbert, L.E., & Evans, D.A. (2010). Cognitive decline in incident Alzheimer disease in a community population. Neurology, 74(12), 951-955.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients, regardless of age, with a diagnosis of dementia
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: None

        Exceptions: Documentation of patient reason(s) for not assessing cognition
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients for whom an assessment of cognition is performed and the results
        reviewed at least once within a 12-month period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: Ongoing assessment includes periodic monitoring of the development
        and evolution of cognitive and noncognitive psychiatric symptoms and their response to
        intervention (Category I). Both cognitive and noncognitive neuropsychiatric and behavioral
        symptoms of dementia tend to evolve over time, so regular monitoring allows detection of
        new symptoms and adaptation of treatment strategies to current needs... Cognitive symptoms
        that almost always require assessment include impairments in memory, executive function,
        language, judgment, and spatial abilities. It is often helpful to track cognitive status
        with a structured simple examination (American Psychiatric Association, 2007).

        The American Psychiatric Association recommends that patients with dementia be assessed for
        the type, frequency, severity, pattern, and timing of symptoms (Category 1C). Quantitative
        measures provide a structured replicable way to document the patient's baseline symptoms
        and determine which symptoms (if any) should be the target of intervention based on factors
        such as frequency of occurrence, magnitude, potential for associated harm to the patient or
        others, and associated distress to the patient. The exact frequency at which measures are
        warranted will depend on clinical circumstances. However, use of quantitative measures as
        treatment proceeds allows more precise tracking of whether nonpharmacological and
        pharmacological treatments are having their intended effect or whether a shift in the
        treatment plan is needed (American Psychiatric Association, 2016).

        Conduct and document an assessment and monitor changes in cognitive status using a reliable
        and valid instrument, e.g., MoCA (Montreal Cognitive Assessment), AD8 (Ascertian Dementia
        8) or other tool. Cognitive status should be reassessed periodically to identify sudden
        changes, as well as to monitor the potential beneficial or harmful effects of environmental
        changes (including safety, care needs, and abuse and/or neglect), specific medications
        (both prescription and non-prescription, for appropriate use and contraindications), or
        other interventions. Proper assessment requires the use of a standardized, objective
        instrument that is relatively easy to use, reliable (with less variability between
        different assessors), and valid (results that would be similar to gold-standard
        evaluations) (California Department of Public Health, 2017).

        Recommendation: Perform regular, comprehensive person-centered assessments and timely
        interim assessments.
        Assessments, conducted at least every 6 months, should prioritize issues that help the
        person with dementia to live fully. These include assessments of the individual and care
        partner’s relationships and subjective experience and assessment of cognition, behavior,
        and function, using reliable and valid tools. Assessment is ongoing and dynamic, combining
        nomothetic (norm based) and idiographic (individualized) approaches (Fazio, Pace, Maslow,
        Zimmerman, & Kallmyer, 2018)

        Recommendation: Assess cognitive status, functional abilities, behavioral and psychological
        symptoms of dementia, medical status, living environment, and safety. Reassess regularly
        and when there is a significant change in condition (U.S. Department of Health and Human
        Services, 2016).
        """
        pass
