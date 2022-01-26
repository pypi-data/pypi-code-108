from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AceInhibitorOrArbOrArni, AcuteInpatient, AnnualWellnessVisit,
    CareServicesInLongTermResidentialFacility, DementiaMedications, Diabetes, DiabeticNephropathy,
    DialysisEducation, Ed, EncounterInpatient, EsrdMonthlyOutpatientServices, Ethnicity,
    FrailtyDevice, FrailtyDiagnosis, FrailtyEncounter, FrailtySymptom,
    GlomerulonephritisAndNephroticSyndrome, HomeHealthcareServices, HospiceCareAmbulatory,
    HypertensiveChronicKidneyDisease, KidneyFailure, NonacuteInpatient, NursingFacilityVisit,
    Observation, OfficeVisit, OncAdministrativeSex, OtherServicesRelatedToDialysis, Outpatient,
    Payer, PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, Proteinuria, Race, UrineProteinTests)


class ClinicalQualityMeasure134v9(ClinicalQualityMeasure):
    """
    Diabetes: Medical Attention for Nephropathy

    Description: The percentage of patients 18-75 years of age with diabetes who had a nephropathy
    screening test or evidence of nephropathy during the measurement period

    Definition: None

    Rationale: As the seventh leading cause of death in the U.S., diabetes kills approximately
    79,500 people a year and affects more than 30 million Americans (9.4 percent of the U.S.
    population) (CDC, 2017a, 2017b). Diabetes is a long-lasting disease marked by high blood
    glucose levels, resulting from the body's inability to produce or use insulin properly (CDC,
    2019). People with diabetes are at increased risk of serious health complications including
    vision loss, heart disease, stroke, kidney failure, amputation of toes, feet or legs, and
    premature death. (CDC, 2016).

    In 2017, diabetes cost the U.S. an estimated $327 billion: $237 billion in direct medical costs
    and $90 billion in reduced productivity. This is a 34 percent increase from the estimated $245
    billion spent on diabetes in 2012 (American Diabetes Association, 2018).

    High blood sugar levels in patients with diabetes put them at a higher risk of damaging their
    kidneys and causing chronic kidney disease, which can lead to kidney failure (CDC, 2016,
    2017c). During 2011-2012 there were 36.5% new cases of chronic kidney disease (stages 1-4)
    among 297,000 diabetic patients 20 years and older (Murphy et al., 2016). In 2014, diabetes
    accounted for 44% of 118,000 new cases of end stage renal disease (United States Renal Data
    System, 2016).

    Guidance: Only patients with a diagnosis of Type 1 or Type 2 diabetes should be included in the
    denominator of this measure; patients with a diagnosis of secondary diabetes due to another
    condition should not be included.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms134v9
    """

    title = 'Diabetes: Medical Attention for Nephropathy'

    identifiers = ['CMS134v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'American Association of Clinical Endocrinologists & American College of Endocrinology. (2015). Clinical practice guidelines for developing a diabetes mellitus comprehensive care plan—2015. Endocrine Practice, 21(Suppl. 1). Retrieved from https://www.aace.com/files/dm-guidelines-ccp.pdf',
        'American Diabetes Association. (2018). Economic costs of diabetes in the U.S. in 2017. Diabetes Care, 41, 917-928. Retrieved from http://care.diabetesjournals.org/content/early/2018/03/20/dci18-0007',
        'American Diabetes Association. (2019). 11. Microvascular complications and foot care: Standards of medical care in diabetes—2019. Diabetes Care, 42(Suppl. 1), S124-S138. https://doi.org/10.2337/dc19-S011',
        'Centers for Disease Control and Prevention. (2016). At a glance 2016: Diabetes—Working to reverse the U.S. epidemic. Atlanta, GA: Author. Retrieved from https://upcap.org/admin/wp-content/uploads/2016/06/Diabetes-at-a-Glance.pdf',
        'Centers for Disease Control and Prevention. (2017a). Health, United States, 2016: With chartbook on long-term trends in health. Retrieved from https://www.cdc.gov/nchs/data/hus/hus16.pdf',
        'Centers for Disease Control and Prevention. (2017b). National diabetes statistics report, 2017. Atlanta, GA: U.S. Department of Health and Human Services, CDC. Retrieved from https://www.cdc.gov/diabetes/pdfs/data/statistics/national-diabetes-statistics-report.pdf',
        'Centers for Disease Control and Prevention. (2019). About diabetes. Retrieved from https://www.cdc.gov/diabetes/basics/diabetes.html',
        'Centers for Disease Control and Prevention. (2017c). National chronic kidney disease fact sheet. Retrieved from https://www.cdc.gov/diabetes/pubs/pdf/kidney_factsheet.pdf',
        'Murphy, D., McCulloch, C. E., Lin, F., et al. (2016). Trends in prevalence of chronic kidney disease in the United States. Annals of Internal Medicine, 165(7), 473-481. Retrieved from https://annals.org/aim/fullarticle/2540849/trends-prevalence-chronic-kidney-disease-united-states',
        'United States Renal Data System. (2016). 2016 USRDS annual data report: Epidemiology of kidney disease in the United States. Bethesda, MD: National Institute of Diabetes and Digestive and Kidney Diseases, National Institutes of Health.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients 18-75 years of age with diabetes with a visit during the
        measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Exclude patients whose hospice care overlaps the measurement period.

        Exclude patients 66 and older who are living long term in an institution for more than 90
        consecutive days during the measurement period.

        Exclude patients 66 and older with advanced illness and frailty because it is unlikely that
        patients will benefit from the services being measured.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients with a screening for nephropathy or evidence of nephropathy during the
        measurement period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: American Diabetes Association (2019):
        Screening
        - At least once a year, assess urinary albumin (e.g., spot urinary albumin-to-creatinine
        ratio [UACR]) and estimated glomerular filtration rate (eGFR) in patients with type 1
        diabetes with duration of >=5 years, in all patients with type 2 diabetes, and in all
        patients with comorbid hypertension. (Level of evidence: B)

        Treatment
        - An angiotensin-converting enzyme (ACE) inhibitor or angiotensin receptor blocker (ARB) is
        not recommended for the primary prevention of diabetic kidney disease in patients with
        diabetes who have normal blood pressure, normal UACR (<30 mg/g creatinine), and normal
        estimated glomerular filtration rate. (Level of evidence: B)
        - In nonpregnant patients with diabetes and hypertension, either an ACE inhibitor or ARB is
        recommended for those with modestly elevated UACR (30-299 mg/g creatinine) (Level of
        evidence: B) and is strongly recommended for those with UACR >=300 mg/g creatinine and/or
        eGFR <60 mL/min/1.73.m2. (Level of evidence: A)
        - Periodically monitor serum creatinine and potassium levels for the development of
        increased creatinine or changes in potassium when ACE inhibitors, ARB, or diuretics are
        used. (Level of evidence: B)
        - Continued monitoring of UACR in patients with albuminuria treated with an ACE inhibitor
        or an ARB is reasonable to assess the response to treatment and progression of chronic
        kidney disease. (Level of evidence: E)
        - When eGFR is <60 mL/min/1.73 m2, evaluate and manage potential complications of chronic
        kidney disease. (Level of evidence: E)
        -Patients should be referred for evaluation for renal replacement treatment if they have an
        eGFR <30 mL/min/1.73 m2. (Level of evidence: A)
        -Promptly refer to a physician experienced in the care of kidney disease for uncertainty
        about the etiology of kidney disease, difficult management issues, and rapidly progressing
        kidney disease. (Level of evidence: B)

        American Association of Clinical Endocrinologists & American College of Endocrinology
        (2015):
        - Beginning 5 years after diagnosis in patients with type 1 diabetes (if diagnosed before
        age 30) or at diagnosis in patients with type 2 diabetes and those with type 1 diabetes
        diagnosed after age 30, annual assessment of serum creatinine to determine the estimated
        glomerular filtration rate (eGFR) and urine albumin excretion rate (AER) should be
        performed to identify, stage, and monitor progression of diabetic nephropathy. (Grade C;
        best evidence level 3)
        - Patients with nephropathy should be counseled regarding the need for optimal glycemic
        control, blood pressure control, dyslipidemia control, and smoking cessation. (Grade B;
        best evidence level 2)
        - In addition, they should have routine monitoring of albuminuria, kidney function
        electrolytes, and lipids. (Grade B; best evidence level 2)
        - Associated conditions such as anemia and bone and mineral disorders should be assessed as
        kidney function declines. (Grade D; best evidence level 4)
        - Referral to a nephrologist is recommended well before the need for renal replacement
        therapy. (Grade D; best evidence level 4)
        """
        pass
