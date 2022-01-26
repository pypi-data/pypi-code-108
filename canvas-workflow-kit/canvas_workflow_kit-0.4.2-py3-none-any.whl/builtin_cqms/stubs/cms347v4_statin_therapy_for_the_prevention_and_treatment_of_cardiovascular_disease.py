from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AnnualWellnessVisit, AtherosclerosisAndPeripheralArterialDisease, Breastfeeding,
    CerebrovascularDiseaseStrokeTia, Diabetes, EndStageRenalDisease, Ethnicity, HepatitisA,
    HepatitisB_269, HighIntensityStatinTherapy, HospiceCareAmbulatory_1584, Hypercholesterolemia,
    IschemicHeartDiseaseOrOtherRelatedDiagnoses, LdlCholesterol, LiverDisease,
    LowIntensityStatinTherapy, ModerateIntensityStatinTherapy, MyocardialInfarction, OfficeVisit,
    OncAdministrativeSex, OutpatientConsultation, OutpatientEncountersForPreventiveCare,
    PalliativeOrHospiceCare, Payer, PregnancyOrOtherRelatedDiagnoses,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesIndividualCounseling, PreventiveCareServicesInitialOfficeVisit18AndUp,
    PreventiveCareServicesOther, Race, Rhabdomyolysis, StableAndUnstableAngina, StatinAllergen)


