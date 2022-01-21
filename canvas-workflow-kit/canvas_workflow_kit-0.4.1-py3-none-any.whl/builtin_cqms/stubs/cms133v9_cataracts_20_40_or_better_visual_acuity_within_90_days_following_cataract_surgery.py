from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AcuteAndSubacuteIridocyclitis, Amblyopia, BestCorrectedVisualAcuityExamUsingSnellenChart,
    BurnConfinedToEyeAndAdnexa, CataractCongenital, CataractMatureOrHypermature,
    CataractPosteriorPolar, CataractSecondaryToOcularDisorders, CentralCornealUlcer,
    CertainTypesOfIridocyclitis, ChoroidalDegenerations, ChoroidalDetachment,
    ChoroidalHemorrhageAndRupture, ChronicIridocyclitis, CloudyCornea, CornealEdema,
    CornealOpacityAndOtherDisordersOfCornea, DegenerationOfMaculaAndPosteriorPole,
    DegenerativeDisordersOfGlobe, DiabeticMacularEdema, DiabeticRetinopathy,
    DisordersOfOpticChiasm, DisordersOfVisualCortex,
    DisseminatedChorioretinitisAndDisseminatedRetinochoroiditis, Ethnicity,
    FocalChorioretinitisAndFocalRetinochoroiditis, Glaucoma,
    GlaucomaAssociatedWithCongenitalAnomaliesDystrophiesAndSystemicSyndromes,
    HereditaryChoroidalDystrophies, HereditaryCornealDystrophies, HereditaryRetinalDystrophies,
    HypotonyOfEye, InjuryToOpticNerveAndPathways, MacularScarOfPosteriorPolar, MorgagnianCataract,
    NystagmusAndOtherIrregularEyeMovements, OncAdministrativeSex, OpenWoundOfEyeball, OpticAtrophy,
    OpticNeuritis, OtherAndUnspecifiedFormsOfChorioretinitisAndRetinochoroiditis,
    OtherBackgroundRetinopathyAndRetinalVascularChanges, OtherDisordersOfOpticNerve,
    OtherEndophthalmitis, OtherProliferativeRetinopathy, PathologicMyopia, Payer,
    PosteriorLenticonus, PriorPenetratingKeratoplasty, PurulentEndophthalmitis, Race,
    RetinalDetachmentWithRetinalDefect, RetinalVascularOcclusion, RetrolentalFibroplasias,
    ScleritisAndEpiscleritis, SeparationOfRetinalLayers, TraumaticCataract, Uveitis,
    VascularDisordersOfIrisAndCiliaryBody, VisualFieldDefects)


