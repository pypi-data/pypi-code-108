from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    ClinicalOralEvaluation, DentalCaries, EncounterInpatient, Ethnicity, HospiceCareAmbulatory,
    OncAdministrativeSex, Payer, Race)


class ClinicalQualityMeasure75v9(ClinicalQualityMeasure):
    """
    Children Who Have Dental Decay or Cavities

    Description: Percentage of children, 6 months - 20 years of age, who have had tooth decay or
    cavities during the measurement period

    Definition: None

    Rationale: Dental caries is the most chronic disease among youth aged 6-19 years. Data from the
    National Health and Nutrition Examination Survey from 2015-2016 showed that approximately 45.8%
    of children and youth aged 2-19 years had total caries (untreated and treated). Prevalence of
    total dental caries (untreated and treated) in primary or permanent teeth increases with age,
    going from 21.4%, 50.5%, and 53.8% among ages 2-5, 6-11, and 12-19, respectively. Total dental
    caries was highest in Hispanic youths aged 2-19 at 57.1% compared to 48.1% for non-Hispanic
    black, 44.6% for non-Asian, and 40.4% for non-Hispanic white youth. Monitoring prevalence of
    untreated and total caries is vital to preventing and controlling oral disease (Fleming &
    Afful, 2018).

    Children who have dental decay or cavities are less likely to be in very good or excellent
    overall health than children without decay or cavities (Edelstein & Chinn, 2009). Children with
    decay are also more likely to have other oral health problems such as toothaches, broken teeth,
    and bleeding gums (Data Resource Center for Child and Adolescent Health, 2007).

    Guidance: This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms75v9
    """

    title = 'Children Who Have Dental Decay or Cavities'

    identifiers = ['CMS75v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'Data Resource Center for Child and Adolescent Health, Child and Adolescent Health Measurement Initiative. (2007). 2007 National Survey of Children’s Health. Baltimore, MD: Author.',
        'Edelstein, B. L., & Chinn, C. H. (2009). Update on disparities in oral health and access to dental care for America’s children. Academic Pediatrics, 9(6), 415-419.',
        'Fleming, E., & Afful, J. (2018). Prevalence of total and untreated dental carries among youth: United States, 2015-2016. NCHS Data Brief No. 307. Hyattsville, MD: National Center for Health Statistics.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Children, 6 months - 20 years of age, with a clinical oral evaluation
        during the measurement period
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
        Numerator: Children who had a diagnosis of cavities or decayed teeth overlapping the
        measurement period

        Exclusions: Not applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: This is an outcome measure. As such, no clinical recommendations
        are included.
        """
        pass
