from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AnnualWellnessVisit, CareServicesInLongTermResidentialFacility,
    DischargeServicesNursingFacility_1065, EncounterInpatient, Ethnicity, HomeHealthcareServices,
    HospiceCareAmbulatory, NursingFacilityVisit, OfficeVisit, OncAdministrativeSex, Payer,
    PneumococcalVaccine, PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, Race)


class ClinicalQualityMeasure127v9(ClinicalQualityMeasure):
    """
    Pneumococcal Vaccination Status for Older Adults

    Description: Percentage of patients 65 years of age and older who have ever received a
    pneumococcal vaccine

    Definition: None

    Rationale: Pneumonia is a common cause of illness and death in the elderly and persons with
    certain underlying conditions. The major clinical syndromes of pneumococcal disease include
    pneumonia, bacteremia and meningitis, with pneumonia being the most common (Centers for Disease
    Control and Prevention [CDC], 2015a). Pneumonia symptoms generally include fever, chills,
    pleuritic chest pain, cough with sputum, dyspnea, tachypnea, hypoxia tachycardia, malaise and
    weakness. There are an estimated 400,000 cases of pneumonia in the U.S. each year and a 5
    percent-7 percent mortality rate, although it may be higher among older adults and adults in
    nursing homes (CDC, 2015b; Janssens & Krause, 2004).

    Among the 91.5 million US adults aged > 50 years, 29,500 cases of IPD, 502,600 cases of
    nonbacteremic pneumococcal pneumonia and 25,400 pneumococcal-related deaths are estimated to
    occur yearly; annual direct and indirect costs are estimated to total $3.7 billion and $1.8
    billion, respectively. Pneumococcal disease remains a substantial burden among older US adults,
    despite increased coverage with 23-valent pneumococcal polysaccharide vaccine, (PPV23) and
    indirect benefits afforded by PCV7 vaccination of young children (Weycker et al., 2011).

    Pneumococcal vaccines have been shown to be highly effective in preventing invasive
    pneumococcal disease. When comparing costs, outcomes and quality adjusted life years,
    immunization with the two recommended pneumococcal vaccines was found to be more economically
    efficient than no vaccination, with an incremental cost-effectiveness ratio of $25,841 per
    quality-adjusted life year gained (Chen et al., 2014).

    Guidance: Patient self-report for procedures as well as immunization s should be recorded in
    'Procedure, Performed' template or 'Immunization, Administered' template in QRDA-1.

    ACIP (Kobayashi, 2015) provides guidance about the proper interval and relative timing for the
    administration of two pneumococcal vaccines; this measure assesses whether patients have
    received at least one of either vaccine.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms127v9
    """

    title = 'Pneumococcal Vaccination Status for Older Adults'

    identifiers = ['CMS127v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'Centers for Disease Control and Prevention. (2015a, June 10). Pneumococcal disease: Symptoms and complications. Retrieved from https://www.cdc.gov/pneumococcal/about/symptoms-complications.html',
        'Centers for Disease Control and Prevention. (2015b, June 19). Pneumococcal vaccination: Clinical Features. Retrieved from http://www.cdc.gov/pneumococcal/clinicians/clinical-features.html#pneumonia',
        'Chen, J., O’Brien, M. A., Yang, H. K., et al. (2014). Cost-effectiveness of pneumococcal vaccines for adults in the United States. Advances in Therapy, 31(4), 392-409.',
        'Janssens, J. P., & Krause, K. H. (2004). Pneumonia in the very old. Lancet Infectious Diseases, 4(2), 112-124.',
        'Kobayashi, M., Bennett, N. M., Gierke, R., et al. (2015). "Intervals between PCV13 and PPSV23 vaccines: Recommendations of the Advisory Committee on Immunization Practices (ACIP)." Morbidity and Mortality Weekly Report, 64(34), 947.',
        'Janssens, J.P., and K.H. Krause. 2004. Pneumonia in the very old. Lancet Infect Dis. 4(2):112–24.',
        'National Heart, Lung, and Blood Institute. (2011). "Pneumonia." Retrieved from http://www.nhlbi.nih.gov/health/dci/Diseases/pnu/pnu_whatis.html',
        'Weycker, D., Strutton, D., Edelsberg, J., et al. (2011). "Clinical and economic burden of pneumococcal disease in older U.S. adults." Vaccine, 28(31), 4955-4960.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients 65 years of age and older with a visit during the measurement
        period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Exclude patients whose hospice care overlaps the measurement period

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients who have ever received a pneumococcal vaccination before the end of the
        measurement period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: In 2014, the Advisory Committee on Immunization Practices (ACIP)
        began recommending a dose of 13-valent pneumococcal conjugate vaccine (PCV13) be followed
        by a dose of 23-valent pneumococcal polysaccharide vaccine (PPSV23) 6-12 months later in
        adults aged 65 and older who have not previously received a pneumococcal vaccination, and
        in persons over the age of two years who are considered to be at higher risk for
        pneumococcal disease due to an underlying condition. The two vaccines should not be
        coadministered and intervals for administration of the two vaccines vary slightly depending
        on the age, risk group, and history of vaccination (Kobayashi et al., 2015).

        In 2015, ACIP updated its recommendation and changed the interval between PCV13 and PPSV23,
        from 6-12 months to at least one year for immunocompetent adults aged >=65 years who have
        not previously received pneumococcal vaccine. For immunocompromised vaccine-naïve adults,
        the minimum acceptable interval between PCV13 and PPSV23 is 8 weeks. Both immunocompetent
        and immunocompromised adults aged >=65 years who have previously received a dose of PPSV23
        when over the age of 65 should receive a dose of PCV13 at least one year after PPSV23 (>=1
        year). Immunocompetent and immunocompromised adults aged >=65 who have previously received
        a dose of PPSV23 when under the age of 65, should also receive a dose of PCV13 at least one
        year after PPSV23 (>=1 year) and then another dose of PPSV23 at least one year after PCV13.
        It is recommended that for those that have this alternative three-dose schedule (2 PPSV23
        and 1 PCV13), the three doses should be spread over a time period of five or more years
        (Kobayashi et al., 2015).
        """
        pass
