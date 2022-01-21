from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    CareServicesInLongTermResidentialFacility, CupToDiscRatio, Ethnicity, NursingFacilityVisit,
    OfficeVisit, OncAdministrativeSex, OphthalmologicalServices,
    OpticDiscExamForStructuralAbnormalities, OutpatientConsultation, Payer,
    PrimaryOpenAngleGlaucoma, Race)


class ClinicalQualityMeasure143v9(ClinicalQualityMeasure):
    """
    Primary Open-Angle Glaucoma (POAG): Optic Nerve Evaluation

    Description: Percentage of patients aged 18 years and older with a diagnosis of primary open-
    angle glaucoma (POAG) who have an optic nerve head evaluation during one or more office visits
    within 12 months

    Definition: None

    Rationale: Glaucoma is a group of diseases that damage the eye’s optic nerve and can result in
    vision loss and blindness. In 2011, 2.71 million persons in the U.S. had primary open-angle
    glaucoma (POAG) and in 2050, an estimated 7.32 million persons will have POAG (Vajaranant, Wu,
    Torres, & Varma, 2012). Furthermore, a study by Rein, Zhang, & Wirth (2006) estimated that the
    total financial burden of major visual disorders among U.S. residents aged 40 years or older
    was $35.4 billion in 2004: $16.2 billion in direct medical costs, $11.1 billion in other direct
    costs, and $8 billion in productivity losses. Of the direct medical costs, approximately $2.9
    billion was attributable to glaucoma (Rein, Zhang, & Wirth, 2006). It is imperative that
    evidence-based care be delivered to all glaucoma patients.

    According to recent guidelines, optic nerve changes are one of the characteristics which
    reflect progression of glaucoma (the other characteristic is visual field). Examination of the
    optic nerve head (ONH) and retinal nerve fiber layer (RNFL) provides valuable structural
    information about optic nerve damage from glaucoma. Visible structural alterations of the ONH
    or RNFL may precede the onset of visual field defects. Careful study of the optic disc neural
    rim for small hemorrhages is important because these hemorrhages sometimes signal focal disc
    damage and visual field loss, and they may signify ongoing optic nerve damage in patients with
    glaucoma (American Academy of Ophthalmology, 2015). Despite evidence emphasizing the value of
    an optic nerve evaluation, there is a gap in documentation patterns of the optic nerve for both
    initial and follow-up care.

    This measure is intended to promote examination and documentation of the structure and function
    of the optic nerve, and to monitor and detect disease progression among patients diagnosed with
    POAG.

    Guidance: Optic nerve head evaluation includes examination of the cup to disc ratio and
    identification of optic disc or retinal nerve abnormalities. Both of these components of the
    optic nerve head evaluation are examined using ophthalmoscopy.

    The measure, as written, does not specifically require documentation of laterality. Coding
    limitations in particular clinical terminologies do not currently allow for that level of
    specificity (ICD-10-CM includes laterality, but SNOMED-CT does not uniformly include this
    distinction). Therefore, at this time, it is not a requirement of this measure to indicate
    laterality of the diagnoses, findings or procedures. Available coding to capture the data
    elements specified in this measure has been provided. It is assumed that the eligible
    professional or eligible clinician will record laterality in the patient medical record, as
    quality care and clinical documentation should include laterality.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms143v9
    """

    title = 'Primary Open-Angle Glaucoma (POAG): Optic Nerve Evaluation'

    identifiers = ['CMS143v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'American Academy of Ophthalmology (2015). Primary open-angle glaucoma Preferred Practice Pattern. San Francisco, CA: American Academy of Ophthalmology.',
        'Rein, D. B., Zhang, P., & Wirth, K. (2006). The economic burden of major adult visual disorders in the United States. Archives of Ophthalmology, 124(12), 1754-1760. doi:10.1001/archopht.124.12.1754',
        'Vajaranant, T. S., Wu, S., Torres, M., & Varma, R. (2012). The changing face of primary open-angle glaucoma in the United States: Demographic and geographic changes from 2011 to 2050. American Journal of Ophthalmology, 154(2). doi:10.1016/j.ajo.2012.02.024',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients aged 18 years and older with a diagnosis of primary open-
        angle glaucoma
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: None

        Exceptions: Documentation of medical reason(s) for not performing an optic nerve head
        evaluation
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients who have an optic nerve head evaluation during one or more office
        visits within 12 months

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: Ophthalmic Evaluation
        The ophthalmic evaluation specifically focuses on the following elements in the
        comprehensive adult medical eye evaluation:

        Visual acuity measurement
        Pupil examination
        Anterior segment examination
        IOP measurement
        Gonioscopy
        Optic nerve head (ONH) and retinal nerve fiber layer (RNFL) examination
        Fundus examination
        (American Academy of Ophthalmology, 2015)

        The optic nerve should be carefully examined for the signs of glaucoma damage, and its
        appearance should be serially documented (I+, moderate quality, strong recommendation)
        (American Academy of Ophthalmology, 2015).
        """
        pass
