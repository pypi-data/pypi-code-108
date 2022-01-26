from typing import List

from canvas_workflow_kit import events
from canvas_workflow_kit.protocol import ClinicalQualityMeasure
from canvas_workflow_kit.recommendation import (InterviewRecommendation, InstructionRecommendation,
                                PrescribeRecommendation, Recommendation)
# flake8: noqa
from canvas_workflow_kit.value_set.v2018 import (
    AnnualWellnessVisit, Ethnicity, FaceToFaceInteraction, HealthAndBehavioralAssessmentInitial,
    HealthAndBehavioralAssessmentReassessment, HealthBehavioralAssessmentIndividual,
    HomeHealthcareServices, LimitedLifeExpectancy, OccupationalTherapyEvaluation, OfficeVisit,
    OncAdministrativeSex, OphthalmologicalServices, Payer,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp, PreventiveCareServicesGroupCounseling,
    PreventiveCareServicesIndividualCounseling, PreventiveCareServicesInitialOfficeVisit18AndUp,
    PreventiveCareServicesOther, PsychVisitDiagnosticEvaluation, PsychVisitPsychotherapy,
    Psychoanalysis, Race, SpeechAndHearingEvaluation, TobaccoNonUser,
    TobaccoUseCessationCounseling, TobaccoUseCessationPharmacotherapy, TobaccoUseScreening,
    TobaccoUser)


