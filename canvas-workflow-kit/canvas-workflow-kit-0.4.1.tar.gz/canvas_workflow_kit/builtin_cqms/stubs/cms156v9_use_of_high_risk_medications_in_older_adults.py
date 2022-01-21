from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AmitriptylineHydrochloride, Amobarbital, Amoxapine, AnnualWellnessVisit, AntiInfectivesOther,
    Atropine, Benztropine, Brompheniramine, Butabarbital, Butalbital, Carbinoxamine,
    CareServicesInLongTermResidentialFacility, Carisoprodol, Chlorpheniramine, Chlorpropamide,
    Chlorzoxazone, Clemastine, Clomipramine, ConjugatedEstrogens, CyclobenzaprineHydrochloride,
    Cyproheptadine, DesiccatedThyroid, Desipramine, Dexbrompheniramine, Dexchlorpheniramine,
    Dicyclomine, Dimenhydrinate, Diphenhydramine, DiphenhydramineHydrochloride, Dipyridamole,
    DischargeServicesNursingFacility, Disopyramide, Doxylamine, EncounterInpatient,
    ErgoloidMesylates, EsterifiedEstrogens, Estradiol, Estropipate, Ethnicity, Glyburide,
    Guanfacine, HomeHealthcareServices, HospiceCareAmbulatory, Hydroxyzine, Hyoscyamine,
    Imipramine, Indomethacin, Isoxsuprine, KetorolacTromethamine,
    ListOfSingleRxnormCodeConceptsForHighRiskDrugsForTheElderly, Meclizine, Megestrol, Meperidine,
    Meprobamate, Metaxalone, Methocarbamol, Methyldopa, Nifedipine, NonbenzodiazepineHypnotics,
    Nortriptyline, NursingFacilityVisit, OfficeVisit, OncAdministrativeSex, OphthalmologicServices,
    Orphenadrine, Paroxetine, Payer, Pentobarbital, Phenobarbital,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, PromethazineHydrochloride, Propantheline,
    Protriptyline, Race, Scopolamine, Secobarbital, Trihexyphenidyl, Trimipramine, Triprolidine)


