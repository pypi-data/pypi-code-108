from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AllergyToEggs, AllergyToInfluenzaVaccine, AnnualWellnessVisit,
    CareServicesInLongTermResidentialFacility, DischargeServicesNursingFacility, EggSubstance,
    EncounterInfluenza, Ethnicity, HomeHealthcareServices, InfluenzaVaccination,
    InfluenzaVaccine_1254, IntoleranceToInfluenzaVaccine, NursingFacilityVisit, OfficeVisit,
    OncAdministrativeSex, OutpatientConsultation, PatientProviderInteraction, Payer,
    PreventiveCareEstablishedOfficeVisit0To17, PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesGroupCounseling, PreventiveCareServicesIndividualCounseling,
    PreventiveCareServicesInitialOfficeVisit0To17, PreventiveCareServicesInitialOfficeVisit18AndUp,
    PreventiveCareServicesOther, PreviousReceiptOfInfluenzaVaccine, Race)


class ClinicalQualityMeasure147v10(ClinicalQualityMeasure):
    """
    Preventive Care and Screening: Influenza Immunization

    Description: Percentage of patients aged 6 months and older seen for a visit between October 1
    and March 31 who received an influenza immunization OR who reported previous receipt of an
    influenza immunization

    Definition: Previous Receipt - receipt of the current season's influenza immunization from
    another provider OR from same provider prior to the visit to which the measure is applied
    (typically, prior vaccination would include influenza vaccine given since August 1st)

    Rationale: Influenza vaccination is the most effective protection against influenza virus
    infection (Centers for Disease Control and Prevention [CDC], 2018). Influenza may lead to
    serious complications including hospitalization or death (CDC, 2018). Influenza vaccine is
    recommended for all persons aged >=6 months who do not have contraindications to vaccination.
    However, data indicate that less than half of all eligible individuals receive an influenza
    vaccination (CDC, 2015). This measure promotes annual influenza vaccination for all persons
    aged >= 6 months.

    Guidance: The timeframe for the visit during the "Encounter, Performed": "Encounter-Influenza"
    or "Procedure, Performed": "Peritoneal Dialysis" or "Procedure, Performed": "Hemodialysis" in
    the Population Criteria-Denominator, refers to the influenza season defined by the measure:
    October through March (October 1 for the year prior to the start of the reporting period
    through March 31 during the reporting period). The "Encounter-Influenza" Grouping OID detailed
    in the data criteria section below is comprised of several individual OIDs of different
    encounter types. The individual OIDs are included in the value set and should be reviewed to
    determine that an applicable visit occurred during the timeframe for "Encounter, Performed":
    "Encounter-Influenza" as specified in the denominator.

    To enable reporting of this measure at the close of the reporting period, this measure will
    only assess the influenza season that ends in March of the reporting period. The subsequent
    influenza season (ending March of the following year) will be measured and reported in the
    following year.

    Due to the changing stance of the CDC/ACIP recommendations regarding the live attenuated
    influenza vaccine (LAIV) for a particular flu season, this measure will not include the
    administration of this specific formulation of the flu vaccination. Given the variance of the
    timeframes for the annual update cycles, program implementation, and publication of revised
    recommendations from the CDC/ACIP, it has been determined that the coding for this measure will
    specifically exclude this formulation, so as not to inappropriately include this form of the
    vaccine for flu seasons when CDC/ACIP explicitly advise against it. However, it is recommended
    that all eligible professionals or eligible clinicians to review the guidelines for each flu
    season to determine appropriateness of the LAIV and other formulations of the flu vaccine.
    Should the LAIV be recommended for administration for a particular flu season, eligible
    professional or clinician may consider one of the following options: 1) satisfy the numerator
    by reporting either previous receipt or using the CVX 88 for unspecified formulation, 2) report
    a denominator exception, either as a patient reason (e.g., for patient preference) or a system
    reason (e.g., the institution only carries LAIV).

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms147v10
    """

    title = 'Preventive Care and Screening: Influenza Immunization'

    identifiers = ['CMS147v10']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'Centers for Disease Control and Prevention. (2018, October 26). About Flu. Retrieved from http://www.cdc.gov/flu/about/disease/index.htm',
        'Centers for Disease Control and Prevention. (2015, September 17). Flu vaccination coverage: United States, 2014-15 influenza season. Retrieved from http://www.cdc.gov/flu/fluvaxview/coverage-1415estimates.htm',
        'Grohskopf, L.A., Alyanak, E., Broder, K. R., Walter, E.B., Fry, A. M., Jernigan, D. B. (2019). Prevention and control of seasonal influenza with vaccines: Recommendations of the Advisory Committee on Immunization Practices—United States, 2019-20 Influenza Season. MMWR Recommendations and Reports; 38(No. RR-3), 1-21. doi: http://dx.doi.org/10.15585/mmwr.rr6803a1',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients aged 6 months and older seen for a visit during the
        measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population and seen for a visit between October 1 and March 31

        Exclusions: None

        Exceptions: Documentation of medical reason(s) for not receiving influenza immunization
        (e.g., patient allergy, other medical reasons).

        Documentation of patient reason(s) for not receiving influenza immunization (e.g., patient
        declined, other patient reasons).

        Documentation of system reason(s) for not receiving influenza immunization (e.g., vaccine
        not available, other system reasons).
        """
        pass

    def in_numerator(self):
        """
        Numerator: Patients who received an influenza immunization OR who reported previous receipt
        of an influenza immunization

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: Routine annual influenza vaccination is recommended for all
        persons aged >= 6 months who do not have contraindications. Optimally, vaccination should
        occur before onset of influenza activity in the community. Although vaccination by the end
        of October is recommended, vaccine administered in December or later, even if influenza
        activity has already begun, is likely to be beneficial in the majority of influenza seasons
        (CDC/Advisory Committee on Immunization Practices [ACIP], 2019).
        """
        pass
