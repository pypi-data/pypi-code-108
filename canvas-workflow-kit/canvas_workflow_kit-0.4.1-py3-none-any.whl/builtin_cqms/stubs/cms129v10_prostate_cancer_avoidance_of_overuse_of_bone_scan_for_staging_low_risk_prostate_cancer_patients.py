from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    BoneScan, Ethnicity, Male, OncAdministrativeSex, PainRelatedToProstateCancer, Payer,
    ProstateCancer, ProstateSpecificAntigenTest, Race)


class ClinicalQualityMeasure129v10(ClinicalQualityMeasure):
    """
    Prostate Cancer: Avoidance of Overuse of Bone Scan for Staging Low Risk Prostate Cancer
    Patients

    Description: Percentage of patients, regardless of age, with a diagnosis of prostate cancer at
    low (or very low) risk of recurrence receiving interstitial prostate brachytherapy, OR external
    beam radiotherapy to the prostate, OR radical prostatectomy who did not have a bone scan
    performed at any time since diagnosis of prostate cancer

    Definition: Risk Strata Definitions: Very Low, Low, Intermediate, High, or Very High-
    Very Low/Low Risk - PSA < 10 ng/mL; AND Gleason score 6 or less/Gleason grade group 1; AND
    clinical stage T1 to T2a.
    Intermediate Risk - PSA 10 to 20 ng/mL; OR Gleason score 7/Gleason grade group 2-3; OR clinical
    stage T2b to T2c.
    High/Very High Risk - PSA > 20 ng/mL; OR Gleason score 8 to 10/Gleason grade group 4-5; OR
    clinically localized stage T3 to T4 (adapted from the National Comprehensive Cancer Network,
    2018).

    External beam radiotherapy - external beam radiotherapy refers to 3D conformal radiation
    therapy (3D-CRT), intensity modulated radiation therapy (IMRT), stereotactic body radiotherapy
    (SBRT), and proton beam therapy.

    Bone scan - bone scan refers to the conventional technetium-99m-MDP bone scan as well as
    18F-NaF PET (or PET/CT) scan.

    Rationale: Multiple studies have indicated that a bone scan is not clinically necessary for
    staging prostate cancer in men with a low (or very low) risk of recurrence and receiving
    primary therapy. For patients who are categorized as low-risk, bone scans are unlikely to
    identify their disease. Furthermore, bone scans are not necessary for low-risk patients who
    have no history or if the clinical examination suggests no bony involvement. Less than 1% of
    low-risk patients are at risk of metastatic disease.

    While clinical practice guidelines do not recommend bone scans in low-risk prostate cancer
    patients, overuse is still common. An analysis of prostate cancer patients in the SEER-Medicare
    database diagnosed from 2004-2007 found that 43% of patients for whom a bone scan was not
    recommended received it (Falchook, Hendrix, & Chen, 2015). The analysis also found that the use
    of bone scans in low-risk patients leads to an annual cost of $4 million dollars to Medicare.
    The overuse of bone scan imaging for low-risk prostate cancer patients is a concept included on
    the American Urological Association's (AUA) list in the Choosing Wisely Initiative as a means
    to promote adherence to evidence-based imaging practices and to reduce health care dollars
    wasted (AUA, 2017). This measure is intended to promote adherence to evidence-based imaging
    practices, lessen the financial burden of unnecessary imaging, and ultimately to improve the
    quality of care for prostate cancer patients in the United States.

    Guidance: A higher score indicates appropriate treatment of patients with prostate cancer at
    low (or very low) risk of recurrence. Only patients with prostate cancer with low (or very low)
    risk of recurrence will be counted in the performance denominator of this measure.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms129v10
    """

    title = 'Prostate Cancer: Avoidance of Overuse of Bone Scan for Staging Low Risk Prostate Cancer Patients'

    identifiers = ['CMS129v10']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'American Urological Association. (2017). A routine bone scan is unnecessary in men with low-risk prostate cancer. Retrieved from http://www.choosingwisely.org/clinician-lists/american-urological-association-routine-bone-scans-with-low-risk-prostate-cancer/ (Original work published in 2013).',
        'American Urological Association, American Society for Radiation Oncology, & Society of Urologic Oncology. (2017). Clinically localized prostate cancer: AUA/ASTRO/SUO Guideline. Retrieved from https://www.auanet.org/guidelines/prostate-cancer-clinically-localized-(2017)',
        'Falchook, A. D., Hendrix, L. H., & Chen, R. C. (2015). Guideline-discordant use of imaging during work-up of newly diagnosed prostate cancer. Journal of Oncology Practice, 11(2), e239-e246. doi:10.1200/jop.2014.001818',
        'National Comprehensive Cancer Network. (2019). Clinical Practice Guidelines in Oncology: Prostate Cancer. Version 4.209. Retrieved from https://www.nccn.org/professionals/physician_gls/pdf/prostate.pdf',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients, regardless of age, with a diagnosis of prostate cancer
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population at low (or very low) risk of recurrence receiving
        interstitial prostate brachytherapy, OR external beam radiotherapy to the prostate, OR
        radical prostatectomy

        Exclusions: None

        Exceptions: Documentation of reason(s) for performing a bone scan (including documented
        pain, salvage therapy, other medical reasons, bone scan ordered by someone other than
        reporting physician)
        """
        pass

    def in_numerator(self):
        """
        Numerator: Patients who did not have a bone scan performed at any time since diagnosis of
        prostate cancer

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: For symptomatic patients and/or those with a life expectancy of
        greater than 5 years, bone imaging is appropriate for patients with unfavorable
        intermediate-risk prostate cancer and T2 disease with PSA over 10 ng/mL, high- or very-high
        risk disease; or symptomatic disease (National Comprehensive Cancer Network, 2019)
        (Evidence Level: Category 2A).

        Clinicians should not perform routine bone scans in the staging of asymptomatic very low-
        or low-risk localized prostate cancer patients (AUA, American Society for Radiation
        Oncology, & Society of Urologic Oncology, 2017) (Strong Recommendation; Evidence Level:
        Grade C).

        A routine bone scan is unnecessary in men with low-risk prostate cancer. Low-risk patients
        are unlikely to have disease identified by bone scan. Accordingly, bone scans are generally
        unnecessary in patients with newly diagnosed prostate cancer who have a PSA <10.0 ng/mL and
        a Gleason score less than 7 unless the patient’s history or clinical examination suggests
        bony involvement. Progression to the bone is much more common in advanced local disease or
        in high-grade disease that is characterized by fast and aggressive growth into surrounding
        areas such as bones or lymph nodes (AUA, 2017).
        """
        pass
