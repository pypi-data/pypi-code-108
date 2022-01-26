from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AndrogenDeprivationTherapyForUrologyCare,
    DexaDualEnergyXrayAbsorptiometryBoneDensityForUrologyCare, Ethnicity, OfficeVisit,
    OncAdministrativeSex, Payer, ProstateCancer, Race)


class ClinicalQualityMeasure645v4(ClinicalQualityMeasure):
    """
    Bone density evaluation for patients with prostate cancer and receiving androgen deprivation
    therapy

    Description: Patients determined as having prostate cancer who are currently starting or
    undergoing androgen deprivation therapy (ADT), for an anticipated period of 12 months or
    greater and who receive an initial bone density evaluation. The bone density evaluation must be
    prior to the start of ADT or within 3 months of the start of ADT.

    Definition: Data Criteria Value Set 2.16.840.1.113762.1.4.1151.38 DEXA, Dual Energy Xray
    Absorptiometry, Bone Density for Urology Care contains 2 LOINC codes identifying the axial and
    appendicular skeleton and will meet the measure intent.

    DEXA - Dual Energy X-ray Absorptiometry - A scan that measures the bone of the spine, hip or
    total body and measures bone mineral density. It is considered one of the most accurate
    measurements.
    PDXA - Peripheral Dual Energy X-ray Absorptiometry - Bone mineral density measurement of the
    wrist, heel or finger.

    First Androgen Deprivation Therapy - The First Androgen Deprivation Therapy (ADT) is measured
    as the first order or administration of ADT for an anticipated period of 12 months or greater
    to a patient with prostate cancer.

    Rationale: Androgen suppression as a treatment for prostate cancer can cause osteoporosis
    (Qaseem, 2008). Men undergoing prolonged androgen deprivation therapy (ADT) incur bone loss at
    a rate higher than menopausal women (Guise, 2007). In preserving bone health, the goal is to
    prevent or treat osteopenia/osteoporosis for the patient on ADT and to prevent or delay
    skeletal related events. The National Osteoporosis Foundation recommendations including a
    baseline assessment of bone density with a DEXA scan and daily calcium and Vitamin D
    supplementation (Watts, 2012). The DEXA scan is the gold standard for bone density screening.
    Men at risk for adverse bone consequences from chronic ADT do not always receive care according
    to evidence-based guidelines. These findings call for improved processes that standardize
    evidence-based practice including baseline and follow up bone density assessment (Watts, 2012).

    Guidance: In order to capture the practitioner's intent of androgen deprivation therapy (ADT)
    for a period of 12 months or greater, SNOMEDCT 456381000124102 which is Injection of leuprolide
    acetate for twelve month period (regime/therapy) is the correct code.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms645v4
    """

    title = 'Bone density evaluation for patients with prostate cancer and receiving androgen deprivation therapy'

    identifiers = ['CMS645v4']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'Oregon Urology',
    ]

    references = [
        'Cosman, F., deBeur, S., LeBoff, M., et al. (2014, June). Clinician’s guide to prevention and treatment of osteoporosis. Osteoporosis International, 25(10), 2359–2381. Retrieved from http://link.springer.com/article/10.1007/s00198-014-2794-2',
        'Finkelstein, J., & Yu, E. (2017). Clinical manifestations, diagnosis, and evaluation of osteoporosis in men. Retrieved from https://www.uptodate.com/contents/clinical-manifestations-diagnosis-and-evaluation-of-osteoporosis-in-men/print?source=see_link',
        'Guise, T., Oefelein, M., Eastham, J., et al. (2007). Estrogenic side effects of androgen deprivation therapy. Reviews in Urology, 9(4), 163-180. Retrieved from https://www.researchgate.net/profile/Celestia_Higano/publication/5619579_Estrogenic_side_effects_of_androgen_deprivation_therapy/links/0c960526434483fdfd000000.pdf',
        'Qaseem, A., Snow, V., Shekelle, P., et al. (2008). Annals of Internal Medicine. Screening for osteoporosis in men: A clinical practice guideline from the American College of Physicians, 2008. Annals of Internal Medicine, 148(9), 680-684. Retrieved from http://annals.org/aim/article/740825/screening-osteoporosis-men-clinical-practice-guideline-from-american-college-physicians',
        'Ward, R., Roberts, C., Bencardino, J., et al. (2016). American College of Radiology: ACR Appropriateness Criteria (R)—Osteoporosis and bone mineral density. Retrieved from https://www.jacr.org/article/S1546-1440(17)30198-9/pdf',
        'Watts, N., Adler, R., Bilezikian, J., et al. (2012, June). Osteoporosis in men: An Endocrine Society clinical practice guideline, Journal of Clinical Endocrinology & Metabolism, 97(6), 1802–1822. Retrieved from https://academic.oup.com/jcem/article-lookup/doi/10.1210/jc.2011-3045',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Male patients with a qualifying encounter in the measurement period AND
        with a diagnosis of prostate cancer AND with an order for ADT or an active medication of
        ADT with an intent for treatment greater than or equal to 12 months during the measurement
        period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: None

        Exceptions: Patient refused recommendation for a bone density evaluation after the start of
        ADT therapy
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients with a bone density evaluation within the two years prior to the start
        of or less than three months after the start of ADT treatment

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: Bone density screening should be performed at the start of
        Androgen Deprivation Therapy (ADT) for prostate cancer. It should also be performed every 2
        years for the patient with continued ADT or for patients with known osteoporosis. Current
        insurance practice is to possibly cover the cost of bone density screening if osteoporosis
        is known or if there is a high-risk drug. Some patients choose to delay bone density
        screening until after ADT is started and they therefore have insurance authorization due to
        the administration of a high-risk drug.
        """
        pass
