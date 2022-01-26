from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AceInhibitorOrArbIngredient, AceInhibitorOrArbOrArni, AllergyToAceInhibitorOrArb,
    CareServicesInLongTermResidentialFacility, DischargeServicesHospitalInpatient,
    EjectionFraction, Ethnicity, HeartFailure, HomeHealthcareServices,
    IntoleranceToAceInhibitorOrArb, LeftVentricularSystolicDysfunction, ModerateOrSevereLvsd,
    NursingFacilityVisit, OfficeVisit, OncAdministrativeSex, OutpatientConsultation,
    PatientProviderInteraction, Payer, Pregnancy, Race, RenalFailureDueToAceInhibitor)


class ClinicalQualityMeasure135v9(ClinicalQualityMeasure):
    """
    Heart Failure (HF): Angiotensin-Converting Enzyme (ACE) Inhibitor or Angiotensin Receptor
    Blocker (ARB) or Angiotensin Receptor-Neprilysin Inhibitor (ARNI) Therapy for Left Ventricular
    Systolic Dysfunction (LVSD)

    Description: Percentage of patients aged 18 years and older with a diagnosis of heart failure
    (HF) with a current or prior left ventricular ejection fraction (LVEF) < 40% who were
    prescribed ACE inhibitor or ARB or ARNI therapy either within a 12-month period when seen in
    the outpatient setting OR at each hospital discharge

    Definition: Prescribed-Outpatient setting: prescription given to the patient for ACE inhibitor
    or ARB or ARNI therapy at one or more visits in the measurement period OR patient already
    taking ACE inhibitor or ARB or ARNI therapy as documented in current medication list.

    Prescribed-Inpatient setting: prescription given to the patient for ACE inhibitor or ARB or
    ARNI therapy at discharge OR ACE inhibitor or ARB or ARNI therapy to be continued after
    discharge as documented in the discharge medication list.

    LVEF < 40% corresponds to qualitative documentation of moderate dysfunction or severe
    dysfunction.

    Rationale: In the absence of contraindications, ACE inhibitors, ARB, or ARNI therapy is
    recommended for all patients with symptoms of heart failure and reduced left ventricular
    systolic function. Recent trial data have shown ARNI to be superior to ACE inhibitor or ARB
    therapy, however an ACE inhibitor or ARB should still be used for patients in which an ARNI is
    contraindicated. Given that ARNI is a newer therapy, uptake has been slow despite updated
    guideline recommendations that support its use. All pharmacologic agents included in this
    measure have been shown to decrease the risk of death and hospitalization for patients with
    heart failure.

    Guidance: This eCQM is to be reported as patient-based or episode-based, depending on the
    clinical setting. To satisfy this measure, it must be reported for all heart failure patients
    at least once during the measurement period if seen in the outpatient setting. If the patient
    has an eligible inpatient discharge during the measurement period, as defined in the measure
    logic, it is expected to be reported at each hospital discharge.

    The requirement of two or more visits used in Population Criteria 1 is to establish that the
    eligible professional or eligible clinician has an existing relationship with the patient.

    A range value should satisfy the logic requirement for 'Ejection Fraction' as long as the
    ranged observation value clearly meets the less than 40% threshold noted in the denominator
    logic. A range that is inclusive of or greater than 40% would not meet the measure requirement.

    Eligible clinicians who have given a prescription for or whose patient is already taking an
    Angiotensin-Converting Enzyme Inhibitor (ACEI) or Angiotensin Receptor Blocker (ARB) would meet
    performance for this measure. Other combination therapies that consist of an ACEI plus
    diuretic, ARB + neprilysin inhibitor (ARNI), ARB plus diuretic, ACEI plus calcium channel
    blocker, ARB plus calcium channel blocker, or ARB plus calcium channel blocker plus diuretic
    would also meet performance for this measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms135v9
    """

    title = 'Heart Failure (HF): Angiotensin-Converting Enzyme (ACE) Inhibitor or Angiotensin Receptor Blocker (ARB) or Angiotensin Receptor-Neprilysin Inhibitor (ARNI) Therapy for Left Ventricular Systolic Dysfunction (LVSD)'

    identifiers = ['CMS135v9']

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
        'Yancy, C. W., Jessup, M., Bozkurt, B., Butler, J., Casey, D. E., Colvin, M. M., … Westlake, C. (2017). 2017 ACC/AHA/HFSA Focused Update of the 2013 ACCF/AHA Guideline for the Management of Heart Failure: A Report of the American College of Cardiology/American Heart Association Task Force on Clinical Practice Guidelines and the Heart Failure Society of America. Circulation,136(6), e137–e161. doi: 10.1161/cir.0000000000000509',
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

        Exceptions: Documentation of medical reason(s) for not prescribing ACE inhibitor or ARB or
        ARNI therapy (e.g., hypotensive patients who are at immediate risk of cardiogenic shock,
        hospitalized patients who have experienced marked azotemia, allergy, intolerance, other
        medical reasons).

        Documentation of patient reason(s) for not prescribing ACE inhibitor or ARB or ARNI therapy
        (e.g., patient declined, other patient reasons).

        Documentation of system reason(s) for not prescribing ACE inhibitor or ARB or ARNI therapy
        (e.g., other system reasons).
        """
        pass

    def in_numerator(self):
        """
        Numerator: Patients who were prescribed ACE inhibitor or ARB or ARNI therapy either within
        a 12-month period when seen in the outpatient setting OR at each hospital discharge

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: The use of ACE inhibitors is beneficial for patients with prior or
        current symptoms of chronic HFrEF to reduce morbidity and mortality (Class I, Level of
        Evidence A) (ACC/AHA/HFSA, 2017).

        Treatment with an ACE inhibitor should be initiated at low doses [see excerpt from
        guideline table below], followed by gradual dose increments if lower doses have been well
        tolerated... Clinicians should attempt to use doses that have been shown to reduce the risk
        of cardiovascular events in clinical trials. If these target doses of an ACE inhibitor
        cannot be used or are poorly tolerated, intermediate doses should be used with the
        expectation that there are likely to be only small differences in efficacy between low and
        high doses. Abrupt withdrawal of treatment with an ACE inhibitor can lead to clinical
        deterioration and should be avoided (ACCF/AHA, 2013).

        Drugs Commonly Used for Stage C HFrEF (abbreviated to align with focus of measure to
        include only ACE inhibitors and ARB therapy)
        Drug                       Initial Daily Dose(s)                           Maximum Dose(s)
        Mean Doses Achieved in
        Clinical Trials
        ACE Inhibitors
           Captopril              6.25 mg 3 times                               50 mg 3 times
        122.7 mg/d
           Enalapril               2.5 mg twice                                    10 to 20 mg
        twice        16.6 mg/d
           Fosinopril             5 to 10 mg once                               40 mg once
        N/A
           Lisinopril              2.5 to 5 mg once                              20 to 40 mg once
        32.5 to 35.0 mg/d
           Perindopril           2 mg once                                        8 to 16 mg once
        N/A
           Quinapril              5 mg twice                                       20 mg twice
        N/A
           Ramipril               1.25 to 2.5 mg once                         10 mg once
        N/A
           Trandolapril          1 mg once                                        4 mg once
        N/A
        Angiotensin Receptor Blockers
           Candesartan         4 to 8 mg once                                32 mg once
        24 mg/d
           Losartan              25 to 50 mg once                             50 to 150 mg once
        129 mg/d
           Valsartan              20 to 40 mg twice                           160 mg twice
        254 mg/d

        The use of ARBs to reduce morbidity and mortality is recommended in patients with current
        or prior symptoms of chronic HFrEF who are intolerant to ACE inhibitors because of cough or
        angioedema (Class I, Level of Evidence A) (ACC/AHA/HFSA, 2017).

        ARBs are reasonable to reduce morbidity and mortality as alternatives to ACE inhibitors as
        first-line therapy for patients with HFrEF, especially for patients already taking ARBs for
        other indications, unless contraindicated (Class IIa, Level of Evidence: A) (ACCF/AHA,
        2013).

        Addition of an ARB may be considered in persistently symptomatic patients with HFrEF who
        are already being treated with an ACE inhibitor and a beta blocker in whom an aldosterone
        antagonist is not indicated or tolerated (Class IIb, Level of Evidence: A) (ACCF/AHA,
        2013).

        The clinical strategy of inhibition of the renin-angiotensin system with ACE inhibitors
        (Level of Evidence A), or ARBs (Level of Evidence A) or ARNI (Level of Evidence B-R) in
        conjunction with evidence-based beta-blockers, and aldosterone antagonists in selected
        patients, is recommended for patients with chronic HFrEF to reduce morbidity and mortality
        (Class I) (ACC/AHA/HFSA, 2017).

        In patients with chronic symptomatic HFrEF NYHA class II or III who tolerate an ACE
        inhibitor or ARB, replacement by an ARNI is recommended to further reduce morbidity and
        mortality (Class I, Level of Evidence: B-R) (ACC/AHA/HFSA, 2017).

        ARNI should not be administered concomitantly with ACE inhibitors or within 36 hours of the
        last dose of an ACE inhibitor (Class III, Level of Evidence B-R) (ACC/AHA/HFSA, 2017).

        ARNI should not be administered to patients with a history of angioedema (Class III
        Recommendation, Level of Evidence C-EO) (ACC/AHA/HFSA, 2017).

        For the hospitalized patient:
        In patients with HFrEF experiencing a symptomatic exacerbation of HF requiring
        hospitalization during chronic maintenance treatment with GDMT [guideline-directed medical
        therapy; GDMT represents optimal medical therapy as defined by ACCF/AHA guideline-
        recommended therapies (primarily Class I)], it is recommended that GDMT be continued in the
        absence of hemodynamic instability or contraindications (Class I, Level of Evidence: B)
        (ACCF/AHA, 2013).
        """
        pass