class ClinicalQualityMeasure156v9(ClinicalQualityMeasure):
    """
    Use of High-Risk Medications in Older Adults

    Description: Percentage of patients 65 years of age and older who were ordered at least two of
    the same high-risk medications.

    Definition: A high-risk medication is identified by either of the following:
         a. A prescription for medications classified as high risk at any dose and for any duration
         b. Prescriptions for medications classified as high risk at any dose with greater than a
    90 day supply

    Rationale: Certain medications (MacKinnon & Hepler, 2003) are associated with increased risk of
    harm from drug side-effects and drug toxicity and pose a concern for patient safety. There is
    clinical consensus that these drugs pose increased risks in older adults (Kaufman, Brodin, &
    Sarafian, 2005). Potentially inappropriate medication use in older adults has been connected to
    significantly longer hospital stay lengths and increased hospitalization costs (Hagstrom et
    al., 2015) as well as increased risk of death (Lau et al. 2004).

    Older adults receiving inappropriate medications are more likely to report poorer health status
    at follow-up, compared to those who receive appropriate medications (Fu, Liu, & Christensen,
    2004). A study of the prevalence of potentially inappropriate medication use in older adults
    found that 40 percent of individuals 65 and older filled at least one prescription for a
    potentially inappropriate medication and 13 percent filled two or more (Fick et al., 2008).
    While some adverse drug events are unavoidable, studies estimate that between 30 and 80 percent
    of adverse drug events in older adults are preventable (MacKinnon & Hepler, 2003).

    Reducing the number of inappropriate prescriptions can lead to improved patient safety and
    significant cost savings.  Conservative estimates of extra costs due to potentially
    inappropriate medications in older adults average $7.2 billion a year (Fu et al., 2007 ).
    Medication use by older adults will likely increase further as the U.S. population ages, new
    drugs are developed, and new therapeutic and preventive uses for medications are discovered
    (Rothberg et al., 2008). The annual direct costs of preventable adverse drug events (ADEs) in
    the Medicare population have been estimated to exceed $800 million (Institute of Medicine,
    2007). By the year 2030, nearly one in five U.S. residents is expected to be aged 65 years or
    older; this age group is projected to more than double in number from 38.7 million in 2008 to
    more than 88.5 million in 2050.  Likewise, the population aged 85 years or older is expected to
    increase almost four-fold, from 5.4 million to 19 million between 2008 and 2050.  As the older
    adult population continues to grow, the number of older adults who present with multiple
    medical conditions for which several medications are prescribed will continue to increase,
    resulting in polypharmacy concerns (Gray & Gardner, 2009).

    Guidance: The intent of the measure is to assess if the patient has been prescribed at least
    two of the same high-risk medications on different days.

    The intent of the measure is to assess if the reporting provider ordered the high-risk
    medication(s). If the patient had a high-risk medication previously prescribed by another
    provider, they would not be counted towards the numerator unless the reporting provider also
    ordered a high-risk medication for them.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms156v9
    """

    title = 'Use of High-Risk Medications in Older Adults'

    identifiers = ['CMS156v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'American Geriatrics Society 2015 Beers Criteria Update Expert Panel. (2015). American Geriatrics Society 2015 updated Beers criteria for potentially inappropriate medication use in older adults. Journal of the American Geriatrics Society, 63(11), 2227-2246.',
        'Beers, M. H. (1997). Explicit criteria for determining potentially inappropriate medication use by the elderly. Archives of Internal Medicine, 157, 1531-1536.',
        'Campanelli, C. M. (2012). American Geriatrics Society updated Beers criteria for potentially inappropriate medication use in older adults: The American Geriatrics Society 2012 Beers Criteria Update Expert Panel. Journal of the American Geriatrics Society, 60(4), 616.',
        'Fick, D. M., Cooper J. W., Wade, W. E., et al. (2003). Updating the Beers criteria for potentially inappropriate medication use in older adults. Archives of Internal Medicine, 163(22), 2716-2724.',
        'Fick, D. M., Mion, L. C., Beers, M. H., et al. (2008). Health outcomes associated with potentially inappropriate medication use in older adults. Research in Nursing & Health, 31(1), 42-51.',
        'Fu, A. Z., Liu, G. G., & Christensen, D. B. (2004). Inappropriate medication use and health outcomes in the elderly. Journal of the American Geriatrics Society, 52(11), 1934-1939.',
        'Gray, C. L., & Gardner, C. (2009). Adverse drug events in the elderly: An ongoing problem. Journal of Managed Care & Specialty Pharmacy, 15(7), 568-571.',
        'Hagstrom, K., Nailor, M., Lindberg, M., Hobbs, L., & Sobieraj, D. M. 2015. Association Between Potentially Inappropriate Medication Use in Elderly Adults and Hospital-Related Outcomes. Journal of the American Geriatrics Society, 63(1), 185-186.',
        'Institute of Medicine, Committee on Identifying and Preventing Medication Errors. (2007). Preventing medication errors. Aspden, P., Wolcott, J. A., Bootman, J. L., & Cronenwatt, L. R. (eds.). Washington, DC: National Academy Press.',
        'Kaufman, M. B., Brodin, K. A., & Sarafian, A. (2005, April/May). Effect of prescriber education on the use of medications contraindicated in older adults in a managed Medicare population. Journal of Managed Care & Specialty Pharmacy, 11(3), 211-219.',
        'Lau, D.T., J.D., Kasper, D.E., Potter, A. Lyles. (2004). Potentially Inappropriate Medication Prescriptions Among Elderly Nursing Home Residents: Their Scope and Associated Resident and Facility Characteristics. Health Services Research, 39(5), 1257-1276.',
        'MacKinnon, N. J., & Hepler, C. D. (2003). Indicators of preventable drug-related morbidity in older adults: Use within a managed care organization. Journal of Managed Care & Specialty Pharmacy, 9(2), 134-141.',
        'Rothberg, M. B., Perkow, P. S., Liu, F., et al. (2008). Potentially inappropriate medication use in hospitalized elders. Journal of Hospital Medicine, 3(2), 91-102.',
        'Zhan, C., Sangl, J., Bierman, A. S., et al. (2001). Potentially inappropriate medication use in the community-dwelling elderly. JAMA, 286(22), 2823-2868.',
        '2019 American Geriatrics Society Beers Criteria Update Expert Panel. (2019). American Geriatrics Society 2019 Updated AGS Beers Criteria for Potentially Inappropriate Medication Use in Older Adults. Journal of the American Geriatrics Society, 67(4), 674-694.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients 65 years and older who had a visit during the measurement
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
        Numerator: Patients with at least two orders for the same high-risk medication on different
        days during the measurement period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: The measure is based on recommendations from the American
        Geriatrics Society Beers Criteria[R] for Potentially Inappropriate Medication Use in Older
        Adults (2019 Update). The criteria were developed through key clinical expert consensus
        processes by Beers in 1997, Zhan in 2001 and an updated process by Fick et al. in 2003,
        2012, 2015, and 2019. The Beers Criteria identifies lists of drugs that are potentially
        inappropriate for all older adults and drugs that are potentially inappropriate in older
        adults based on various high-risk factors such as dosage, days supply and underlying
        diseases or conditions.
        NCQA's Geriatric Measurement Advisory Panel recommended a subset of drugs that should be
        used with caution in older adults for inclusion in the measure based upon the
        recommendations in the Beers Criteria.
        """
        pass
