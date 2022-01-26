from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    EncounterInpatient, Ethnicity, Female, HomeHealthcareServices, HospiceCareAmbulatory, HpvTest,
    OfficeVisit, OncAdministrativeSex, PapTest, Payer,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, Race)


class ClinicalQualityMeasure124v9(ClinicalQualityMeasure):
    """
    Cervical Cancer Screening

    Description: Percentage of women 21-64 years of age who were screened for cervical cancer using
    either of the following criteria:
    *  Women age 21-64 who had cervical cytology performed within the last 3 years
    *  Women age 30-64 who had cervical human papillomavirus (HPV) testing performed within the
    last 5 years

    Definition: None

    Rationale: All women are at risk for cervical cancer. In 2019, an estimated 13,170 women were
    diagnosed with cervical cancer in the U.S., resulting in an estimated 4,250 deaths (National
    Cancer Institute, 2019). If pre-cancerous lesions are detected early by Pap tests and treated,
    the likelihood of survival is nearly 100 percent (American Cancer Society, 2019).

    Guidance: To ensure the measure is only looking for a cervical cytology test only after a woman
    turns 21 years of age, the youngest age in the initial population is 23.

    Patient self-report for procedures as well as diagnostic studies should be recorded in
    'Procedure, Performed' template or 'Diagnostic Study, Performed' template in QRDA-1.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms124v9
    """

    title = 'Cervical Cancer Screening'

    identifiers = ['CMS124v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'American Cancer Society. (2019). Cancer Prevention & Early Detection Facts & Figures 2019-2020. Atlanta: American Cancer Society.',
        'National Cancer Institute. (2019). SEER Cancer Statistics Review, 1975-2016. Retrieved October 17, 2019, from SEER website: https://seer.cancer.gov/csr/1975_2016/index.html',
        'US Preventive Services Task Force, Curry, S. J., Krist, A. H., Owens, D. K., Barry, M. J., Caughey, A. B., … Wong, J. B. (2018). Screening for Cervical Cancer: US Preventive Services Task Force Recommendation Statement. JAMA, 320(7), 674–686. https://doi.org/10.1001/jama.2018.10897',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Women 23-64 years of age with a visit during the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Women who had a hysterectomy with no residual cervix or a congenital absence of
        cervix.

        Exclude patients whose hospice care overlaps the measurement period.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Women with one or more screenings for cervical cancer. Appropriate screenings
        are defined by any one of the following criteria:
        *  Cervical cytology performed during the measurement period or the two years prior to the
        measurement period for women who are at least 21 years old at the time of the test

        *  Cervical human papillomavirus (HPV) testing performed during the measurement period or
        the four years prior to the measurement period for women who are 30 years or older at the
        time of the test

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: US Preventive Services Task Force (USPSTF) (2018) "The USPSTF
        recommends screening for cervical cancer every 3 years with cervical cytology alone in
        women aged 21 to 29 years. For women aged 30 to 65 years, the USPSTF recommends screening
        every 3 years with cervical cytology alone, every 5 years with high-risk human
        papillomavirus (hrHPV) testing alone, or every 5 years with hrHPV testing in combination
        with cytology (cotesting) (A recommendation)"

        "The USPSTF recommends against screening for cervical cancer in women older than 65 years
        who have had adequate prior screening and are not otherwise at high risk for cervical
        cancer. (D recommendation)"

        "The USPSTF recommends against screening for cervical cancer in women younger than 21
        years. (D recommendation)"

        "The USPSTF recommends against screening for cervical cancer in women who have had a
        hysterectomy with removal of the cervix and do not have a history of a high-grade
        precancerous lesion (ie, cervical intraepithelial neoplasia [CIN] grade 2 or 3) or cervical
        cancer. (D recommendation)"
        """
        pass
