from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AlcoholAndDrugDependence, AlcoholAndDrugDependenceTreatment, DetoxificationVisit,
    DischargeServicesHospitalInpatient, DischargeServicesHospitalInpatientSameDayDischarge,
    EmergencyDepartmentVisit, EncounterInpatient, Ethnicity, HospiceCareAmbulatory,
    HospitalInpatientVisitInitial, HospitalObservationCareInitial, OfficeVisit,
    OncAdministrativeSex, OpiateAntagonists, Payer, PsychVisitPsychotherapy, Race,
    TelehealthServices)


class ClinicalQualityMeasure137v9(ClinicalQualityMeasure):
    """
    Initiation and Engagement of Alcohol and Other Drug Dependence Treatment

    Description: Percentage of patients 13 years of age and older with a new episode of alcohol or
    other drug abuse or (AOD) dependence who received the following. Two rates are reported.

    a. Percentage of patients who initiated treatment including either an intervention or
    medication for the treatment of AOD abuse or dependence within 14 days of the diagnosis
    b. Percentage of patients who engaged in ongoing treatment including two additional
    interventions or a medication for the treatment of AOD abuse or dependence within 34 days of
    the initiation visit. For patients who initiated treatment with a medication, at least one of
    the two engagement events must be a treatment intervention.

    Definition: The initiation visit is the first visit for alcohol or other drug dependence
    treatment within 14 days after a diagnosis of alcohol or other drug dependence.

    Treatment includes inpatient AOD admissions, outpatient visits, intensive outpatient encounters
    or partial hospitalization.

    The Intake Period: January 1-November 14 of the measurement year. The Intake Period is used to
    capture new episodes of Alcohol or Drug Dependence. The November 14 cut-off date ensures that
    all services can occur before the measurement period ends.

    Rationale: There are more deaths, illnesses and disabilities from substance abuse than from any
    other preventable health condition. In 2017, 19.7 million individuals in the U.S. age 12 or
    older (approximately 8 percent of the population) were classified as having an SUD within the
    past year (SAMHSA, 2018). Despite the high prevalence of SUD in the U.S., only 20 percent of
    individuals with SUD receive any substance use treatment and only 13 percent receive treatment
    in a specialty SUD program (SAMHSA, 2018a).

    Guidance: The new episode of alcohol and other drug dependence should be the first episode of
    the measurement period that is not preceded in the 60 days prior by another episode of alcohol
    or other drug dependence.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms137v9
    """

    title = 'Initiation and Engagement of Alcohol and Other Drug Dependence Treatment'

    identifiers = ['CMS137v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'American Psychiatric Association: Work Group on Substance Use Disorders. (2006). Practice Guideline for the Treatment of Patients with Substance Use Disorders Second Edition. American Psychiatric Association (APA); 2006 Aug. 276 pg. [1789 references]. Retrieved from https://psychiatryonline.org/pb/assets/raw/sitewide/practice_guidelines/guidelines/substanceuse.pdf',
        'Michigan Quality Improvement Consortium. (2017). Screening, diagnosis, and referral for substance use disorders. Southfield, (MI): Michigan Quality Improvement Consortium. Retrieved from http://www.mqic.org/pdf/mqic_screening_diagnosis_and_referral_for_substance_use_disorders_cpg.pdf',
        'Schneider Institute for Health Policy, Brandeis University. 2001. Substance Abuse: The Nation\'s Number One Health Problem. Princeton: Robert Wood Johnson Foundation.',
        'Department of Veteran Affairs, Department of Defense. (2015). VA/DoD Clinical Practice Guideline for the Management of Substance Use Disorders. Washington DC: Department of Veterans Affairs, Department of Defense.',
        'Kampman, K., Jarvis, M. (2015). American Society of Addiction Medicine (ASAM) National Practice Guideline for the Use of Medications in the Treatment of Addiction Involving Opioid Use. Journal of Addiction Medicine; 9(5): 358–367. DOI: 10.1097/ADM.0000000000000166.',
        'Pietras, S., M. Azur, J. Brown. 2015. Review of Medication-Assisted Treatment Guidelines and Measures for Opioid and Alcohol Use. (ASPE). Report prepared by Mathematica Policy Research for the U.S. Department of Health and Human Services, Assistant Secretary for Planning and Evaluation, Office of Disability, Aging and Long-Term Care Policy. https://aspe.hhs.gov/sites/default/files/pdf/205171/MATguidelines.pdf (November 16, 2016)',
        'Reus, V. et al. (2018). Practice Guideline for the Pharmacological Treatment of Patients with Alcohol Use Disorder. American Journal of Psychiatry, 175(1), 86-90. doi:10.1176/appi.ajp.2017.1750101',
        'Substance Abuse and Mental Health Services Administration (SAMHSA). 2018a. “Key Substance Use and Mental Health Indicators in the United States: Results from the 2017 National Survey on Drug Use and Health.” Retrieved from https://www.samhsa.gov/data/sites/default/files/cbhsq-reports/NSDUHFFR2017/NSDUHFFR2017.htm#sud11',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients age 13 years of age and older who were diagnosed with a new
        episode of alcohol, opioid, or other drug abuse or dependency during a visit between
        January 1 and November 14 of the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Exclude patients with a previous active diagnosis of alcohol, opioid or other
        drug abuse or dependence in the 60 days prior to the first episode of alcohol or drug
        dependence.

        Exclude patients whose hospice care overlaps the measurement period.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Numerator 1: Initiation of treatment includes either an intervention or
        medication for the treatment of AOD abuse or dependence within 14 days of the diagnosis.

        Numerator 2: Engagement in ongoing treatment includes two additional interventions or a
        medication for the treatment of AOD abuse or dependence within 34 days of the initiation
        visit. For patients who initiated treatment with a medication, at least one of the two
        engagement events must be a treatment intervention (i.e., engagement for these members
        cannot be satisfied with medication treatment alone).

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: American Psychiatric Association (2018)
        * Patients with alcohol use disorder should have a documented comprehensive and person-
        centered treatment plan that includes evidence-based nonpharmacological and pharmacological
        treatments. [1C]
        * Naltrexone or acamprosate be offered to patients with moderate to severe alcohol use
        disorder who have a goal of reducing alcohol consumption or achieving abstinence, prefer
        pharmacotherapy or have not responded to nonpharmacological treatments alone, and have no
        contraindications to the use of these medications. [1B]
        * Disulfiram should be offered to patients with moderate to severe alcohol use disorder who
        have a goal of achieving abstinence, prefer disulfiram or are intolerant to or have not
        responded to naltrexone and acamprosate, are capable of understanding the risks of alcohol
        consumption while taking disulfiram, and have no contraindications to the use of this
        medication. [2C]
        * Topiramate or gabapentin be offered to patients with moderate to severe alcohol use
        disorder who have a goal of reducing alcohol consumption or achieving abstinence, prefer
        topiramate or gabapentin or are intolerant to or have not responded to naltrexone and
        acamprosate, and have no contraindications to the use of these medications. [2C]

        American Psychiatric Association (2006)
        * Because many substance use disorders are chronic, patients usually require long-term
        treatment, although the intensity and specific components of treatment may vary over time
        [I rating].
        * It is important to intensify the monitoring for substance use during periods when the
        patient is at a high risk of relapsing, including during the early stages of treatment,
        times of transition to less intensive levels of care, and the first year after active
        treatment has ceased [I rating].
        * Outpatient treatment of substance use disorders is appropriate for patients whose
        clinical condition or environmental circumstances do not require a more intensive level of
        care [I rating]. As in other treatment settings, a comprehensive approach is optimal,
        using, where indicated, a variety of psychotherapeutic and pharmacological interventions
        along with behavioral monitoring [I rating ].
        * Disulfiram is also recommended for patients with alcohol dependence [II rating].
        * Naltrexone, injectable naltrexone, acamprosate, a y-aminobutyric acid (GABA) are
        recommended for patients with alcohol dependence [I rating]. Disulfiram is also recommended
        for patients with alcohol dependence [II rating].
        * Methadone and buprenorphine are recommended for patients with opioid dependence [I
        rating].
        * Naltrexone is an alternative strategy [I rating].

        American Society of Addiction Medicine (2015)
        * Methadone and buprenorphine are recommended for opioid use disorder treatment and
        withdrawal management.
        * Naltrexone (oral; extended-release injectable) is recommended for relapse prevention.

        Michigan Quality Improvement Consortium (2017)
        *Patients with substance use disorder or risky substance use: Patient Education and Brief
        Intervention by PCP or Trained Staff (e.g. RN, MSW)
        *If diagnosed with substance use disorder or risky substance use, initiate an intervention
        within 14 days.
        *Frequent follow-up is helpful to support behavior change; preferably 2 visits within 30
        days.
        *Refer to a substance abuse health specialist, an addiction physician specialist, or a
        physician experienced in pharmacologic management of addiction.

        Department of Veterans Affairs/Department of Defense (2015)
        * Offer referral to specialty SUD care for addiction treatment if based on willingness to
        engage. [B]
        * For patients with moderate-severe alcohol use disorder, we recommend: Acamprosate,
        Disulfiram, Naltrexone- oral or extended release, or Topiramate. [A]
        * Medications should be offered in combined with addiction-focused counseling. offering one
        or more of the following interventions considering patient preference and provider
        training/competence: Behavioral Couples Therapy for alcohol use disorder, Cognitive
        Behavioral Therapy for substance use disorders, Community Reinforcement Approach,
        Motivational Enhancement Therapy, 12-Step Facilitation. [A]
        * For patients with opioid use disorder we recommend buprenorphine/naloxone or methadone in
        an Opioid Treatment Program. For patients for whom agonist treatment is contraindicated,
        unacceptable, unavailable, or discontinued, we recommend extended-release injectable
        naltrexone. [A]
        * For patients initiated in an intensive phase of outpatient or residential treatment,
        recommend ongoing systematic relapse prevention efforts or recovery support, individualized
        on the basis of treatment response. [A]
        """
        pass
