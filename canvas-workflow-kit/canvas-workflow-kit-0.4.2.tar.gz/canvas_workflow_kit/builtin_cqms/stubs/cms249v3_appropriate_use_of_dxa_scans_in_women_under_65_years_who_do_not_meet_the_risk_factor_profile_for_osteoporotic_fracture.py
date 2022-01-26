from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AnkylosingSpondylitis, AromataseInhibitors, AverageNumberOfDrinksPerDrinkingDay, BmiRatio,
    ChronicLiverDisease, ChronicMalnutrition, CushingsSyndrome,
    DxaDualEnergyXrayAbsorptiometryScan, EhlersDanlosSyndrome, EndStageRenalDisease, Ethnicity,
    Female, GlucocorticoidsOralOnly, HistoryOfHipFractureInParent, Hyperparathyroidism,
    Hyperthyroidism, Lupus, MalabsorptionSyndromes, MarfansSyndrome, OfficeVisit,
    OncAdministrativeSex, OsteogenesisImperfecta, Osteopenia, Osteoporosis, OsteoporoticFractures,
    OutpatientConsultation, Payer, PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, PreventiveCareServicesOther,
    PsoriaticArthritis, Race, RheumatoidArthritis, TobaccoUseScreening, Type1Diabetes, White)


class ClinicalQualityMeasure249v3(ClinicalQualityMeasure):
    """
    Appropriate Use of DXA Scans in Women Under 65 Years Who Do Not Meet the Risk Factor Profile
    for Osteoporotic Fracture

    Description: Percentage of female patients 50 to 64 years of age without select risk factors
    for osteoporotic fracture who received an order for a dual-energy x-ray absorptiometry (DXA)
    scan during the measurement period

    Definition: The measure allows for clinicians to use the Fracture Risk Assessment Tool
    (FRAX[R]) to calculate 10-year absolute fracture risk. The FRAX was developed by the World
    Health Organization in 2008 to evaluate a patient's 10-year probability of hip fracture and
    major osteoporotic fracture (clinical spine, forearm, hip, or shoulder fracture). It is
    applicable to people aged 40-90 years.

    Rationale: This measure is expected to increase recording of patient risk for fracture data and
    decrease the amount of inappropriate DXA scans. Current osteoporosis guidelines recommend using
    bone measurement testing to assess osteoporosis risk in women 65 years and older. In
    postmenopausal women younger than age 65, guidelines recommend using a formal clinical risk
    assessment tool to establish a patient's risk for osteoporosis, in order to determine whether
    to screen a patient for osteoporosis using bone measurement testing. Clinical information, such
    as age, body mass index (BMI), parental hip fracture history, and smoking and alcohol use, can
    be used to determine a woman's fracture risk (U.S. Preventive Services Task Force [USPSTF],
    2018). Additionally, there are potentially avoidable harms associated with screening for
    osteoporosis in general, including exposure to radiation, false positive exams, and resulting
    side effects from unnecessary osteoporosis medications, which add costs to an already burdened
    health care system (Lim, Hoeksema, & Sherin, 2009).

    Guidance: There are two ways that a patient can be excluded from the measure:
    1. The patient has a specific number of "combination" risk factors (the number of risk factors
    varies by age).
    2. The patient has one or more of the "independent" risk factors, including a 10-year
    probability of major osteoporotic fracture of 8.4 percent or higher as determined by the FRAX.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms249v3
    """

    title = 'Appropriate Use of DXA Scans in Women Under 65 Years Who Do Not Meet the Risk Factor Profile for Osteoporotic Fracture'

    identifiers = ['CMS249v3']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'Lim, L. S., Hoeksema, L. J., & Sherin, K. (2009). Screening for osteoporosis in the adult U.S. population: ACPM position statement on preventive practice. American Journal of Preventive Medicine, 36(4), 366-375.',
        'National Institute for Health and Clinical Excellence. (2017). Osteoporosis: Fragility fracture risk. Retrieved from https://www.nice.org.uk/guidance/cg146/chapter/1-Guidance',
        'U.S. Preventive Services Task Force, Curry S. J., Krist, A. H., et al. (2018). Screening for osteoporosis to prevent fractures: U.S. Preventive Services Task Force recommendation statement. JAMA, 319(24), 2521-2531.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Female patients ages 50 to 64 years with an encounter during the
        measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Exclude patients with a combination of risk factors (as determined by age) or
        one of the independent risk factors

        Ages: 50-54 (>=4 combination risk factors) or 1 independent risk factor
        Ages: 55-59 (>=3 combination risk factors) or 1 independent risk factor
        Ages: 60-64 (>=2 combination risk factors) or 1 independent risk factor

        COMBINATION RISK FACTORS [The following risk factors are all combination risk factors; they
        are grouped by when they occur in relation to the measurement period]:

        The following risk factors may occur any time in the patient's history but must be active
        during the measurement period:
        White (race)
        BMI <= 20 kg/m2 (must be the first BMI of the measurement period)
        Smoker (current during the measurement period)
        Alcohol consumption (> two units per day (one unit is 12 oz. of beer, 4 oz. of wine, or 1
        oz. of liquor))

        The following risk factor may occur any time in the patient's history and must not start
        during the measurement period:
        Osteopenia

        The following risk factors may occur at any time in the patient's history or during the
        measurement period:
        Rheumatoid arthritis
        Hyperthyroidism
        Malabsorption Syndromes: celiac disease, inflammatory bowel disease, ulcerative colitis,
        Crohn's disease, cystic fibrosis, malabsorption
        Chronic liver disease
        Chronic malnutrition

        The following risk factors may occur any time in the patient's history and do not need to
        be active at the start of the measurement period:
        Documentation of history of hip fracture in parent
        Osteoporotic fracture
        Glucocorticoids (>= 5 mg/per day) [cumulative medication duration >= 90 days]

        INDEPENDENT RISK FACTORS (The following risk factors are all independent risk factors; they
        are grouped by when they occur in relation to the measurement period):

        The following risk factors may occur at any time in the patient's history and must not
        start during the measurement period:
        Osteoporosis

        The following risk factors may occur at any time in the patient's history prior to the
        start of the measurement period, but do not need to be active during the measurement
        period:
        Gastric bypass
        FRAX[R] ten-year probability of all major osteoporosis related fracture >= 8.4 percent
        Aromatase inhibitors

        The following risk factors may occur at any time in the patient's history or during the
        measurement period:
        Type I Diabetes
        End stage renal disease
        Osteogenesis imperfecta
        Ankylosing spondylitis
        Psoriatic arthritis
        Ehlers-Danlos syndrome
        Cushing's syndrome
        Hyperparathyroidism
        Marfan syndrome
        Lupus

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Female patients who received an order for at least one DXA scan in the
        measurement period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: USPSTF:
        "The USPSTF recommends screening for osteoporosis with bone measurement testing to prevent
        osteoporotic fractures in women 65 years and older." This is a B recommendation.

        "The USPSTF concludes that the current evidence is insufficient to assess the balance of
        benefits and harms of screening for osteoporosis to prevent osteoporotic fractures in men."
        This is an I statement.

        "Several tools are available to assess osteoporosis risk: the Simple Calculated
        Osteoporosis Risk Estimate (SCORE; Merck), Osteoporosis Risk Assessment Instrument (ORAI),
        Osteoporosis Index of Risk (OSIRIS), and the Osteoporosis Self-Assessment Tool (OST). These
        tools seem to perform similarly and are moderately accurate at predicting osteoporosis. The
        FRAX tool (University of Sheffield), which assesses a person's 10-year risk of fracture, is
        also a commonly used tool."

        "The USPSTF recommends screening for osteoporosis with bone measurement testing to prevent
        osteoporotic fractures in postmenopausal women younger than 65 years who are at increased
        risk of osteoporosis, as determined by a formal clinical risk assessment tool." This is a B
        recommendation.
        "For postmenopausal women younger than 65 years who have at least 1 risk factor, a
        reasonable approach to determine who should be screened with bone measurement testing is to
        use a clinical risk assessment tool."

        "Because the benefits of treatment are greater in persons at higher risk of fracture, one
        approach is to perform bone measurement testing in postmenopausal women younger than 65
        years who have a 10-year FRAX risk of major osteoporotic fracture (MOF) (without DXA)
        greater than that of a 65-year-old white woman without major risk factors. For example, in
        the United States, a 65-year-old white woman of mean height and weight without major risk
        factors has a 10-year FRAX risk of MOF of 8.4%."

        The National Institute for Health and Clinical Excellence’s Osteoporosis Guidelines:
        "Consider assessment of fracture risk:
        a. in all women aged 65 years and over and all men aged 75 years and over
        b. in women aged under 65 years and men aged under 75 years in the presence of risk
        factors, for
        example:
        *previous fragility fracture
        *current use or frequent/ recent use of oral or systemic glucocorticoids
        *history of falls
        *family history of hip fracture
        *other causes of secondary osteoporosis
        *low body mass index (BMI) (less than 18.5 kg/m2)
        *smoking
        *alcohol intake of more than 14 units per week for women and more than 21 units per week
        for men."

        "Do not routinely assess fracture risk in people aged under 50 years unless they have major
        risk
        factors (for example, current or frequent/recent use of oral or systemic glucocorticoids,
        untreated
        premature menopause or previous fragility fracture), because they are unlikely to be at
        high risk."

        "Estimate absolute risk when assessing risk of fracture (for example, the predicted risk of
        major osteoporotic or hip fracture over 10 years, expressed as a percentage."

        "Use either FRAX (without a bone mineral density [BMD] value if a dual energy X-ray
        absorptiometry [DXA] scan has not previously been undertaken) or QFracture, within their
        allowed age ranges, to estimate 10-year predicted absolute fracture risk when assessing
        risk of fracture."

        "Do not routinely measure BMD to assess fracture risk without prior assessment using FRAX
        (without a BMD value) or QFracture."

        "Take into account that risk assessment tools may underestimate fracture risk in certain
        circumstances, for example if a person:
        *has a history of multiple fractures
        *has had previous vertebral fracture(s)
        *has a high alcohol intake
        *is taking high-dose oral or high-dose systemic glucocorticoids (more than 7.5 mg
        prednisolone
        or equivalent per day for 3 months or longer)
        *has other causes of secondary osteoporosis."
        """
        pass