class ClinicalQualityMeasure347v4(ClinicalQualityMeasure):
    """
    Statin Therapy for the Prevention and Treatment of Cardiovascular Disease

    Description: Percentage of the following patients - all considered at high risk of
    cardiovascular events - who were prescribed or were on statin therapy during the measurement
    period:
    *Adults aged >= 21 years who were previously diagnosed with or currently have an active
    diagnosis of clinical atherosclerotic cardiovascular disease (ASCVD); OR
    *Adults aged >= 21 years who have ever had a fasting or direct low-density lipoprotein
    cholesterol (LDL-C) level >= 190 mg/dL or were previously diagnosed with or currently have an
    active diagnosis of familial or pure hypercholesterolemia; OR
    *Adults aged 40-75 years with a diagnosis of diabetes with a fasting or direct LDL-C level of
    70-189 mg/dL

    Definition: Clinical atherosclerotic cardiovascular disease (ASCVD) includes:
    *  Acute coronary syndromes
    *  History of myocardial infarction
    *  Stable or unstable angina
    *  Coronary or other arterial revascularization
    *  Stroke or transient ischemic attack (TIA)
    *  Peripheral arterial disease of atherosclerotic origin

    Lipoprotein density cholesterol (LDL-C) result:
    *  A fasting or direct LDL-C laboratory test performed and test result documented in the
    medical record.

    Statin therapy:
    *  Administration of one or more of a group of medications that are used to lower plasma
    lipoprotein levels in the treatment of hyperlipoproteinemia.

    Statin Medication Therapy List (NOTE: List does NOT include dosage):

    [Generic name] (Brand or trade name) and (-) Medication type, if applicable:
    [Atorvastatin] (Lipitor) - Statin
    [Fluvastatin] (Lescol XL or Lescol) - Statin
    [Lovastatin (Mevinolin)](Mevacor or Altoprev) -Statin
    [Pitavastatin]Livalo
    [Pravastatin Sodium] (Pravachol) - Statin
    [Rosuvastatin Calcium] (Crestor) - Statin
    [Simvastatin] (Zocor) - Statin
    [Amlodipine Besylate/Atorvastatin Calcium] (Caduet) - Combination
    [Ezetimibe/Simvastatin] (Vytorin) - Combination

    Some patients may not be appropriate to prescribe or use statin therapy (see
    exceptions and exclusions for a complete list).

    "Statin intolerance is the inability to tolerate a dose of statin required to reduce a person's
    CV risk sufficiently from their baseline risk and could result from different statin related
    side effects including: muscle symptoms, headache, sleep disorders, dyspepsia, nausea, rash,
    alopecia, erectile dysfunction, gynecomastia, and/or arthritis" (Banach et al., 2015, p.2 ).

    Patients that experience symptoms such as these may prefer not to take or continue statin
    therapy and therefore may be exempt from the denominator.

    Rationale: "Cardiovascular disease (CVD) is the leading cause of death in the United States,
    causing approximately 1 of every 3 deaths in the United States in 2015. In 2015, stroke caused
    approximately 1 of every 19 deaths in the United States and the estimated annual costs for CVD
    and stroke were $329.7 billion, including $199.2 billion in direct costs (hospital services,
    physicians and other professionals, prescribed medications, home health care, and other medical
    durables) and $130.5 billion in indirect costs from lost future productivity (cardiovascular
    and stroke premature deaths). CVD costs more than any other diagnostic group" (Benjamin et al.,
    2018).

    Data collected between 2011 and 2014 indicates that more than 94.6 million U.S. adults, 20
    years or older, had total cholesterol levels equal to 200 mg/dL or more, while almost 28.5
    million had levels 240 mg/dL or more (Benjamin et al., 2018). Elevated blood cholesterol is a
    major risk factor for CVD and statin therapy has been associated with a reduced risk of CVD.
    Numerous randomized trials have demonstrated that treatment with a statin reduces LDL-C, and
    reduces the risk of major cardiovascular events by approximately 20 percent (Ference, 2015).

    In 2013, guidelines on the treatment of blood cholesterol to reduce atherosclerotic
    cardiovascular risk in adults were published (see Stone et al., 2014). This guideline was
    published by an Expert Panel, which synthesized evidence from randomized controlled trials to
    identify people most likely to benefit from cholesterol-lowering therapy. The American College
    of Cardiology (ACC)/American Heart Association (AHA) Guideline recommendations are intended to
    provide a strong evidence-based foundation for the treatment of blood cholesterol for the
    primary and secondary prevention and treatment of Atherosclerotic Cardiovascular Disease
    (ASCVD) in adult men and women (21 years of age or older). The document concludes the addition
    of statin therapy reduces the risk of ASCVD among high-risk individuals, defined as follows:
    individuals with clinical ASCVD, with LDL-C >= 190 mg/dL, or with diabetes and LDL-C 70-189
    mg/dL (Stone et al., 2014).

    One study that surveyed U.S. cardiology, primary care, and endocrinology practices found that 1
    in 4 guideline-eligible patients were not on a statin and less than half were on the
    recommended statin intensity. Untreated and undertreated patients had significantly higher
    LDL-C levels than those receiving guideline-directed statin treatment (Navar et al., 2017). The
    Statin Safety Expert Panel that participated in an NLA Statin Safety Task Force meeting in
    October 2013 reaffirms the general safety of statin therapy.

    However, 1 in 10 people who try taking a statin will report some kind of intolerance, most
    commonly muscle aches. Other known low risk circumstances of statin intolerance include side
    effects such as myopathy, cognitive dysfunction, increased hepatic transaminase levels, and new
    onset diabetes. Statin intolerance usually does not involve substantial risk for mortality or
    permanent disability (Guyton et al., 2014). Ultimately, the panel members concluded that for
    most patients requiring statin therapy, the potential benefits of statin therapy outweigh the
    potential risks. In general terms, the benefits of statins to prevent non-fatal myocardial
    infarction, revascularization, stroke, and CVD mortality, far outweighs any potential harm
    related to the drug (Jacobson, 2014).

    Guidance: Numerator instructions and guidance:
    -Current statin therapy use must be documented in the patient's current medication list or
    ordered during the measurement period.
    -ONLY statin therapy meets the measure Numerator criteria (NOT other cholesterol lowering
    medications).
    -Prescription or order does NOT need to be linked to an encounter or visit; it may be called to
    the pharmacy.
    -Statin medication "samples" provided to patients can be documented as "current statin therapy"
    if documented in the medication list in health/medical record.
    -Patients who meet the denominator criteria for inclusion, but are not prescribed or using
    statin therapy, will NOT meet performance for this measure. There is only one performance rate
    calculated for this measure; the weighted average of the three populations.
    -Adherence to statin therapy is not calculated in this measure.

    Denominator Guidance:
    The denominator covers three distinct populations. Use the following process to prevent
    counting patients more than once.

    Denominator Population 1:
    Patients aged >= 21 years at the beginning of the measurement period with clinical ASCVD

    -If YES, meets Denominator Population 1 risk category
    -If NO, screen for next risk category

    Denominator Population 2:
    Patients aged >= 21 years at the beginning of the measurement period who have ever had a
    fasting or direct laboratory test result of LDL-C >= 190 mg/dL or were previously diagnosed
    with or currently have an active diagnosis of familial or pure hypercholesterolemia

    -If YES, meets Denominator Population 2 risk category
    -If NO, screen for next risk category

    Denominator Population 3:
    Patients aged 40 to 75 years at the beginning of the measurement period with Type 1 or Type 2
    diabetes and with a LDL-C result of 70 -189 mg/dL recorded as the highest fasting or direct
    laboratory test result in the measurement year or during the two years prior to the beginning
    of the measurement period

    -If YES, meets Denominator Population 3 risk category
    -If NO, patient does NOT meet Denominator criteria and is NOT eligible for measure inclusion

    Denominator Guidance for Encounter:
    -In order for the patient to be included in the denominator, the patient must have ONE
    denominator-eligible visit, defined as follows:

    --Outpatient encounter visit type
    --Encounter, performed: initial or established office visit, face-to-face interaction,
    preventive care services, or annual wellness visit

    LDL-C Laboratory test result options:
    The measure can be reported for all patients with a documented fasting or direct LDL-C level
    recorded as follows:

    To meet Denominator Population 1:
    There is no LDL-C result required.

    To meet Denominator Population 2:
    If a patient has ANY previous fasting or direct laboratory result of LDL-C >= 190 mg/dL, report
    the highest value >= 190 mg/dL.

    To meet Denominator Population 3:
    If a patient has more than one LDL-C result during the measurement period or during the two
    years before the start of the measurement period, report the highest level recorded during
    either time. The Denominator Exception, "Patients with diabetes who have the most recent
    fasting or direct LDL-C laboratory test result < 70 mg/dL and are not taking statin therapy"
    applies only to Denominator Population 3.

    Intensity of statin therapy in primary and secondary prevention:

    The expert panel of the 2013 ACC/AHA Guidelines (Stone et al., 2014) defines recommended
    intensity of statin therapy on the basis of the average expected LDL-C response to specific
    statin and dose. Although intensity of statin therapy is important in managing cholesterol,
    this measure assesses prescription of ANY statin therapy, irrespective of intensity. Assessment
    of appropriate intensity and dosage documentation added too much complexity to allow inclusion
    of statin therapy intensity in the measure at this time.

    Lifestyle modification coaching:
    A healthy lifestyle is important for the prevention of cardiovascular disease. However,
    lifestyle modification monitoring and documentation added too much complexity to allow its
    inclusion in the measure at this time.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms347v4
    """

    title = 'Statin Therapy for the Prevention and Treatment of Cardiovascular Disease'

    identifiers = ['CMS347v4']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'PCPI(R) Foundation (PCPI[R])',
    ]

    references = [
        'Banach, M., Rizzo, M., Toth, P.,Famier M., Davidson M. H., Al-Rasadi, K., …Mikhailidis, D. P. (2015). Statin intolerance: An attempt at a unified definition. Position paper from an International Lipid Expert Panel. Archives of Medical Science, 11(1), 1-23. doi: 10.5114/aoms.2015.49807',
        'Benjamin, E. J., Virani, S. S., Callaway, C. W., Chamberlain, A. M., Chang, A. R., Cheng, S., …Munter, P. (2018). Heart disease and stroke statistics—2018 update: A report from the American Heart Association. Circulation, 137(12), e67-e492. doi.10.1161/CIR.0000000000000558',
        'Ference, B.A. (2015, March 10). Statins and the risk of developing new-onset Type 2 diabetes: Expert analysis. Retrieved from https://www.acc.org/latest-in-cardiology/articles/2015/03/10/08/10/statins-and-the-risk-of-developing-new-onset-type-2-diabetes',
        'Guyton, J. R., Bays, H. E., Grundy, S. M., Jacobson, T. A. (2014). As assessment by the Statin Intolerance Panel: 2014 update. Journal of Clinical Lipidology, 8(3 Suppl.), S79. doi/10.1016/jacl.2014.03.002',
        'Jacobson, T. A. (2014). Executive summary: NLA Task Force on Statin Safety—2014 update. Journal of Clinical Lipidology, 8(3 Suppl.), S1-S4. doi:10.1016/jacl.2014.03.002',
        'Maddox, T. M., Borden, W. B., Tang, F., Virani, S. S., Oetgen, W. J., Mullen, B., …Rumsfeld, J. S. (2014). Implications of the 2013 ACC/AHA cholesterol guidelines for adults in contemporary cardiovascular practice: insights from the NCDR Pinnacle Registry. Journal of American College of Cardiology, 64(21), 2183-2192. doi:10.1016/j.acc.2014.08.041',
        'Navar, M., Wang, T. Y., Li, S.,Robinson, J. G., Goldberg, A. C., Virani, S., …Peterson, E. D. (2017). Lipid management in contemporary community practice: Results from the Provider Assessment of Lipid Management (PALM) Registry. American Heart Journal, 193, 84-92. doi.10.1016/j.ahj.2017.08.005',
        'Stone, N. J., Robinson, J., Lichtenstein, A. H., Bairey Merz, C., Blum, C. B., Eckel, R. H., …Wilson, P. W. (2014). 2013 ACC/AHA guideline on the treatment of blood cholesterol to reduce atherosclerotic cardiovascular risk in adults: A report of the American College of Cardiology/American Heart Association Task Force on Practice Guidelines Circulation, 129(25, Suppl. 2), S1-S45. doi.10.1161/01.cir.0000437738.63853.7a',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients aged 21 years and older at the beginning of the
        measurement period with a patient encounter during the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: All patients who meet one or more of the following criteria (considered at
        "high risk" for cardiovascular events, under ACC/AHA guidelines):

        1) Patients aged >= 21 years at the beginning of the measurement period with clinical ASCVD
        diagnosis

        2) Patients aged >= 21 years at the beginning of the measurement period who have ever had a
        fasting or direct laboratory result of LDL-C >=190 mg/dL or were previously diagnosed with
        or currently have an active diagnosis of familial or pure hypercholesterolemia

        3) Patients aged 40 to 75 years at the beginning of the measurement period with Type 1 or
        Type 2 diabetes and with an LDL-C result of 70-189 mg/dL recorded as the highest fasting or
        direct laboratory test result in the measurement year or during the two years prior to the
        beginning of the measurement period

        Exclusions: Patients who have a diagnosis of pregnancy
        Patients who are breastfeeding
        Patients who have a diagnosis of rhabdomyolysis

        Exceptions: Patients with adverse effect, allergy, or intolerance to statin medication
        Patients who are receiving palliative or hospice care
        Patients with active liver disease or hepatic disease or insufficiency
        Patients with end-stage renal disease (ESRD)
        Patients with diabetes who have the most recent fasting or direct LDL-C laboratory test
        result < 70 mg/dL and are not taking statin therapy
        """
        pass

    def in_numerator(self):
        """
        Numerator: Patients who are actively using or who receive an order (prescription) for
        statin therapy at any point during the measurement period

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: This electronic clinical quality measure is intended to align with
        the 2013 ACC/AHA Guideline on the Treatment of Blood Cholesterol (Stone et al., 2014),
        which indicates the use of statins as the first line of cholesterol-lowering medication
        therapy to lower the risk of ASCVD among at-risk populations.

        Recommendations for Treatment of Blood Cholesterol to Reduce Atherosclerotic Cardiovascular
        Risk in Adults - Statin Treatment:
        Secondary Prevention:
        1. High-intensity statin therapy should be initiated or continued as first-line therapy in
        women and men <=75 years of age who have clinical ASCVD, unless contraindicated. (Level of
        Evidence A), (Stone et al., 2014)

        2. In individuals with clinical ASCVD in whom high-intensity statin therapy would otherwise
        be used, when high-intensity statin therapy is contraindicated or when characteristics
        predisposing to statin-associated adverse effects are present, moderate-intensity statin
        should be used as the second option, if tolerated. (Level of Evidence A), (Stone et al.,
        2014)

        Primary Prevention in Individuals >= 21 Years of Age With LDL-C >=190 mg/dL:
        2. Adults >=21 years of age with primary LDL-C >=190 mg/dL should be treated with statin
        therapy. (10-year ASCVD risk estimation is not required.) (Level of Evidence B), (Stone et
        al., 2014)

        Primary Prevention in Individuals With Diabetes and LDL-C 70-189 mg/dL:
        1. Moderate-intensity statin therapy should be initiated or continued for adults 40-75
        years of age with diabetes. (Level of Evidence A), (Stone et al., 2014)
        """
        pass
