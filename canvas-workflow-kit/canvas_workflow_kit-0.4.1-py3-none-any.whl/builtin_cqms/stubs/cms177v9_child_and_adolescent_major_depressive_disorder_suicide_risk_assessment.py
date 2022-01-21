from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    Ethnicity, GroupPsychotherapy, OfficeVisit, OncAdministrativeSex, OutpatientConsultation,
    Payer, PsychVisitDiagnosticEvaluation, PsychVisitFamilyPsychotherapy, PsychVisitPsychotherapy,
    Psychoanalysis, Race, TelehealthServices)


class ClinicalQualityMeasure177v9(ClinicalQualityMeasure):
    """
    Child and Adolescent Major Depressive Disorder (MDD): Suicide Risk Assessment

    Description: Percentage of patient visits for those patients aged 6 through 17 years with a
    diagnosis of major depressive disorder with an assessment for suicide risk

    Definition: Numerator Definition: The specific type and magnitude of the suicide risk
    assessment is intended to be at the discretion of the individual clinician and should be
    specific to the needs of the patient. At a minimum, suicide risk assessment should evaluate:
    1. Risk (e.g., age, sex, stressors, comorbid conditions, hopelessness, impulsivity) and
    protective factors (e.g., religious belief, concern not to hurt family) that may influence the
    desire to attempt suicide.
    2. Current severity of suicidality.
    3. Most severe point of suicidality in episode and lifetime.

    Low burden tools to track suicidal ideation and behavior such as the Columbia-Suicidal Severity
    Rating Scale can also be used. Because no validated assessment tool or instrument fully meets
    the aforementioned requirements for the suicide risk assessment, individual tools or
    instruments have not been explicitly included in coding.

    Rationale: Research has shown that patients with major depressive disorder are at a high risk
    for suicide attempts and completion - among the most significant and devastating sequelae of
    the disease. Suicide risk is a critical consideration in children and adolescents with MDD and
    an important aspect of care that should be assessed at each visit and subsequently managed to
    minimize that risk. Additionally, the importance of the assessments is underscored by research
    (Louma, Martin, & Pearson, 2002) that indicates that many individuals who die by suicide do
    make contact with primary care providers and mental health services beforehand. More
    specifically, approximately 15% of suicide victims aged 35 years or younger had seen a mental
    health professional within 1 month of suicide while approximately 23% had seen a primary care
    provider within 1 month of suicide.

    Guidance: This eCQM is an episode-based measure. A suicide risk assessment should be performed
    at every visit for major depressive disorder during the measurement period.

    In recognition of the growing use of integrated and team-based care, the diagnosis of
    depression and the assessment for suicide risk need not be performed by the same provider or
    clinician.

    Suicide risk assessments completed via telehealth services can also meet numerator performance.

    This measure is an episode-of-care measure; the level of analysis for this measure is every
    visit for major depressive disorder during the measurement period. For example, at every visit
    for MDD, the patient should have a suicide risk assessment.

    Use of a standardized tool(s) or instrument(s) to assess suicide risk will meet numerator
    performance, so long as the minimum criteria noted above is evaluated. Standardized tools can
    be mapped to the concept "Intervention, Performed": "Suicide risk assessment (procedure)"
    included in the numerator logic below, as no individual suicide risk assessment tool or
    instrument would satisfy the requirements alone.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms177v9
    """

    title = 'Child and Adolescent Major Depressive Disorder (MDD): Suicide Risk Assessment'

    identifiers = ['CMS177v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'American Academy of Child and Adolescent Psychiatry. (2007). Practice parameter for the assessment and treatment of children and adolescents with depressive disorders. Journal of the American Academy of Child and Adolescent Psychiatry, 46(11), 1503-1526. doi:10.1097/chi.0b013e318145ae1c',
        'American Psychiatric Association. (2010). Practice guideline for the treatment of patients with major depressive disorder. 3rd edition. Retrieved from http://psychiatryonline.org/pb/assets/raw/sitewide/practice_guidelines/guidelines/mdd.pdf (This guideline was reaffirmed in 2015.)',
        'Luoma, J. B., Martin, C. E., & Pearson, J. L. (2002). Contact with mental health and primary care providers before suicide: A review of the evidence. American Journal of Psychiatry, 159(6), 909-916. doi:10.1176/appi.ajp.159.6.909',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patient visits for those patients aged 6 through 17 years with a
        diagnosis of major depressive disorder
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: None

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patient visits with an assessment for suicide risk

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: The evaluation must include assessment for the presence of harm to
        self or others (MS) (American Academy of Child and Adolescent Psychiatry, 2007).

        Suicidal behavior exists along a continuum from passive thoughts of death to a clearly
        developed plan and intent to carry out that plan. Because depression is closely associated
        with suicidal thoughts and behavior, it is imperative to evaluate these symptoms at the
        initial and subsequent assessments. For this purpose, low burden tools to track suicidal
        ideation and behavior such as the Columbia-Suicidal Severity Rating Scale can be used.
        Also, it is crucial to evaluate the risk (e.g., age, sex, stressors, comorbid conditions,
        hopelessness, impulsivity) and protective factors (e.g., religious belief, concern not to
        hurt family) that might influence the desire to attempt suicide. The risk for suicidal
        behavior increases if there is a history of suicide attempts, comorbid psychiatric
        disorders (e.g., disruptive disorders, substance abuse), impulsivity and aggression,
        availability of lethal agents (e.g., firearms), exposure to negative events (e.g., physical
        or sexual abuse, violence), and a family history of suicidal behavior (American Academy of
        Child and Adolescent Psychiatry, 2007).

        A careful and ongoing evaluation of suicide risk is necessary for all patients with major
        depressive disorder (Category I). Such an assessment includes specific inquiry about
        suicidal thoughts, intent, plans, means, and behaviors; identification of specific
        psychiatric symptoms (e.g., psychosis, severe anxiety, substance use) or general medical
        conditions that may increase the likelihood of acting on suicidal ideas; assessment of past
        and, particularly, recent suicidal behavior; delineation of current stressors and potential
        protective factors (e.g., positive reasons for living, strong social support); and
        identification of any family history of suicide or mental illness (Category I) (American
        Psychiatric Association, 2010, reaffirmed 2015).
        """
        pass
