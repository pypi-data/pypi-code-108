from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    BipolarDisorder, CareServicesInLongTermResidentialFacility, ContactOrOfficeVisit, Dysthymia,
    Ethnicity, MajorDepressionIncludingRemission, OncAdministrativeSex, PalliativeCareEncounter,
    PalliativeOrHospiceCare, Payer, PersonalityDisorderEmotionallyLabile,
    PervasiveDevelopmentalDisorder, Phq9AndPhq9MTools, Race, SchizophreniaOrPsychoticDisorder)


class ClinicalQualityMeasure159v9(ClinicalQualityMeasure):
    """
    Depression Remission at Twelve Months

    Description: The percentage of adolescent patients 12 to 17 years of age and adult patients 18
    years of age or older with major depression or dysthymia who reached remission 12 months (+/-
    60 days) after an index event.

    Definition: Denominator Identification Period:
    The period in which eligible patients can have an index event. The denominator identification
    period occurs prior to the measurement period and is defined as 14 months to two months prior
    to the start of the measurement period. For patients with an index event, there needs to be
    enough time following index for the patients to have the opportunity to reach remission twelve
    months +/- 60 days after the index event date.

    Index Event Date:
    The date in which the first instance of elevated PHQ-9 or PHQ-9M greater than nine and
    diagnosis of depression or dysthymia occurs during the denominator identification measurement
    period. Patients may be screened using PHQ-9 and PHQ-9M up to 7 days prior to the office visit
    (including the day of the office visit).


    Measure Assessment Period:
    The index event date marks the start of the measurement assessment period for each patient
    which is 14 months (12 months +/- 60 days) in length to allow for a follow-up PHQ-9 or PHQ-9M
    between 10 and 14 months following the index event. This assessment period is fixed and does
    not start over with a higher PHQ-9 or PHQ-9M that may occur after the index event date.

    Remission is defined as a PHQ-9 or PHQ-9M score of less than five.

    Twelve months is defined as the point in time from the index event date extending out twelve
    months and then allowing a grace period of sixty days prior to and sixty days after this date.
    The most recent PHQ-9 or PHQ-9M score less than five obtained during this four month period is
    deemed as remission at twelve months, values obtained prior to or after this period are not
    counted as numerator compliant (remission).

    Rationale: Adults:
    Depression is a common and treatable mental disorder. 8.1% of American adults age 20 and over
    had depression in a given 2 week period. Women (10.4%) were almost twice as likely as men
    (5.5%) to have had depression. The prevalence of depression among adults decreased as family
    income levels increased. About 80% of adults with depression reported at least some difficulty
    with work, home, or social activities because of their depression symptoms (Centers for Disease
    Control and Prevention, 2018).

    Depression is a risk factor for development of chronic illnesses such as diabetes and CHD and
    adversely affects the course, complications and management of chronic medical illness. Both
    maladaptive health risk behaviors and psychobiological factors associated with depression may
    explain depression's negative effect on outcomes of chronic illness. (Katon, W.J., 2011)

    Adolescents and Adults:
    The Centers for Disease Control and Prevention states that during 2009-2012 an estimated 7.6%
    of the U.S. population aged 12 and over had depression, including 3% of Americans with severe
    depressive symptoms. Almost 43% of persons with severe depressive symptoms reported serious
    difficulties in work, home and social activities, yet only 35% reported having contact with a
    mental health professional in the past year.
    Depression is associated with higher mortality rates in all age groups. People who are
    depressed are 30 times more likely to take their own lives than people who are not depressed
    and five times more likely to abuse drugs. Depression is the leading cause of medical
    disability for people aged 14 to 44. Depressed people lose 5.6 hours of productive work every
    week when they are depressed, fifty percent of which is due to absenteeism and short-term
    disability.

    Adolescents:
    In 2014, an estimated 2.8 million adolescents age 12 to 17 in the United States had at least
    one major depressive episode (MDE) in the past year. This represented 11.4% of the U.S.
    population. The same survey found that only 41.2 percent of those who had a MDE received
    treatment in the past year. The 2013 Youth Risk Behavior Survey of students grades 9 to 12
    indicated that during the past 12 months 39.1% (F) and 20.8% (M) indicated feeling sad or
    hopeless almost every day for at least 2 weeks, planned suicide attempt 16.9% (F) and 10.3%
    (M), with attempted suicide 10.6% (F) and 5.4% (M). Adolescent-onset depression is associated
    with chronic depression in adulthood. Many mental health conditions (anxiety, bipolar,
    depression, eating disorders, and substance abuse) are evident by age 14. The 12-month
    prevalence of MDEs increased from 8.7% in 2005 to 11.3% in 2014 in adolescents and from 8.8% to
    9.6% in young adults (both P < .001). The increase was larger and statistically significant
    only in the age range of 12 to 20 years. The trends remained significant after adjustment for
    substance use disorders and sociodemographic factors. Mental health care contacts overall did
    not change over time; however, the use of specialty mental health providers increased in
    adolescents and young adults, and the use of prescription medications and inpatient
    hospitalizations increased in adolescents. In 2015, 9.7% of adolescents in MN who were screened
    for depression or other mental health conditions, screened positively.

    Guidance: When a baseline assessment is conducted with PHQ 9M, the follow-up assessment can use
    either a PHQ 9M or PHQ 9.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms159v9
    """

    title = 'Depression Remission at Twelve Months'

    identifiers = ['CMS159v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'MN Community Measurement',
    ]

    references = [
        'Duffy, F. F., Chung, H., Trivedi, M., et al. (2008, October). Systematic use of patient-rated depression severity monitoring: Is it helpful and feasible in clinical psychiatry? Psychiatric Services, 59(10), 1148-1154.',
        'Hunkeler, E. M., Meresman, J. F., Hargreaves, W. A., et al. (2000, August). Efficacy of nurse telehealth care and peer support in augmenting treatment of depression in primary care. Archives of Family Medicine, 9(8), 700-708.',
        'Katon, W.J. (2011) Epidemiology and treatment of depression in patients with chronic medical illness Dialogues in Clinical Neuroscience v.13(1) PMC3181964',
        'Kroenke, K., Spitzer, R. L., & Williams, J. B. W. (2001). The PHQ-9: Validity of a brief depression severity measure. Journal of General Internal Medicine, 16(9), 606-613. Retrieved from https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1495268/',
        'Lowe, B., Unutzer, J., Callahan, C. M., et al. (2004). Monitoring depression treatment outcomes with the Patient Health Questionnaire-9. Medical Care, 42(12), 1194-1201.',
        'Rush, A. J., Trivedi, M. H., Wisniewski, S. R., et al. (2006). Acute and longer-term outcomes in depressed outpatients requiring one or several treatment steps: A STAR*D report. American Journal of Psychiatry, 163, 1905-1917.',
        'Simon, G. E., Van Korff, M., Rutter, C., et al. (2000). Randomised trial of monitoring, feedback, and management of care by telephone to improve treatment of depression in primary care. BMJ, 320, 550-554.',
        'Trangle , M., Gursky, J., Haight, R., et al. Depression, adults in primary care. (Updated 2016, March). Retrieved from https://www.icsi.org/guidelines__more/catalog_guidelines_and_more/catalog_guidelines/catalog_behavioral_health_guidelines/depression/',
        'Trivedi, M. H. (2009). Tools and strategies for ongoing assessment of depression: A measurement-based approach to remission. Journal of Clinical Psychiatry, 70, 26-31.',
        'Trivedi, M. H., Rush, A. J., Wisniewski, S. R., et al. (2006). Evaluation of outcomes with citalopram for depression using measurement-based care in STAR*D: Implications for clinical practice. American Journal of Psychiatry, 163(1), 28-40.',
        'Unutzer, J., Katon, W., Callahan, C. M., et al. (2002). Collaborative care management of late-life depression in the primary care setting: A randomized controlled trial. JAMA, 288, 2836-2845.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Adolescent patients 12 to 17 years of age and adult patients 18 years
        of age and older with a diagnosis of major depression or dysthymia and an initial PHQ-9 or
        PHQ-9M score greater than nine during the index event. Patients may be screened using PHQ-9
        and PHQ-9M up to 7 days prior to the office visit (including the day of the office visit).
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: 1: Patients who died
        2: Patients who received hospice or palliative care services
        3: Patients who were permanent nursing home residents
        4: Patients with a diagnosis of bipolar disorder
        5: Patients with a diagnosis of personality disorder emotionally labile
        6: Patients with a diagnosis of schizophrenia or psychotic disorder
        7: Patients with a diagnosis of pervasive developmental disorder

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Adolescent patients 12 to 17 years of age and adult patients 18 years of age and
        older who achieved remission at twelve months as demonstrated by a twelve month (+/- 60
        days) PHQ-9 or PHQ-9M score of less than five

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: Adults:
        Source: Institute for Clinical Systems Improvement (ICSI) Health Care Guideline for Adult
        Depression in Primary Care (Trangle et al., 2016)

        Recommendations and algorithm notations supporting depression outcomes and duration of
        treatment according to ICSI's Health Care Guideline:

        Recommendation: Clinicians should establish and maintain follow-up with patients.
        Appropriate, reliable follow-up is highly correlated with improved response and remission
        scores. It is also correlated with the improved safety and efficacy of medications and
        helps prevent relapse.

        Proactive follow-up contacts (in person, telephone) based on the collaborative care model
        have been shown to significantly lower depression severity (Unutzer et al., 2002).  In the
        available clinical effectiveness trials conducted in real clinical practice settings, even
        the addition of a care manager leads to modest remission rates (Trivedi et al., 2006;
        Unutzer et al., 2002).  Interventions are critical to educating the patient regarding the
        importance of preventing relapse, safety and efficacy of medications, and management of
        potential side effects.  Establish and maintain initial follow-up contact intervals
        (office, phone, other) (Hunkeler et al., 2000; Simon et al., 2000).

        PHQ-9 as monitor and management tool.  The PHQ-9 is an effective management tool, as well,
        and should be used routinely for subsequent visits to monitor treatment outcomes and
        severity. It can also help the clinician decide if/how to modify the treatment plan (Duffy
        et al., 2008; Lowe et al., 2004).  Using a measurement-based approach to depression care,
        PHQ-9 results and side effect evaluation should be combined with treatment algorithms to
        drive patients toward remission.  A five-point drop in PHQ-9 score is considered the
        minimal clinically significant difference (Trivedi, 2009).

        The goals of treatment should be to achieve remission, reduce relapse and recurrence, and
        return to previous level of occupational and psychosocial function.

        If using a PHQ-9 tool, remission translates to PHQ-9 score of less than 5 (Kroenke, 2001).
        Results from the STAR*D study showed that remission rates lowered with more treatment
        steps, but the overall cumulative rate was 67% (Rush et al., 2006).

        Response and remission take time. In the STAR*D study, longer times than expected were
        needed to reach response or remission. In fact, one-third of those who ultimately responded
        did so after six weeks. Of those who achieved remission by Quick Inventory of Depressive
        Symptomatology (QIDS), 50% did so only at or after six weeks of treatment (Trivedi et al.,
        2006). If the primary care clinician is seeing some improvement, continue working with that
        patient to augment or increase dosage to reach remission. This can take up to three months.

        This measure assesses achievement of remission, which is a desired outcome of effective
        depression treatment and monitoring.

        Adult Depression in Primary Care - Guideline Aims
        - Increase the percentage of patients with major depression or persistent depressive
        disorder who have improvement in outcomes from treatment for major depression or persistent
        depressive disorder.
        - Increase the percentage of patients with major depression or persistent depressive
        disorder who have follow-up to assess for outcomes from treatment.
        - Improve communication between the primary care physician and the mental health care
        clinician (if patient is co-managed).

        Adolescents:
        Source: American Academy of Child and Adolescent Psychiatry Practice Parameter for the
        Assessment and Treatment of Children and Adolescents with Depressive Disorders (2007)
        http://www.jaacap.com/article/S0890-8567(09)62053-0/pdf

        Recommendations:
        Recommendations supporting depression outcomes and duration of treatment according to AACAP
        guideline:
        - Treatment of depressive disorders should always include an acute and continuation phase;
        some children may also require maintenance treatment. The main goal of the acute phase is
        to achieve response and ultimately full symptomatic remission (definitions below).
        - Each phase of treatment should include psychoeducation, supportive management, and family
        and school involvement.
        - Education, support, and case management appear to be sufficient treatment for the
        management of depressed children and adolescents with an uncomplicated or brief depression
        or with mild psychosocial impairment.
        - For children and adolescents who do not respond to supportive psychotherapy or who have
        more complicated depressions, a trial with specific types of psychotherapy and/or
        antidepressants is indicated.

        Sources:
        Guidelines for Adolescent Depression in Primary Care (GLAD-PC) (2018)
        http://pediatrics.aappublications.org/content/141/3/e20174081
        Guidelines for adolescent depression in primary care (GLAD-PC): II. Treatment and ongoing
        management
        http://pediatrics.aappublications.org/content/141/3/e20174082

        Recommendations supporting depression outcomes and duration of treatment according to GLAD-
        PC:
        Recommendations for Ongoing Management of Depression:
        - Mild depression: consider a period of active support and monitoring before starting other
        evidence-based treatment
        - Moderate or severe major clinical depression or complicating factors:
          -- consultation with mental health specialist with agreed upon roles
          -- evidence based treatment (CBT or IPT and/or antidepressant SSRI)
        - Monitor for adverse effects during antidepressant therapy
          -- clinical worsening, suicidality, unusual changes in behavior
        - Systematic and regular tracking of goals and outcomes
          -- improvement in functioning status and resolution of depressive symptoms
        Regardless of the length of treatment, all patients should be monitored on a monthly basis
        for 6 to 12 months after the full resolution of symptoms
        """
        pass
