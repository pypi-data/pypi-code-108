from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    BmiPercentile, CounselingForNutrition, CounselingForPhysicalActivity, EncounterInpatient,
    Ethnicity, Height, HomeHealthcareServices, HospiceCareAmbulatory, OfficeVisit,
    OncAdministrativeSex, Payer, Pregnancy, PreventiveCareEstablishedOfficeVisit0To17,
    PreventiveCareServicesGroupCounseling, PreventiveCareServicesIndividualCounseling,
    PreventiveCareServicesInitialOfficeVisit0To17, Race, Weight)


class ClinicalQualityMeasure155v9(ClinicalQualityMeasure):
    """
    Weight Assessment and Counseling for Nutrition and Physical Activity for Children and
    Adolescents

    Description: Percentage of patients 3-17 years of age who had an outpatient visit with a
    Primary Care Physician (PCP) or Obstetrician/Gynecologist (OB/GYN) and who had evidence of the
    following during the measurement period. Three rates are reported.

     - Percentage of patients with height, weight, and body mass index (BMI) percentile
    documentation
     - Percentage of patients with counseling for nutrition
     - Percentage of patients with counseling for physical activity

    Definition: None

    Rationale: Over the last four decades, childhood obesity has more than tripled in children and
    adolescents 2 to 19 years of age (from a rate of approximately 5 percent to 18.5 percent)
    (Fryar, Carroll, & Ogden, 2014; Hales et al., 2017). Non-Hispanic black and Hispanic youth are
    more likely to be obese than their non-Hispanic white and non-Hispanic Asian counterparts. In
    2015-2016, approximately 22 percent of non-Hispanic black and 26 percent of Hispanic youth were
    obese compared to approximately 14 percent of non-Hispanic white and 11 percent of non-Hispanic
    Asian youth (Hales et al., 2017).

    Childhood obesity has both immediate and long-term effects on health and well-being. Children
    who are obese have higher rates of physical health conditions, such as risk factors for
    cardiovascular disease (like high blood pressure and high cholesterol), type 2 diabetes,
    asthma, sleep apnea, and joint problems. There is also a correlation between childhood obesity
    and mental health conditions, such as anxiety and depression (Centers for Disease Control and
    Prevention, 2016). In addition, children who are obese are more likely to be obese as adults
    and are therefore at risk for adult health problems, such as heart disease, type 2 diabetes,
    and several types of cancer (Centers for Disease Control and Prevention, 2016).

    The direct medical costs associated with childhood obesity total about $19,000 per child,
    contributing to the $14 billion spent on care related to childhood obesity in the United States
    (Finkelstein, Graham, & Malhotra, 2014).

    Because obesity can become a lifelong health issue, it is important to screen for obesity in
    children and adolescents, and to provide interventions that promote weight loss (U.S.
    Preventive Services Task Force, 2017).

    Guidance: The visit must be performed by a PCP or OB/GYN.
    Because BMI norms for youth vary with age and sex, this measure evaluates whether BMI
    percentile, rather than an absolute BMI value, is assessed.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms155v9
    """

    title = 'Weight Assessment and Counseling for Nutrition and Physical Activity for Children and Adolescents'

    identifiers = ['CMS155v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'Centers for Disease Control and Prevention. (2016). Childhood obesity causes & consequences. Retrieved from https://www.cdc.gov/obesity/childhood/causes.html',
        'Finkelstein, E. A., Graham, W. C. K., & Malhotra, R. (2014). Lifetime direct medical costs of childhood obesity. Pediatrics, 133(5), 854-862.',
        'Fryar, C. D., Carroll, M. D., & Ogden, C. L. (2014). Prevalence of overweight and obesity among children and adolescents: United States, 1963-1965 through 2011-2012. Health E-Stats. Retrieved from https://www.cdc.gov/nchs/data/hestat/obesity_child_11_12/obesity_child_11_12.htm',
        'Hagan, J. F., Shaw, J. S., & Duncan, P. M. (eds.). (2017). Bright futures: Guidelines for health supervision of infants, children, and adolescents, 4th ed. Elk Grove Village, IL: American Academy of Pediatrics.',
        'Hales, C.M., Carroll, M.D., Fryar C.D., et al. (2017). Prevalence of obesity among adults and youth: United States, 2015-2016. NCHS Data Brief. Retrieved from https://www.cdc.gov/nchs/data/databriefs/db288.pdf',
        'U.S. Preventive Services Task Force. (2017). Screening and interventions for overweight in children and adolescents: Recommendation statement. Rockville, MD: Agency for Healthcare Research and Quality. https://www.uspreventiveservicestaskforce.org/Page/Document/UpdateSummaryFinal/obesity-in-children-and-adolescents-screening1?ds=1&s=obesity',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients 3-17 years of age with at least one outpatient visit with a
        primary care physician (PCP) or an obstetrician/gynecologist (OB/GYN) during the
        measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Patients who have a diagnosis of pregnancy during the measurement period.

        Exclude patients whose hospice care overlaps the measurement period.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Numerator 1: Patients who had a height, weight and body mass index (BMI)
        percentile recorded during the measurement period
        Numerator 2: Patients who had counseling for nutrition during the measurement period
        Numerator 3: Patients who had counseling for physical activity during the measurement
        period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: U.S. Preventive Services Task Force (2017) - The task force
        recommends that clinicians screen for obesity in children and adolescents 6 years and older
        and offer or refer them to comprehensive, intensive behavioral interventions to promote
        improvements in weight status. (B recommendation)

        American Academy of Pediatrics – Bright Futures (Hagan, Shaw, & Duncan, 2017) -

        - Plot and assess BMI percentiles routinely for early recognition of overweight and
        obesity.
        - Assess barriers to healthy eating and physical activity.
        - Provide anticipatory guidance for nutrition and physical activity.
        """
        pass
