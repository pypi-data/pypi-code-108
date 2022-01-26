from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    EncounterToEvaluateBmi, Ethnicity, FollowUpForAboveNormalBmi, FollowUpForBelowNormalBmi,
    HospiceCareAmbulatory_1584, MedicationsForAboveNormalBmi, MedicationsForBelowNormalBmi,
    OncAdministrativeSex, PalliativeOrHospiceCare, Payer, PregnancyOrOtherRelatedDiagnoses, Race,
    ReferralsWhereWeightAssessmentMayOccur)


class ClinicalQualityMeasure69v9(ClinicalQualityMeasure):
    """
    Preventive Care and Screening: Body Mass Index (BMI) Screening and Follow-Up Plan

    Description: Percentage of patients aged 18 years and older with a BMI documented during the
    current encounter or within the previous twelve months AND who had a follow-up plan documented
    if most recent BMI was outside of normal parameters

    Definition: Normal BMI Parameters:  Age 18 years and older BMI >= 18.5 and < 25 kg/m2

    BMI- Body mass index (BMI) is a number calculated using the Quetelet index: weight divided by
    height squared (W/H2) and is commonly used to classify weight categories. BMI can be calculated
    using:

    Metric Units:  BMI = Weight (kg) / (Height (m) x Height (m))
    OR
    English Units:  BMI = Weight (lbs.) / (Height (in) x Height (in)) x 703

    Follow-Up Plan - Proposed outline of treatment to be conducted as a result of a BMI out of
    normal parameters. A follow-up plan may include, but is not limited to: documentation of
    education, referral (for example a Registered Dietitian Nutritionist (RDN), occupational
    therapist, physical therapist, primary care provider, exercise physiologist, mental health
    professional, or surgeon) for lifestyle/behavioral therapy, pharmacological interventions,
    dietary supplements, exercise counseling and/or nutrition counseling

    Rationale: BMI Above Normal Parameters

    Obesity is a chronic, multifactorial disease with complex psychological, environmental (social
    and cultural), genetic, physiologic, metabolic and behavioral causes and consequences. The
    prevalence of overweight and obese people is increasing worldwide at an alarming rate in both
    developing and developed countries. Environmental and behavioral changes brought about by
    economic development, modernization and urbanization have been linked to the rise in global
    obesity. The health consequences are becoming apparent (Fitch, 2013).

    Hales et al. (2017), report that the prevalence of obesity among adults and youth in the United
    States was 39.8% and 18.5% respectively, from 2015-2016. They note that obesity prevalence was
    higher among adults in the 40-59 age bracket than those in the 20-39 age bracket, for both men
    and women. Hales et al. (2017) also disaggregated the data according to ethnicity and noted
    that obesity prevalence was higher among non-Hispanic black and Hispanic adults and youth when
    compared with other races ethnicities. While obesity prevalence was lower among non-Hispanic
    Asian men and women, obesity prevalence among men, was comparable between non-Hispanic black
    and non-Hispanic white men. Obesity prevalence was higher among Hispanic men compared with non-
    Hispanic black men. While the prevalence among non-Hispanic black and Hispanic women was
    comparable, the prevalence for both groups was higher than that of non-Hispanic white women.
    Most notably, Hales et al. (2017), report that the prevalence of obesity in the United States
    remains higher than the Healthy People 2020 goals of 14.5% among youth and 30.5% among adults.

    More than a third of U.S. adults have a body mass index [BMI] >= 30 kg/m2; substantially at
    increased risk for diabetes and cardiovascular disease (CVD) (Flegal et al., 2012; Ogden et
    al., 2014). Behavioral weight management treatment has been identified as an effective first-
    line treatment for obesity with an average initial weight loss of eight to ten percent. This
    percentage weight loss is associated with a significant risk reduction for diabetes and CVD
    (Wadden, Butryn & Wilson, 2007). Despite the availability of effective interventions, two-
    thirds of obese U.S. patients were not offered or referred to weight management treatment
    during their primary care visit between 2005 and 2006, (Ma et al., 2009). In addition, the rate
    of weight management counseling in primary care significantly decreased by ten percent (40% to
    30%) between 1995-1996 and 2007-2008 (Kraschnewski et al., 2013). This suggests that the
    availability of evidence based clinical guidelines since 2008 obesity management in primary
    care remains suboptimal (Fitzpatrick & Stevens, 2017).

    BMI continues to be a common and reasonably reliable measurement to identify overweight and
    obese adults who may be at an increased risk for future morbidity. Although good quality
    evidence supports obtaining a BMI, it is important to recognize it is not a perfect
    measurement. BMI is not a direct measure of adiposity and as a consequence it can over or
    underestimate adiposity. BMI is a derived value that correlates well with total body fat and
    markers of secondary complications, e.g., hypertension and dyslipidemia (Barlow & the Expert
    Committee, 2007).

    In contrast with waist circumference, BMI and its associated disease and mortality risk appear
    to vary among ethnic subgroups. Female African American populations appear to have the lowest
    mortality risk at a BMI of 26.2-28.5 kg/m2 and 27.1-30.2 kg/m2 for women and men, respectively.
    In contrast, Asian populations may experience lowest mortality rates starting at a BMI of 23 to
    24 kg/m2. The correlation between BMI and diabetes risk also varies by ethnicity (LeBlanc et
    al., 2011, pp. 2-3).

    Screening for BMI and follow-up therefore is critical to closing this gap and contributes to
    quality goals of population health and cost reduction. However, due to concerns for other
    underlying conditions (such as bone health) or nutrition related deficiencies providers are
    cautioned to use clinical judgment and take these into account when considering weight
    management programs for overweight patients, especially the elderly (National Heart, Lung, and
    Blood Institute [NHLBI] Obesity Education Initiative, 1998, p. 91).

    It is important to enhance beneficiary access to all existing providers of Intensive Behavioral
    Therapy for obesity (IBT) which would result in decreased healthcare costs and lower obesity
    rates. Dietary counseling performed by a Registered Dietitian Nutritionist (RDN) is more
    effective than by a primary care clinician. IBT provided by RDNs for 6-12 months shows
    significant mean weight loss of up to 10% of body weight, maintained over one year’s time
    (Raynor & Champagne, 2016).

    BMI below Normal Parameters

    On the other end of the body weight spectrum is underweight (BMI < 18.5 kg/m2), which is
    equally detrimental to population health. When compared to normal weight individuals (BMI
    18.5-25 kg/m2), underweight individuals have significantly higher death rates with a Hazard
    Ratio of 2.27 and 95% confidence intervals (CI) = 1.78, 2.90 (Borrell & Lalitha, 2014).

    Poor nutrition or underlying health conditions can result in underweight (Fryar & Ogden, 2012).
    The National Health and Nutrition Examination Survey (NHANES) results from the 2007-2010
    indicate that women are more likely to be underweight than men. Therefore patients should be
    equally screened for underweight and followed up with nutritional counselling to reduce
    mortality and morbidity associated with underweight.

    Guidance: *  This eCQM is a patient-based measure. This measure is to be reported a minimum of
    once per reporting period for patients seen during the reporting period.
    *  There is no diagnosis associated with this measure.
    *  This measure may be reported by eligible professionals who perform the quality actions
    described in the measure based on the services provided at the time of the qualifying visit and
    the measure-specific denominator coding.

    BMI Measurement Guidance:
    *  Height and Weight - An eligible professional or their staff is required to measure both
    height and weight. Both height and weight must be measured within twelve months of the current
    encounter and may be obtained from separate encounters. Self-reported values cannot be used.
    *  The BMI may be documented in the medical record of the provider or in outside medical
    records obtained by the provider.
    *  If the most recent documented BMI is outside of normal parameters, then a follow-up plan is
    documented during the encounter or during the previous twelve months of the current encounter.
    *  If more than one BMI is reported during the measurement period, the most recent BMI will be
    used to determine if the performance has been met.
    *  Review the exclusions and exceptions criteria to determine those patients that BMI
    measurement may not be appropriate or necessary.

    Follow-Up Plan Guidance:

     * The documented follow-up plan must be based on the most recent documented BMI, outside of
    normal parameters, example: "Patient referred to nutrition counseling for BMI above or below
    normal parameters."

    (See Definitions for examples of follow-up plan treatments).

    Variation has been noted in studies exploring optimal BMI ranges for the elderly (see Donini et
    al., [2012]; Holme & Tonstad [2015]; Diehr et al. [2008]). Notably however, all these studies
    have arrived at ranges that differ from the standard range for ages 18 and older, which is
    >=18.5 and < 25 kg/m2. For instance, both Donini et al. (2012) and Holme and Tonstad (2015)
    reported findings that suggest that higher BMI (higher than the upper end of 25kg/m2) in the
    elderly may be beneficial. Similarly, worse outcomes have been associated with being
    underweight (at a threshold higher than 18.5 kg/m2) at age 65 (Diehr et al. 2008). Because of
    optimal BMI range variation recommendations from these studies, no specific optimal BMI range
    for the elderly is used. However, it may be appropriate to exempt certain patients from a
    follow-up plan by applying the exception criteria. See denominator exception section for
    examples.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms69v9
    """

    title = 'Preventive Care and Screening: Body Mass Index (BMI) Screening and Follow-Up Plan'

    identifiers = ['CMS69v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'Barlow, S. E., & the Expert Committee. (2007). Expert committee recommendations regarding the prevention, assessment, and treatment of child and adolescent overweight and obesity: Summary report. Pediatrics, 120(Suppl. 4), S164-S192. doi:10.1542/peds.2007-2329C',
        'Borrell, L. N., & Samuel, L. (2014). Body mass index categories and mortality risk in U.S. adults: The effect of overweight and obesity on advancing death. American Journal of Public Health, 104(3), 512-519. doi:10.2105/AJPH.2013.301597',
        'Centers for Disease Control and Prevention (CDC). (2012). National Health and Nutrition Examination Survey (NHANES). Prevalence of underweight among adults aged 20 and over: United States, 1960–1962 Through 2011–2012. Retrieved from https://www.cdc.gov/nchs/data/hestat/underweight_adult_11_12/underweight_adult_11_12.htm',
        'Diehr, P., O’Meara, E. S., Fitzpatrick A., Newman, A. B., Kuller, L., Burke, G. (2008). Weight, mortality, years of healthy life, and active life expectancy in older adults. Journal of the American Geriatrics Society, 56(1), 76-83. doi:10.1111/j.1532-5415.01500.x',
        'Donini, L. M., Savina, C., Gennaro, E., De Felice, M. R., Rosano, A., Pandolfo, M. M., Del Balzo, V., …Chumlea, W. C. et al. (2012). A systematic review of the literature concerning the relationship between obesity and mortality in the elderly. The Journal of Nutrition, Health & Aging, 16(1), 89-98. doi:10.1007/s12603-011-0073-x',
        'Flegal, K. M., Carroll, M. D., Kit, B. K., & Ogden, C. L. (2012). Prevalence of obesity and trends in the distribution of body mass index among U. S. adults, 1999-2010. JAMA, 307(5), 491-497. doi.10.1001/jama.2012.39',
        'Fitch, A., Everling, L., Fox, C.,Goldberg, J., Heim, C., Johnson, K., …Webb, B. (2013, May). Prevention and management of obesity for adults. Bloomington, MN: Institute for Clinical Systems Improvement.',
        'Fitzpatrick, S. L., & Stevens, V. J. (2017, June 1). Adult obesity management in primary care, 2008-2013. Preventive Medicine, 99, 128-133. Retrieved from http://dx.doi.org/10.1016/j.ypmed.2017.02.020 doi:10.1016.j.ypmed.2017.01.020',
        'Fryar, C. D., & Ogden, C. L. (2012). Prevalence of underweight among adults aged 20 and over: United States, 1960-1962 through 2007-2010. Hyattsville, MD: NCHS, Division of Health and Nutrition Examination Surveys. Retrieved from http://www.cdc.gov/nchs/data/hestat/underweight_adult_07_10/underweight_adult_07_10.pdf',
        'Garvey, W. T., Mechanick, J. I., Brett, E. M., Garber, A. J., Hurley, D. L., Jastrebodd. A. M., …and Reviewers of the AACE/ACE Obesity Clinical Practice Guidelines. (2016). American Association of Clinical Endocrinologists and American College of Endocrinology comprehensive clinical practice guidelines for medical care of patients with obesity. Endocrine Practice, 22(Suppl. 3), 1-203. doi:10.4158/EP161365GL',
        'Hales, C. M., Carroll, M. D., Fryar, C. D., et al. (2017, October). Prevalence of obesity among adults and youth: United States, 2015-2016. NCHS Data Brief No. 288. Retrieved from https://www.cdc.gov/nchs/products/databriefs/db288.htm',
        'Holme, I., & Tonstad, S. (2015). Survival in elderly men in relation to midlife and current BMI. Age and Ageing, 44(3), 434-439.',
        'LeBlanc, E., O’Connor, E., Whitlock, E. P., et al. (2011). Screening for and management of obesity and overweight in adults (Evidence Report No. 89; AHRQ Publication No. 11-05159-EF-1). Rockville, MD: Agency for Healthcare Research and Quality.',
        'Kraschnewski, J. L., Sciamanna, C. N, Stuckey, H. L., et al. (2013, February). A silent response to the obesity epidemic: Decline in US physician weight counseling, 51 (2). Retrieved from http://prowellness.vmhost.psu.edu/wp-content/uploads/obesity_epidemic.pdf',
        'NHLBI Obesity Education Initiative. (1998). Clinical guidelines on the identification, evaluation, and treatment of overweight and obesity in adults (Report No. 98-4083). Bethesda, MD: NHLBI.',
        'Ogden, C.L., Carroll, M.D., Fryar, C.D., Flegal, K.M. (2015). Prevalence of obesity among adults and youth: United States, 2011–2014. NCHS data brief, no 219. Hyattsville, MD: National Center for Health Statistics. Retrieved from https://www.cdc.gov/nchs/data/databriefs/db219.pdf',
        'Raynor, H. A., & Champagne, C. M. (2016). Position of the Academy of Nutrition and Dietetics: Interventions for the treatment of overweight and obesity in adults. Journal of the Academy of Nutrition and Dietetics, 116(1), 129-147. doi:10.1016/jand.2015.10.031',
        'U.S. Preventive Services Task Force. (2018). Behavioral weight loss interventions to prevent obesity-related morbidity and mortality in adults: U.S. Preventive Services Task Force recommendation statement. JAMA, 320(11), 1163–1171. doi:10.1001/jama.2018.13022',
        'Wadden, T. A, Butryn, M. L., Wilson, C. (2007). Lifestyle modification for the management of obesity. Gastroenterology, 132 (6), 2226-2238. doi: 10.1053/j.gastro.2007.03.051',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients aged 18 and older on the date of the encounter with at
        least one eligible encounter during the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Patients who are pregnant
        Patients receiving palliative or hospice care

        Exceptions: Patients with a documented medical reason for not documenting BMI or for not
        documenting a follow-up plan for a BMI outside normal parameters (e.g., elderly patients
        (65 or older) for whom weight reduction/weight gain would complicate other underlying
        health conditions such as illness or physical disability, mental illness, dementia,
        confusion, or nutritional deficiency such as vitamin/mineral deficiency; patients in an
        urgent or emergent medical situation where time is of the essence and to delay treatment
        would jeopardize the patient’s health status)

        Patients who refuse measurement of height and/or weight
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients with a documented BMI during the encounter or during the previous
        twelve months, AND when the BMI is outside of normal parameters, a follow-up plan is
        documented during the encounter or during the previous twelve months of the current
        encounter

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: All adults should be screened annually using a BMI measurement.
        BMI measurements >= 25 kg/m2 should be used to initiate further evaluation of overweight or
        obesity after taking into account age, gender, ethnicity, fluid status, and muscularity;
        therefore, clinical evaluation and judgment must be used when BMI is employed as the
        anthropometric indicator of excess adiposity, particularly in athletes and those with
        sarcopenia (Garvey et al., 2016 AACE/ACE Guidelines, 2016, pp. 12-13) (Grade A).

        Overweight and Underweight Categories:
        Underweight < 18.5; Normal weight 18.5-24.9; Overweight 25-29.9; Obese class I 30-34.9;
        Obese class II 35-39.9; Obese class III >= 40 (Garvey et al., 2016 AACE/ACE Guidelines,
        2016, p. 15).

        BMI cutoff point value of >= 23 kg/m2 should be used in the screening and confirmation of
        excess adiposity in Asian adults (Garvey et al., 2016 AACE/ACE Guidelines, 2016, p. 13)
        (Grade B).

        Lifestyle/Behavioral Therapy for Overweight and Obesity should include behavioral
        interventions that enhance adherence to prescriptions for a reduced-calorie meal plan and
        increased physical activity (behavioral interventions can include: self-monitoring of
        weight, food intake, and physical activity; clear and reasonable goal-setting; education
        pertaining to obesity, nutrition, and physical activity; face-to-face and group meetings;
        stimulus control; systematic approaches for problem solving; stress reduction; cognitive
        restructuring [i.e., cognitive behavioral therapy], motivational interviewing; behavioral
        contracting; psychological counseling; and mobilization of social support structures)
        (Garvey et al., 2016 AACE/ACE Guidelines, 2016, p. 22) (Grade A).

        Behavioral lifestyle intervention should be tailored to a patient's ethnic, cultural,
        socioeconomic, and educational background (Garvey et al., 2016 AACE/ACE Guidelines, 2016,
        p. 22) (Grade B).

        The USPSTF recommends that clinicians offer or refer adults with a body mass index (BMI) of
        30 kg/m2 or higher  to intensive, multicomponent behavioral interventions  (USPSTF, 2018)
        (Grade B).

        Interventions:
        - Effective intensive behavioral interventions were designed to help participants achieve
        or maintain a >= 5% weight loss through a combination of dietary changes and increased
        physical activity
        - Most interventions lasted for 1 to 2 years, and the majority had >= 12 sessions in the
        first year
        - Most behavioral interventions focused on problem solving to identify barriers, self-
        monitoring of weight, peer support, and relapse prevention
        - Interventions also provided tools to support weight loss or weight loss maintenance
        (e.g., pedometers, food scales, or exercise videos) (USPSTF, 2018)

        Nutritional safety for the elderly should be considered when recommending weight reduction.
        "A clinical decision to forego obesity treatment in older adults should be guided by an
        evaluation of the potential benefits of weight reduction for day-to-day functioning and
        reduction of the risk of future cardiovascular events, as well as the patient's motivation
        for weight reduction. Care must be taken to ensure that any weight reduction program
        minimizes the likelihood of adverse effects on bone health or other aspects of nutritional
        status" (NHLBI Obesity Education Initiative, 1998, p. 91) (Evidence Category D). In
        addition, weight reduction prescriptions in older persons should be accompanied by proper
        nutritional counseling and regular body weight monitoring (NHLBI Obesity Education
        Initiative, 1998, p. 91).

        The possibility that a standard approach to weight loss will work differently in diverse
        patient populations must be considered when setting expectations about treatment outcomes
        (NHLBI Obesity Education Initiative, 1998, p. 97) (Evidence Category B).
        """
        pass
