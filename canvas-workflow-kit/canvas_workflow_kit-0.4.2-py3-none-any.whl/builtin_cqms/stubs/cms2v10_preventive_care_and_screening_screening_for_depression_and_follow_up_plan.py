from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AdolescentDepressionMedications, AdultDepressionMedications, BipolarDiagnosis,
    DepressionDiagnosis, EncounterToScreenForDepression, Ethnicity,
    FollowUpForAdolescentDepression, FollowUpForAdultDepression, OncAdministrativeSex, Payer,
    PhysicalTherapyEvaluation, Race, ReferralForAdolescentDepression, ReferralForAdultDepression)


class ClinicalQualityMeasure2v10(ClinicalQualityMeasure):
    """
    Preventive Care and Screening: Screening for Depression and Follow-Up Plan

    Description: Percentage of patients aged 12 years and older screened for depression on the date
    of the encounter or up to 14 days prior to the date of the encounter using an age-appropriate
    standardized depression screening tool AND if positive, a follow-up plan is documented on the
    date of the eligible encounter

    Definition: Screening:
    Completion of a clinical or diagnostic tool used to identify people at risk of developing or
    having a certain disease or condition, even in the absence of symptoms.

    Standardized Depression Screening Tool: A normalized and validated depression screening tool
    developed for the patient population in which it is being utilized.

    Examples of standardized depression screening tools include but are not limited to:
    *  Adolescent Screening Tools (12-17 years)
       *  Patient Health Questionnaire for Adolescents (PHQ-A)
       *  Beck Depression Inventory-Primary Care Version (BDI-PC)
       *  Mood Feeling Questionnaire (MFQ)
       *  Center for Epidemiologic Studies Depression Scale (CES-D)
       *  Patient Health Questionnaire (PHQ-9)
       *  Pediatric Symptom Checklist (PSC-17)
       *  PRIME MD-PHQ2
    *  Adult Screening Tools (18 years and older)
       *  Patient Health Questionnaire (PHQ9)
       *  Beck Depression Inventory (BDI or BDI-II)
       *  Center for Epidemiologic Studies Depression Scale (CES-D)
       *  Depression Scale (DEPS)
       *  Duke Anxiety-Depression Scale (DADS)
       *  Geriatric Depression Scale (GDS)
       *  Cornell Scale for Depression in Dementia (CSDD)
       *  PRIME MD-PHQ2
       *  Hamilton Rating Scale for Depression (HAM-D)
       *  Quick Inventory of Depressive Symptomatology Self-Report (QID-SR)
       *  Computerized Adaptive Testing Depression Inventory (CAT-DI)
       *  Computerized Adaptive Diagnostic Screener (CAD-MDD)
    * Perinatal Screening Tools
       *  Edinburgh Postnatal Depression Scale
       *  Postpartum Depression Screening Scale
       *  Patient Health Questionnaire 9 (PHQ-9)
       *  Beck Depression Inventory
       *  Beck Depression Inventory-II
       *  Center for Epidemiologic Studies Depression Scale
       *  Zung Self-rating Depression Scale

    Follow-Up Plan:
    Documented follow-up for a positive depression screening must include one or more of the
    following:
     *  Referral to a practitioner who is qualified to diagnose and treat depression
     *  Pharmacological interventions
     *  Other interventions or follow-up for the diagnosis or treatment of depression

    Rationale: Depression is a serious medical illness associated with higher rates of chronic
    disease, increased health care utilization, and impaired functioning (Katon, 2003; Wells et
    al., 1989). 2016 U.S. survey data indicate that 12.8 percent of adolescents (3.1 million
    adolescents) had a major depressive episode (MDE) in the past year, with nine percent of
    adolescents (2.2 million adolescents) having one MDE with severe impairment. The same data
    indicate that 6.7 percent of adults aged 18 or older (16.2 million adults) had at least one MDE
    with 4.3 percent of adults (10.3 million adults) having one MDE with severe impairment in the
    past year (Substance Abuse and Mental Health Services Administration, 2017). Data indicate that
    severity of depressive symptoms factor into having difficulty with work, home, or social
    activities. For example, as the severity of depressive symptoms increased, rates of having
    difficulty with work, home, or social activities related to depressive symptoms increased. For
    those twelve and older with mild depressive symptoms, 45.7% reported difficulty with activities
    and those with severe depressive symptoms, 88.0% reported difficulty (Pratt & Brody, 2014).
    Children and teens with major depressive disorder (MDD) have been found to have difficulty
    carrying out their daily activities, relating to others, growing up healthy, and also are at an
    increased risk of suicide (Siu on behalf of the U.S. Preventive Services Task Force [USPSTF],
    2016). Additionally, perinatal depression (considered here as depression arising in the period
    from conception to the end of the first postnatal year) affects up to 12% of women (Woody,
    Ferrari, Siskind, Whiteford, & Harris, 2017). Depression and other mood disorders, such as
    bipolar disorder and anxiety disorders, especially during the perinatal period, can have
    devastating effects on women, infants, and families (American College of Obstetricians and
    Gynecologists, 2018). Maternal suicide rates rise over hemorrhage and hypertensive disorders as
    a cause of maternal mortality (Palladino, Singh, Campbell, Flynn, & Gold, 2011).

    Negative outcomes associated with depression make it crucial to screen in order to identify and
    treat depression in its early stages. While Primary Care Providers (PCPs) serve as the first
    line of defense in the detection of depression, studies show that PCPs fail to recognize up to
    50% of depressed patients (Borner, Braunstein, St. Victor, & Pollack, 2010). "In nationally
    representative U.S. surveys, about eight percent of adolescents reported having major
    depression in the past year. Only 36% to 44% of children and adolescents with depression
    receive treatment, suggesting that the majority of depressed youth are undiagnosed and
    untreated" (Siu on behalf of USPSTF, 2016, p. 360 & p. 364). Evidence supports that screening
    for depression in pregnant and postpartum women is of moderate net benefit and treatment
    options for positive depression screening should be available for patients twelve and older
    including pregnant and postpartum women.

    If preventing negative patient outcomes is not enough, the substantial economic burden of
    depression for individuals and society alike makes a case for screening for depression on a
    regular basis. Depression imposes economic burden through direct and indirect costs: "In the
    United States, an estimated $22.8 billion was spent on depression treatment in 2009, and lost
    productivity cost an additional estimated $23 billion in 2011" (Siu & USPSTF, 2016, p.
    383-384).

    This measure seeks to align with clinical guideline recommendations as well as the Healthy
    People 2020 recommendation for routine screening for mental health problems as a part of
    primary care for both children and adults (U.S. Department of Health and Human Services, 2014)
    and makes an important contribution to the quality domain of community and population health.

    Guidance: A depression screen is completed on the date of the encounter or up to 14 days prior
    to the date of the encounter using an age-appropriate standardized depression screening tool
    AND if positive, a follow-up plan must be documented on the date of the encounter, such as
    referral to a practitioner who is qualified to treat depression, pharmacological interventions
    or other interventions for the treatment of depression.

    This eCQM is a patient-based measure. Depression screening is required once per measurement
    period, not at all encounters.

    The intent of the measure is to screen for depression in patients who have never had a
    diagnosis of depression or bipolar disorder prior to the eligible encounter used to evaluate
    the numerator. Patients who have ever been diagnosed with depression or bipolar disorder will
    be excluded from the measure.

    Screening Tools:
     *  An age-appropriate, standardized, and validated depression screening tool must be used for
    numerator compliance.
     *  The name of the age-appropriate standardized depression screening tool utilized must be
    documented in the medical record.
     *  The depression screening must be reviewed and addressed in the office of the provider,
    filing the code, on the date of the encounter. Positive pre-screening results indicating a
    patient is at high risk for self-harm should receive more urgent intervention as determined by
    the provider practice.
     *  The screening should occur during a qualifying encounter or up to 14 days prior to the date
    of the qualifying encounter.
     *  The measure assesses the most recent depression screening completed either during the
    eligible encounter or within the 14 days prior to that encounter. Therefore, a clinician would
    not be able to complete another screening at the time of the encounter to count towards a
    follow-up, because that would serve as the most recent screening. In order to satisfy the
    follow-up requirement for a patient screening positively, the eligible clinician would need to
    provide one of the aforementioned follow-up actions, which does not include use of a
    standardized depression screening tool.

    Follow-Up Plan:

    The follow-up plan must be related to a positive depression screening, for example: "Patient
    referred for psychiatric evaluation due to positive depression screening."

    Examples of a follow-up plan include but are not limited to:
     *  Referral to a practitioner or program for further evaluation for depression, for example,
    referral to a psychiatrist, psychologist, social worker, mental health counselor, or other
    mental health service such as family or group therapy, support group, depression management
    program, or other service for treatment of depression
     *  Other interventions designed to treat depression such as behavioral health evaluation,
    psychotherapy, pharmacological interventions, or additional treatment options

    Should a patient screen positive for depression, a clinician should opt to complete a suicide
    risk assessment when appropriate and based on individual patient characteristics. However, for
    the purposes of this measure, a suicide risk assessment or additional screening using a
    standardized tool will not qualify as a follow-up plan.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms2v10
    """

    title = 'Preventive Care and Screening: Screening for Depression and Follow-Up Plan'

    identifiers = ['CMS2v10']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'American College of Obstetricians and Gynecologists, Committee on Obstetric Practice. (2018). ACOG Committee Opinion Number 757: Screening for perinatal depression. Obstetrics and Gynecology, 132(5), e208-e212. doi: 10.1097/AOG.0000000000002927',
        'Borner, I., Braunstein, J. W., St. Victor, R., & Pollack, J. (2010). Evaluation of a 2-question screening tool for detecting depression in adolescents in primary care. Clinical Pediatrics, 49(10), 947-995. doi:10.1177/0009922810370203',
        'Katon, W. J. (2003). Clinical and health services relationships between major depression, depressive symptoms, and general medical illness. Biological Psychiatry, 54(3), 216-226. doi: 10.1016/s0006-3223(03)00273-7',
        'Palladino, C. L., Singh, V., Campbell, J., Flynn, H., & Gold, K. (2011). Homicide and suicide during the perinatal period: Findings from the National Violent Death Reporting System. Obstetrics and Gynecology, 118(5), 1056-1063. doi:10.1097/AOG.0b013e31823294da',
        'Pratt, L. A., & Brody, D. J. (2014). Depression in the U.S. household population, 2009-2012. NCHS Data Brief No. 172. Hyattsville, MD: U.S. Department of Health and Human Services, Centers for Disease Control and Prevention, National Center for Health Statistics. Retrieved from https://www.cdc.gov/nchs/data/databriefs/db172.pdf',
        'Siu, A. L., on behalf of USPSTF. (2016). Screening for depression in children and adolescents: U.S. Preventive Services Task Force recommendation statement. Annals of Internal Medicine, 164(5), 360-366. doi:10.7326/M15-2957',
        'Siu, A. L., & USPSTF. (2016). Screening for depression in adults: U.S. Preventive Services Task Force recommendation statement. Journal of the American Medical Association, 315(4), 380-387. doi:10.1001/jama.2015.18392.',
        'Substance Abuse and Mental Health Services Administration. (2017). Key substance use and mental health indicators in the United States: Results from the 2016 National Survey on Drug Use and Health. Rockville, MD: Center for Behavioral Health Statistics and Quality, Substance Abuse and Mental Health Services Administration. Retrieved from https://www.samhsa.gov/data/sites/default/files/NSDUH-FFR1-2016/NSDUH-FFR1-2016.htm',
        'Trangle, M., Gursky, J., Haight, R., Hardwig, J., Hinnenkamp, T., Kessler, D.,… Myszkowski, M. (2016). Adult depression in primary care. Bloomington, MN: Institute for Clinical Systems Improvement. Retrieved from https://www.icsi.org/guideline/depression/',
        'U.S. Department of Health and Human Services. (2014). Healthy People 2020: Mental health and mental disorders. Washington, DC: U.S. Department of Health and Human Services. Retrieved from http://www.healthypeople.gov/2020/topicsobjectives2020/objectiveslist.aspx?topicId=28',
        'Wells, K. B., Stewart, A., Hays, R. D., Burnam, M. A., Rogers, W., Daniels, M., … Ware, J. (1989). The functioning and well-being of depressed patients. Results from the Medical Outcomes Study. Journal of the American Medical Association, 262(7), 914-919. Abstract retrieved from https://www.ncbi.nlm.nih.gov/pubmed/2754791',
        'Woody, C. A., Ferrari, A. J., Siskind, D. J., Whiteford, H. A., & Harris, M. G. (2017). A systematic review and meta-regression of the prevalence and incidence of perinatal depression. Journal of Affective Disorders, 219, 88-92. doi:10.1016/j.jad.2017.05.003',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients aged 12 years and older at the beginning of the
        measurement period with at least one eligible encounter during the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Patients who have been diagnosed with depression or with bipolar disorder

        Exceptions: Patient Reason(s)
        Patient refuses to participate
        OR
        Medical Reason(s)
        Documentation of medical reason for not screening patient for depression (e.g., cognitive,
        functional, or motivational limitations that may impact accuracy of results; patient is in
        an urgent or emergent situation where time is of the essence and to delay treatment would
        jeopardize the patient's health status)
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients screened for depression on the date of the encounter or up to 14 days
        prior to the date of the encounter using an age-appropriate standardized tool AND if
        positive, a follow-up plan is documented on the date of the eligible encounter

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: Adolescent Recommendation (12-18 years):

        "The USPSTF recommends screening for MDD in adolescents aged 12 to 18 years. Screening
        should be implemented with adequate systems in place to ensure accurate diagnosis,
        effective treatment, and appropriate follow-up (B recommendation)" (Siu on behalf of
        USPSTF, 2016, p. 360).

        Adult Recommendation (18 years and older):

        "The USPSTF recommends screening for depression in the general adult population, including
        pregnant and postpartum women. Screening should be implemented with adequate systems in
        place to ensure accurate diagnosis, effective treatment, and appropriate follow-up (B
        recommendation)" (Siu & USPSTF, 2016, p. 380).

        The Institute for Clinical Systems Improvement (ICSI) health care guideline, Adult
        Depression in Primary Care, provides the following recommendations:
        1. "Clinicians should routinely screen all adults for depression using a standardized
        instrument."
        2. "Clinicians should establish and maintain follow-up with patients."
        3. "Clinicians should screen and monitor depression in pregnant and post-partum women."
        (Trangle et al., 2016, p. 8-10).
        """
        pass
