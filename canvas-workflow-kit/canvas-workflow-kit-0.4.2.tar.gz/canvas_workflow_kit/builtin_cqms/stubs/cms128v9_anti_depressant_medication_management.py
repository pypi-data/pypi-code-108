from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AnnualWellnessVisit, AntidepressantMedication, EncounterInpatient, Ethnicity,
    HomeHealthcareServices, HospiceCareAmbulatory, MajorDepression, NursingFacilityVisit,
    OfficeVisit, OncAdministrativeSex, Payer, PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, PsychVisitDiagnosticEvaluation,
    PsychVisitPsychotherapy, Race, TelephoneEvaluation, TelephoneManagement)


class ClinicalQualityMeasure128v9(ClinicalQualityMeasure):
    """
    Anti-depressant Medication Management

    Description: Percentage of patients 18 years of age and older who were treated with
    antidepressant medication, had a diagnosis of major depression, and who remained on an
    antidepressant medication treatment. Two rates are reported.
    a. Percentage of patients who remained on an antidepressant medication for at least 84 days (12
    weeks).
    b. Percentage of patients who remained on an antidepressant medication for at least 180 days (6
    months).

    Definition: Index Prescription Start Date (IPSD): The earliest prescription dispensing event
    for an antidepressant medication during the period of 245 days prior to the start of the
    measurement period through 120 days after the start of the measurement period.
    The "continuous treatment" described in this measure allows for gaps in medication treatment up
    to a total 30 days during the 114-day period (numerator 1) or 51 days during the 231-day period
    (numerator 2). Gaps can include either gaps used to change medication, or treatment gaps to
    refill the same medication.

    Rationale: In 2017, over 17 million adults in the United States had at least one major
    depressive episode in the past 12 months (SAMHSA, 2018), and depression is estimated to affect
    nearly a quarter of adults in their lifetime (Burcusa & Iacono, 2007). Depression is associated
    with other chronic diseases, as it adversely affects the course, complications and management
    of other chronic medical illnesses such as diabetes, cancer, cardiovascular disease and asthma
    (Katon & Guico-Pabia, 2011).

    Symptoms of depression include appetite and sleep disturbances, anxiety, irritability and
    decreased concentration (Charbonneau
    et al., 2005). The American Psychiatric Association recommends use of antidepressant medication
    and behavioral therapies, such as psychotherapy, to treat depression (American Psychiatric
    Association, 2010).

    For the past 50 years, antidepressant medication has proven to be effective especially for
    patients with more severe symptoms (Fournier et al., 2010). Among patients who initiate
    antidepressant treatment, one in three discontinues treatment within one month, before the
    effect of medication can be assessed, and nearly one in two discontinues treatment within three
    months (Simon, 2002).

    Clinical guidelines for depression emphasize the importance of effective clinical management in
    increasing patients’ medication compliance, monitoring treatment effectiveness, and identifying
    and managing side effects. If pharmacological treatment is initiated, appropriate dosing and
    continuation of therapy through the acute and continuation phases decrease recurrence of
    depression. Thus, evaluation of duration of pharmacological treatment serves as an important
    indicator in promoting patient compliance with the establishment and maintenance of an
    effective medication regimen.

    Guidance: To identify new treatment episodes for major depression, there must be a 105-day
    negative medication history (a period during which the patient was not taking antidepressant
    medication) prior to the first dispensing event associated with the Index Episode Start Date
    (Index Prescription Start Date).

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms128v9
    """

    title = 'Anti-depressant Medication Management'

    identifiers = ['CMS128v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'American Psychiatric Association. (2010). Practice guideline for the treatment of patients with major depressive disorder, 3rd edition. Arlington: Author.',
        'Burcusa, S. L., & Iacono, W. G. (2007). Risk for recurrence in depression. Clinical Psychology Review, 27(8), 959-985.',
        'Charbonneau, A., Bruning, W., Titus-Howard, T., et al. (2005). The community initiative on depression: Report from a multiphase work site depression intervention. Journal of Occupational and Environmental Medicine, 47(1), 60-67.',
        'Fournier, J. C., DeRubeis, R. J., Hollon, S. D., et al. (2010). Antidepressant drug effects and depression severity: A patient-level meta-analysis. JAMA, 303(1), 47-53.',
        'Katon, W., & Guico-Pabia, C. J. (2011). Improving quality of depression care using organized systems of care: A review of the literature. The Primary Care Companion to CNS Disorders, 13(1).',
        'Simon, G. E. (2002). Evidence review: Efficacy and effectiveness of antidepressant treatment in primary care. General Hospital Psychiatry, 24(4), 213-224.',
        'Substance Abuse and Mental Health Services Administration (SAMHSA). (2018). Results from the 2017 National Survey on drug use and health: detailed tables. Retrieved from: https://www.samhsa.gov/data/sites/default/files/cbhsq-reports/NSDUHDetailedTabs2017/NSDUHDetailedTabs2017.htm#tab8-56A',
        'Department of Veterans Affairs, and Health Affairs, Department of Defense. (2000). Management of Major Depressive Disorder in Adults in the Primary Care Setting. Retrieved from: http://www.oqp.med.va.gov/cpg/MDD/MDD_Base.htm',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients 18 years of age and older who were dispensed antidepressant
        medications within 245 days (8 months) prior to the measurement period through the first
        120 days (4 months) of the measurement period, and were diagnosed with major depression 60
        days prior to, or 60 days after the dispensing event and had a visit 60 days prior to, or
        60 days after the dispensing event
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Patients who were actively on an antidepressant medication in the 105 days
        prior to the Index Prescription Start Date.

        Exclude patients whose hospice care overlaps the measurement period.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Numerator 1: Patients who have received antidepressant medication for at least
        84 days (12 weeks) of continuous treatment during the 114-day period following the Index
        Prescription Start Date.

        Numerator 2: Patients who have received antidepressant medications for at least 180 days (6
        months) of continuous treatment during the 231-day period following the Index Prescription
        Start Date.

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: American Psychiatric Association (2010):
        • “An antidepressant medication is recommended as an initial treatment choice for patients
        with mild to moderate major depressive disorder [I: Recommended with substantial clinical
        confidence] and definitely should be provided for those with severe major depressive
        disorder unless electroconvulsive therapy (ECT) is planned [I: Recommended with substantial
        clinical confidence].”

        • Patients should be given a realistic notion of what can be expected during the different
        phases of treatment, including the likely time course of symptom response and the
        importance of adherence for successful treatment and prophylaxis [I].

        • During the acute phase of treatment, patients should be
        carefully and systematically monitored on a regular basis
        to assess their response to pharmacotherapy, identify the
        emergence of side effects (e.g., gastrointestinal symptoms,
        sedation, insomnia, activation, changes in weight, and cardiovascular,
        neurological, anticholinergic, or sexual side effects),
        and assess patient safety [I].

        • “During the continuation phase of treatment, the patient should be carefully monitored
        for signs of possible relapse [I: Recommended with substantial clinical confidence].
        Systematic assessment of symptoms, side effects, adherence, and functional status is
        essential [I: Recommended with substantial clinical confidence], and may be facilitated
        through the use of clinician- and/or patient-administered rating scales [II: Recommended
        with moderate clinical confidence]. To reduce the risk of relapse, patients who have been
        treated successfully with antidepressant medications in the acute phase should continue
        treatment with these agents for 4–9 months [I: Recommended with substantial clinical
        confidence].”

        Department of Veterans Affairs, and Health Affairs, Department of Defense (2000):
        •“When antidepressant pharmacotherapy is used, the following key messages should be given
        to enhance adherence to medication: [B: A recommendation that clinicians provide (the
        service) to eligible patients.]
        • Most people need to be on medication for at least 6 to 12 months after adequate response
        • It usually takes 2 to 6 weeks before improvements are seen
        • Continue to take the medication even after feeling better
        • Do not discontinue taking medications without first discussing with your provider.”
        """
        pass
