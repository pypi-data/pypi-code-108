from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AdhdMedications, BehavioralHealthFollowUpVisit, EncounterInpatient, Ethnicity,
    HomeHealthcareServices, HospiceCareAmbulatory, HospitalObservationCareInitial, Narcolepsy,
    OfficeVisit, OncAdministrativeSex, OutpatientConsultation, Payer,
    PreventiveCareEstablishedOfficeVisit0To17, PreventiveCareServicesGroupCounseling,
    PreventiveCareServicesIndividualCounseling, PreventiveCareServicesInitialOfficeVisit0To17,
    PsychVisitDiagnosticEvaluation, PsychVisitPsychotherapy,
    PsychotherapyAndPharmacologicManagement, Race, TelehealthServices, TelephoneManagement)


class ClinicalQualityMeasure136v10(ClinicalQualityMeasure):
    """
    Follow-Up Care for Children Prescribed ADHD Medication (ADD)

    Description: Percentage of children 6-12 years of age and newly dispensed a medication for
    attention-deficit/hyperactivity disorder (ADHD) who had appropriate follow-up care.  Two rates
    are reported.
    a. Percentage of children who had one follow-up visit with a practitioner with prescribing
    authority during the 30-Day Initiation Phase.
    b. Percentage of children who remained on ADHD medication for at least 210 days and who, in
    addition to the visit in the Initiation Phase, had at least two additional follow-up visits
    with a practitioner within 270 days (9 months) after the Initiation Phase ended.

    Definition: Intake Period: The five-month period starting 90 days prior to the start of the
    measurement period and ending 60 days after the start of the measurement period.

    Index Prescription Start Date (IPSD): The earliest prescription dispensing date for an ADHD
    medication where the date is in the Intake Period and an ADHD medication was not dispensed
    during the 120 days prior.

    Initiation Phase: The 30 days following the IPSD.

    Continuation and Maintenance Phase: The 31-300 days following the IPSD.

    Rationale: Attention-deficit/hyperactivity disorder (ADHD) is the most common neurobehavioral
    disorder of childhood and can profoundly affect the academic achievement, well-being, and
    social interactions of children (American Academy of Pediatrics, 2011). The American
    Psychiatric Association states in the Diagnostic and Statistical Manual of Mental Disorders
    that five percent of children have ADHD (American Psychiatric Association, 2013). However,
    other studies in the US have estimated higher rates in community samples.  For example, a study
    examining data from the National Survey of Children's Health estimated that approximately 9.4%
    of children 2-17 years of age (6.1 million) had ever been diagnosed with ADHD, according to
    parent report in 2016 (Danielson et al., 2016). Among those children, 6 out of 10 (62%) were
    taking medication for their ADHD and represent 1 out of 20 of all U.S. children. Just under
    half (47%) received any behavioral treatment for their ADHD in the past year (Danielson et al.,
    2016).

    There are many symptoms associated with ADHD. Children with ADHD may experience significant
    functional problems, such as school difficulties, academic underachievement, troublesome
    relationships with family members and peers and behavioral problems (American Academy of
    Pediatrics, 2000). For instance, recent studies have found that parents whose children have a
    history of ADHD report significantly more peer problems and a higher rate of non-fatal injuries
    compared to parents whose children do not have a history of ADHD (Strine et al., 2006; Xiang et
    al., 2005). Additional studies suggest that there is an increased risk for drug use disorders
    in adolescents with untreated ADHD (National Institute on Drug Abuse, 2010). One of the
    national objectives of the Department of Health and Human Services Healthy People 2020
    initiative is to increase the proportion of children with mental health problems who receive
    treatment.

    Medication treatment has been found to be effective for managing ADHD, but requires careful
    monitoring by physicians. Studies have shown that psychostimulants are highly effective for
    75-90% of children with ADHD by reducing symptoms of hyperactivity, impulsivity and
    inattention; improving classroom performance and behavior; and promoting increased interaction
    with teachers, parents and peers (U.S. Department of Health and Human Services, 1999). Some
    reported adverse effects of stimulant ADHD medications include appetite loss, abdominal pain,
    headaches, sleep disturbance, decreasing growth velocity, and less commonly, hallucinations and
    other psychotic symptoms. Additionally, treatments for children with ADHD are frequently not
    sustained despite the fact that they are at greater risk of significant problems if they
    discontinue treatment (Wolraich et al., 2011). Effective management mitigates the risk of
    discontinuing treatment.

    The intent of this measure is to ensure timely and continuous follow-up visits for children who
    are newly prescribed ADHD medication. The goal is to encourage monitoring of children for
    medication effectiveness, occurrence of side effects and adherence.

    Guidance: CUMULATIVE MEDICATION DURATION is an individual's total number of medication days
    over a specific period; the period counts multiple prescriptions with gaps in between, but does
    not count the gaps during which a medication was not dispensed.

    To determine the cumulative medication duration, determine first the number of the medication
    Days for each prescription in the period: the number of doses divided by the dose frequency per
    day. Then add the Medication Days for each prescription without counting any days between the
    prescriptions.

    For example, there is an original prescription for 30 days with 2 refills for thirty days each.
    After a gap of 3 months, the medication was prescribed again for 60 days with 1 refill for 60
    days. The cumulative medication duration is (30 x 3) + (60 x 2) = 210 days over the 10 month
    period.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms136v10
    """

    title = 'Follow-Up Care for Children Prescribed ADHD Medication (ADD)'

    identifiers = ['CMS136v10']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'American Academy of Pediatrics. (2011, November). ADHD: Clinical practice guideline for the diagnosis, evaluation, and treatment of attention-deficit/hyperactivity disorder in children and adolescents. Pediatrics, 128(5), 1007-1022.',
        'American Academy of Pediatrics. (2000). Clinical practice guideline: Diagnosis and evaluation of the child with attention-deficit/hyperactivity disorder. Pediatrics, 105(5), 1158-1170.',
        'American Psychiatric Association. (2013). Diagnostic and statistical manual of mental disorders, 5th edition (DSM-5). Washington, DC: Author.',
        'Danielson, M. L., Bitsko, R. H., Ghandour, R. M., et al. (2016). Prevalence of parent-reported ADHD diagnosis and associated treatment among U.S. children and adolescents. Journal of Clinical Child & Adolescent Psychology, 47(2), 199-212.',
        'Jensen, P., Hinshaw, S. P., Swanson, J. M., et al. (2001). Findings from the NIMH multimodal treatment study of ADHD (MTA): Implications and applications for primary care providers. Journal of Developmental and Behavioral Pediatrics, 22(1), 60-73.',
        'National Institute on Drug Abuse. (2010, September). Common Comorbidities with Substance Use Disorders. Retrieved from http://www.drugabuse.gov/publications/research-reports/comorbidity-addiction-other-mental-illnesses/how-common-are-comorbid-drug-use-other-mental-diso',
        'Pliszka, S., & AACAP Work Group on Quality Issues. (2007). Practice parameter for the assessment and treatment of children and adolescents with attention-deficit/hyperactivity disorder. Journal of the American Academy of Child and Adolescent Psychiatry, 46(7), 894-921.',
        'Robb, J. A., Sibley, M. H., Pelham, W. E., Jr., et al. (2011, September). The estimated annual cost of ADHD to the U.S. education system. School Mental Health, 3(3), 169-177. Retrieved from http://link.springer.com/article/10.1007/s12310-011-9057-6#',
        'Strine, T. W., Lesesne, C. A., Okoro, C. A., et al. (2006). Emotional and behavioral difficulties and impairments in everyday functioning among children with a history of attention-deficit/hyperactivity disorder. Preventing Chronic Disease, 3(2), A52.',
        'Swensen, A. R., Birnbaum, H. G., Secnik, K., et al. (2003). Attention-deficit/hyperactivity disorder: Increased costs for patients and their families. Journal of the American Academy of Child Adolescent Psychiatry, 42(12), 1415-1423.',
        'U.S. Department of Health and Human Services. (1999). Mental health: A report of the surgeon general. Retrieved from http://profiles.nlm.nih.gov/ps/retrieve/ResourceMetadata/NNBBHS',
        'Wolraich, M., Brown, L., Brown, R. T., et al. (2011). ADHD: clinical practice guideline for the diagnosis, evaluation, and treatment of attention-deficit/hyperactivity disorder in children and adolescents. Pediatrics, 128(5), 1007-1022.',
        'Xiang, H., Stallones, L., Chen, G., et al. (2005). Nonfatal injuries among U.S. children with disabling conditions: Opportunity for improvement. American Journal of Public Health, 95(11), 1970-1975.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Initial Population 1: Children 6-12 years of age who were dispensed an
        ADHD medication during the Intake Period and who had a visit during the measurement period.

        Initial Population 2: Children 6-12 years of age who were dispensed an ADHD medication
        during the Intake Period and who remained on the medication for at least 210 days out of
        the 300 days following the IPSD, and who had a visit during the measurement period.
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Denominator Exclusion 1: Exclude patients diagnosed with narcolepsy at any
        point in their history or during the measurement period.

        Exclude patients who had an acute inpatient stay with a principal diagnosis of mental
        health or substance abuse during the 30 days after the IPSD.

        Exclude patients who were actively on an ADHD medication in the 120 days prior to the Index
        Prescription Start Date.

        Exclude patients whose hospice care overlaps the measurement period.

        Denominator Exclusion 2: Exclude patients diagnosed with narcolepsy at any point in their
        history or during the measurement period.

        Exclude patients who had an acute inpatient stay with a principal diagnosis of mental
        health or substance abuse during the 300 days after the IPSD.

        Exclude patients who were actively on an ADHD medication in the 120 days prior to the Index
        Prescription Start Date.

        Exclude patients whose hospice care overlaps the measurement period.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Numerator 1: Patients who had at least one face-to-face visit with a
        practitioner with prescribing authority within 30 days after the IPSD.

        Numerator 2: Patients who had at least one face-to-face visit with a practitioner with
        prescribing authority during the Initiation Phase, and at least two follow-up visits during
        the Continuation and Maintenance Phase. One of the two visits during the Continuation and
        Maintenance Phase may be a telephone visit with a practitioner.

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: American Academy of Child and Adolescent Psychiatry (AACAP)
        Practice Parameter for the Assessment and Treatment of Children and Adolescents with ADHD

        - Overall Guideline
        The key to effective long-term management of the patient with ADHD is continuity of care
        with a clinician experienced in the treatment of ADHD. The frequency and duration of
        follow-up sessions should be individualized for each family and patient, depending on the
        severity of ADHD symptoms; the degree of comorbidity of other psychiatric illness; the
        response to treatment; and the degree of impairment in home, school, work, or peer-related
        activities. The clinician should establish an effective mechanism for receiving feedback
        from the family and other important informants in the patient's environment to be sure
        symptoms are well controlled and side effects are minimal. Although this parameter does not
        seek to set a formula for the method of follow-up, significant contact with the clinician
        should typically occur two to four times per year in cases of uncomplicated ADHD and up to
        weekly sessions at times of severe dysfunction or complications of treatment.

        - Recommendation 6: A Well-Thought-Out and Comprehensive Treatment Plan Should Be Developed
        for the Patient With ADHD. The treatment plan should be reviewed regularly and modified if
        the patient's symptoms do not respond. Minimal Standard [MS]

        - Recommendation 9. During a Psychopharmacological Intervention for ADHD, the Patient
        Should Be Monitored for Treatment-Emergent Side Effects. Minimal Standard [MS]

        - Recommendation 12. Patients Should Be Assessed Periodically to Determine Whether There Is
        Continued Need for Treatment or If Symptoms Have Remitted. Treatment of ADHD Should
        Continue as Long as Symptoms Remain Present and Cause Impairment. Minimal Standard [MS]

        American Academy of Pediatrics Clinical Practice Guideline for the Diagnosis, Evaluation
        and Treatment of ADHD in Children and Adolescents

        - Action Statement 4: The primary care clinician should recognize ADHD as a chronic
        condition and, therefore, consider children and adolescents with ADHD as children and youth
        with special health care needs. Management of children and youth with special health care
        needs should follow the principles of the chronic care model and the medical home. Grade B:
        Strong Recommendation

        Additionally, in the supplemental information provided along with the 2011 American Academy
        of Pediatrics Guideline, the following recommendations are made:
        - “A face-to-face follow-up visit is recommended by the fourth week of medication, during
        which clinicians review the responses to the varying doses and monitor adverse effects,
        pulse, blood pressure, and weight.”
        - “Subsequent visits will depend on the response but should occur at least 2 times per
        year, until it is clear that target goals are progressing and stable, and then periodically
        as determined by the family and the clinician.”
        """
        pass
