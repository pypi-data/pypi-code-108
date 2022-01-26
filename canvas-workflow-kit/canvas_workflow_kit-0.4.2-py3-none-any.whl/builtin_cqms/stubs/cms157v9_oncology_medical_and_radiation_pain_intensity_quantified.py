from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    Cancer, Ethnicity, OfficeVisit, OncAdministrativeSex, Payer, Race,
    StandardizedPainAssessmentTool)


class ClinicalQualityMeasure157v9(ClinicalQualityMeasure):
    """
    Oncology: Medical and Radiation - Pain Intensity Quantified

    Description: Percentage of patient visits, regardless of patient age, with a diagnosis of
    cancer currently receiving chemotherapy or radiation therapy in which pain intensity is
    quantified

    Definition: None

    Rationale: An estimated 1.7 million new cases of cancer are diagnosed in the US each year (NIH,
    2017). Pain is a commonly occurring symptom for cancer patients as 30% to 50% (510,000 to
    850,000 each year based on current statistics) will experience moderate to severe pain (Wiffen,
    Wee, Derry, Bell, & Moore, 2017). Initial and ongoing pain assessments are essential to
    determine the pathophysiology of pain and ensure proper pain management. According to the
    National Comprehensive Cancer Network (NCCN), there is increasing evidence in oncology that
    survival is linked to symptom reporting and control and that pain management contributes to
    broad quality-of-life improvement (2018). Cancer patients have reported that pain interferes
    with their mood, work, relationships with other people, sleep and overall enjoyment of life
    (Moryl et al., 2018). To maximize patient outcomes, pain management is an essential part of
    oncologic management (NCCN, 2018).

    A recent analysis of registry data for chronic pain cancer patients found average pain
    intensity reported as mild (24.6% of patients), moderate (41.5%), and severe (33.9%). The study
    also indicated that patient report of pain relief is inversely related to the average pain
    intensity reported (Moryl et al., 2018). These data suggest that assessing and managing a
    cancer patient’s pain is critical and there remains significant room for improvement in
    assessing and mitigating cancer-related pain. A prospective study of changes in pain severity
    of cancer patients found that, at initial assessment, 47% of patients reported pain. At follow-
    up, the patients with pain at initial assessment reported reduced pain (32.2%), stable pain
    (48.2%) and worse pain (19.6%). Of the 53% of patients reporting no pain at initial assessment,
    82.6% reported stable pain and 17.4% reported worse pain at follow-up assessment (Zhao et al.,
    2014). This study highlights the importance of initial and ongoing assessments of pain to
    identify gaps and ensure proper pain management.

    Guidance: This eCQM is an episode-of-care measure; the level of analysis for this measure is
    every visit for patients with a diagnosis of cancer who are also currently receiving
    chemotherapy or radiation therapy during the measurement period.

    For patients receiving radiation therapy, pain intensity should be quantified at each radiation
    treatment management encounter where the patient and physician have a face-to-face interaction.
    Due to the nature of some applicable coding related to radiation therapy (e.g., delivered in
    multiple fractions), the billing date for certain codes may or may not be the same as the face-
    to-face encounter date. In this instance, for the reporting purposes of this measure, the
    billing date should be used to pull the appropriate patients into the initial population. It is
    expected, though, that the numerator criteria would be performed at the time of the actual
    face-to-face encounter during the series of treatments. A lookback (retrospective) period of 7
    days, including the billing date, may be used to identify the actual face-to-face encounter,
    which is required to assess the numerator. Therefore, pain intensity should be quantified
    during the face-to-face encounter occurring on the actual billing date or within the 6 days
    prior to the billing date.

    For patients receiving chemotherapy, pain intensity should be quantified at each face-to-face
    encounter with the physician while the patient is currently receiving chemotherapy. For
    purposes of identifying eligible encounters, patients "currently receiving chemotherapy" refers
    to patients administered chemotherapy within 30 days prior to the encounter AND administered
    chemotherapy within 30 days after the date of the encounter.

    Pain intensity should be quantified using a standard instrument, such as a 0-10 numerical
    rating scale, visual analog scale, a categorical scale, or pictorial scale. Examples include
    the Faces Pain Rating Scale and the Brief Pain Inventory (BPI).

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms157v9
    """

    title = 'Oncology: Medical and Radiation - Pain Intensity Quantified'

    identifiers = ['CMS157v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'Moryl, N., Dave, V., Glare, P., Bokhari, A., Malhotra, V. T., Gulati, A., … Inturrisi, C. E. (2018). Patient-Reported Outcomes and Opioid Use by Outpatient Cancer Patients. The Journal of Pain: official journal of the American Pain Society, 19(3), 278–290. doi:10.1016/j.jpain.2017.11.001',
        'National Comprehensive Cancer Network (NCCN). (2018). NCCN Clinical Practice Guidelines in Oncology. Adult Cancer Pain Version I.2018. Retrieved from http://www.nccn.org',
        'National Comprehensive Cancer Network (NCCN). (2019). NCCN Clinical Practice Guidelines in Oncology. Adult Cancer Pain Version 3.2019. Retrieved from http://www.nccn.org',
        'National Institutes of Health - National Cancer Institute. (2017). Cancer Statistics. Retrieved from https://www.cancer.gov/about-cancer/understanding/statistics',
        'Wiffen, P. J., Wee, B., Derry, S., Bell, R. F., & Moore, R. A. (2017). Opioids for cancer pain - an overview of Cochrane reviews. The Cochrane database of systematic reviews, 7(7), CD012592. doi:10.1002/14651858.CD012592.pub2',
        'Zhao, F., Chang, V. T., Cleeland, C., Cleary, J. F., Mitchell, E. P., Wagner, L. I., & Fisch, M. J. (2014). Determinants of pain severity changes in ambulatory patients with cancer: an analysis from Eastern Cooperative Oncology Group trial E2Z02. Journal of clinical oncology : official journal of the American Society of Clinical Oncology, 32(4), 312–319. doi:10.1200/JCO.2013.50.6071',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patient visits, regardless of patient age, with a diagnosis of
        cancer currently receiving chemotherapy or radiation therapy
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: None

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Patient visits in which pain intensity is quantified

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: -Screen all patients for pain at each contact.

        -Routinely quantify and document pain intensity and quality as characterized by the patient
        (whenever possible). Include patient reporting of breakthrough pain, treatments used and
        their impact on pain, adequacy of comfort, satisfaction with pain relief, provider
        assessment of impact on function, and any special issues for the patient relevant to pain
        treatment. If necessary, get additional information from caregiver regarding pain and
        impact on function.

        -Perform comprehensive pain assessment if new or worsening pain is present, and regularly
        for persisting pain.

        Various methods and tools exist to assess pain severity. Intensity of pain should be
        quantified using a numerical rating scale (i.e., 0-10), visual analog scale, categorical
        scale, or pictorial scale (e.g., The Faces Pain Rating Scale) (Category 2A) (National
        Comprehensive Cancer Network, 2019).
        """
        pass
