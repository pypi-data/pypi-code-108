from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    Ethnicity, HospitalServicesForUrologyCare, MorbidObesity, OfficeVisit, OncAdministrativeSex,
    Payer, Race, UrinaryRetention)


class ClinicalQualityMeasure771v2(ClinicalQualityMeasure):
    """
    Urinary Symptom Score Change 6-12 Months After Diagnosis of Benign Prostatic Hyperplasia

    Description: Percentage of patients with an office visit within the measurement period and with
    a new diagnosis of clinically significant Benign Prostatic Hyperplasia who have International
    Prostate Symptoms Score (IPSS) or American Urological Association (AUA) Symptom Index (SI)
    documented at time of diagnosis and again 6-12 months later with an improvement of 3 points

    Definition: Clinically significant Benign Prostatic Hyperplasia (BPH) is BPH with lower urinary
    tract symptoms (LUTS).
    IPSS - International Prostate Symptom Score
    AUA-SI - American Urological Association-Symptom Index
    QOL - Quality of Life score

    Rationale: Benign prostatic hyperplasia (BPH) is one of the most common conditions affecting
    older men, with a prevalence of 50% by age 60 years and 90% by the ninth decade of life
    (Medina, Parra, & Moore, 1999). The enlarged gland had been proposed to contribute to the
    overall lower urinary tract symptoms (LUTS) complex (McVary et al., 2014). Although LUTS
    secondary to BPH is not often a life-threatening condition, the impact of LUTS/BPH on quality
    of life can be significant (Wei, Calhoun, & Jacobsen, 2005). The American Urological
    Association Symptom Index (AUA-SI) and the International Prostate Symptom Score (IPSS) were
    developed to measure outcomes in studies of different treatments for BPH (Wuerstle et al.,
    2011). The IPSS uses the same questions as the AUA-SI, but also adds a disease-specific quality
    of life question (OLeary, 2005). The IPSS was adopted in 1993 by the World Health Organization.
    It is a reproducible, validated index designed to determine disease severity and response to
    therapy (D’Silva, Dahm, & Wong, 2014). It includes 3 storage symptom questions (frequency,
    nocturia, urgency) and four voiding symptoms (feeling of incomplete emptying, intermittency,
    straining, and a weak stream) as well as a Bother question: If you were to spend the rest of
    your life with your urinary condition just the way it is now, how would you feel about that? A
    three-point improvement in the score is considered meaningful (McVary et al., 2014).

    Guidance: The IPSS is inclusive of the symptom index score and the quality of life score. The
    AUA-SI is the symptom index score alone and must be added to the QOL score. The AUA-SI with the
    QOL equals the IPSS. Both of these are the urinary symptom score.

    The patient must have a urinary symptom score (USS) within 1 month after initial diagnosis. If
    more than one USS in the initial one month, then the first USS counts. The patient must have a
    USS again at 6-12 months after the initial diagnosis and if more than one USS in this time
    frame, then the last USS counts.

    Hospitalization within 30 days of Initial BPH Diagnosis refers to a 30-day period between the
    end of the hospitalization and the clinical office setting BPH diagnosis. This is due to
    aggravating factors from hospitalization, such as bed rest, medications, surgery, and altered
    body functions.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms771v2
    """

    title = 'Urinary Symptom Score Change 6-12 Months After Diagnosis of Benign Prostatic Hyperplasia'

    identifiers = ['CMS771v2']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'Large Urology Group Practice Association (LUGPA)',
    ]

    references = [
        'D\'Silva, K. A., Dahm, P., & Wong, C. L. (2014). Does this man with lower urinary tract symptoms have bladder outlet obstruction? The Rational Clinical Examination: A systematic review. Journal of the American Medical Association, 312(5), 535-542. Retrieved from https://www.ncbi.nlm.nih.gov/pubmed/25096693',
        'McVary, K. T., Roehrborn, C. G., Avins, A. L., et al. (2014). Management of benign prostatic hyperplasia. Retrieved from http://www.auanet.org/guidelines/benign-prostatic-hyperplasia-(2010-reviewed-and-validity-confirmed-2014)',
        'Medina, J. J., Parra, R. O., & Moore, R. G. (1999). Benign prostatic hyperplasia (the aging prostate). Medical Clinics of North America, 83(5), 1213-1229. Retrieved from http://www.sciencedirect.com/science/article/pii/S0025712505701590',
        'O’Leary, M. P. (2005). Validity of the Bother Score in the evaluation and treatment of symptomatic benign prostatic hyperplasia. Reviews in Urology, 7(1), 1-10. Retrieved from https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1477553/',
        'Wei, J., Calhoun, E., & Jacobsen, S. (2005). Urologic diseases in America project: Benign prostatic hyperplasia. Journal of Urology, 173(4), 1256-1261. Retrieved from https://www.ncbi.nlm.nih.gov/pubmed/15758764',
        'Wuerstle, M. C., Van Den Eeden, S. K., Poon, K. T., et al. (2011). Contribution of common medications to lower urinary tract symptoms in men. Archives of Internal Medicine, 171(18), 1680-1682. Retrieved from https://www.ncbi.nlm.nih.gov/pubmed/21987200',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Male patients with an initial diagnosis of benign prostatic hyperplasia
        6 months prior to, or during the measurement period, and a urinary symptom score assessment
        within 1 month of initial diagnosis and a follow-up urinary symptom score assessment within
        6-12 months, who had a qualifying visit during the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Patients with urinary retention that starts within 1 year of initial BPH
        diagnosis.
        Patients with an initial BPH diagnosis that starts during, or within 30 days of
        hospitalization.
        Patients with a diagnosis of morbid obesity, or with a BMI Exam >40 before the follow up
        urinary symptom score.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients with a documented improvement of at least 3 points in their urinary
        symptom score during the measurement period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: The symptoms of BPH are LUTS symptoms. There are other disorders
        with similar symptoms that need to be excluded. History, physical examination, and testing
        are required prior to a diagnosis of BPH. IPSS by itself is not a reliable diagnostic tool
        for LUTS suggestive of BPH, but serves as a quantitative measure of LUTS after the
        diagnosis is established (D’Silva, Dahm, & Wong, 2014). Medical and surgical interventions
        for BPH recommend a follow up IPSS evaluation to determine effectiveness of treatment. IPSS
        should be evaluated at the time of diagnosis and after definitive treatment.
        """
        pass
