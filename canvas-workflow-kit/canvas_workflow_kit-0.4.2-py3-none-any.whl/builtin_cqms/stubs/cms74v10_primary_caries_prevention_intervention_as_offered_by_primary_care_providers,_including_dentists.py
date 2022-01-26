from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    ClinicalOralEvaluation, EncounterInpatient, Ethnicity, HospiceCareAmbulatory, OfficeVisit,
    OncAdministrativeSex, Payer, PreventiveCareEstablishedOfficeVisit0To17,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit0To17, PreventiveCareServicesInitialOfficeVisit18AndUp,
    Race)


class ClinicalQualityMeasure74v10(ClinicalQualityMeasure):
    """
    Primary Caries Prevention Intervention as Offered by Primary Care Providers, including Dentists

    Description: Percentage of children, 6 months - 20 years of age, who received a fluoride
    varnish application during the measurement period

    Definition: None

    Rationale: The literature reflects that fluoride varnish, when applied to the teeth of high-
    risk children, reduces, in conjunction with anticipatory guidance provided to the caregiver,
    the risk of the child developing caries (Weintraub et al., 2006).

    Guidance: This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms74v10
    """

    title = 'Primary Caries Prevention Intervention as Offered by Primary Care Providers, including Dentists'

    identifiers = ['CMS74v10']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'Weintraub, J. A., Ramos-Gomez, F., Jue, B., et al. (2006). Fluoride varnish efficacy in preventing early childhood caries. Journal of Dental Research, 85(2), 172-176.',
        'Weyant, R. J., Tracy, S. L., Anselmo, T. T., et al. (2013). Topical fluoride for caries prevention: Executive summary of the updated clinical recommendations and supporting systematic review. Journal of the American Dental Association, 144(11), 1279-1291. doi: 10.14219/jada.archive.2013.0057',
        'Moyer, V.A. on behalf of the US Preventive Services Task Force. (2014). Prevention of dental caries in children from birth through age 5 years: US Preventive Services Task Force recommendation statement. Pediatrics, 133(6), 1102-1111.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Children, 6 months - 20 years of age, with a visit during the
        measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Exclude patients whose hospice care overlaps the measurement period

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Children who receive a fluoride varnish application during the measurement
        period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: ADA clinical recommendations for use of professionally applied or
        prescription-strength, home-use topical fluorides for caries prevention in patients at
        elevated risk of developing caries:

        - Younger Than 6 Years - 2.26 percent fluoride varnish at least every three to six months

        - 6-18 Years - 2.26 percent fluoride varnish at least every three to six months OR 1.23
        percent fluoride (APF*) gel for four minutes at least every three to six months

        - Older Than 18 Years - 2.26 percent fluoride varnish at least every three to six months OR
        1.23 percent fluoride (APF) gel for four minutes at least every three to six months (Weyant
        et al., 2013)

        The USPSTF [US Preventive Services Task Force] recommends that primary care clinicians
        apply fluoride varnish to the primary teeth of all infants and children starting at the age
        of primary tooth eruption. (B recommendation)
        """
        pass
