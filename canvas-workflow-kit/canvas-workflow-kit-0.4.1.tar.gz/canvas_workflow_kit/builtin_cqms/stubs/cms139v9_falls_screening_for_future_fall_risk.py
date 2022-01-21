from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AnnualWellnessVisit, AudiologyVisit, CareServicesInLongTermResidentialFacility,
    DischargeServicesNursingFacility, EncounterInpatient, Ethnicity, FallsScreening,
    HomeHealthcareServices, HospiceCareAmbulatory, NursingFacilityVisit, OfficeVisit,
    OncAdministrativeSex, OphthalmologicalServices, Payer,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesIndividualCounseling, PreventiveCareServicesInitialOfficeVisit18AndUp,
    Race)


class ClinicalQualityMeasure139v9(ClinicalQualityMeasure):
    """
    Falls: Screening for Future Fall Risk

    Description: Percentage of patients 65 years of age and older who were screened for future fall
    risk during the measurement period

    Definition: Screening for Future Fall Risk: Assessment of whether an individual has experienced
    a fall or problems with gait or balance.  A specific screening tool is not required for this
    measure, however potential screening tools include the Morse Fall Scale and the timed Get-Up-
    And-Go test.

    Fall: A sudden, unintentional change in position causing an individual to land at a lower
    level, on an object, the floor, or the ground, other than as a consequence of sudden onset of
    paralysis, epileptic seizure, or overwhelming external force.

    Rationale: As the leading cause of both fatal and nonfatal injuries for older adults, falls are
    one of the most common and significant health issues facing people aged 65 years or older
    (Schneider, Shubert and Harmon, 2010). Moreover, the rate of falls increases with age (Dykes et
    al., 2010). Older adults are five times more likely to be hospitalized for fall-related
    injuries than any other cause-related injury. It is estimated that one in every three adults
    over 65 will fall each year (Centers for Disease Control and Prevention 2015). In those over
    age 80, the rate of falls increases to fifty percent (Doherty et al., 2009). Falls are also
    associated with substantial cost and resource use, approaching $30,000 per fall hospitalization
    Woolcott et al., 2011). Identifying at-risk patients is the most important part of management,
    as applying preventive measures in this vulnerable population can have a profound effect on
    public health (al-Aama, 2011). Family physicians have a pivotal role in screening older
    patients for risk of falls, and applying preventive strategies for patients at risk (al-Aama,
    2011).

    Guidance: This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms139v9
    """

    title = 'Falls: Screening for Future Fall Risk'

    identifiers = ['CMS139v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'al-Aama, T. 2011. "Falls in the Elderly: Spectrum and Prevention." Can Fam Physician 57(7):771-6.',
        'American Geriatrics Society and British Geriatric Society. (2010) Prevention of Falls in Older Persons Clinical Practice Guidelines. Accessed June 14, 2018. Available at https://www.archcare.org/sites/default/files/pdf/2010-prevention-of-falls-in-older-persons-ags-and-bgs-clinical-practice-guideline.pdf',
        'Centers for Disease Control and Prevention. 2015. "Important Facts about Falls" (December 14, 2015) http://www.cdc.gov/HomeandRecreationalSafety/Falls/adultfalls.html',
        'Doherty, M., and J. Crossen-Sills. 2009. "Fall Risk: Keep your patients in balance." The Nurse Practitioner: The American Journal of Primary Health Care 34(12):46-51.',
        'Dykes, P.C., D.L. Carroll DL, A. Hurley A, S. Lipsitz S, A. Benoit A, F. Chang F, S. Meltzer S, R. Tsurikova R, L. Zuyov L, B. Middleton B. 2010. "Fall Prevention in Acute Care Hospitals: A Randomized Trial." JAMA . 2010;304(17):1912-1918.',
        'Schneider, E.C., T.E. Shubert, and K.J. Harmon. 2010. "Addressing the Escalating Public Health Issue of Falls Among Older Adults." NC Med J 71(6):547-52.',
        'Woolcott, J.C., K.M. Khan, S. Mitrovic, A.H. Anis, C.A. Marra. 2011. "The Cost of Fall Related Presentations to the ED: A Prospective, In-Person, Patient-Tracking Analysis of Health Resource Utilization." Osteporos Int [Epub ahead of print].',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients aged 65 years and older with a visit during the measurement
        period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Exclude patients whose hospice care overlaps the measurement period.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patients who were screened for future fall risk at least once within the
        measurement period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: All older persons who are under the care of a heath professional
        (or their caregivers) should be asked at least once a year about falls.  (AGS/BGS/AAOS
        2010)

        Older persons who present for medical attention because of a fall, report recurrent falls
        in the past year, or demonstrate abnormalities of gait and/or balance should have a fall
        evaluation performed.  This evaluation should be performed by a clinician with appropriate
        skills and experience, which may necessitate referral to a specialist (e.g., geriatrician).
        (AGS/BGS/AAOS 2010)
        """
        pass
