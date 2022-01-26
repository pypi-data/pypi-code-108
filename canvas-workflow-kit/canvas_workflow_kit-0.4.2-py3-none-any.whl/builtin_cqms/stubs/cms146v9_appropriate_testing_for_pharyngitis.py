from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AcutePharyngitis, AcuteTonsillitis, AntibioticMedicationsForPharyngitis,
    ComorbidConditionsForRespiratoryConditions, CompetingConditionsForRespiratoryConditions,
    EmergencyDepartmentVisit, EncounterInpatient, Ethnicity, GroupAStreptococcusTest,
    HomeHealthcareServices, HospiceCareAmbulatory, HospitalObservationCareInitial,
    MedicalDisabilityExam, OfficeVisit, OncAdministrativeSex, OutpatientConsultation, Payer,
    PreventiveCareEstablishedOfficeVisit0To17, PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesGroupCounseling, PreventiveCareServicesIndividualCounseling,
    PreventiveCareServicesInitialOfficeVisit0To17, PreventiveCareServicesInitialOfficeVisit18AndUp,
    PreventiveCareServicesOther, Race, TelephoneVisits)


class ClinicalQualityMeasure146v9(ClinicalQualityMeasure):
    """
    Appropriate Testing for Pharyngitis

    Description: The percentage of episodes for patients 3 years and older with a diagnosis of
    pharyngitis that resulted in an antibiotic dispensing event and a group A streptococcus (strep)
    test

    Definition: None

    Rationale: Group A streptococcal bacterial infections and other infections that cause
    pharyngitis (which are most often viral) often produce the same signs and symptoms (Shulman et
    al., 2012). The American Academy of Pediatrics, the Centers for Disease Control and Prevention,
    and the Infectious Diseases Society of America all recommend a diagnostic test for Strep A to
    improve diagnostic accuracy and avoid unnecessary antibiotic treatment (Linder et al ., 2005).

    Estimated economic costs of pediatric streptococcal pharyngitis in the United States range from
    $224 million to $539 million per year, including indirect costs related to parental work
    losses. At a higher level, the economic cost of antibiotic resistance varies but has extended
    as high as $20 billion in excess direct healthcare costs, with additional costs to society for
    lost productivity as high as $35 billion a year (2008 dollars) (Pfoh et al, 2008).

    Guidance: This is an episode of care measure that examines all eligible episodes for the
    patient during the measurement period.

    This eCQM is an episode-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms146v9
    """

    title = 'Appropriate Testing for Pharyngitis'

    identifiers = ['CMS146v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'Linder, J. A., Bates, D. W., Lee, G. M., et al. (2005). Antibiotic treatment of children with sore throat. JAMA, 294(18), 2315-2322.',
        'Pfoh, E., Wessels, M.R., Goldmann, D., et al. (2008). Burden and economic cost of group A streptococcal pharyngitis. Pediatrics, 121(2), 229-234. doi: 10.1542/peds.2007-0484',
        'Shulman, S. T., Bisno, A. L., Clegg, H. W., et al. (2012). Clinical practice guideline for the diagnosis and management of group A streptococcal pharyngitis: 2012 update by the Infectious Diseases Society of America. Clinical Infectious Diseases, 55(10), E86-E102. doi:10.1093/cid/cis629',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Outpatient, telephone, online assessment, observation, or emergency
        department (ED) visits with a diagnosis of pharyngitis and an antibiotic dispensing event
        among patients 3 years or older
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Exclude episodes where the patient is taking antibiotics in the 30 days prior
        to the episode date.

        Exclude episodes where the patient had a competing comorbid condition during the 12 months
        prior to or on the episode date.

        Exclude episodes when the patient had hospice care overlapping with the measurement period.

        Exclude episodes where the patient had a competing diagnosis within three days after the
        episode date.

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: A group A streptococcus test in the seven-day period from three days prior to
        the episode date through three days after the episode date

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: Infectious Disease Society of America (2012)

        The Infectious Diseases Society of America "recommends swabbing the throat and testing for
        GAS pharyngitis by rapid antigen detection test (RADT) and/or culture because the clinical
        features alone do not reliably discriminate between GAS and viral pharyngitis except when
        overt viral features like rhinorrhea, cough, oral ulcers, and/or hoarseness are present"
        """
        pass
