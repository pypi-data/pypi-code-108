from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    DiagnosisOfHypertension, DietaryRecommendations, EncounterToScreenForBloodPressure, Ethnicity,
    FollowUpWithin4Weeks, FollowUpWithinOneYear, LifestyleRecommendation, OncAdministrativeSex,
    Payer, PharmacologicTherapyForHypertension, Race, RecommendationToIncreasePhysicalActivity,
    ReferralOrCounselingForAlcoholConsumption, ReferralToPrimaryCareOrAlternateProvider,
    WeightReductionRecommended)


class ClinicalQualityMeasure22v9(ClinicalQualityMeasure):
    """
    Preventive Care and Screening: Screening for High Blood Pressure and Follow-Up Documented

    Description: Percentage of patient visits for patients aged 18 years and older seen during the
    measurement period who were screened for high blood pressure AND a recommended follow-up plan
    is documented, as indicated, if blood pressure is pre-hypertensive or hypertensive

    Definition: Blood Pressure (BP) Classification:
    BP is defined by four (4) BP reading classifications: Normal, Pre-Hypertensive, First
    Hypertensive, and Second Hypertensive Readings

    Recommended BP Follow-Up:
    The Joint National Committee on the Prevention, Detection, Evaluation, and Treatment of High
    Blood Pressure (JNC 7) recommends BP screening intervals, lifestyle modifications and
    interventions based on the current BP reading as listed in the "Recommended Blood Pressure
    Follow-Up Interventions" listed below

    Recommended Lifestyle Modifications:
    The JNC 7 report outlines lifestyle modifications which must include one or more of the
    following as indicated:
      *  Weight Reduction
      *  Dietary Approaches to Stop Hypertension (DASH) Eating Plan
      *  Dietary Sodium Restriction
      *  Increased Physical Activity
      *  Moderation in alcohol (ETOH) Consumption

    Second Hypertensive Reading:
    Requires a BP reading of systolic BP >= 140 mmHg OR diastolic BP >= 90 mmHg during the current
    encounter AND a most recent BP reading within the last 12 months systolic BP >= 140 mmHg OR
    diastolic BP >= 90 mmHg

    Second Hypertensive Reading BP Interventions:
    The JNC 7 report outlines BP follow-up interventions for a second hypertensive BP reading and
    must include one or more of the following as indicated:
      *  Anti-Hypertensive Pharmacologic Therapy
      *  Laboratory Tests
      *  Electrocardiogram (ECG)

    Recommended Blood Pressure Follow-Up Interventions:
      *  Normal BP: No follow-up required for systolic BP < 120 mmHg AND diastolic BP < 80 mmHg
      *  Pre-Hypertensive BP: Follow-up with rescreen every year with systolic BP of 120-139 mmHg
    OR
          diastolic BP of 80-89 mmHg AND recommend lifestyle modifications OR referral to
          Alternative/Primary Care Provider
      *  First Hypertensive BP Reading: Patients with one elevated reading of systolic BP >= 140
    mmHg
          OR diastolic BP >= 90 mmHg:
               *  Follow-up with rescreen > 1 day and < 4 weeks AND recommend lifestyle
    modifications
                   OR referral to Alternative/Primary Care Provider
      *  Second Hypertensive BP Reading: Patients with second elevated reading of systolic
          BP >= 140 mmHg OR diastolic BP >= 90 mmHg:
               *  Follow-up with Recommended lifestyle recommendations AND one or more of the
    Second
                   Hypertensive Reading Interventions OR referral to Alternative/Primary Care
    Provider

    Rationale: Hypertension is a prevalent condition that affects approximately 66.9 million people
    in the United States. It is estimated that about 20-40% of the adult population has
    hypertension; the majority of people over age 65 have a hypertension diagnosis (Appleton SL, et
    al., 2012 and Luehr D, et al., 2012). Winter (2013) noted that 1 in 3 American adults have
    hypertension and the lifetime risk of developing hypertension is 90% (Winter KH, et al., 2013).
    The African American population or non-Hispanic Blacks, the elderly, diabetics and those with
    chronic kidney disease are at increased risk of stroke, myocardial infarction and renal
    disease. Non-Hispanic Blacks have the highest prevalence at 38.6% (Winter KH, et al., 2013).
    Hypertension is a major risk factor for ischemic heart disease, left ventricular hypertrophy,
    renal failure, stroke and dementia (Luehr D, et al., 2012).

    Hypertension is the most common reason for adult office visits other than pregnancy. Garrison
    (2013) stated that in 2007, 42 million ambulatory visits were attributed to hypertension
    (Garrison GM and Oberhelman S, 2013). It also has the highest utilization of prescription
    drugs. Numerous resources and treatment options are available, yet only about 40-50% of the
    hypertensive patients have their blood pressure under control (<140/90) (Appleton SL, et al.,
    2012, Luehr D, et al., 2012). In addition to medication non-compliance, poor outcomes are also
    attributed to poor adherence to lifestyle changes such as a low-sodium diet, weight loss,
    increased exercise and limiting alcohol intake. Many adults find it difficult to continue
    medications and lifestyle changes when they are asymptomatic. Symptoms of elevated blood
    pressure usually do not occur until secondary problems arise such as with vascular diseases
    (myocardial infarction, stroke, heart failure and renal insufficiency) (Luehr D, et al., 2012).

    Appropriate follow-up after blood pressure measurement is a pivotal component in preventing the
    progression of hypertension and the development of heart disease. Detection of marginally or
    fully elevated blood pressure by a specialty clinician warrants referral to a provider familiar
    with the management of hypertension and prehypertension. The 2010 ACCF/AHA Guideline for the
    Assessment of Cardiovascular Risk in Asymptomatic Adults continues to support using a global
    risk score such as the Framingham Risk Score, to assess risk of coronary heart disease (CHD) in
    all asymptomatic adults (Greenland P, et al., 2010). Lifestyle modifications have demonstrated
    effectiveness in lowering blood pressure (JNC 7, 2003). The synergistic effect of several
    lifestyle modifications results in greater benefits than a single modification alone. Baseline
    diagnostic/laboratory testing establishes if a co-existing underlying condition is the etiology
    of hypertension and evaluates if end organ damage from hypertension has already occurred.
    Landmark trials such as ALLHAT have repeatedly proven the efficacy of pharmacologic therapy to
    control blood pressure and reduce the complications of hypertension. Follow-up intervals based
    on blood pressure control have been established by the JNC 7 and the USPSTF.

    Guidance: This eCQM is an episode-based measure and should be reported at every visit for
    patients aged 18 years and older. This measure will be calculated based upon the clinical
    actions performed at every visit during the measurement period for each patient. The measure
    requires that blood pressure measurements (i.e., diastolic and systolic) be obtained during
    each visit in order to determine the blood pressure reading used to evaluate if an intervention
    is needed.

    Both the systolic and diastolic blood pressure measurements are required for inclusion. If
    there are multiple blood pressures obtained during a patient visit, only the last, or most
    recent, pressure measurement will be used to evaluate the measure requirements.

    The intent of this measure is to screen patients for high blood pressure and provide
    recommended follow-up as indicated. The documented follow-up plan must be related to the
    current blood pressure reading as indicated, example: "Patient referred to primary care
    provider for BP management."

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms22v9
    """

    title = 'Preventive Care and Screening: Screening for High Blood Pressure and Follow-Up Documented'

    identifiers = ['CMS22v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'Appleton, S. L., Neo, C., Hill, C. L., Douglas, K. A., & Adams, R. J. (2013). Untreated hypertension: prevalence and patient factors and beliefs associated with under-treatment in a population sample. Journal of Human Hypertension, 27, 453-462. doi:10.1038/jhh.2012.62ID',
        'Garrison, G. M. & Oberhelman, S. (2013). Screening for hypertension annually compared with current practice. Annals of Family Medicine, 11 (2), 116-121. doi:10.1370/afm.1467',
        'Greenland, P., Alpert, J. S., Beller, G. A., Benjamin, E. J., Budoff, M. J., Fayad, Z. A., Foster, E., Hlatky, M. A., Hodgson, J. M., Kushner, F. G., Lauer, M. S., Shaw, L. J., Smith, S. C., Jr, Taylor, A. J., Weintraub, W. S., Wenger, N. K., Jacobs, A. K., Smith, S. C., Jr, Anderson, J. L., Albert, N., … American Heart Association (2010). 2010 ACCF/AHA guideline for assessment of cardiovascular risk in asymptomatic adults: a report of the American College of Cardiology Foundation/American Heart Association Task Force on Practice Guidelines. Journal of the American College of Cardiology, 56(25), e50–e103. https://doi.org/10.1016/j.jacc.2010.09.001',
        'Luehr, D., Woolley, T., Burke, R., Dohmen, F., Hayes, R., Johnson, M...., Schoenleber, M. (2012). Hypertension diagnosis and treatment; Institute for Clinical Systems Improvement health care guideline. Updated November, 2012.',
        'U.S. Preventive Services Task Force (USPSTF) (2007). Screening for high blood pressure: U.S. Preventive Services Task Force reaffirmation recommendation statement. Annals of Internal Medicine; 147(11):783-6',
        'U.S. Department of Health and Human Services, National Institutes of Health, National Heart, Lung, and Blood Institute & National High Blood Pressure Education Program (2003). The Seventh Report of the Joint National Committee on the Prevention, Detection, Evaluation, and Treatment of High Blood Pressure (JNC-7). NIH Publication No. 03-5233',
        'Winter, K. H., Tuttle, L. A. & Viera, A.J. (2013). Hypertension. Primary Care Clinics in Office Practice, 40, 179-194. doi:10.1016/j.pop.2012.11.008',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patient visits for patients aged 18 years and older at the
        beginning of the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Patient has an active diagnosis of hypertension

        Exceptions: Documentation of medical reason(s) for not screening for high blood pressure
        (e.g., patient is in an urgent or emergent medical situation where time is of the essence
        and to delay treatment would jeopardize the patient's health status).

        Documentation of patient reason(s) for not screening for blood pressure measurements or for
        not ordering an appropriate follow-up intervention if patient is pre-hypertensive or
        hypertensive (e.g., patient refuses).
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patient visits where patients were screened for high blood pressure AND have a
        recommended follow-up plan documented, as indicated, if the blood pressure is pre-
        hypertensive or hypertensive

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: The U.S. Preventive Services Task Force (USPSTF) recommends
        screening for high blood pressure in adults age 18 years and older. This is a grade A
        recommendation.
        """
        pass
