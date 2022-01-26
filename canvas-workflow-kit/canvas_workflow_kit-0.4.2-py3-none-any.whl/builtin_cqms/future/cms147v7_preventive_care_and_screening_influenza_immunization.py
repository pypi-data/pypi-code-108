from canvas_workflow_kit import events
from canvas_workflow_kit.protocol import ClinicalQualityMeasure
from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.recommendation import ImmunizationRecommendation
from canvas_workflow_kit.value_set.v2018 import (
    AllergyToEggs, AllergyToInfluenzaVaccine, AnnualWellnessVisit,
    CareServicesInLongTermResidentialFacility, DischargeServicesNursingFacility, EggSubstance,
    EncounterInfluenza, Ethnicity, FaceToFaceInteraction, Hemodialysis, HomeHealthcareServices,
    InfluenzaVaccination, InfluenzaVaccinationDeclined, InfluenzaVaccine_1254,
    IntoleranceToInfluenzaVaccine, NursingFacilityVisit, OfficeVisit, OncAdministrativeSex,
    OutpatientConsultation, PatientProviderInteraction, Payer, PeritonealDialysis,
    PreventiveCareEstablishedOfficeVisit0To17, PreventiveCareInitialOfficeVisit0To17,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp, PreventiveCareServicesGroupCounseling,
    PreventiveCareServicesIndividualCounseling, PreventiveCareServicesInitialOfficeVisit18AndUp,
    PreventiveCareServicesOther, PreviousReceiptOfInfluenzaVaccine, Race)  # flake8: noqa