class ClinicalQualityMeasure133v9(ClinicalQualityMeasure):
    """
    Cataracts: 20/40 or Better Visual Acuity within 90 Days Following Cataract Surgery

    Description: Percentage of cataract surgeries for patients aged 18 and older with a diagnosis
    of uncomplicated cataract and no significant ocular conditions impacting the visual outcome of
    surgery and had best-corrected visual acuity of 20/40 or better (distance or near) achieved in
    the operative eye within 90 days following the cataract surgery

    Definition: None

    Rationale: In the United States, cataracts affect more than 24 million adults over 40 years
    (National Eye Institute, 2019). According to the American Academy of Ophthalmology (2016),
    cataract surgery has a substantial beneficial impact on visual function and on quality of life.

    1. Scientific basis for measuring visual acuity outcomes after cataract surgery
    The only reason to perform cataract surgery (other than for a limited set of medical
    indications) is to improve a patient's vision and associated functioning. The use of a 20/40
    visual acuity threshold is based on several considerations. First, it is the level for
    unrestricted operation of a motor vehicle in the US. Second, it has been consistently used by
    the FDA in its assessment for approval of intraocular lens (IOL) and other vision devices.
    Third, it is the literature standard to denote success in cataract surgery. Fourth, work by
    West et al. in the Salisbury Eye Study suggests that 20/40 is a useful threshold for 50th
    percentile functioning for several vision-related tasks.

    Most patients achieve excellent visual acuity after cataract surgery (20/40 or better). This
    outcome is achieved consistently through careful attention through the accurate measurement of
    axial length and corneal power and the appropriate selection of an IOL power calculation
    formula. As such, it reflects the care and diligence with which the surgery is assessed,
    planned and executed. Failure to achieve this after surgery in eyes without comorbid ocular
    conditions that would impact the success of the surgery would reflect care that should be
    assessed for opportunities for improvement.

    The exclusion of patients with other ocular and systemic conditions known to increase the risk
    of an adverse outcome reflects the findings of the two published prediction rule papers for
    cataract surgery outcomes, by Mangione et al. (1995) and Steinberg et al. (1994). In both
    papers, the presence of comorbid glaucoma and macular degeneration negatively impacted the
    likelihood of successful outcomes of surgery. Further, as noted in the prior indicator,
    exclusion of eyes with ocular conditions that could impact the success of the surgery would NOT
    eliminate the large majority of eyes undergoing surgery while also minimizing the potential
    adverse selection that might otherwise occur relative to those patients with the most complex
    situations who might benefit the most from having surgery to maximize their remaining vision.

    2. Evidence of a gap in care
    Cataract surgery successfully restores vision in the majority of people who have the procedure.

    Data from a study of 368,256 cataract surgeries show that corrected visual acuity (CDVA) of 0.5
    (20/40) or better was achieved in 94.3% and CDVA of 1.0 (20/20) or better was achieved in 61.3%
    of cases (Lundstrom, Barry, Henry, Rosen & Stenevi, 2013).

    Additionally, data from a UK multi-center Cataract National Dataset found a postoperative
    visual acuity of 6/12 (20/40) or better was achieved for 94.7% of eyes with no co-pathologies
    and in 79.9% of eyes with one or more co-pathologies (Jaycock et al., 2009).

    A rate of 85.5-94.7% of patients achieving a 20/40 or better visual acuity in the context of
    approximately 3 million cataract surgeries in the US annually would mean that between 160,000
    to 435,000 individuals would not achieve a 20/40 or better visual acuity which suggests an
    opportunity for improvement.

    Guidance: This eCQM is an episode-based measure, meaning there may be more than one reportable
    event for a given patient during the measurement period. The level of analysis for this measure
    is each cataract surgery during the measurement period, including instances where more than one
    cataract procedure was performed during the measurement period. Every cataract surgery during
    the measurement period should be counted as a measurable denominator event for the measure
    calculation.

    Only procedures performed during January 1 - September 30 of the reporting period will be
    considered for this measure, in order to determine if 20/40 or better visual acuity has been
    achieved within the 90 days following the cataract procedure. Cataract procedures performed
    during October 1 - December 31 are excluded from the initial population.

    The measure, as written, does not specifically require documentation of laterality. Coding
    limitations in particular clinical terminologies do not currently allow for that level of
    specificity (ICD-10-CM includes laterality, but SNOMED-CT does not uniformly include this
    distinction). Therefore, at this time, it is not a requirement of this measure to indicate
    laterality of the diagnoses, findings or procedures. Available coding to capture the data
    elements specified in this measure has been provided. It is assumed that the eligible
    professional or eligible clinician will record laterality in the patient medical record, as
    quality care and clinical documentation should include laterality.

    This measure is to be reported by the clinician performing the cataract surgery procedure.
    Clinicians who provide only preoperative or postoperative management of cataract patients are
    not eligible for this measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms133v9
    """

    title = 'Cataracts: 20/40 or Better Visual Acuity within 90 Days Following Cataract Surgery'

    identifiers = ['CMS133v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'American Academy of Ophthalmology. (2016). Cataract in the adult eye Preferred Practice Pattern. San Francisco, CA: American Academy of Ophthalmology.',
        'Jaycock, P., Johnston, R. L., Taylor, H., Adams, M., Tole, D. M., Galloway, P., … UK EPR user group (2009). The Cataract National Dataset electronic multi-centre audit of 55,567 operations: Updating benchmark standards of care in the United Kingdom and internationally. Eye, 23(1), 38-49. doi:10.1038/sj.eye.6703015',
        'Lundstrom, M., Barry, P., Henry, Y., Rosen, P., & Stenevi, U. (2013). Visual outcome of cataract surgery; Study from the European Registry of Quality Outcomes for Cataract and Refractive Surgery. Journal of Cataract & Refractive Surgery, 39(5), 673-679. doi:10.1016/j.jcrs.2012.11.026',
        'Mangione, C. M., Orav, J., Lawrence, M. G., Phillips, R.S., Seddon, J.M., & Goldman, L. (1995). Prediction of visual function after cataract surgery: A prospectively validated model. Archives of Ophthalmology, 113(10), 1305-1311. doi:10.1001/archopht.1995.01100100093037',
        'National Eye Institute. (2019). Cataract data and statistics. Retrieved from https://nei.nih.gov/eyedata/cataract',
        'Steinberg, E. P., Tielsch, J. M., Schein, O. D., Javitt, J. C., Sharkey, P., Cassard, S. D., … Damiano, A. M. (1994). National study of cataract surgery outcomes: Variation in 4-month postoperative outcomes as reflected in multiple outcome measures. Ophthalmology, 101(6), 1131-1141. doi:10.1016/s0161-6420(94)31210-3',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All cataract surgeries for patients aged 18 years and older who did not
        meet any exclusion criteria
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Cataract surgeries in patients with significant ocular conditions impacting the
        visual outcome of surgery

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Cataract surgeries with best-corrected visual acuity of 20/40 or better
        (distance or near) achieved in the operative eye within 90 days following cataract surgery

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: This is an outcome measure. As such, there is no statement in the
        guideline specific to this measurement topic.
        """
        pass
