from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    Ethnicity, HumanImmunodeficiencyVirusHivLaboratoryTestCodesAbAndAg,
    IndicatorsOfHumanImmunodeficiencyVirusHiv, OfficeVisit, OncAdministrativeSex, Payer,
    PreventiveCareEstablishedOfficeVisit0To17, PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit0To17, PreventiveCareServicesInitialOfficeVisit18AndUp,
    Race)


class ClinicalQualityMeasure349v3(ClinicalQualityMeasure):
    """
    HIV Screening

    Description: Percentage of patients aged 15-65 at the start of the measurement period who were
    between 15-65 years old when tested for HIV

    Definition: None

    Rationale: Human immunodeficiency virus (HIV) is a communicable infection that leads to a
    progressive disease with a long asymptomatic period. There were an estimated 38,700 new HIV
    infections in the United States in 2016 (Centers for Disease Control and Prevention, 2019a).
    Without treatment, most persons develop acquired immunodeficiency syndrome (AIDS) within 10
    years of HIV infection. Antiretroviral therapy (ART) delays this progression and increases the
    length of survival, but it is most effective when initiated during the asymptomatic phase.
    Persons living with HIV who use ART and achieve viral suppression can have a nearly normal life
    expectancy (Samji et al., 2013).  DHHS Guidelines for the Use of Antiretroviral Agents in
    HIV-1-Infected Adults and Adolescents recommends antiretroviral therapy for all HIV-infected
    individuals to reduce the risk of disease progression (regardless of CD4 cell count at
    diagnosis) (Panel on Antiretroviral Guidelines for Adults and Adolescents, 2017).

    CDC estimates that, at the end of 2016, approximately 14% of the 1.1 million adults and
    adolescents living with HIV infection in the United States were unaware of their infection
    (Centers for Disease Control and Prevention, 2018b). Among persons diagnosed with HIV in 2017,
    approximately 21% were diagnosed with Stage 3 HIV (AIDS) at the time of HIV diagnosis (Centers
    for Disease Control and Prevention, 2019c), which is when the median CD4 count at diagnosis is
    less than 200 cells/mm3 for persons aged greater than or equal to 6 years (Centers for Disease
    Control and Prevention, 2019a). HIV screening identifies infected persons who were previously
    unaware of their infection, which enables them to seek medical and social services that can
    improve their health and the quality and length of their lives. Additionally, using ART with
    high levels of medication adherence has been shown to substantially reduce risk for HIV
    transmission (Panel on Antiretroviral Guidelines for Adults and Adolescents, 2017).

    Based on the Behavioral Risk Factor Surveillance System (BRFSS), the percentage of ever tested
    for HIV increased from 42.9% in 2011 to 45.9% in 2017. Despite this increase, less than half of
    US adults have ever been tested for HIV over ten years after CDC’s recommendations (Patel et
    al., 2019).

    Guidance: This measure evaluates the proportion of patients aged 15 to 65 at the start of the
    measurement period who have documentation of having received an HIV test at least once on or
    after their 15th birthday and before their 66th birthday. In order to satisfy the measure, the
    reporting provider must have documentation of the administration of the laboratory test present
    in the patient's medical record. In cases where the HIV test was performed elsewhere, providers
    cannot rely on patient attestation or self-report to meet the measure requirements, as previous
    research has shown that patient self-report is an unreliable indicator of previous HIV testing
    history. Rather, providers must request documentation of those test results. If such
    documentation is not available, the patient should be considered still eligible for HIV
    screening. If such documentation is available, but cannot be provided in a standardized,
    structured format (such that the lab test and results can be readily incorporated as structured
    data within the EHR), providers should enter the information into their EHR as a laboratory
    test in a manner consistent with the EHR in use. If the specific Human Immunodeficiency Virus
    (HIV) Laboratory Test LOINC code of the test is not known, the entry should use the more
    generic code LOINC panel code [75622-1].

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms349v3
    """

    title = 'HIV Screening'

    identifiers = ['CMS349v3']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'Mathematica',
    ]

    references = [
        'Centers for Disease Control and Prevention. (2019a). Estimated HIV incidence and prevalence in the United States, 2010–2016; Table 1, page 20. HIV Surveillance Supplemental Report, 24(1). Retrieved from http://www.cdc.gov/hiv/library/reports/hiv-surveillance.html',
        'Centers for Disease Control and Prevention. (2019b). Estimated HIV incidence and prevalence in the United States, 2010–2016. HIV Surveillance Supplemental Report, 24(1). Retrieved from https://www.cdc.gov/hiv/pdf/library/reports/surveillance/cdc-hiv-surveillance-supplemental-report-vol-24-1.pdf',
        'Centers for Disease Control and Prevention. (2019c, June). Monitoring selected national HIV prevention and care objectives by using HIV surveillance data—United States and 6 dependent areas, 2017. HIV Surveillance Supplemental Report, 24(3). Retrieved from https://www.cdc.gov/hiv/pdf/library/reports/surveillance/cdc-hiv-surveillance-supplemental-report-vol-24-3.pdf',
        'Centers for Disease Control and Prevention. (2006). Revised recommendations for HIV testing of adults, adolescents, and pregnant women in health care settings. Morbidity and Mortality Weekly Report, 55(RR-14), 1-17.',
        'Owens, on behalf of the U.S. Preventive Task Force. (2019). Screening for HIV: US Preventive Services Task Force Recommendation Statement. JAMA, 321(23), 2326-2336.',
        'Panel on Antiretroviral Guidelines for Adults and Adolescents. (2017). Guidelines for the use of antiretroviral agents in HIV-1-infected adults and adolescents. Retrieved from https://aidsinfo.nih.gov/contentfiles/lvguidelines/adultandadolescentgl.pdf',
        'Patel, D., Johnson, C.H., Krueger, A. et al. (2019). Trends in HIV Testing Among US Adults, Aged 18–64 Years, 2011–2017. AIDS Behav.',
        'Samji, H., Cescon, A., Hogg, R. S., et al. (2013). Closing the gap: Increases in life expectancy among treated HIV-positive individuals in the United States and Canada. PLoS One, 8, e81355.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients 15 to 65 years of age at the start of the measurement period
        AND who had at least one outpatient visit during the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Patients diagnosed with HIV prior to the start of the measurement period

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients with documentation of an HIV test performed on or after their 15th
        birthday and before their 66th birthday

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: The US Preventive Services Task Force recommends that clinicians
        screen for HIV infection in adolescents and adults aged 15 to 65 years. Younger adolescents
        and older adults who are at increased risk should also be screened (A Recommendation)
        (Owens, et al., 2019).

        Since 2006, the CDC has recommended routine opt-out HIV screening (i.e., patient is
        notified that testing will be performed unless the patient declines) in healthcare
        facilities of adolescents and adults 13-64 years of age and HIV diagnostic testing of
        adolescents and adults with clinical signs or symptoms consistent with HIV infection
        (Centers for Disease Control and Prevention, 2006).
        """
        pass
