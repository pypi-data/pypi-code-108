from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AcuteInpatient, AnnualWellnessVisit, CareServicesInLongTermResidentialFacility,
    DementiaMedications, Diabetes, Ed, EncounterInpatient, Ethnicity, FrailtyDevice,
    FrailtyDiagnosis, FrailtyEncounter, FrailtySymptom, Hba1CLaboratoryTest,
    HomeHealthcareServices, HospiceCareAmbulatory, NonacuteInpatient, NursingFacilityVisit,
    Observation, OfficeVisit, OncAdministrativeSex, Outpatient, Payer,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, Race)


class ClinicalQualityMeasure122v9(ClinicalQualityMeasure):
    """
    Diabetes: Hemoglobin A1c (HbA1c) Poor Control (> 9%)

    Description: Percentage of patients 18-75 years of age with diabetes who had hemoglobin A1c >
    9.0% during the measurement period

    Definition: None

    Rationale: As the seventh leading cause of death in the U.S., diabetes kills approximately
    79,500 people a year and affects more than 30 million Americans (9.4 percent of the U.S.
    population) (Centers for Disease Control and Prevention [CDC], 2017a, 2017b). Diabetes is a
    long-lasting disease marked by high blood glucose levels, resulting from the body's inability
    to produce or use insulin properly (CDC, 2019). People with diabetes are at increased risk of
    serious health complications including vision loss, heart disease, stroke, kidney failure,
    amputation of toes, feet or legs, and premature death (CDC, 2016).

    In 2017, diabetes cost the U.S. an estimated $327 billion: $237 billion in direct medical costs
    and $90 billion in reduced productivity. This is a 34 percent increase from the estimated $245
    billion spent on diabetes in 2012 (American Diabetes Association, 2018).

    Controlling A1c blood levels help reduce the risk of microvascular complications (eye, kidney
    and nerve diseases) (CDC, 2014).

    Guidance: Patient is numerator compliant if most recent HbA1c level >9%, the most recent HbA1c
    result is missing, or if there are no HbA1c tests performed and results documented during the
    measurement period. If the HbA1c test result is in the medical record, the test can be used to
    determine numerator compliance.

    Only patients with a diagnosis of Type 1 or Type 2 diabetes should be included in the
    denominator of this measure; patients with a diagnosis of secondary diabetes due to another
    condition should not be included.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms122v9
    """

    title = 'Diabetes: Hemoglobin A1c (HbA1c) Poor Control (> 9%)'

    identifiers = ['CMS122v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'American Diabetes Association. (2018). Economic costs of diabetes in the U.S. in 2017. Diabetes Care, 41, 917-928. Retrieved from http://care.diabetesjournals.org/content/early/2018/03/20/dci18-0007',
        'American Diabetes Association. (2019). 6. Glycemic targets: Standards of medical care in diabetes—2019. Diabetes Care, 42(Suppl. 1), S61-S70. https://doi.org/10.2337/dc19-S006',
        'Centers for Disease Control and Prevention. (2014). National diabetes statistics report, 2014. Atlanta, GA: U.S. Department of Health and Human Services, CDC. Retrieved from http://www.thefdha.org/pdf/diabetes.pdf',
        'Centers for Disease Control and Prevention. (2016). At a glance 2016: Diabetes—Working to reverse the U.S. epidemic. Atlanta, GA: Author. Retrieved from https://upcap.org/admin/wp-content/uploads/2016/06/Diabetes-at-a-Glance.pdf',
        'Centers for Disease Control and Prevention. (2017a). Health, United States, 2016: With chartbook on long-term trends in health. Retrieved from https://www.cdc.gov/nchs/data/hus/hus16.pdf',
        'Centers for Disease Control and Prevention. (2017b). National diabetes statistics report, 2017. Atlanta, GA: U.S. Department of Health and Human Services, CDC. Retrieved from https://www.cdc.gov/diabetes/pdfs/data/statistics/national-diabetes-statistics-report.pdf',
        'Centers for Disease Control and Prevention. (2019). About diabetes. Retrieved from https://www.cdc.gov/diabetes/basics/diabetes.html',
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
        Numerator: Patients whose most recent HbA1c level (performed during the measurement period)
        is >9.0%

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: American Diabetes Association (2019):

        - A reasonable A1C goal for many nonpregnant adults is <7%. (Level of evidence: A)

        - Providers might reasonably suggest more stringent A1C goals (such as <6.5% [48 mmol/mol])
        for selected individual patients if this can be achieved without significant hypoglycemia
        or other adverse effects of treatment (i.e. polypharmacy). Appropriate patients might
        include those with short duration of diabetes, type 2 diabetes treated with lifestyle or
        metformin only, long life expectancy, or no significant cardiovascular disease (CVD).
        (Level of evidence: C)

        - Less stringent A1C goals (such as <8% [64 mmol/mol]) may be appropriate for patients with
        a history of severe hypoglycemia, limited life expectancy, advanced microvascular or
        macrovascular complications, extensive comorbid
         conditions, or long-standing diabetes in whom the goal is difficult to achieve despite
        diabetes self-management education, appropriate glucose monitoring, and effective doses of
        multiple glucose-lowering agents including insulin. (Level of evidence: B)
        """
        pass
