from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AcuteInpatient, AnnualWellnessVisit, CareServicesInLongTermResidentialFacility, CtColonography,
    DementiaMedications, Ed, EncounterInpatient, Ethnicity, FecalOccultBloodTestFobt, FitDna,
    FrailtyDevice, FrailtyDiagnosis, FrailtyEncounter, FrailtySymptom, HomeHealthcareServices,
    HospiceCareAmbulatory, MalignantNeoplasmOfColon, NonacuteInpatient, NursingFacilityVisit,
    Observation, OfficeVisit, OncAdministrativeSex, Outpatient, Payer,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, Race)


class ClinicalQualityMeasure130v9(ClinicalQualityMeasure):
    """
    Colorectal Cancer Screening

    Description: Percentage of adults 50-75 years of age who had appropriate screening for
    colorectal cancer

    Definition: None

    Rationale: Colorectal cancer represents eight percent of all new cancer cases and is the second
    leading cause of cancer deaths in the United States. In 2019, an estimated 145,600 new cases of
    colorectal cancer and an estimated 51,020 deaths attributed to it. According to the National
    Cancer Institute, about 4.2 percent of men and women will be diagnosed with colorectal cancer
    at some point during their lifetimes. For most adults, older age is the most important risk
    factor for colorectal cancer, although being male and black are also associated with higher
    incidence and mortality. Colorectal cancer is most frequently diagnosed among people 65 to 74
    years old (National Cancer Institute, 2019).

    Screening can be effective for finding precancerous lesions (polyps) that could later become
    malignant, and for detecting early cancers that can be more easily and effectively treated.
    Precancerous polyps usually take about 10 to 15 years to develop into colorectal cancer, and
    most can be found and removed before turning into cancer. The five-year relative survival rate
    for people whose colorectal cancer is found in the early stage before it has spread is about 90
    percent (American Cancer Society, 2018).

    Guidance: Patient self-report for procedures as well as diagnostic studies should be recorded
    in "Procedure, Performed" template or "Diagnostic Study, Performed" template in QRDA-1.

    Do not count digital rectal exams (DRE), fecal occult blood tests (FOBTs) performed in an
    office setting or performed on a sample collected via DRE.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms130v9
    """

    title = 'Colorectal Cancer Screening'

    identifiers = ['CMS130v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'American Cancer Society. (2018). Can Colorectal Polyps and Cancer Be Found Early? Retrieved October 17, 2019, from https://www.cancer.org/cancer/colon-rectal-cancer/detection-diagnosis-staging/detection.html',
        'National Cancer Institute. (2019). SEER Cancer Statistics Review, 1975-2016. Retrieved October 17, 2019, from SEER website: https://seer.cancer.gov/csr/1975_2016/index.html',
        'US Preventive Services Task Force, Bibbins-Domingo, K., Grossman, D. C., Curry, S. J., Davidson, K. W., Epling, J. W., … Siu, A. L. (2016). Screening for Colorectal Cancer: US Preventive Services Task Force Recommendation Statement. JAMA, 315(23), 2564–2575. https://doi.org/10.1001/jama.2016.5989',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients 50-75 years of age with a visit during the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Exclude patients whose hospice care overlaps the measurement period.

        Exclude patients with a diagnosis or past history of total colectomy or colorectal cancer.

        Exclude patients 66 and older who are living long term in an institution for more than 90
        consecutive days during the measurement period.

        Exclude patients 66 and older with advanced illness and frailty because it is unlikely that
        patients will benefit from the services being measured.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients with one or more screenings for colorectal cancer. Appropriate
        screenings are defined by any one of the following criteria:
        - Fecal occult blood test (FOBT) during the measurement period
        - Flexible sigmoidoscopy during the measurement period or the four years prior to the
        measurement period
        - Colonoscopy during the measurement period or the nine years prior to the measurement
        period
        - FIT-DNA during the measurement period or the two years prior to the measurement period
        - CT Colonography during the measurement period or the four years prior to the measurement
        period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: The U.S. Preventive Services Task Force (2016) recommends
        screening for colorectal cancer starting at age 50 years and continuing until age 75 years.
        This is a Grade A recommendation (U.S. Preventive Services Task Force, 2016).
        Appropriate screenings are defined by any one of the following:
        -Colonoscopy (every 10 years)
        -Flexible sigmoidoscopy (every 5 years)
        -Fecal occult blood test (annually)
        -FIT-DNA (every 3 years)
        -Computed tomographic colonography (every 5 years)
        """
        pass
