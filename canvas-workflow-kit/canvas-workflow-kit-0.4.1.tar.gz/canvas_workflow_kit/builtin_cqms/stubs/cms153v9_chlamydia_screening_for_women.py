from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    CarrierOfPredominantlySexuallyTransmittedInfection, Chlamydia, ChlamydiaScreening,
    ComplicationsOfPregnancyChildbirthAndThePuerperium, ContraceptiveMedications,
    DiagnosticStudiesDuringPregnancy, EncounterInpatient, Ethnicity, Female, GenitalHerpes,
    GonococcalInfectionsAndVenerealDiseases, Hiv, HomeHealthcareServices, HospiceCareAmbulatory,
    InflammatoryDiseasesOfFemaleReproductiveOrgans, Isotretinoin, OfficeVisit,
    OncAdministrativeSex, OtherFemaleReproductiveConditions, Payer,
    PreventiveCareEstablishedOfficeVisit0To17, PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit0To17, PreventiveCareServicesInitialOfficeVisit18AndUp,
    Race, SexuallyActive, Syphilis, XRayStudyAllInclusive)


class ClinicalQualityMeasure153v9(ClinicalQualityMeasure):
    """
    Chlamydia Screening for Women

    Description: Percentage of women 16-24 years of age who were identified as sexually active and
    who had at least one test for chlamydia during the measurement period

    Definition: None

    Rationale: Chlamydia trachomatis is the most common sexually transmitted bacterial infection in
    the U.S., resulting in roughly 1.7 million cases (Centers for Disease Control and Prevention,
    2018). Chlamydia infections are often asymptomatic, but, if left untreated, can lead to serious
    and irreversible complications (U.S. Preventive Services Task Force, 2014; Centers for Disease
    Control and Prevention, 2018).

    Women are particularly vulnerable when infected with chlamydia. Left untreated, chlamydia can
    cause pelvic inflammatory disease (PID), which can lead to chronic pelvic pain or infertility.
    Pregnant women may also transmit the infection to their infant, potentially resulting in
    neonatal pneumonia (Centers for Disease Control and Prevention, 2018).

    Guidance: Codes to identify sexually active women include codes for: pregnancy, sexually
    transmitted infections, contraceptives or contraceptive devices, and infertility treatments.

    The denominator exclusion does not apply to patients who qualify for the initial population
    (IP) based on services other than the pregnancy test alone. These other services include
    services for sexually transmitted infections, contraceptives or contraceptive devices and
    infertility treatments. For example, a patient who has both a pregnancy test and a chlamydia
    diagnosis, either of which would qualify them for the IP, would not be eligible for this
    denominator exclusion.

    Patient self-report for procedures as well as diagnostic studies should be recorded in
    'Procedure, Performed' template or 'Diagnostic Study, Performed' template in QRDA-1. Patient
    self-report is not allowed for laboratory tests.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms153v9
    """

    title = 'Chlamydia Screening for Women'

    identifiers = ['CMS153v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'Centers for Disease Control and Prevention (CDC). (2019). Sexually Transmitted Disease Surveillance 2018. Atlanta: U.S. Department of Health and Human Services.',
        'LeFevre, M. L., & U.S. Preventive Services Task Force. (2014). Screening for Chlamydia and gonorrhea: U.S. Preventive Services Task Force recommendation statement. Annals of Internal Medicine, 161(12), 902–910. https://doi.org/10.7326/M14-1981',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Women 16 to 24 years of age who are sexually active and who had a visit
        in the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Women who are only eligible for the initial population due to a pregnancy test
        and who had an x-ray or an order for a specified medication within 7 days of the pregnancy
        test.

        Exclude patients whose hospice care overlaps the measurement period.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Women with at least one chlamydia test during the measurement period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: U.S. Preventive Services Task Force (2014):
        The task force recommends screening for chlamydia in sexually active females aged 24 years
        or younger and in older women who are at increased risk for infection (B recommendation)
        """
        pass