class ClinicalQualityMeasure138v6(ClinicalQualityMeasure):
    """
    Preventive Care and Screening: Tobacco Use: Screening and Cessation Intervention

    Description: Percentage of patients aged 18 years and older who were screened for tobacco use
    one or more times within 24 months AND who received tobacco cessation intervention if
    identified as a tobacco user

    Three rates are reported:
    a. Percentage of patients aged 18 years and older who were screened for tobacco use one or more
    times within 24 months
    b. Percentage of patients aged 18 years and older who were screened for tobacco use and
    identified as a tobacco user who received tobacco cessation intervention
    c. Percentage of patients aged 18 years and older who were screened for tobacco use one or more
    times within 24 months AND who received tobacco cessation intervention if identified as a
    tobacco user

    Definition: Tobacco Use - Includes any type of tobacco
    Tobacco Cessation Intervention - Includes brief counseling (3 minutes or less), and/or
    pharmacotherapy -- Note:  Concepts aligned with brief counseling (eg, minimal and intensive
    advice/counseling interventions conducted both in person and over the phone) are included in
    the value set for the numerator.  Other concepts such as written self-help materials (eg,
    brochures, pamphlets) and complementary/alternative therapies are not included in the value set
    and do not qualify for the numerator.

    Rationale: This measure is intended to promote adult tobacco screening and tobacco cessation
    interventions for those who use tobacco products. There is good evidence that tobacco screening
    and brief cessation intervention (including counseling and/or pharmacotherapy) is successful in
    helping tobacco users quit. Tobacco users who are able to stop using tobacco lower their risk
    for heart disease, lung disease, and stroke.

    Guidance: If a patient uses any type of tobacco (ie, smokes or uses smokeless tobacco), the
    expectation is that they should receive tobacco cessation intervention: either counseling
    and/or pharmacotherapy.

    If a patient has multiple tobacco use screenings during the 24 month period, only the most
    recent screening, which has a documented status of tobacco user or tobacco non-user, will be
    used to satisfy the measure requirements.

    If tobacco use status of a patient is unknown, the patient does not meet the screening
    component required to be counted in the numerator and should be considered a measure failure.
    Instances where tobacco use status of "unknown" is recorded include: 1) the patient was not
    screened; or 2) the patient was screened and the patient (or caregiver) was unable to provide a
    definitive answer.  If the patient does not meet the screening component of the numerator but
    has an allowable medical exception, then the patient should be removed from the denominator of
    the measure and reported as a valid exception.

    The medical reason exception may be applied to either the screening data element OR to any of
    the applicable tobacco cessation intervention data elements (counseling and/or pharmacotherapy)
    included in the measure.

    If a patient has a diagnosis of limited life expectancy, that patient has a valid denominator
    exception for not being screened for tobacco use or for not receiving tobacco use cessation
    intervention (counseling and/or pharmacotherapy) if identified as a tobacco user.

    As noted above in a recommendation statement from the USPSTF, the current evidence is
    insufficient to recommend electronic nicotine delivery systems (ENDS) including electronic
    cigarettes for tobacco cessation.  Additionally, ENDS are not currently classified as tobacco
    in the recent evidence review to support the update of the USPSTF recommendation given that the
    devices do not burn or use tobacco leaves.  In light of the current lack of evidence, the
    measure does not currently capture e-cigarette usage as either tobacco use or a cessation aid.

    The requirement of "Count >=2 Encounter, Performed" is to establish that the eligible
    professional or eligible clinician has an existing relationship with the patient for certain
    types of encounters.

    This measure contains three reporting rates which aim to identify patients who were screened
    for tobacco use (rate/population 1), patients who were identified as tobacco users and who
    received tobacco cessation intervention (rate/population 2), and a comprehensive look at the
    overall performance on tobacco screening and cessation intervention (rate/population 3). By
    separating this measure into various reporting rates, the eligible professional or eligible
    clinician will be able to better ascertain where gaps in performance exist, and identify
    opportunities for improvement. The overall rate (rate/population 3) can be utilized to compare
    performance to prior published versions of this measure.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms138v6
    """

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'Siu AL; U.S. Preventive Services Task Force. Behavioral and Pharmacotherapy Interventions for Tobacco Smoking Cessation in Adults, Including Pregnant Women: U.S. Preventive Services Task Force Recommendation Statement. Ann Intern Med. 2015 Oct 20;163(8):622-34.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients aged 18 years and older seen for at least two visits or at
        least one preventive visit during the measurement period
        """
        age = self.patient.age_at(self.timeframe.end)
        if age < 18 or age >= 76:
            return False

        # FIX: how do we count visits and tell the difference between a normal vist and a "preventive" visit?

        return True

    def in_denominator(self, population=1):
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
        Documentation of medical reason(s) for not screening for tobacco use (eg, limited life
        expectancy, other medical reason)

        Population 2:
        Documentation of medical reason(s) for not providing tobacco cessation intervention (eg,
        limited life expectancy, other medical reason)

        Population 3:
        Documentation of medical reason(s) for not screening for tobacco use OR for not providing
        tobacco cessation intervention for patients identified as tobacco users (eg, limited life
        expectancy, other medical reason)
        """
        # oddly this protocol is actually three protocols packed into
        # one with three different denominator and numerator
        # definitions.  I don't know how we'd support this from a
        # caller perspective, but for now we'll take an optional param
        # to in_denominator and in_numerator which defaults to #1.
        if not self.in_initial_population():
            return False

        if self.patient.conditions.before(self.timeframe.start).find(LimitedLifeExpectancy):
            return False

        if population in (1, 3):
            return True
        elif population == 2 and self.patient.conditions.before(
                self.timeframe.start).find(TobaccoUser):
            return True

        return False

    def in_numerator(self, population=1):
        """
        Numerator: Population 1:
        Patients who were screened for tobacco use at least once within 24 months

        Population 2:
        Patients who received tobacco cessation intervention

        Population 3:
        Patients who were screened for tobacco use at least once within 24 months AND who received
        tobacco cessation intervention if identified as a tobacco user

        Exclusions: Not Applicable
        """
        screening = self.patient.interviews.within_two_years(
            self.timeframe).find(TobaccoUseScreening)
        meds = self.patient.medications.within_two_years(
            self.timeframe).find(TobaccoUseCessationPharmacotherapy)
        counseling = self.patient.instructions.within_two_years(
            self.timeframe).find(TobaccoUseCessationCounseling)

        if population == 1:
            if screening:
                return True
        elif population == 2:
            if counseling:
                return True
        elif population == 3:
            if screening and (meds or counseling):
                return True

        return False

    def compute_results(self):
        """
        Clinical recommendation: The USPSTF recommends that clinicians ask all adults about tobacco
        use, advise them to stop using tobacco, and provide behavioral interventions and U.S. Food
        and Drug Administration (FDA)-approved pharmacotherapy for cessation to adults who use
        tobacco. (Grade A Recommendation) (U.S. Preventive Services Task Force, 2015)

        The USPSTF recommends that clinicians ask all pregnant women about tobacco use, advise them
        to stop using tobacco, and provide behavioral interventions for cessation to pregnant women
        who use tobacco. (Grade A Recommendation) (U.S. Preventive Services Task Force, 2015)

        The USPSTF concludes that the current evidence is insufficient to recommend electronic
        nicotine delivery systems for tobacco cessation in adults, including pregnant women. The
        USPSTF recommends that clinicians direct patients who smoke tobacco to other cessation
        interventions with established effectiveness and safety (previously stated). (Grade I
        Statement) (U.S. Preventive Services Task Force, 2015)
        """
        patient = self.patient

        recommendations: List[Recommendation] = []
        status = 'not_applicable'
        narrative = ''

        # no screening in 2 years?  they should be screened
        screening = patient.interviews.within_two_years(
            self.timeframe).find(TobaccoUseScreening).last()
        if not screening:
            rec = InterviewRecommendation(patient=patient, questionnaire=TobaccoUseScreening)
            recommendations.append(rec)
            status = 'due'
            narrative = rec.narrative

        else:
            # they have been screened, see if they're a smoker
            # FIX: what's the right way to do this that doesn't depend on the particular language used?
            if 'currently' in screening['results'][0]['narrative'].lower():
                # advise meds or
                meds = patient.medications.within_two_years(
                    self.timeframe).find(TobaccoUseCessationPharmacotherapy)
                counseling = patient.instructions.within_two_years(
                    self.timeframe).find(TobaccoUseCessationCounseling)
                if meds or counseling:
                    status = 'current'
                    narrative = f'{patient.first_name} is a tobacco user but has received tobacco use cessation intervention.'
                else:
                    recommendations.append(
                        InstructionRecommendation(
                            patient=patient, instruction=TobaccoUseCessationCounseling))

                    recommendations.append(
                        PrescribeRecommendation(
                            patient=patient, prescription=TobaccoUseCessationPharmacotherapy))

                    status = 'due'
                    narrative = f'{patient.first_name} is a tobacco user and should receive tobacco use cessation intervention.'

        return {'status': status, 'narrative': narrative, 'recommendations': recommendations}