class ClinicalQualityMeasure147v7(ClinicalQualityMeasure):
    """
    Preventive Care and Screening: Influenza Immunization

    Description: Percentage of patients aged 6 months and older seen for a visit between October 1
    and March 31 who received an influenza immunization OR who reported previous receipt of an
    influenza immunization

    Definition: Previous Receipt - receipt of the current season's influenza immunization from
    another provider OR from same provider prior to the visit to which the measure is applied
    (typically, prior vaccination would include influenza vaccine given since August 1st)

    Rationale: Influenza vaccination is the most effective protection against influenza virus
    infection (CDC, 2016). Influenza may lead to serious complications including hospitalization or
    death (CDC, 2016). Influenza vaccine is recommended for all persons aged >=6 months who do not
    have contraindications to vaccination. However, data indicate that less than half of all
    eligible individuals receive an influenza vaccination (CDC, 2015). This measure promotes annual
    influenza vaccination for all persons aged >= 6 months.

    Guidance: The timeframe for the visit during the "Encounter, Performed: Encounter-Influenza" or
    "Procedure, Performed: Peritoneal Dialysis" or "Procedure, Performed: Hemodialysis" in the
    Population Criteria-Denominator, refers to the influenza season defined by the measure: October
    through March (October 1 for the year prior to the start of the reporting period through March
    31 during the reporting period).  The "Encounter-Influenza" Grouping OID detailed in the data
    criteria section below is comprised of several individual OIDs of different encounter types.
    The individual OIDs are included in the value set and should be reviewed to determine that an
    applicable visit occurred during the timeframe for "Encounter, Performed: Encounter-Influenza"
    as specified in the denominator.

    To enable reporting of this measure at the close of the reporting period, this measure will
    only assess the influenza season that ends in March of the reporting period. The subsequent
    influenza season (ending March of the following year) will be measured and reported in the
    following year.

    To account for the majority of reporting years' appropriate flu season duration, the measure
    logic will look at the first 89 days of the measurement period for the appropriate criteria and
    actions to be present/performed (January 1 through March 31). The measure developer believes it
    is best to keep the logic as static as possible from one reporting year to the next. Therefore,
    during leap years, only encounters that occur through March 30 will be counted in the
    denominator.

    As a result of updated CDC/ACIP guidelines which include the interim recommendation that live
    attenuated influenza vaccine (LAIV) should not be used due to low effectiveness against
    influenza A(H1N1)pdm09 in the United States during the 2013-14 and 2015-16 seasons, the measure
    specifications have been updated and no longer include LAIV or intranasal flu vaccine as an
    option for numerator eligibility.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms147v7
    """

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'Seasonal Influenza: Flu Basics. Centers for Disease Control and Prevention Web site.  http://www.cdc.gov/flu/about/disease/index.htm. Updated May 4, 2016. Accessed June 23, 2016.',
        'Flu vaccination coverage: United States, 2014-15 Influenza Season. Centers for Disease Control and Prevention Web site.  http://www.cdc.gov/flu/fluvaxview/coverage-1415estimates.htm. Updated September 17, 2015. Accessed June 23, 2016.',
        'Grohskopf LA, Sokolow LZ, Broder KR, et al. Prevention and Control of Seasonal Influenza with Vaccines. MMWR Recomm Rep 2016;65(No. RR-5):1-54. DOI: http://dx.doi.org/10.15585/mmwr.rr6505a',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients aged 6 months and older seen for a visit during the
        measurement period
        """
        # FIX: what exactly is 6 months old?  Probably we need age_at
        # to return days here not fractions of a year.
        age = self.patient.age_at(self.timeframe.end)
        if age < 0.5:
            return False

        return True

    def in_denominator(self):
        """
        Denominator: Equals Initial Population and seen for a visit between October 1 and March 31

        Exclusions: None

        Exceptions: Documentation of medical reason(s) for not receiving influenza immunization
        (eg, patient allergy, other medical reasons).

        Documentation of patient reason(s) for not receiving influenza immunization (eg, patient
        declined, other patient reasons).

        Documentation of system reason(s) for not receiving influenza immunization (eg, vaccine not
        available, other system reasons).
        """
        if not self.in_initial_population():
            return False

        if self.patient.conditions.before(
                self.timeframe.start).find(IntoleranceToInfluenzaVaccine):
            return False

        # FIX: how to check for patient declined flu shot?

        return True

    def immunization_timeframe(self):
        """
        Returns the timeframe within-which the immunization is recommended, Oct 1 to March 31.
        """
        start = self.timeframe.start.replace(month=10, day=1)
        end = start.shift(months=5, days=30)
        return Timeframe(start=start, end=end)

    def in_numerator(self):
        """
        Numerator: Patients who received an influenza immunization OR who reported previous receipt
        of an influenza immunization

        Exclusions: Not Applicable
        """
        if self.patient.immunizations.within(
                self.immunization_timeframe()).find(InfluenzaVaccine_1254):
            return True

        return False

    def compute_results(self):
        """
        Clinical recommendation: Routine annual influenza vaccination is recommended for all
        persons aged >= 6 months who do not have contraindications. Optimally, vaccination should
        occur before onset of influenza activity in the community. Health care providers should
        offer vaccination by October, if possible. Vaccination should continue to be offered as
        long as influenza viruses are circulating. (CDC/Advisory Committee on Immunization
        Practices (ACIP), 2016)
        """
        patient = self.patient
        recommendations = []
        status = 'not_applicable'
        narrative = ''

        # only recommend flu vaccines between October 1 and the end of March
        immunization_timeframe = self.immunization_timeframe()
        if immunization_timeframe.contains(self.timeframe.start):
            rec = ImmunizationRecommendation(patient, InfluenzaVaccine_1254)
            recommendations.append(rec)

            # FIX: check if they already have the vaccine
            if self.patient.immunizations.within(immunization_timeframe).find(
                    InfluenzaVaccine_1254):
                status = 'current'
                narrative = f'{patient.first_name} has their {InfluenzaVaccine_1254.name} this year.'
            else:
                status = 'due'
                narrative = rec.narrative

        return {'status': status, 'narrative': narrative, 'recommendations': recommendations}
