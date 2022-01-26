from typing import List, Optional, Union

from canvas_workflow_kit import events
from canvas_workflow_kit.protocol import ClinicalQualityMeasure
from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.recommendation import VitalSignRecommendation, InstructionRecommendation, Recommendation

# flake8: noqa
from canvas_workflow_kit.value_set.v2018 import (
    AboveNormalFollowUp, AboveNormalMedications, BelowNormalFollowUp, BelowNormalMedications,
    BmiEncounterCodeSet, BmiLoincValue, Ethnicity, OncAdministrativeSex, PalliativeCareEncounter,
    PalliativeCare, Payer, PregnancyDx, Race, ReferralsWhereWeightAssessmentMayOccur,
    BmiPercentile, Height, Weight)


class ClinicalQualityMeasure69v6(ClinicalQualityMeasure):
    """
    Preventive Care and Screening: Body Mass Index (BMI) Screening and Follow-Up Plan

    Description: Percentage of patients aged 18 years and older with a BMI documented during the
    current encounter or during the previous twelve months AND with a BMI outside of normal
    parameters, a follow-up plan is documented during the encounter or during the previous twelve
    months of the current encounter

    Normal Parameters:       Age 18 years and older BMI => 18.5 and < 25 kg/m2

    Definition: BMI- Body mass index (BMI) is a number calculated using the Quetelet index: weight
    divided by height squared (W/H2) and is commonly used to classify weight categories. BMI can be
    calculated using:

    Metric Units:  BMI = Weight (kg) / (Height (m) x Height (m))
    OR
    English Units: BMI = Weight (lbs.) / (Height (in) x Height (in)) x 703

    Follow-Up Plan - Proposed outline of treatment to be conducted as a result of a BMI out of
    normal parameters. A follow-up plan may include, but is not limited to: documentation of
    education, referral (for example a registered dietician, nutritionist, occupational therapist,
    physical therapist, primary care provider, exercise physiologist, mental health professional,
    or surgeon), pharmacological interventions, dietary supplements, exercise counseling or
    nutrition counseling.

    Rationale: BMI Above Normal Parameters

    Obesity is a chronic, multifactorial disease with complex psychological, environmental (social
    and cultural), genetic, physiologic, metabolic and behavioral causes and consequences. The
    prevalence of overweight and obese people is increasing worldwide at an alarming rate in both
    developing and developed countries. Environmental and behavioral changes brought about by
    economic development, modernization and urbanization have been linked to the rise in global
    obesity. The health consequences are becoming apparent (ICSI 2013. p.6).

    Nationally, nearly 38 percent of adults are obese [NHANES, 2013-2014 data]. Nearly 8 percent of
    adults are extremely obese (BMI greater than or equal to 40.0); Obesity rates are higher among
    women (40.4 percent) compared to men (35.0 percent). Between 2005 and 2014, the difference in
    obesity among women was 5.1 percent higher among women and 1.7 percent higher among men. Women
    are also almost twice as likely (9.9 percent) to be extremely obese compared to men (5.5
    percent); In addition, rates are the highest among middle-age adults (41 percent for 40- to
    59-year-olds), compared to 34.3 percent of 20- to 39-year-olds and 38.5 percent of adults ages
    60 and older (Flegal KM, Kruszon-Moran D, Carroll MD, et al, 2016, p.2286-2290). Obesity is one
    of the biggest drivers of preventable chronic diseases and healthcare costs in the United
    States. Currently, estimates for these costs range from $147 billion to nearly $210 billion per
    year Cawley J and Meyerhoefer C., 2012 & Finkelstein, Trogdon, Cohen, et al., 2009). There are
    significant racial and ethnic inequities [NHANES, 2013-2014 data]: Obesity rates are higher
    among Blacks (48.4 percent) and Latinos (42.6 percent) than among Whites (36.4 percent) and
    Asian Americans (12.6 percent).The inequities are highest among women: Blacks have a rate of
    57.2 percent, Latinos of 46.9 percent, Whites of 38.2 percent and Asians of 12.4 percent. For
    men, Latinos have a rate of 37.9 percent, Blacks of 38.0 percent and Whites of 34.7 percent.
    Black women (16.8 percent) are twice as likely to be extremely obese as White women (9.7
    percent) (Flegal KM, Kruszon-Moran D, Carroll MD, et al., 2016, pp. 2284-2291).

    BMI continues to be a common and reasonably reliable measurement to identify overweight and
    obese adults who may be at an increased risk for future morbidity. Although good quality
    evidence supports obtaining a BMI, it is important to recognize it is not a perfect
    measurement. BMI is not a direct measure of adiposity and as a consequence it can over- or
    underestimate adiposity. BMI is a derived value that correlates well with total body fat and
    markers of secondary complications, e.g., hypertension and dyslipidemia (Barlow, 2007).

    In contrast with waist circumference, BMI and its associated disease and mortality risk appear
    to vary among ethnic subgroups. Female African American populations appear to have the lowest
    mortality risk at a BMI of 26.2-28.5 kg/m2 and 27.1-30.2 kg/m2 for women and men, respectively.
    In contrast, Asian populations may experience lowest mortality rates starting at a BMI of 23 to
    24 kg/m2. The correlation between BMI and diabetes risk also varies by ethnicity (LeBlanc,
    2011. p.2-3)

    Screening for BMI and follow-up therefore is critical to closing this gap and contributes to
    quality goals of population health and cost reduction. However, due to concerns for other
    underlying conditions (such as bone health) or nutrition related deficiencies providers are
    cautioned to use clinical judgment and  take these into account when considering weight
    management programs for overweight patients, especially the elderly (NHLBI Obesity Education
    Initiative, 1998, p. 91).

    BMI below Normal Parameters

    On the other end of the body weight spectrum is underweight (BMI <18.5 kg/m2), which is equally
    detrimental to population health. When compared to normal weight individuals(BMI 18.5-25
    kg/m2), underweight individuals have significantly higher death rates with a Hazard Ratio of
    2.27 and  95% confidence intervals (CI) = 1.78, 2.90 (Borrell & Lalitha (2014).

    Poor nutrition or underlying health conditions can result in underweight (Fryer & Ogden, 2012).
    The National Health and Nutrition Examination Survey (NHANES) results from the 2007-2010
    indicate that women are more likely to be underweight than men (2012). Therefore patients
    should be equally screened for underweight and followed up with nutritional counselling to
    reduce mortality and morbidity associated with underweight.

    Guidance: *  There is no diagnosis associated with this measure.
    *  This measure is to be reported a minimum of once per reporting period for patients seen
    during the reporting period.
    *  This measure may be reported by eligible professionals who perform the quality actions
    described in the measure based on the services provided at the time of the qualifying visit and
    the measure-specific denominator coding.

    BMI Measurement Guidance:
    *  Height and Weight - An eligible professional or their staff is required to measure both
    height and weight. Both height and weight must be measured within twelve months of the current
    encounter and may be obtained from separate encounters.  Self-reported values cannot be used.
    *  The BMI may be documented in the medical record of the provider or in outside medical
    records obtained by the provider.
    *  If the most recent documented BMI is outside of normal parameters, then a follow-up plan is
    documented during the encounter or during the previous twelve months of the current encounter.
    * If more than one BMI is reported during the measurement period, the most recent BMI will be
    used to determine if the performance has been met.
    * Review the exclusions criteria to determine those patients that BMI measurement may not be
    appropriate or necessary.

    Follow-Up Plan Guidance:

         1.      *  The documented follow-up plan must be based on the most recent documented BMI,
    outside of normal parameters, example: "Patient referred to nutrition counseling for BMI above
    or below normal parameters."

    (See Definitions for examples of follow-up plan treatments).
    Variation has been noted in studies exploring optimal BMI ranges for the elderly (see Donini et
    al., (2012); Holme and Tonstad (2015); and Diehr et al. (2008). Notably however, all these
    studies have arrived at ranges that differ from the standard range for ages 18 and older, which
    is >=18.5 and < 25 kg/m2. For instance, both Donini et al. (2012) and Holme and Tonstad (2015)
    reported findings that suggest that higher BMI (higher than the upper end of 25kg/m2) in the
    elderly may be beneficial. Similarly, worse outcomes have been associated with being
    underweight (at a threshold higher than 18.5 kg/m2) at age 65 (Diehr et al. 2008). Because of
    optimal BMI range variation recommendations from these studies, no specific optimal BMI range
    for the elderly is used. However, It may be appropriate to exempt certain patients from a
    follow-up plan by applying the exception criteria. Review the following to apply the Medical
    Reason exception criteria:
    The Medical Reason exception could include, but is not limited to, the following patients as
    deemed appropriate by the health care provider:
         *     Elderly Patients (65 or older) for whom weight reduction/weight gain would
    complicate other underlying health conditions such as the following examples:
                 *Illness or physical disability
                 *Mental illness, dementia, confusion
    *Nutritional deficiency such as Vitamin/mineral deficiency*

         *     Patients in an urgent or emergent medical situation where time is of the essence and
    to delay treatment would jeopardize the patient's health status

    More information: https://ecqi.healthit.gov/ecqm/measures/cms69v6
    """

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'Quality Insights',
    ]

    references = [
        'Barlow SE, the Expert Committee. Expert committee recommendations regarding the prevention, assessment, and treatment of child and adolescent overweight and obesity: summary report. Pediatrics 2007;120:S164-92.',
        'Barnes PM, & Schoenborn CA (2012). Trends in adults receiving a recommendation for exercise or other physical activity from a physician or other health professional. Centers for Disease Control and Prevention (CDC), National Center for Health Statistics (NCHS) Data Brief, No. 86: Feb 2012.',
        'Borrell, L.N. & Samuel, L. (2014). Body mass index categories and mortality risk in US adults: The effect of overweight and obesity on advancing death. American Journal of Public Health, 104, 512-519.',
        'Cawley J and Meyerhoefer C. The medical care costs of obesity: an instrumental variables approach. Journal of Health Economics, 31(1): 219-230, 2012.',
        'Diehr P, O\'Meara ES, Fitzpatrick A, Newman AB, Kuller L, Burke G. (2008) Weight, mortality, years of healthy life, and active life expectancy in older adults. Journal of American Geriatrics Society, 56, 76-83.',
        'Donini, L. M., Savina, C., Gennaro, E., De Felice, M. R., Rosano, A., Pandolfo, M. M., ... Chumlea, W. C. (2012). A Systematic Review Of The Literature Concerning The Relationship Between Obesity And Mortality In The Elderly. The Journal of Nutrition, Health & Aging, 16(1), 89-98.',
        'Finkelstein, E.A., Trogdon, J.G., Cohen, J.W., & Dietz, W. (2009). Annual Medical Spending Attributable To Obesity: Payer-And Service-Specific Estimates. Health Affairs, 28(5), w822-w831. doi: 10.1377/hlthaff.28.5.w822',
        'Fitch A, Everling L, Fox C, Goldberg J, Heim C, Johnson K, Kaufman T, Kennedy E, Kestenbaun C, Lano M, Leslie D, Newell T, O\'Connor P, Slusarek B, Spaniol A, Stovitz S, Webb B. Institute for Clinical Systems Improvement. Prevention and Management of Obesity for Adults, 4-10. Updated May 2013.',
        'Fryar, C. D., & Ogden, C. L. (2012). Prevalence of underweight among adults aged 20 and over: United States, 1960-1962 through 2007-2010. National Center for Health Statistics, Division of Health and Nutrition Examination Surveys. Retrieved from http://www.cdc.gov/nchs/data/hestat/underweight_adult_07_10/underweight_adult_07_10.pdf',
        'Garvey, W. T., Mechanick, J. I., Brett, E. M., Garber, A. J., Hurley, D. L., Jastreboff, A. M., Nadolsky, K., ... Reviewers of the AACE/ACE Obesity Clinical Practice Guidelines. (January 01, 2016). AMERICAN ASSOCIATION OF CLINICAL ENDOCRINOLOGISTS AND AMERICAN COLLEGE OF ENDOCRINOLOGY COMPREHENSIVE CLINICAL PRACTICE GUIDELINES FOR MEDICAL CARE OF PATIENTS WITH OBESITY. Endocrine Practice: Official Journal of the American College of Endocrinology and the American Association of Clinical Endocrinologists, 22, 1-203.',
        'Holme, I., & Tonstad, S. (2015) Survival in elderly men in relation to midlife and current BMI. Age and Ageing, 44, 3, 434-9.',
        'Jensen, M.D., Ryan, D.H., Apovian, C.M., Ard, J.D., Comuzzie, A. G., Donato, K.A., ... Yanovski, S.Z. (2013). Practice guidelines and the obesity society report of the american college of cardiology/american heart association task force on 2013 AHA/ACC/TOS guideline for the management of overweight and obesity in adults: A report of the american college of cardiology/american heart association task force on practice guidelines and the obesity society. Circulation. doi: 10.1161/01.cir.0000437739.71477.',
        'LeBlanc E, O\'Connor E, Whitlock EP, et al. Screening for and management of obesity and overweight in adults. Evidence Report No. 89. AHRQ Publication No. 11-05159-EF-1. Rockville, MD: Agency for Healthcare Research and Quality. October 2011.',
        'NHLBI Obesity Education Initiative. (1998). Clinical guidelines on the identification, evaluation, and treatment of overweight and obesity in adults.',
        'Ogden, C. L., Carroll, M. D., Kit, B. K., & Flegal, K. M. (2013). Prevalence of obesity among adults: United States, 2011-2012, Centers for Disease Control and Prevention (CDC), National Center for Health Statistics (NCHS) Data Brief, No. 131: Oct 2013. Retrieved from http://www.cdc.gov/nchs/data/databriefs/db131.pdf',
        'The State of Obesity. (n.d). Obesity Rates and Trends Overview. Retrieved from http://stateofobesity.org/obesity-rates-trends-overview/ (Access October 2016)',
        'The State of Obesity. (n.d). The Healthcare Costs of Obesity. Retrieved from http://stateofobesity.org/healthcare-costs-obesity/(Accessed October 2016)',
        'Wilkinson, J., Bass, C., Diem, S., Gravley, A., Harvey, L. Hayes, R., Johnson, K., Maciosek, M., McKeon, K., Milteer, L., Morgan, J., Rothe, P., Snellman, L., Solberg, L., Storlie, C., & Vincent, P. (2013). Institute for Clinical Systems Improvement. Preventive Services for Adults. Retrieved from https://www.icsi.org/_asset/gtjr9h/PrevServAdults-Interactive0912.pdf.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients 18 and older on the date of the encounter with at least
        one eligible encounter during the measurement period
        """
        age = self.patient.age_at(self.timeframe.end)
        if age < 18:
            return False
        return True

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Patients who are pregnant
        Patients receiving palliative care
        Patients who refuse measurement of height and/or weight or refuse follow-up

        Exceptions: Patients with a documented Medical Reason:
        * Elderly Patients (65 or older) for whom weight reduction/weight gain would complicate
        other underlying health conditions such as the following examples:
             *Illness or physical disability
             *Mental illness, dementia, confusion
             *Nutritional deficiency, such as Vitamin/mineral deficiency

        * Patients in an urgent or emergent medical situation where time is of the essence and to
        delay treatment would jeopardize the patient's health status
        """
        if not self.in_initial_population():
            return False

        # FIX: this isn't quite right - we need a more accurate way to
        # assess whether the patient is presently pregnant here
        if self.patient.conditions.within_one_year(self.timeframe).find(PregnancyDx):
            return False

        # FIX: how do we check for a PalliativeCareEncounter?  We have
        # Encounter but it doesn't appear to have codes attached.

        # FIX: how do we check to see if the patient has refused a
        # height/weight measure or refused a follow-up plan?

        return True

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
        Clinical recommendation: As cited in Fetch et al. (2013), The Institute for Clinical
        Systems Improvement (ICSI) Health Care Guideline,  Prevention and Management of Obesity for
        Adults provides the Strength of Recommendation as Strong for the following:
               -Record height, weight and calculate body mass index at least annually
        -Clinicians should consider waist circumference measurement to estimate disease risk for
        patients who have normal or overweight BMI scores. For adult patients with a BMI of 25 to
        34.9 kg/m2, sex-specific waist circumference cutoffs should be used in conjunction with BMI
        to identify increased disease risk.

        Individuals who are overweight (BMI 25<30), and who do not have indicators of increased CVD
        risk (e.g., diabetes, pre-diabetes, hypertension, dyslipidemia, elevated waist
        circumference) or other obesity-related comorbidities and
        individuals who have a history of overweight and are now normal weight with risk factors at
        acceptable levels:

        'Advise to frequently measure their own weight, and to avoid weight gain by adjusting their
        food intake if they start to gain more than a few pounds. Also, advice patients that
        engaging in regular physical activity will help them avoid weight gain.' (2013 AHA/AAC/TOS
        Obesity Guideline, p. 20)

        'Advise overweight and obese individuals who would benefit from weight loss to participate
        for >=6 months in a comprehensive lifestyle program that assists participants in adhering
        to a lower calorie diet and in increasing physical activity through the use of behavioral
        strategies... NHLBI Grade A (Strong)' (2013 AHA/AAC/TOS Obesity Guideline, p. 15)

        USPSTF Clinical Guideline (Grade B Recommendation)
        Individuals with a body mass index (BMI) of 30 kg/m2 or higher should be offered or
        referred to intensive, multicomponent behavioral interventions that include the following
        components:
        -       Behavioral management activities, such as setting weight-loss goals
        -       Improving diet or nutrition and increasing physical activity
        -       Addressing barriers to change
        -       Self-monitoring
        -       Strategizing how to maintain lifestyle changes


        Nutritional safety for the elderly should be considered when recommending weight reduction.
        'A clinical decision to forego obesity treatment in older adults should be guided by an
        evaluation of the potential benefits of weight reduction for day-to-day functioning and
        reduction of the risk of future cardiovascular events, as well as the patient's motivation
        for weight reduction. Care must be taken to ensure that any weight reduction program
        minimizes the likelihood of adverse effects on bone health or other aspects of nutritional
        status' Evidence Category D. (NHLBI Obesity Education Initiative, 1998, p. 91). In
        addition, weight reduction prescriptions in older persons should be accompanied by proper
        nutritional counseling and regular body weight monitoring. (NHLBI Obesity Education
        Initiative, 1998, p. 91).

        The possibility that a standard approach to weight loss will work differently in diverse
        patient populations must be considered when setting expectations about treatment outcomes.
        Evidence Category B. (NHLBI Obesity Education Initiative, 1998).
        """
        recommendations: List[Recommendation] = []
        status = 'not_applicable'
        narrative = ''

        patient = self.patient
        bmi = self.compute_bmi()

        # FIX: the text discuses recommending a waist measurement for
        # certain BMI ranges, but doesn't say what to do with that
        # information and it's not in the numerator.  Include it?

        year_range = Timeframe(start=self.timeframe.end.shift(years=-1), end=self.timeframe.end)
        followups = patient.instructions.within(year_range).find(AboveNormalFollowUp |
                                                                 BelowNormalFollowUp)

        if not bmi:
            narrative = f"{patient.first_name} should have their height and weight measured to assess their BMI."
            status = 'due'
            recommendations.append(VitalSignRecommendation(patient=self.patient))

        elif (bmi >= 18.5 and bmi < 25.0):
            narrative = f"{patient.first_name}'s BMI {bmi:.1f} is within normal range. " \
                        f'This protocol is satisfied.'
            status = 'current'
        elif bmi < 18.5:
            if followups:
                status = 'current'
                narrative = f"{patient.first_name}'s BMI {bmi:.1f} is below the normal range (18.5-25). " \
                            f"A followup instruction given with the last year satisfies this protocol."
            else:
                recommendations.append(
                    InstructionRecommendation(
                        patient=self.patient, instruction=AboveNormalFollowUp))
                status = 'due'
                narrative = f"{patient.first_name}'s BMI {bmi:.1f} is below the normal range (18.5-25). " \
                            f"You should discuss a follow-up plan with {patient.first_name}."
        else:
            if followups:
                status = 'current'
                narrative = f"{patient.first_name}'s BMI {bmi:.1f} is above the normal range (18.5-25). " \
                            f"A followup instruction given with the last year satisfies this protocol."
            else:
                recommendations.append(
                    InstructionRecommendation(
                        patient=self.patient, instruction=AboveNormalFollowUp))
                status = 'due'
                narrative = f"{patient.first_name}'s BMI {bmi:.1f} is above the normal range (18.5-25). " \
                            f"You should discuss a follow-up plan with {patient.first_name}."

        return {'status': status, 'narrative': narrative, 'recommendations': recommendations}

    def compute_bmi(self) -> Optional[float]:
        patient = self.patient
        t = self.timeframe
        bmi = None

        # look for a BMI or a height and weight within the period
        bmi_v = patient.vitalsigns.within_one_year(t).find(BmiPercentile | BmiLoincValue).last()

        if bmi_v:
            bmi = float(bmi_v['value'])
        else:
            height_v = patient.vitalsigns.within_one_year(t).find(Height).last()
            weight_v = patient.vitalsigns.within_one_year(t).find(Weight).last()

            if (height_v and weight_v):
                height: Optional[float]
                weight: Optional[float]

                # convert to metric if needed
                if height_v['units'] == 'in':
                    height = float(height_v['value']) * 0.0254
                elif height_v['units'] == 'm':
                    height = float(height_v['value'])
                elif height_v['units'] == 'cm':
                    height = float(height_v['value']) / 100.0
                else:
                    # unexepected unit, ignore - could throw an error here but who would catch it?
                    height = None

                # convert to metric if needed
                if weight_v['units'] == 'lbs':
                    weight = float(weight_v['value']) * 0.453592
                elif weight_v['units'] == 'kg':
                    weight = float(weight_v['value'])
                else:
                    # unexepected unit, ignore - could throw an error here but who would catch it?
                    weight = None

                if height and weight:
                    bmi = weight / (height * height)

        return bmi
