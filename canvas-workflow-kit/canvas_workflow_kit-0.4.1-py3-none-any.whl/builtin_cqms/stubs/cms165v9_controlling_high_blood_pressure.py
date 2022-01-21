from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AcuteInpatient, AnnualWellnessVisit, CareServicesInLongTermResidentialFacility,
    ChronicKidneyDiseaseStage5, DementiaMedications, Ed, EncounterInpatient, EndStageRenalDisease,
    EsrdMonthlyOutpatientServices, EssentialHypertension, Ethnicity, FrailtyDevice,
    FrailtyDiagnosis, FrailtyEncounter, FrailtySymptom, HomeHealthcareServices,
    HospiceCareAmbulatory, KidneyTransplantRecipient, NonacuteInpatient, NursingFacilityVisit,
    Observation, OfficeVisit, OncAdministrativeSex, Outpatient, Payer, Pregnancy,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, Race)


class ClinicalQualityMeasure165v9(ClinicalQualityMeasure):
    """
    Controlling High Blood Pressure

    Description: Percentage of patients 18-85 years of age who had a diagnosis of hypertension
    overlapping the measurement period or the year prior to the measurement period, and whose most
    recent blood pressure was adequately controlled (<140/90mmHg) during the measurement period

    Definition: None

    Rationale: High blood pressure (HBP), also known as hypertension, is when the pressure in blood
    vessels is higher than normal (Centers for Disease Control and Prevention [CDC], 2016). The
    causes of hypertension are multiple and multifaceted and can be based on genetic
    predisposition, environmental risk factors, being overweight and obese, sodium intake,
    potassium intake, physical activity, and alcohol use. High Blood Pressure is common, according
    to the National Health and Nutrition Examination Survey (NHANES), approximately 85.7 million
    adults >= 20 years of age had HBP (140/90 mm Hg) between 2011 to 2014 (Crim, 2012). Between
    2011-2014 the prevalence of hypertension (>=140/90 mm Hg) among US adults 60 and older was
    approximately 67.2 percent (Benjamin et al., 2017).

    HBP, known as the “silent killer,” increases risks of heart disease and stroke which are two of
    the leading causes of death in the U.S. (Yoon, Fryar, & Carroll, 2015). A person who has HBP is
    four times more likely to die from a stroke and three times more likely to die from heart
    disease (CDC, 2012) The National Vital Statistics Systems Center for Disease Control and
    Prevention reported that in 2014 there were approximately 73,300 deaths directly due to HBP and
    410,624 deaths with any mention of HBP (CDC, 20145).Between 2004 and 2014 the number of deaths
    due to HBP rose by 34.1 percent (Benjamin et al., 2017). Managing and treating HBP would reduce
    cardiovascular disease mortality for males and females by 30.4 percent and 38.0 percent,
    respectively (Patel et al., 2015).

    The estimated annual average direct and indirect cost of HBP from 2012 to 2013 was $51.2
    billion (Benjamin et al., 2017). Total direct costs of HBP is projected to increase to $200
    billion by 2030 (Benjamin et al., 2017). A study on cost-effectiveness on treating hypertension
    found that controlling HBP in patients with cardiovascular disease and systolic blood pressures
    of >=160 mm Hg could be effective and cost-saving (Moran et al., 2015).

    Many studies have shown that controlling high blood pressure reduces cardiovascular events and
    mortality. The Systolic Blood Pressure Intervention Trial (SPRINT) investigated the impact of
    obtaining a SBP goal of <120 mm Hg compared to a SBP goal of <140 mm Hg among patients 50 and
    older with established cardiovascular disease and found that the patients with the former goal
    had reduced cardiovascular events and mortality (SPRINT Research Group et al., 2015).

    Controlling HBP will significantly reduce the risks of cardiovascular disease mortality and
    lead to better health outcomes like reduction of heart attacks, stroke, and kidney disease
    (James et al., 2014). Thus, the relationship between the measure (control of hypertension) and
    the long-term clinical outcomes listed is well established.

    Guidance: In reference to the numerator element, only blood pressure readings performed by a
    clinician or a remote monitoring device are acceptable for numerator compliance with this
    measure.

    Do not include BP readings:
    -Taken during an acute inpatient stay or an ED visit
    -Taken on the same day as a diagnostic test or diagnostic or therapeutic procedure that
    requires a change in diet or change in medication on or one day before the day of the test or
    procedure, with the exception of fasting blood tests.
    -Reported by or taken by the member

    If no blood pressure is recorded during the measurement period, the patient's blood pressure is
    assumed "not controlled."

    If there are multiple blood pressure readings on the same day, use the lowest systolic and the
    lowest diastolic reading as the most recent blood pressure reading.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms165v9
    """

    title = 'Controlling High Blood Pressure'

    identifiers = ['CMS165v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'American Diabetes Association. (2019). 10. Cardiovascular disease and risk management: Standards of medical care in diabetes—2019. Diabetes Care, 42(Suppl. 1), S103-S123. https://doi.org/10.2337/dc19S010',
        'Benjamin, E. J., Blaha, M. J., Chiuve, S. E., et al. (2017). Heart disease and stroke statistics-2017 update: A report from the American Heart Association. Circulation, 135(10), e146-e603.doi: 10.1161/CIR.0000000000000485',
        'Centers for Disease Control and Prevention. (2012). Vital signs: Getting blood pressure under control. Retrieved from https://www.cdc.gov/vitalsigns/hypertension/index.html',
        'Centers for Disease Control and Prevention. Division for Heart Disease and Stroke Prevention. (2016). High blood pressure fact sheet. Retrieved from https://www.cdc.gov/dhdsp/data_statistics/fact_sheets/fs_bloodpressure.htm',
        'Centers for Disease Control and Prevention, National Center for Health Statistics. (2015). Underlying Cause of Death 1999-2013 on CDC WONDER Online Database. Data are from the Multiple Cause of Death Files, 1999-2013, as compiled from data provided by the 57 vital statistics jurisdictions through the Vital Statistics Cooperative Program. Retrieved from http://wonder.cdc.gov/ucd-icd10.html',
        'Crim, M. T., Yoon, S. S., Ortiz, E., et al. (2012). National surveillance definitions for hypertension prevalence and control among adults. Circulation: Cardiovascular Quality and Outcomes. 2012, ;5(3), :343-–351. doi: 10.1161/ CIRCOUTCOMES.111.963439.',
        'Moran, A. E., Odden, M. C., Thanataveerat, A., et al.Tzong KY, Rasmussen PW, Guzman D, Williams L, Bibbins-Domingo K, Coxson PG, Goldman L. (2015). Cost-effectiveness of hypertension therapy according to 2014 guidelines. [published correction appears in N Engl J. Med. 2015;372:1677]. New England Journal of Medicine. 2015 ;372, 447-455. doi: 10.1056/NEJMsa1406751. [published correction appears on page 1677]',
        'Patel, S. A., Winkel, M., Ali, M. K., et al. (2015). Cardiovascular mortality associated with 5 leading risk factors: National and state preventable fractions estimated from survey data. Annals of Internal Medicine, 163(4), 245-253. doi: 10.7326/M14-1753',
        'Qaseem, A., Wilt, T. J., Rich, R., et al. (2017). Pharmacologic treatment of hypertension in adults aged 60 years or older to higher versus lower blood pressure targets: A clinical practice guideline from the American College of Physicians and the American Academy of Family Physicians. Annals of Internal Medicine, 166(6), 430-437. Retrieved from https://annals.org/aim/fullarticle/2598413/pharmacologic-treatment-hypertension-adults-aged-60-years-older-higher-versus',
        'SPRINT Research Group, Wright, J. T., Jr., Williamson, J. D., et al. (2015). A randomized trial of intensive versus standard blood-pressure control. New England Journal of Medicine, 373(22), 2103–2116.',
        'U.S. Preventive Services Task Force. (2015). Screening for high blood pressure in adults: U.S. Preventive Services Task Force recommendation statement. Annals of Internal Medicine, 163(10), 778-787. Retrieved from https://annals.org/aim/fullarticle/2456129/screening-high-blood-pressure-adults-u-s-preventive-services-task',
        'Whelton, P. K., Carey, R. M., Aronow, W. S., et al. (2017). Guideline for the prevention, detection, evaluation, and management of high blood pressure in adults: A report of the American College of Cardiology/American Heart Association Task Force on Clinical Practice Guidelines. Journal of the American College of Cardiology. https://doi.org/10.1161/HYP.0000000000000065',
        'Yoon, S. S., Fryar, C. D., & Carroll, M. D. (2015). Hypertension prevalence and control among adults: United States, 2011-2014. NCHS Data Brief No. 220. Hyattsville, MD: National Center for Health Statistics.',
        'Farley TA, Dalal MA, Mostashari F, Frieden TR. Deaths preventable in the US by improvements in the use of clinical preventive services. Am J Prev Med. 2010;38:600-9. Retrieved from https://www.ajpmonline.org/article/S0749-3797(10)00207-2/fulltext',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients 18-85 years of age who had a visit and diagnosis of essential
        hypertension overlapping the measurement period or the year prior to the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Patients with evidence of end stage renal disease (ESRD), dialysis or renal
        transplant before or during the measurement period. Also exclude patients with a diagnosis
        of pregnancy during the measurement period.

        Exclude patients whose hospice care overlaps the measurement period.

        Exclude patients 66 and older who are living long term in an institution for more than 90
        consecutive days during the measurement period.

        Exclude patients 66 and older with advanced illness and frailty because it is unlikely that
        patients will benefit from the services being measured.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients whose most recent blood pressure is adequately controlled (systolic
        blood pressure < 140 mmHg and diastolic blood pressure < 90 mmHg) during the measurement
        period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: The U.S. Preventive Services Task Force (2015) recommends
        screening for high blood pressure in adults age 18 years and older. This is a grade A
        recommendation.

        American College of Cardiology/American Heart Association (2017)

        -For adults with confirmed hypertension and known CVD or 10-year ASCVD event risk of 10% or
        higher, a blood pressure target of less than 130/80 mmHg is recommended (Level of evidence:
        B-R (for systolic blood pressures), Level of evidence: C-EO (for diastolic blood pressure))

        -For adults with confirmed hypertension, without additional markers of increased CVD risk,
        a blood pressure target of less than 130/80 mmHg may be reasonable (Note: clinical trial
        evidence is strongest for a target blood pressure of 140/90 mmHg in this population.
        However, observational studies suggest that these individuals often have a high lifetime
        risk and would benefit from blood pressure control earlier in life) (Level of evidence:
        B-NR (for systolic blood pressure), Level of evidence: C-EO (for diastolic blood pressure))

        American College of Physicians and the American Academy of Family Physicians (2017):

        -Initiate or intensify pharmacologic treatment in some adults aged 60 years or older at
        high cardiovascular risk, based on individualized assessment, to achieve a target systolic
        blood pressure of less than 140 mmHg (Grade: weak recommendation, Quality of evidence: low)

        -Initiate or intensify pharmacologic treatment in adults aged 60 years or older with a
        history of stroke or transient ischemic attack to achieve a target systolic blood pressure
        of less than 140 mmHg to reduce the risk of recurrent stroke (Grade: weak recommendation,
        Quality of evidence: moderate)

        American Diabetes Association (2019):

        -For individuals with diabetes and hypertension at higher cardiovascular risk (existing
        atherosclerotic cardiovascular disease or 10-year atherosclerotic cardiovascular disease
        risk >15%), a blood pressure target of <130/80 mmHg may be appropriate, if it can be safely
        attained (Level of evidence: C)-For individuals with diabetes and hypertension at lower
        risk for cardiovascular disease (10-year atherosclerotic cardiovascular disease risk <15%),
        treat to a blood pressure target of <140/90 mmHg (Level of evidence: A)
        """
        pass
