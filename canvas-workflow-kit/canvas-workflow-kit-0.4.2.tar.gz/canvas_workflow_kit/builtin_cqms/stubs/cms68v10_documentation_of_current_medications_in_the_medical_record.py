from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    EncounterToDocumentMedications, Ethnicity, OncAdministrativeSex, Payer, Race)


class ClinicalQualityMeasure68v10(ClinicalQualityMeasure):
    """
    Documentation of Current Medications in the Medical Record

    Description: Percentage of visits for patients aged 18 years and older for which the eligible
    professional or eligible clinician attests to documenting a list of current medications using
    all immediate resources available on the date of the encounter

    Definition: Current Medications:
    Medications the patient is presently taking including all prescriptions, over-the-counters,
    herbals and vitamin/mineral/dietary (nutritional) supplements with each medication's name,
    dosage, frequency and administered route.

    Route:
    Documentation of the way the medication enters the body (some examples include but are not
    limited to: oral, sublingual, subcutaneous injections, and/or topical).

    Rationale: According to the National Center for Health Statistics, during the years of
    2011-2014, 46.9 percent of patients (both male and female) were prescribed at least one
    prescription medication with 10.9 percent taking 5 or more medications. Additionally, 90.6
    percent of patients (both male and female) aged 65 years and older were prescribed at least one
    medication with 40.7 percent taking 5 or more medications (2017).  In this context, maintaining
    an accurate and complete medication list has proven to be a challenging documentation endeavor
    for various health care provider settings. While most of outpatient encounters (2/3) result in
    providers prescribing at least one medication, hospitals have been the focus of medication
    safety efforts (Stock, Scott, & Gurtel, 2009). Nassaralla, Naessens, Chaudhry, Hansen, and
    Scheitel (2007) caution that this is at odds with the current trend, where patients with
    chronic illnesses are increasingly being treated in the outpatient setting and require careful
    monitoring of multiple medications. Additionally, Nassaralla et al. (2007) reveal that it is in
    fact in outpatient settings where more fatal adverse drug events (ADE) occur when these are
    compared to those occurring in hospitals (1 of 131 outpatient deaths compared to 1 in 854
    inpatient deaths). In the outpatient setting, ADEs occur 25% of the time and over one-third of
    these are considered preventable (Tache, Sonnichsen, & Ashcroft, 2011). Particularly vulnerable
    are patients over 65 years, with evidence suggesting that the rate of ADEs per 10,000 person
    per year increases with age; 25-44 years old at 1.3; 45-64 at 2.2, and 65 + at 3.8 (Sarkar,
    López, & Maselli, 2011). Another vulnerable group is chronically ill individuals. These
    population groups are more likely to experience ADEs and subsequent hospitalization.

    A multiplicity of providers and inadequate care coordination among them has been identified as
    barriers to collecting complete and reliable medication records. Data indicate that
    reconciliation and documentation continue to be poorly executed with discrepancies occurring in
    92% (74 of 80 patients) of medication lists among admittance to the emergency room. Of 80
    patients included in the study, the home medications were reordered for 65% of patients on
    their admission and of the 65% the majority (29%) had a change in their dosing interval, while
    23% had a change in their route of administration, and 13% had a change in dose. A total of 361
    medication discrepancies, or the difference between the medications patients were taking before
    admission and those listed in their admission orders, were identified in at least 74 patients
    (Poornima et al., 2015). The study found that "Through an appropriate reconciliation programme,
    around 80% of errors relating to medication and the potential harm caused by these errors could
    be reduced" (Penumarthi et al., 2015, p. 243).

    Documentation of current medications in the medical record facilitates the process of
    medication review and reconciliation by the provider, which is necessary for reducing ADEs and
    promoting medication safety. The need for provider to provider coordination regarding
    medication records, and the existing gap in implementation, is highlighted in the American
    Medical Association's Physician's Role in Medication Reconciliation, which states that
    "critical patient information, including medical and medication histories, current medications
    the patient is receiving and taking, and sources of medications, is essential to the delivery
    of safe medical care. However, interruptions in the continuity of care and information gaps in
    patient health records are common and significantly affect patient outcomes" (2007, p. 7). This
    is because clinical decisions based on information that is incomplete and/or inaccurate are
    likely to lead to medication error and ADEs. Weeks, Corbette, and Stream (2010) noted similar
    barriers and identified the utilization of health information technology as an opportunity for
    facilitating the creation of universal medication lists. One 2015 meta-analysis showed an
    association between EHR documentation with an overall RR of 0.46 (95% CI = 0.38 to 0.55; P <
    0.001) and ADEs with an overall RR of 0.66 (95% CI = 0.44 to 0.99; P = 0.045). This meta-
    analysis provides evidence that the use of the EHR can improve the quality of healthcare
    delivered to patients by reducing medication errors and ADEs (Campanella et al., 2016).

    Guidance: This eCQM is an episode-based measure. This measure is to be reported for every
    encounter during the measurement period.

    Eligible professionals or eligible clinicians reporting this measure may document medication
    information received from the patient, authorized representative(s), caregiver(s) or other
    available healthcare resources.

    This list must include all known prescriptions, over-the-counter (OTC) products, herbals,
    vitamins, minerals, dietary (nutritional) supplements AND must contain the medications' name,
    dosage, frequency and route of administration.

    This measure should also be reported if the eligible professional or eligible clinician
    documented the patient is not currently taking any medications.

    By reporting the action described in this measure, the provider attests to having documented a
    list of current medications utilizing all immediate resources available at the time of the
    encounter.

    This version of the eCQM uses QDM version 5.5.  Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms68v10
    """

    title = 'Documentation of Current Medications in the Medical Record'

    identifiers = ['CMS68v10']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'American Medical Association. (2007). The physician’s role in medication reconciliation: Issues, strategies, and safety principles. Retrieved from https://pogoe.org/sites/default/files/Medication%20Reconciliation.pdf',
        'Campanella, P., Lovato, E., Marone, C., Fallacara, L., Mancuso, A., Ricciardi, W., & Specchia, M. L. (2016). The impact of electronic health records on health care quality: A systematic review and meta-analysis. European Journal of Public Health, 26(1), 60-64. doi:10.1093/eurpub/ckv122',
        'Nassaralla, C. L., Naessens, J. M., Chaudhry, R., Hansen, M. A., & Scheitel, S. M. (2007). Implementation of a medication reconciliation process in an ambulatory internal medicine clinic. Quality and Safety in Health Care, 16(2), 90-94. doi:10.1136/qshc.2006.021113',
        'National Center for Health Statistics. (2017). Health, United States, 2017: Supplementary Table 79: Prescription drug use in the United States by sex, race, age, and origin. Retrieved from https://www.cdc.gov/nchs/data/hus/2017/079.pdf',
        'National Quality Forum. (2010). Safe practices for better healthcare - 2010 update. Retrieved from http://www.qualityforum.org/Projects/Safe_Practices_2010.aspx',
        'Penumarthi, P., Pasala, R., T V, R., Nagasubramanian, VR., Devi, G S., Seshadri, P. (2015). Medication reconciliation and medication error prevention in an emergency department of a tertiary care hospital. Journal of Young Pharmacists, 7(3), 241-249. doi:10.5530/jyp.2015.3.15',
        'Sarkar, U., López, A., Maselli, J.H., Gonzales, R. (2011). Adverse drug events in U.S. adult ambulatory medical care. Health Services Research, 46(5), 1517-1533. doi:10.1111/j.1475-6773.2011.01269.x',
        'Stock, R., Scott, J., & Gurtel, S. (2009). Using an electronic prescribing system to ensure accurate medication lists in a large multidisciplinary medical group. The Joint Commission Journal on Quality and Patient Safety, 35(5), 271-277.',
        'Tache, S. V., Sonnichsen, A., & Ashcroft, D. M. (2011). Prevalence of adverse drug events in ambulatory care: A systematic review. The Annals of Pharmacotherapy, 45(7-8), 977-989. doi: 10.1345/aph.1P627',
        'The Joint Commission. (2019). Ambulatory Health Care National Patient Safety Goals. Retrieved from https://www.jointcommission.org/assets/1/6/2019_AHC_NPSGs_final.pdf',
        'Weeks, D. L., Corbette, C. F., & Stream, G. (2010). Beliefs of ambulatory care physicians about accuracy of patient medication records and technology-enhanced solutions to improve accuracy. Journal for Healthcare Quality, 32(5), 12-21. doi:10.1111/j.1945-1474.2010.00097.x',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All visits occurring during the 12 month measurement period for
        patients aged 18 years and older
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: None

        Exceptions: Documentation of a medical reason(s) for not documenting, updating, or
        reviewing the patient’s current medications list (e.g., patient is in an urgent or emergent
        medical situation where time is of the essence and to delay treatment would jeopardize the
        patient's health status)
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Eligible professional or eligible clinician attests to documenting, updating or
        reviewing the patient's current medications using all immediate resources available on the
        date of the encounter

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: The Joint Commission's 2019 Ambulatory Health Care National
        Patient Safety Goals guide providers to maintain and communicate accurate patient
        medication information. Specifically, the section "Use Medicines Safely NPSG.03.06.01"
        states the following: "Record and pass along correct information about a patient’s
        medicines. Find out what medicines the patient is taking. Compare those medicines to new
        medicines given to the patient. Make sure the patient knows which medicines to take when
        they are at home. Tell the patient it is important to bring their up-to-date list of
        medicines every time they visit a doctor."

        The National Quality Forum's Safe Practices for Better Healthcare - 2010 Update, states the
        following: "the healthcare organization must develop, reconcile, and communicate an
        accurate patient medication list throughout the continuum of care" (p. 40).
        """
        pass
