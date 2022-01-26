from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AnnualWellnessVisit, Ethnicity, HomeHealthcareServices, LimitedLifeExpectancy,
    OccupationalTherapyEvaluation, OfficeVisit, OncAdministrativeSex, OphthalmologicalServices,
    Payer, PhysicalTherapyEvaluation, PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesGroupCounseling, PreventiveCareServicesIndividualCounseling,
    PreventiveCareServicesInitialOfficeVisit18AndUp, PreventiveCareServicesOther,
    PsychVisitDiagnosticEvaluation, PsychVisitPsychotherapy, Psychoanalysis, Race,
    SpeechAndHearingEvaluation, TobaccoUseCessationCounseling, TobaccoUseCessationPharmacotherapy,
    TobaccoUseScreening)


class ClinicalQualityMeasure138v9(ClinicalQualityMeasure):
    """
    Preventive Care and Screening: Tobacco Use: Screening and Cessation Intervention

    Description: Percentage of patients aged 18 years and older who were screened for tobacco use
    one or more times within 12 months AND who received tobacco cessation intervention if
    identified as a tobacco user

    Three rates are reported:
    a. Percentage of patients aged 18 years and older who were screened for tobacco use one or more
    times within 12 months
    b. Percentage of patients aged 18 years and older who were identified as a tobacco user who
    received tobacco cessation intervention
    c. Percentage of patients aged 18 years and older who were screened for tobacco use one or more
    times within 12 months AND who received tobacco cessation intervention if identified as a
    tobacco user

    Definition: Tobacco Use - Includes any type of tobacco
    Tobacco Cessation Intervention - Includes brief counseling (3 minutes or less), and/or
    pharmacotherapy -- Note: Concepts aligned with brief counseling (e.g., minimal and intensive
    advice/counseling interventions conducted both in person and over the phone) are included in
    the value set for the numerator. Other concepts such as written self-help materials (e.g.,
    brochures, pamphlets) and complementary/alternative therapies are not included in the value set
    and do not qualify for the numerator. Brief counseling also may be of longer duration or be
    performed more frequently, as evidence shows there is a dose-response relationship between the
    intensity of counseling provided (either length or frequency) and tobacco cessation rates (U.S.
    Preventive Services Task Force, 2015).

    Rationale: This measure is intended to promote adult tobacco screening and tobacco cessation
    interventions for those who use tobacco products. There is good evidence that tobacco screening
    and brief cessation intervention (including counseling and/or pharmacotherapy) is successful in
    helping tobacco users quit. Tobacco users who are able to stop using tobacco lower their risk
    for heart disease, lung disease, and stroke.

    Guidance: The requirement of two or more visits is to establish that the eligible professional
    or eligible clinician has an existing relationship with the patient for certain types of
    encounters.

    To satisfy the intent of this measure, a patient must have at least one tobacco use screening
    during the 12-month period. If a patient has multiple tobacco use screenings during the
    12-month period, only the most recent screening, which has a documented status of tobacco user
    or tobacco non-user, will be used to satisfy the measure requirements.

    If a patient uses any type of tobacco (i.e., smokes or uses smokeless tobacco), the expectation
    is that they should receive tobacco cessation intervention: either counseling and/or
    pharmacotherapy.

    As noted above in a recommendation statement from the USPSTF, the current evidence is
    insufficient to recommend electronic nicotine delivery systems (ENDS) including electronic
    cigarettes for tobacco cessation. Additionally, ENDS are not currently classified as tobacco in
    the recent evidence review to support the update of the USPSTF recommendation given that the
    devices do not burn or use tobacco leaves. In light of the current lack of evidence, the
    measure does not currently capture e-cigarette usage as either tobacco use or a cessation aid.

    If tobacco use status of a patient is unknown, the patient does not meet the screening
    component required to be counted in the numerator and should be considered a measure failure.
    Instances where tobacco use status of "unknown" is recorded include: 1) the patient was not
    screened; or 2) the patient was screened and the patient (or caregiver) was unable to provide a
    definitive answer. If the patient does not meet the screening component of the numerator but
    has an allowable medical exception, then the patient should be removed from the denominator of
    the measure and reported as a valid exception.

    In order to promote a team-based approach to patient care, the tobacco cessation intervention
    can be performed by another healthcare provider; therefore, the tobacco use screening and
    tobacco cessation intervention do not need to be performed by the same provider or clinician.

    The medical reason exception may be applied to either the screening data element OR to any of
    the applicable tobacco cessation intervention data elements (counseling and/or pharmacotherapy)
    included in the measure.

    If a patient has a diagnosis of limited life expectancy, that patient has a valid denominator
    exception for not being screened for tobacco use or for not receiving tobacco use cessation
    intervention (counseling and/or pharmacotherapy) if identified as a tobacco user.

    This measure contains three reporting rates which aim to identify patients who were screened
    for tobacco use (rate/population 1), patients who were identified as tobacco users and who
    received tobacco cessation intervention (rate/population 2), and a comprehensive look at the
    overall performance on tobacco screening and cessation intervention (rate/population 3). By
    separating this measure into various reporting rates, the eligible professional or eligible
    clinician will be able to better ascertain where gaps in performance exist, and identify
    opportunities for improvement. The overall rate (rate/population 3) can be utilized to compare
    performance to published versions of this measure prior to the 2018 performance year, when the
    measure had a single performance rate. For accountability reporting in the CMS MIPS program,
    the rate for population 2 is used for performance.

    The denominator of population criteria 2 is a subset of the resulting numerator for population
    criteria 1, as population criteria 2 is limited to assessing if patients identified as tobacco
    users received an appropriate tobacco cessation intervention. For all patients, population
    criteria 1 and 3 are applicable, but population criteria 2 will only be applicable for those
    patients who are identified as tobacco users. Therefore, data for every patient that meets the
    initial population criteria will only be submitted for population 1 and 3, whereas data
    submitted for population 2 will be for a subset of patients who meet the initial population
    criteria, as the denominator has been further limited to those who were identified as tobacco
    users.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms138v9
    """

    title = 'Preventive Care and Screening: Tobacco Use: Screening and Cessation Intervention'

    identifiers = ['CMS138v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'Siu, A. L.; U.S. Preventive Services Task Force. (2015). Behavioral and pharmacotherapy interventions for tobacco smoking cessation in adults, including pregnant women: U.S. Preventive Services Task Force recommendation statement. Annals of Internal Medicine, 163(8), 622-634. doi:10.7326/M15-2023',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients aged 18 years and older seen for at least two visits or at
        least one preventive visit during the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Population 1:
        Equals Initial Population

        Population 2:
        Equals Initial Population who were screened for tobacco use and identified as a tobacco
        user

        Population 3:
        Equals Initial Population

        Exclusions: None

        Exceptions: Population 1:
        Documentation of medical reason(s) for not screening for tobacco use (e.g., limited life
        expectancy, other medical reason)

        Population 2:
        Documentation of medical reason(s) for not providing tobacco cessation intervention (e.g.,
        limited life expectancy, other medical reason)

        Population 3:
        Documentation of medical reason(s) for not screening for tobacco use OR for not providing
        tobacco cessation intervention for patients identified as tobacco users (e.g., limited life
        expectancy, other medical reason)
        """
        pass

    def in_numerator(self):
        """
        Numerator: Population 1:
        Patients who were screened for tobacco use at least once within 12 months

        Population 2:
        Patients who received tobacco cessation intervention

        Population 3:
        Patients who were screened for tobacco use at least once within 12 months AND who received
        tobacco cessation intervention if identified as a tobacco user

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: The USPSTF recommends that clinicians ask all adults about tobacco
        use, advise them to stop using tobacco, and provide behavioral interventions and U.S. Food
        and Drug Administration (FDA)-approved pharmacotherapy for cessation to adults who use
        tobacco (Grade A Recommendation) (U.S. Preventive Services Task Force, 2015).

        The USPSTF recommends that clinicians ask all pregnant women about tobacco use, advise them
        to stop using tobacco, and provide behavioral interventions for cessation to pregnant women
        who use tobacco (Grade A Recommendation) (U.S. Preventive Services Task Force, 2015).

        The USPSTF concludes that the current evidence is insufficient to recommend electronic
        nicotine delivery systems for tobacco cessation in adults, including pregnant women. The
        USPSTF recommends that clinicians direct patients who smoke tobacco to other cessation
        interventions with established effectiveness and safety (previously stated) (Grade I
        Statement) (U.S. Preventive Services Task Force, 2015).
        """
        pass
