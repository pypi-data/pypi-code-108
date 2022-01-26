from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    CareServicesInLongTermResidentialFacility, DiabeticRetinopathy, Ethnicity,
    LevelOfSeverityOfRetinopathyFindings, MacularEdemaFindingsPresent, MacularExam,
    NursingFacilityVisit, OfficeVisit, OncAdministrativeSex, OphthalmologicalServices,
    OutpatientConsultation, Payer, Race)


class ClinicalQualityMeasure142v9(ClinicalQualityMeasure):
    """
    Diabetic Retinopathy: Communication with the Physician Managing Ongoing Diabetes Care

    Description: Percentage of patients aged 18 years and older with a diagnosis of diabetic
    retinopathy who had a dilated macular or fundus exam performed with documented communication to
    the physician who manages the ongoing care of the patient with diabetes mellitus regarding the
    findings of the macular or fundus exam at least once within 12 months

    Definition: Communication - May include documentation in the medical record indicating that the
    findings of the dilated macular or fundus exam were communicated (e.g., verbally, by letter)
    with the clinician managing the patient's diabetic care OR a copy of a letter in the medical
    record to the clinician managing the patient's diabetic care outlining the findings of the
    dilated macular or fundus exam.

    Findings - Includes level of severity of retinopathy (e.g., mild nonproliferative, moderate
    nonproliferative, severe nonproliferative, very severe nonproliferative, proliferative) AND the
    presence or absence of macular edema.

    Rationale: Diabetic retinopathy is a prevalent complication of diabetes, estimated to affect
    28.5% of diabetic patients in the US (Zhang et al., 2010). Diabetic Retinopathy is a key
    indicator of systemic complications of diabetes (Zhang, 2010). Coordination of care between the
    eye care specialist and the physician managing a patient’s ongoing diabetes care is essential
    in stemming the progression of vision loss. Communication from the eye care specialist to a
    primary care physician facilitates the exchange of information about the severity and
    progression of a patient’s diabetic retinopathy, adherence to recommended ocular care, need for
    follow-up visits, and treatment plans (Storey, Murchison, Pizzi, Hark, Dai, Leiby & Haller,
    2016). Data from the Diabetes Control and Complications Trial showed that diabetic treatment
    and maintenance of glucose control delays the onset and slows the progression of diabetic
    retinopathy (Aiello & DCCT/EDIC Research Group, 2014).

    Guidance: The measure, as written, does not specifically require documentation of laterality.
    Coding limitations in particular clinical terminologies do not currently allow for that level
    of specificity (ICD-10-CM includes laterality, but SNOMED-CT does not uniformly include this
    distinction). Therefore, at this time, it is not a requirement of this measure to indicate
    laterality of the diagnoses, findings or procedures. Available coding to capture the data
    elements specified in this measure has been provided. It is assumed that the eligible
    professional or eligible clinician will record laterality in the patient medical record, as
    quality care and clinical documentation should include laterality.

    The communication of results to the primary care physician providing ongoing care of a
    patient's diabetes should be completed soon after the dilated exam is performed. Eligible
    professionals or eligible clinicians reporting on this measure should note that all data for
    the reporting year is to be submitted by the deadline established by CMS. Therefore, eligible
    professionals or eligible clinicians who see patients towards the end of the reporting period
    (i.e., December in particular), should communicate the results of the dilated macular exam as
    soon as possible in order for those patients to be counted in the measure numerator.
    Communicating the results as soon as possible after the date of the exam will ensure the data
    are included in the submission to CMS.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms142v9
    """

    title = 'Diabetic Retinopathy: Communication with the Physician Managing Ongoing Diabetes Care'

    identifiers = ['CMS142v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'Aiello, L. P., & DCCT/EDIC Research Group (2014). Diabetic retinopathy and other ocular findings in the diabetes control and complications trial/epidemiology of diabetes interventions and complications study. Diabetes care, 37(1), 17–23. doi:10.2337/dc13-2251',
        'American Academy of Ophthalmology. (2017). Diabetic retinopathy Preferred Practice Pattern. San Francisco, CA: American Academy of Ophthalmology.',
        'Storey, P. P., Murchison, A. P., Pizzi, L. T., Hark, L. A., Dai, Y., Leiby, B. E., & Haller, J. A. Impact of physician communication on diabetic eye examination adherence: Results from a Retrospective Cohort Analysis. Retina. 2016 Jan;36(1):20-7. doi:10.1097/IAE.0000000000000652',
        'Zhang, X., Saaddine, J. B., Chou, C. F., Cotch, M. F., Cheng, Y. J., Geiss, L. S., … Klein, R. (2010). Prevalence of diabetic retinopathy in the United States, 2005-2008. JAMA, 304(6), 649–656. doi:10.1001/jama.2010.1111',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients aged 18 years and older with a diagnosis of diabetic
        retinopathy
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population who had a dilated macular or fundus exam performed

        Exclusions: None

        Exceptions: Documentation of medical reason(s) for not communicating the findings of the
        dilated macular or fundus exam to the physician who manages the ongoing care of the patient
        with diabetes.

        Documentation of patient reason(s) for not communicating the findings of the dilated
        macular or fundus exam to the physician who manages the ongoing care of the patient with
        diabetes.
        """
        pass

    def in_numerator(self):
        """
        Numerator: Patients with documentation, at least once within 12 months, of the findings of
        the dilated macular or fundus exam via communication to the physician who manages the
        patient's diabetic care

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: The ophthalmologist should refer patients with diabetes to a
        primary care physician for appropriate management of their systemic condition and should
        communicate examination results to the physician managing the patient's ongoing diabetes
        care (III; Good Quality; Strong Recommendation) (American Academy of Ophthalmology, 2017).

        Ophthalmologists should communicate the ophthalmologic findings and level of retinopathy
        with the primary care physician as well as the need for optimizing metabolic control (III;
        Good Quality; Strong Recommendation) (American Academy of Ophthalmology, 2017).

        Close partnership with the primary care physician is important to make sure that the care
        of the patient is optimized (III; Good Quality; Strong Recommendation) (American Academy of
        Ophthalmology, 2017).
        """
        pass
