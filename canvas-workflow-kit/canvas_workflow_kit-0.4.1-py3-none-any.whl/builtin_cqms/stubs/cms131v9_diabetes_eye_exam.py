from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AcuteInpatient, AnnualWellnessVisit, CareServicesInLongTermResidentialFacility,
    DementiaMedications, Diabetes, DiabeticRetinopathy, Ed, EncounterInpatient, Ethnicity,
    FrailtyDevice, FrailtyDiagnosis, FrailtyEncounter, FrailtySymptom, HomeHealthcareServices,
    HospiceCareAmbulatory, NonacuteInpatient, NursingFacilityVisit, Observation, OfficeVisit,
    OncAdministrativeSex, OphthalmologicalServices, Outpatient, Payer,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, Race, RetinalOrDilatedEyeExam)


class ClinicalQualityMeasure131v9(ClinicalQualityMeasure):
    """
    Diabetes: Eye Exam

    Description: Percentage of patients 18-75 years of age with diabetes and an active diagnosis of
    retinopathy overlapping the measurement period who had a retinal or dilated eye exam by an eye
    care professional during the measurement period or diabetics with no diagnosis of retinopathy
    overlapping the measurement period who had a retinal or dilated eye exam by an eye care
    professional during the measurement period or in the 12 months prior to the measurement period

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

    Diabetic retinopathy is progressive damage to the small blood vessels in the retina that may
    result in loss of vision. It is the leading cause of blindness in adults between 20-74 years of
    age. Approximately 4.1 million adults are affected by diabetic retinopathy (CDC, 2015).

    Guidance: Only patients with a diagnosis of Type 1 or Type 2 diabetes should be included in the
    denominator of this measure; patients with a diagnosis of secondary diabetes due to another
    condition should not be included.

    The eye exam must be performed by an ophthalmologist or optometrist.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms131v9
    """

    title = 'Diabetes: Eye Exam'

    identifiers = ['CMS131v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'American Diabetes Association. (2018). Economic costs of diabetes in the U.S. in 2017. Diabetes Care, 41, 917-928. Retrieved from http://care.diabetesjournals.org/content/early/2018/03/20/dci18-0007',
        'American Diabetes Association. (2019). 11. Microvascular complications and foot care: Standards of medical care in diabetes—2019. Diabetes Care, 42(Suppl. 1), S 124-S138. https://doi.org/10.2337/dc19-S011',
        'Centers for Disease Control and Prevention. (2017a). Health, United States, 2016: With chartbook on long-term trends in health. Retrieved from https://www.cdc.gov/nchs/data/hus/hus16.pdf',
        'Centers for Disease Control and Prevention. (2017b). National diabetes statistics report, 2017. Atlanta, GA: U.S. Department of Health and Human Services, CDC. Retrieved from https://www.cdc.gov/diabetes/pdfs/data/statistics/national-diabetes-statistics-report.pdf',
        'Centers for Disease Control and Prevention. (2019). About diabetes. Retrieved from https://www.cdc.gov/diabetes/basics/diabetes.html',
        'Centers for Disease Control and Prevention. (2016). At a glance 2016: Diabetes—Working to reverse the U.S. epidemic. Atlanta, GA: Author. Retrieved from https://upcap.org/admin/wp-content/uploads/2016/06/Diabetes-at-a-Glance.pdf',
        'Centers for Disease Control and Prevention. (2015). Common eye disorders: Diabetic retinopathy. Retrieved from https://www.cdc.gov/visionhealth/basics/ced/index.html',
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
        Numerator: Patients with an eye screening for diabetic retinal disease. This includes
        diabetics who had one of the following:
        •Diabetic with a diagnosis of retinopathy that overlaps the measurement period and a
        retinal or dilated eye exam by an eye care professional in the measurement period
        •Diabetic with no diagnosis of retinopathy overlapping the measurement period and a retinal
        or dilated eye exam by an eye care professional in the measurement period or the year prior
        to the measurement period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: American Diabetes Association (2019):

        - Adults with type 1 diabetes should have an initial dilated and comprehensive eye
        examination by an ophthalmologist or optometrist within 5 years after the onset of
        diabetes. (Level of evidence: B)

        - Patients with type 2 diabetes should have an initial dilated and comprehensive eye
        examination by an ophthalmologist or optometrist at the time of the diabetes diagnosis.
        (Level of evidence: B)

        -If there is no evidence of retinopathy for one or more annual eye exam and glycemia is
        well controlled, then exams every 1–2 years may be considered. If any level of diabetic
        retinopathy is present, subsequent dilated retinal examinations should be repeated at least
        annually by an ophthalmologist or optometrist. If retinopathy is progressing or sight
        threatening, then examinations will be required more frequently. (Level of evidence: B)
        """
        pass
