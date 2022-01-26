from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AcuteInpatient, AnnualWellnessVisit, CareServicesInLongTermResidentialFacility,
    DementiaMedications, Ed, EncounterInpatient, Ethnicity, Female, FrailtyDevice,
    FrailtyDiagnosis, FrailtyEncounter, FrailtySymptom, HistoryOfBilateralMastectomy,
    HomeHealthcareServices, HospiceCareAmbulatory, Mammography, NonacuteInpatient,
    NursingFacilityVisit, Observation, OfficeVisit, OncAdministrativeSex, Outpatient, Payer,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, Race, StatusPostLeftMastectomy,
    StatusPostRightMastectomy, UnilateralMastectomyUnspecifiedLaterality)


class ClinicalQualityMeasure125v9(ClinicalQualityMeasure):
    """
    Breast Cancer Screening

    Description: Percentage of women 50-74 years of age who had a mammogram to screen for breast
    cancer in the 27 months prior to the end of the Measurement Period

    Definition: None

    Rationale: Breast cancer is one of the most common types of cancers, accounting for 15 percent
    of all new cancer diagnoses in the U.S. (Noone et al, 2018). In 2015, over 3 million women were
    estimated to be living with breast cancer in the U.S. and it is estimated that 12 percent of
    women will be diagnosed with breast cancer at some point during their lifetime (Noone et al,
    2018).

    While there are other factors that affect a woman's risk of developing breast cancer, advancing
    age is a primary risk factor. Breast cancer is most frequently diagnosed among women ages
    55-64; the median age at diagnosis is 62 years (Noone et al, 2018).

    The chance of a woman being diagnosed with breast cancer in a given year increases with age. By
    age 40, the chances are 1 in 68; by age 50 it becomes 1 in 43; by age 60, it is 1 in 29
    (American Cancer Society, 2017).

    Guidance: Patient self-report for procedures as well as diagnostic studies should be recorded
    in 'Procedure, Performed' template or 'Diagnostic Study, Performed' template in QRDA-1.

    This measure evaluates primary screening. Do not count biopsies, breast ultrasounds, or MRIs
    because they are not appropriate methods for primary breast cancer screening.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms125v9
    """

    title = 'Breast Cancer Screening'

    identifiers = ['CMS125v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'American Cancer Society. 2017. “Breast Cancer Facts & Figures 2017-2018.” (February 8, 2019). Retrieved from https://www.cancer.org/content/dam/cancer-org/research/cancer-facts-and-statistics/breast-cancer-facts-and-figures/breast-cancer-facts-and-figures-2017-2018.pdf',
        'Noone, A.M., Howlader, N., Krapcho, M., Miller, D., Brest, A., Yu, M., Ruhl, J., Tatalovich, Z., Mariotto, A., Lewis, D.R., Chen, H.S., Feuer, E.J., Cronin, K.A. (eds). 2018. “SEER Cancer Statistics Review, 1975-2015.” National Cancer Institute. Bethesda, MD. (February 8, 2019) Retrieved from https://seer.cancer.gov/csr/1975_2015/',
        'U.S. Preventive Services Task Force. (2016). Screening for breast cancer: U.S. Preventive Services Task Force recommendation statement. Annals of Internal Medicine, 164(4), 279-296.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Women 51-74 years of age with a visit during the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Women who had a bilateral mastectomy or who have a history of a bilateral
        mastectomy or for whom there is evidence of a right and a left unilateral mastectomy.

        Exclude patients whose hospice care overlaps the measurement period.

        Exclude patients 66 and older who are living long term in an institution for more than 90
        consecutive days during the measurement period.

        Exclude patients 66 and older with advanced illness and frailty because it is unlikely that
        patients will benefit from the services being measured.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Women with one or more mammograms during the 27 months prior to the end of the
        measurement period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: The U.S. Preventive Services Task Force (USPSTF) recommends
        biennial screening mammography for women aged 50-74 years (B recommendation).

        The decision to start screening mammography in women prior to age 50 years should be an
        individual one. Women who place a higher value on the potential benefit than the potential
        harms may choose to begin biennial screening between the ages of 40 and 49 years (C
        recommendation). (USPSTF, 2016)

        The USPSTF concludes that the current evidence is insufficient to assess the balance of
        benefits and harms of screening mammography in women aged 75 years or older (I statement).
        (USPSTF, 2016)

        The USPSTF concludes that the current evidence is insufficient to assess the benefits and
        harms of digital breast tomosynthesis (DBT) as a primary screening method for breast cancer
        (I Statement). (USPSTF, 2016)

        The USPSTF concludes that the current evidence is insufficient to assess the balance of
        benefits and harms of adjunctive screening for breast cancer using breast ultrasonography,
        magnetic resonance imaging, DBT, or other methods in women identified to have dense breasts
        on an otherwise negative screening mammogram (I statement). (USPSTF, 2016)
        """
        pass
