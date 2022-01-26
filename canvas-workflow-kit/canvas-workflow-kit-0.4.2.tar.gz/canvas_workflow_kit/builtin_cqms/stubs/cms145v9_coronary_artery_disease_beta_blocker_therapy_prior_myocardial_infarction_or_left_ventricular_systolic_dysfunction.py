from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AllergyToBetaBlockerTherapy, Arrhythmia, Asthma, AtrioventricularBlock, BetaBlockerTherapy,
    BetaBlockerTherapyForLvsd, BetaBlockerTherapyIngredient, Bradycardia, CardiacPacerInSitu,
    CareServicesInLongTermResidentialFacility, CoronaryArteryDiseaseNoMi, EjectionFraction,
    Ethnicity, HeartRate, HomeHealthcareServices, Hypotension, IntoleranceToBetaBlockerTherapy,
    LeftVentricularSystolicDysfunction, ModerateOrSevereLvsd, MyocardialInfarction,
    NursingFacilityVisit, OfficeVisit, OncAdministrativeSex, OutpatientConsultation,
    PatientProviderInteraction, Payer, Race)


class ClinicalQualityMeasure145v9(ClinicalQualityMeasure):
    """
    Coronary Artery Disease (CAD): Beta-Blocker Therapy-Prior Myocardial Infarction (MI) or Left
    Ventricular Systolic Dysfunction (LVEF <40%)

    Description: Percentage of patients aged 18 years and older with a diagnosis of coronary artery
    disease seen within a 12-month period who also have a prior MI or a current or prior LVEF <40%
    who were prescribed beta-blocker therapy

    Definition: Prescribed may include prescription given to the patient for beta-blocker therapy
    at one or more visits in the measurement period OR patient already taking beta-blocker therapy
    as documented in current medication list.

    Prior Myocardial Infarction (MI) for denominator 2 is limited to those occurring within the
    past 3 years.

    Rationale: For patients with coronary artery disease (CAD), beta-blockers are recommended for 3
    years after myocardial infarction or acute coronary syndrome. Beta-blockers, particularly
    carvedilol, metoprolol succinate, or bisoprolol which have been shown to reduce risk of death,
    are recommended indefinitely for patients with CAD and LV systolic dysfunction. These agents
    have proven efficacy in reducing angina onset and improving the ischemic threshold during
    exercise. In patients who have suffered an MI, beta-blockers significantly reduce deaths and
    recurrent MIs (ACCF/AHA/ACP/AATS/PCNA/SCAI/STS, 2012).

    Nonadherence to cardioprotective medications is prevalent among outpatients with CAD and can be
    associated with a broad range of adverse outcomes, including all-cause and cardiovascular
    mortality, cardiovascular hospitalizations, and the need for revascularization procedures
    (ACC/AHA, 2002).

    This measure is intended to promote beta-blocker usage in select patients with CAD.

    Guidance: Beta-blocker therapy:
    - For patients with prior MI, beta-blocker therapy includes any agent within the beta-blocker
    drug class. As of 2015, no recommendations or evidence are cited in current stable ischemic
    heart disease guidelines for preferential use of specific agents
    - For patients with prior LVEF <40%, beta-blocker therapy includes the following: bisoprolol,
    carvedilol, or sustained release metoprolol succinate

    The requirement of two or more visits is to establish that the eligible professional or
    eligible clinician has an existing relationship with the patient.

    A range value should satisfy the logic requirement for 'Ejection Fraction' as long as the
    ranged observation value clearly meets the less than 40% threshold noted in the denominator
    logic. A range that is inclusive of or greater than 40% would not meet the measure requirement.

    If a patient has had a myocardial infarction (MI) within the past 3 years and a current or
    prior LVEF < 40% (or moderate or severe LVSD), the patient should only be counted in Population
    Criteria 1.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms145v9
    """

    title = 'Coronary Artery Disease (CAD): Beta-Blocker Therapy-Prior Myocardial Infarction (MI) or Left Ventricular Systolic Dysfunction (LVEF <40%)'

    identifiers = ['CMS145v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'Fihn, S. D., Gardin, J. M., Abrams, J., Berra, K., Blankenship, J. C., Dallas, A. P., … Williams, S. V. (2012). 2012 ACCF/AHA/ACP/AATS/PCNA/SCAI/STS Guideline for the Diagnosis and Management of Patients With Stable Ischemic Heart Disease. Circulation, 126(25), e354–e471. doi: 10.1161/cir.0b013e318277d6a0',
        'Gibbons, R. J., Abrams, J., Chatterjee, K., Daley, J., Deedwania, P.K, Douglas J.S., … Smith Jr., S.C. (2002). ACC/AHA 2002 Guideline Update for the Management of Patients with Chronic StableAangina: A Report of the American College of Cardiology/American Heart Association Task Force on Practice Guidelines (Committee to Update the 1999 Guidelines for the Management of Patients with Chronic Stable Angina). Circulation, 107(1), 149-158. doi:10.1161/01.CIR.0000047041.66447.29',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients aged 18 years and older with a diagnosis of coronary
        artery disease seen within a 12-month period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population who also have prior (within the past 3 years) MI or
        a current or prior LVEF <40%

        Exclusions: None

        Exceptions: Documentation of medical reason(s) for not prescribing beta-blocker therapy
        (e.g., allergy, intolerance, other medical reasons).

        Documentation of patient reason(s) for not prescribing beta-blocker therapy (e.g., patient
        declined, other patient reasons).

        Documentation of system reason(s) for not prescribing beta-blocker therapy (e.g., other
        reasons attributable to the health care system).
        """
        pass

    def in_numerator(self):
        """
        Numerator: Patients who were prescribed beta-blocker therapy

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: Beta-blocker therapy should be started and continued for 3 years
        in all patients with normal LV function after MI or ACS (Class I, Level of Evidence: B)
        (ACCF/AHA/ACP/AATS/PCNA/SCAI/STS, 2012).

        Beta-blocker therapy should be used in all patients with LV systolic dysfunction (EF <=
        40%) with heart failure or prior MI, unless contraindicated. (Use should be limited to
        carvedilol, metoprolol succinate, or bisoprolol, which have been shown to reduce risk of
        death.) (Class I, Level of Evidence: A) (ACCF/AHA/ACP/AATS/PCNA/SCAI/STS, 2012).
        """
        pass
