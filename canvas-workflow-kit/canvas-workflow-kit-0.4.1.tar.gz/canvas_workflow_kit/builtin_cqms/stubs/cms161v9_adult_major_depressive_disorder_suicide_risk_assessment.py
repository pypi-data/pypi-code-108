from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    EmergencyDepartmentVisit, Ethnicity, OfficeVisit, OncAdministrativeSex, OutpatientConsultation,
    Payer, PsychVisitDiagnosticEvaluation, PsychVisitPsychotherapy, Psychoanalysis, Race,
    TelehealthServices)


class ClinicalQualityMeasure161v9(ClinicalQualityMeasure):
    """
    Adult Major Depressive Disorder (MDD): Suicide Risk Assessment

    Description: All patient visits during which a new diagnosis of MDD or a new diagnosis of
    recurrent MDD was identified for patients aged 18 years and older with a suicide risk
    assessment completed during the visit

    Definition: The specific type and magnitude of the suicide risk assessment is intended to be at
    the discretion of the individual clinician and should be specific to the needs of the patient.
    At a minimum, suicide risk assessment should evaluate:
    1) Suicidal ideation
    2) Patient's intent of initiating a suicide attempt
    AND, if either is present,
    3) Patient plans for a suicide attempt
    4) Whether the patient has means for completing suicide

    Low burden tools to track suicidal ideation and behavior such as the Columbia-Suicide Severity
    Rating Scale (C-SSRS) and the Suicide Assessment Five-Step Evaluation and Triage (SAFE-T) can
    also be used. Because no validated assessment tool or instrument fully meets the aforementioned
    requirements for the suicide risk assessment, individual tools or instruments have not been
    explicitly included in coding.

    Rationale: This measure aims to improve rates of clinician assessment of suicide risk during an
    encounter where a new or recurrent episode of major depressive disorder is identified. In an
    epidemiologic study (2010) of mental illness in the United States with a large, representative
    sample, 69% of respondents with lifetime suicide attempts had also met diagnostic criteria for
    major depressive disorder. When considering other mood disorders related to depression, such as
    dysthymia and bipolar disorders, this rate increases to 74% (Bolton & Robinson, 2010). In a
    2014 study conducted by Ahmedani et al., 50% of individuals who completed a suicide had been
    seen in a health care setting within four weeks prior. Better assessment and identification of
    suicide risk in the health care setting should lead to improved connection to treatment and
    reduction in suicide attempts and deaths by suicide.

    Guidance: This eCQM is an episode-of-care measure and should be reported for each instance of a
    new or recurrent episode of major depressive disorder (MDD); every new or recurrent episode
    will count separately in the Initial Population.

    As the guidelines state, it is important to assess for additional factors which may increase or
    decrease suicide risk, such as presence of additional symptoms (e.g., psychosis, severe
    anxiety, hopelessness, severe chronic pain); presence of substance abuse, history and
    seriousness of previous attempts, particularly, recent suicidal behavior, current stressors and
    potential protective factors (e.g., positive reasons for living, strong social support), family
    history of suicide or mental illness or recent exposure to suicide, impulsivity and potential
    for risk to others, including history of violence or violent or homicidal ideas, plans, or
    intentions, and putting one's affairs in order (e.g., giving away possessions, writing a will).
    In addition, although the measure focuses on the initial visit, it is critical that suicide
    risk be monitored especially for the 90 days following the initial visit and throughout MDD
    treatment.

    It is expected that a suicide risk assessment will be completed at the visit during which a new
    diagnosis is made or at the visit during which a recurrent episode is first identified (i.e.,
    at the initial evaluation). For the purposes of this measure, an episode of major depressive
    disorder (MDD) would be considered to be recurrent if a patient has not had an MDD-related
    encounter in the past 105 days. If there is a gap of 105 or more days between visits for major
    depressive disorder (MDD), that would imply a recurrent episode. The 105-day look-back period
    is an operational provision and not a clinical recommendation, or definition of relapse,
    remission, or recurrence.

    In recognition of the growing use of integrated and team-based care, the diagnosis of
    depression and the assessment for suicide risk need not be performed by the same provider or
    clinician.

    Suicide risk assessments completed via telehealth services can also meet numerator performance.

    Use of a standardized tool(s) or instrument(s) to assess suicide risk will meet numerator
    performance. Standardized tools can be mapped to the concept "Intervention, Performed":
    "Suicide risk assessment (procedure)" included in the numerator logic below.

    The logic statement for the age requirement, as written, captures patients who turn 18 years
    old during the measurement period so that these patients are included in the measure, so long
    as the minimum criteria noted above is evaluated. To ensure all patients with major depressive
    disorder (MDD) are assessed for suicide risk, there are two clinical quality measures
    addressing suicide risk assessment; CMS 177 covers children and adolescents aged 6 through 17,
    and CMS 161 covers the adult population aged 18 years and older, as no individual suicide risk
    assessment tool or instrument would satisfy the requirements alone.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms161v9
    """

    title = 'Adult Major Depressive Disorder (MDD): Suicide Risk Assessment'

    identifiers = ['CMS161v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'American Psychiatric Association. (2010a). Practice guideline for the treatment of patients with major depressive disorder. 3rd edition. Retrieved from http://psychiatryonline.org/pb/assets/raw/sitewide/practice_guidelines/guidelines/mdd.pdf (This guideline was reaffirmed in 2015.)',
        'American Psychiatric Association. (2010b). Guidelines for selecting a treatment setting for patients at risk for suicide or suicidal behaviors. Retrieved from http://psychiatryonline.org/pb/assets/raw/sitewide/practice_guidelines/guidelines/suicide.pdf',
        'Ahmedani, B. K., Simon, G. E., Stewart, C., Beck, A., Waitzfelder, B. E., Rossom, R.,… Solberg, L. I.(2014). Health care contacts in the year before suicide death. Journal of General Internal Medicine, 29(6), 870-877. doi:10.1007/s11606-014-2767-3',
        'Bolton, J. M., & Robinson, J. (2010). Population-attributable fractions of Axis I and Axis II mental disorders for suicide attempts: Findings from a representative sample of the adult, noninstitutionalized U.S. population. American Journal of Public Health, 100(12), 2473-2480. doi:10.2105/ajph.2010.192252',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patient visits during which a new diagnosis of MDD, single or recurrent
        episode, was identified
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
        Numerator: Patient visits during which a new diagnosis of MDD, single or recurrent episode,
        was identified and a suicide risk assessment was completed during the visit

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: A careful and ongoing evaluation of suicide risk is necessary for
        all patients with major depressive disorder [I] (American Psychiatric Association, 2010a,
        reaffirmed 2015).

        Such an assessment includes specific inquiry about suicidal thoughts, intent, plans, means,
        and behaviors; identification of specific psychiatric symptoms (e.g., psychosis, severe
        anxiety, substance use) or general medical conditions that may increase the likelihood of
        acting on suicidal ideas; assessment of past and, particularly, recent suicidal behavior;
        delineation of current stressors and potential protective factors (e.g., positive reasons
        for living, strong social support); and identification of any family history of suicide or
        mental illness [I] (American Psychiatric Association, 2010a, reaffirmed 2015).

        As part of the assessment process, impulsivity and potential for risk to others should also
        be evaluated, including any history of violence or violent or homicidal ideas, plans, or
        intentions [I] (American Psychiatric Association, 2010a, reaffirmed 2015).

        The patient's risk of harm to him- or herself and to others should also be monitored as
        treatment proceeds [I] (American Psychiatric Association, 2010a, reaffirmed 2015).

        Guidelines for Selecting a Treatment Setting for Patients at Risk for Suicide or Suicidal
        Behaviors (from American Psychiatric Association’s Practice Guideline for Assessment and
        Treatment of Patients With Suicidal Behaviors, 2010b):
        Admission generally indicated
        After a suicide attempt or aborted suicide attempt if:
        * Patient is psychotic
        * Attempt was violent, near-lethal, or premeditated
        * Precautions were taken to avoid rescue or discovery
        * Persistent plan and/or intent is present
        * Distress is increased or patient regrets surviving
        * Patient is male, older than age 45 years, especially with new onset of psychiatric
        illness or suicidal thinking
        * Patient has limited family and/or social support, including lack of stable living
        situation
        * Current impulsive behavior, severe agitation, poor judgment, or refusal of help is
        evident
        * Patient has change in mental status with a metabolic, toxic, infectious, or other
        etiology requiring further workup in a structured setting

        In the presence of suicidal ideation with:
        * Specific plan with high lethality
        * High suicidal intent

        Admission may be necessary
        After a suicide attempt or aborted suicide attempt, except in circumstances for which
        admission is generally indicated

        In the presence of suicidal ideation with:
        * Psychosis
        * Major psychiatric disorder
        * Past attempts, particularly if medically serious
        * Possibly contributing medical condition (e.g., acute neurological disorder, cancer,
        infection)
        * Lack of response to or inability to cooperate with partial hospital or outpatient
        treatment
        * Need for supervised setting for medication trial or ECT
        * Need for skilled observation, clinical tests, or diagnostic assessments that require a
        structured setting
        * Limited family and/or social support, including lack of stable living situation
        * Lack of an ongoing clinician-patient relationship or lack of access to timely outpatient
        follow-up
        * Evidence of putting one's affairs in order (e.g., giving away possessions, writing a
        will)

        In the absence of suicide attempts or reported suicidal ideation/plan/intent but evidence
        from the psychiatric evaluation and/or history from others suggests a high level of suicide
        risk and a recent acute increase in risk

        Release from emergency department with follow-up recommendations may be possible
        After a suicide attempt or in the presence of suicidal ideation/plan when:
        * Suicidality is a reaction to precipitating events (e.g., exam failure, relationship
        difficulties), particularly if the patient's view of situation has changed since coming to
        emergency department
        * Plan/method and intent have low lethality
        * Patient has stable and supportive living situation
        * Patient is able to cooperate with recommendations for follow-up, with treater contacted,
        if possible, if patient is currently in treatment

        Outpatient treatment may be more beneficial than hospitalization
        Patient has chronic suicidal ideation and/or self-injury without prior medically serious
        attempts, if a safe and supportive living situation is available and outpatient psychiatric
        care is ongoing.
        """
        pass
