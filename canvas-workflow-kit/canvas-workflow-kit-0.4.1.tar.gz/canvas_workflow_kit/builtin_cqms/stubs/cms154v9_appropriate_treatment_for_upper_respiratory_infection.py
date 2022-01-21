from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AntibioticMedicationsForPharyngitis, ComorbidConditionsForRespiratoryConditions,
    CompetingConditionsForRespiratoryConditions, EmergencyDepartmentVisit, EncounterInpatient,
    Ethnicity, HospiceCareAmbulatory, HospitalObservationCareInitial, OfficeVisit,
    OncAdministrativeSex, Payer, PreventiveCareEstablishedOfficeVisit0To17,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit0To17, PreventiveCareServicesInitialOfficeVisit18AndUp,
    Race, TelephoneVisits, UpperRespiratoryInfection)


class ClinicalQualityMeasure154v9(ClinicalQualityMeasure):
    """
    Appropriate Treatment for Upper Respiratory Infection (URI)

    Description: Percentage of episodes for patients 3 months of age and older with a diagnosis of
    upper respiratory infection (URI) that did not result in an antibiotic dispensing event.

    Definition: None

    Rationale: Most URI, also known as the common cold, are caused by viruses that require no
    antibiotic treatment. Too often, antibiotics are prescribed inappropriately, which can lead to
    antibiotic resistance (when antibiotics can no longer cure bacterial infections). In the United
    States, at least 2 million antibiotic-resistant illnesses and 23,000 deaths occur each year, at
    a cost to the U.S. economy of at least $30 billion.

    Guidance: This is an episode of care measure that examines all eligible episodes for the
    patient during the measurement period.

    This eCQM is a episode-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms154v9
    """

    title = 'Appropriate Treatment for Upper Respiratory Infection (URI)'

    identifiers = ['CMS154v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'Centers for Disease Control and Prevention. (2018). Be antibiotics aware: Smart use, best care. Retrieved from https://www.cdc.gov/features/antibioticuse/',
        'Fashner, J., Ericson, K., & Werner, S. (2012). Treatment of the common cold in children and adults. American Family Physician, 86(2), 153-159.',
        'Harris, A.M., Hicks, L.A., Qaseem, A. (2016.) "Appropriate antibiotic use for acute respiratory tract infection in adults: advice for high-value care from the American College of Physicians and The Centers for Disease Control and Prevention." Ann Intern Med. 164(6):425-434.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Outpatient visits, telephone visits, online assessments, observation
        stays or emergency department visits with a diagnosis of URI during the measurement period
        among patients 3 months of age and older.
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Exclude URI episodes when the patient had a competing comorbid condition during
        the 12 months prior to or on the episode date.

        Exclude URI episodes when the patient had a new or refill prescription of antibiotics in
        the 30 days prior to or on the episode date.

        Exclude URI episodes when the patient had competing diagnosis on or three days after the
        episode date.

        Exclude URI episodes when the patient had hospice care overlapping with the measurement
        period.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: URI episodes without a prescription for antibiotic medication on or 3 days after
        the outpatient visit, telephone visit, online assessment, observation stay or emergency
        department visit for an upper respiratory infection

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: American Family Physician (Fashner, Ericson, and Werner, Khilberg
        2012)

        - Antibiotics should not be used for the treatment of cold symptoms in children or adults.
        (A)

        - Nonsteroidal anti-inflammatory drugs reduce pain secondary to upper respiratory tract
        infection in adults. (A)

        - Decongestants, antihistamine/decongestant combinations, and intranasal ipratropium
        (Atrovent) may improve cold symptoms in adults. (B)
        """
        pass
