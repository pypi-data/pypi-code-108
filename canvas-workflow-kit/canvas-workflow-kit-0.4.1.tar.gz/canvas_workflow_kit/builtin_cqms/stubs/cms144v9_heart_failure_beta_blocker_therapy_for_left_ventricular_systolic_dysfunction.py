from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AllergyToBetaBlockerTherapy, Arrhythmia, Asthma, AtrioventricularBlock,
    BetaBlockerTherapyForLvsd, BetaBlockerTherapyIngredient, Bradycardia, CardiacPacerInSitu,
    CareServicesInLongTermResidentialFacility, DischargeServicesHospitalInpatient,
    EjectionFraction, Ethnicity, HeartFailure, HeartRate, HomeHealthcareServices, Hypotension,
    IntoleranceToBetaBlockerTherapy, LeftVentricularSystolicDysfunction, ModerateOrSevereLvsd,
    NursingFacilityVisit, OfficeVisit, OncAdministrativeSex, OutpatientConsultation,
    PatientProviderInteraction, Payer, Race)


class ClinicalQualityMeasure144v9(ClinicalQualityMeasure):
    """
    Heart Failure (HF): Beta-Blocker Therapy for Left Ventricular Systolic Dysfunction (LVSD)

    Description: Percentage of patients aged 18 years and older with a diagnosis of heart failure
    (HF) with a current or prior left ventricular ejection fraction (LVEF) < 40% who were
    prescribed beta-blocker therapy either within a 12-month period when seen in the outpatient
    setting OR at each hospital discharge

    Definition: Prescribed-Outpatient setting: prescription given to the patient for beta-blocker
    therapy at one or more visits in the measurement period OR patient already taking beta-blocker
    therapy as documented in current medication list.

    Prescribed-Inpatient setting: prescription given to the patient for beta-blocker therapy at
    discharge OR beta-blocker therapy to be continued after discharge as documented in the
    discharge medication list.

    LVEF < 40% corresponds to qualitative documentation of moderate dysfunction or severe
    dysfunction.

    Rationale: Beta-blockers are recommended for all patients with stable heart failure and left
    ventricular systolic dysfunction, unless contraindicated. Treatment should be initiated as soon
    as a patient is diagnosed with left ventricular systolic dysfunction and does not have low
    blood pressure, fluid overload, or recent treatment with an intravenous positive inotropic
    agent. Beta-blockers have been shown to lessen the symptoms of heart failure, improve the
    clinical status of patients, reduce future clinical deterioration, and decrease the risk of
    mortality and the combined risk of mortality and hospitalization.

    Guidance: This eCQM is to be reported as patient-based or episode-based, depending on the
    clinical setting. To satisfy this measure, it must be reported for all heart failure patients
    at least once during the measurement period if seen in the outpatient setting. If the patient
    has an eligible inpatient discharge during the measurement period, as defined in the measure
    logic, it is expected to be reported at each hospital discharge.

    A range value should satisfy the logic requirement for 'Ejection Fraction' as long as the
    ranged observation value clearly meets the less than 40% threshold noted in the denominator
    logic. A range that is inclusive of or greater than 40% would not meet the measure requirement.

    Beta-blocker therapy:
    -For patients with prior LVEF < 40%, beta-blocker therapy should include bisoprolol,
    carvedilol, or sustained release metoprolol succinate.

    The requirement of two or more visits used in Population Criteria 1 is to establish that the
    eligible professional or eligible clinician has an existing relationship with the patient.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms144v9
    """

    title = 'Heart Failure (HF): Beta-Blocker Therapy for Left Ventricular Systolic Dysfunction (LVSD)'

    identifiers = ['CMS144v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'American Medical Association (AMA)',
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'Yancy, C. W., Jessup, M., Bozkurt, B., Butler, J., Casey, D. E., Drazner, M. H., … Wilkoff, B. L. (2013). 2013 ACCF/AHA Guideline for the Management of Heart Failure A Report of the American College of Cardiology Foundation/American Heart Association Task Force on Practice Guidelines. Circulation, 128(16), e240–e327. doi: https://doi.org/10.1161/CIR.0b013e31829e8776',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients aged 18 years and older with a diagnosis of heart failure
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population with a current or prior LVEF < 40%

        Exclusions: None

        Exceptions: Documentation of medical reason(s) for not prescribing beta-blocker therapy
        (e.g., low blood pressure, fluid overload, asthma, patients recently treated with an
        intravenous positive inotropic agent, allergy, intolerance, other medical reasons).

        Documentation of patient reason(s) for not prescribing beta-blocker therapy (e.g., patient
        declined, other patient reasons).

        Documentation of system reason(s) for not prescribing beta-blocker therapy (e.g., other
        reasons attributable to the healthcare system).
        """
        pass

    def in_numerator(self):
        """
        Numerator: Patients who were prescribed beta-blocker therapy either within a 12-month
        period when seen in the outpatient setting OR at each hospital discharge

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: Use of 1 of the 3 beta blockers proven to reduce mortality (e.g.,
        bisoprolol, carvedilol, and sustained-release metoprolol succinate) is recommended for all
        patients with current or prior symptoms of HFrEF [heart failure with reduced ejection
        fraction], unless contraindicated, to reduce morbidity and mortality (Class I, Level of
        Evidence: A) (ACCF/AHA, 2013).

        Treatment with a beta blocker should be initiated at very low doses [see excerpt from
        guideline table below] followed by gradual increments in dose if lower doses have been well
        tolerated... Clinicians should make every effort to achieve the target doses of the beta
        blockers shown to be effective in major clinical trials. Even if symptoms do not improve,
        long-term treatment should be maintained to reduce the risk of major clinical events.
        Abrupt withdrawal of treatment with a beta blocker can lead to clinical deterioration and
        should be avoided (ACCF/AHA, 2013).

        Drugs Commonly Used for Stage C HFrEF (abbreviated to align with focus of measure to
        include only Beta-blocker therapy)
        Drug                               Initial Daily Dose(s)       Maximum Dose(s)        Mean
        Doses Achieved in Clinical Trials

        Beta Blockers
        Bisoprolol                         1.25 mg once               10 mg once
        8.6 mg/d
        Carvedilol                         3.125 mg twice            50 mg twice
        37 mg/d
        Carvedilol  CR                  10 mg once                  80 mg once
        N/A
        Metoprolol succinate        12.5 to 25 mg once      200 mg once                159 mg/d
        extended release
        (metoprolol CR/XL)

        For the hospitalized patient:
        In patients with HFrEF experiencing a symptomatic exacerbation of HF requiring
        hospitalization during chronic maintenance treatment with GDMT [guideline-directed medical
        therapy; GDMT represents optimal medical therapy as defined by ACCF/AHA guideline-
        recommended therapies (primarily Class I)], it is recommended that GDMT be continued in the
        absence of hemodynamic instability or contraindications (Class I, Level of Evidence: B)
        (ACCF/AHA, 2013).

        Initiation of beta-blocker therapy is recommended after optimization of volume status and
        successful discontinuation of intravenous diuretics, vasodilators, and inotropic agents.
        Beta-blocker therapy should be initiated at a low dose and only in stable patients. Caution
        should be used when initiating beta blockers in patients who have required inotropes during
        their hospital course (Class I, Level of Evidence: B) (ACCF/AHA, 2013).
        """
        pass
