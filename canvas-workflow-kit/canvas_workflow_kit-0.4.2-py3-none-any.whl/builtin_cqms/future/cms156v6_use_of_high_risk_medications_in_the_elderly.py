from canvas_workflow_kit import events
from canvas_workflow_kit.protocol import ClinicalQualityMeasure
from canvas_workflow_kit.recommendation import TaskRecommendation
# flake8: noqa
from canvas_workflow_kit.value_set.v2018 import (
    AcetaminophenAspirinDiphenhydramine, AcetaminophenBrompheniramine, AcetaminophenButalbital,
    AcetaminophenButalbitalCaffeine, AcetaminophenButalbitalCaffeineCodeine,
    AcetaminophenChlorpheniramine, AcetaminophenChlorpheniramineDextromethorphan,
    AcetaminophenChlorpheniramineDextromethorphanGuaifenesin,
    AcetaminophenChlorpheniramineDextromethorphanPhenylephrine,
    AcetaminophenChlorpheniramineDextromethorphanPseudoephedrine,
    AcetaminophenChlorpheniraminePhenylephrine, AcetaminophenChlorpheniraminePseudoephedrine,
    AcetaminophenDexbrompheniramine, AcetaminophenDextromethorphanDiphenhydramine,
    AcetaminophenDextromethorphanDiphenhydraminePhenylephrine,
    AcetaminophenDextromethorphanDoxylamine, AcetaminophenDextromethorphanDoxylaminePhenylephrine,
    AcetaminophenDextromethorphanDoxylaminePseudoephedrine, AcetaminophenDiphenhydramine,
    AcetaminophenDiphenhydraminePhenylephrine, AcetaminophenDiphenhydraminePseudoephedrine,
    AcetaminophenDoxylaminePhenylephrine, AmitriptylineChlordiazepoxide,
    AmitriptylineHydrochloride, AmitriptylinePerphenazine, Amobarbital, AnnualWellnessVisit,
    AntiInfectivesOther, AspirinButalbitalCaffeine, AspirinButalbitalCaffeineCodeine,
    AspirinCaffeineOrphenadrine, AspirinCarisoprodol, AspirinCarisoprodolCodeine,
    AspirinChlorpheniraminePhenylephrine, AspirinDiphenhydramineCitrate, AspirinMeprobamate,
    AtropineChlorpheniramineHyoscyaminePseudoephedrineScopolamine,
    AtropineHyoscyaminePhenobarbitalScopolamine, BazedoxifeneConjugatedEstrogens, Benztropine,
    Brompheniramine, BrompheniramineChlophedianolPhenylephrine,
    BrompheniramineChlophedianolPseudoephedrine, BrompheniramineCodeine,
    BrompheniramineCodeinePhenylephrine, BrompheniramineCodeinePseudoephedrine,
    BrompheniramineDextromethorphanPhenylephrine, BrompheniramineDextromethorphanPseudoephedrine,
    BrompheniraminePhenylephrine, BrompheniraminePseudoephedrine, Butabarbital,
    CarbetapentaneChlorpheniramineEphedrinePhenylephrine,
    CarbetapentaneChlorpheniraminePhenylephrine, Carbinoxamine, Carisoprodol,
    ChlophedianolChlorpheniraminePhenylephrine, ChlophedianolDexbrompheniraminePhenylephrine,
    ChlophedianolDexbrompheniraminePseudoephedrine,
    ChlophedianolDexchlorpheniraminePseudoephedrine, Chlorpheniramine, ChlorpheniramineCodeine,
    ChlorpheniramineCodeinePhenylephrine, ChlorpheniramineCodeinePseudoephedrine,
    ChlorpheniramineDextromethorphan, ChlorpheniramineDextromethorphanPhenylephrine,
    ChlorpheniramineDextromethorphanPseudoephedrine, ChlorpheniramineDihydrocodeinePhenylephrine,
    ChlorpheniramineHydrocodone, ChlorpheniramineHydrocodonePseudoephedrine,
    ChlorpheniramineIbuprofenPseudoephedrine, ChlorpheniraminePhenylephrine,
    ChlorpheniraminePhenylephrinePhenyltoloxamine, ChlorpheniraminePhenylephrinePyrilamine,
    ChlorpheniraminePseudoephedrine, Chlorpropamide, Chlorzoxazone, Clemastine, Clomipramine,
    CodeineDexbrompheniraminePseudoephedrine, CodeineDexchlorpheniraminePhenylephrine,
    CodeinePhenylephrinePromethazine, CodeinePromethazine, CodeinePseudoephedrineTriprolidine,
    ConjugatedEstrogens, ConjugatedEstrogensMedroxyprogesterone, CyclobenzaprineHydrochloride,
    DesiccatedThyroid, Dexbrompheniramine, DexbrompheniramineDextromethorphanPhenylephrine,
    DexbrompheniramineDextromethorphanPseudoephedrine,
    DexbrompheniramineMaleatePseudoephedrineHydrochloride, DexbrompheniraminePhenylephrine,
    DexbrompheniraminePseudoephedrine, Dexchlorpheniramine,
    DexchlorpheniramineDextromethorphanPseudoephedrine, DexchlorpheniraminePhenylephrine,
    DexchlorpheniraminePseudoephedrine, DextromethorphanDiphenhydraminePhenylephrine,
    DextromethorphanDoxylamine, DextromethorphanDoxylaminePseudoephedrine,
    DextromethorphanPromethazine, DienogestEstradiolMultiphasic, DiphenhydramineHydrochloride,
    DiphenhydramineIbuprofen, DiphenhydramineMagnesiumSalicylate, DiphenhydramineNaproxen,
    DiphenhydraminePhenylephrine, DiphenhydraminePseudoephedrine, Dipyridamole,
    DischargedToHealthCareFacilityForHospiceCare, DischargedToHomeForHospiceCare, Disopyramide,
    Doxylamine, DoxylaminePhenylephrine, DoxylaminePseudoephedrine, DoxylaminePyridoxine,
    DrospirenoneEstradiol, EncounterInpatient, ErgoloidMesylates, EsterifiedEstrogens,
    EsterifiedEstrogensMethyltestosterone, Estradiol, EstradiolLevonorgestrel,
    EstradiolNorethindrone, EstradiolNorgestimateBiphasic, Estropipate, Ethnicity,
    FaceToFaceInteraction, Glyburide, GlyburideMetformin, Guanfacine,
    HighRiskMedicationsForTheElderly, HighRiskMedicationsWithDaysSupplyCriteria,
    HomeHealthcareServices, HospiceCareAmbulatory, HydrochlorothiazideMethyldopa, Hydroxyzine,
    Imipramine, Indomethacin, Isoxsuprine, KetorolacTromethamine, Megestrol, Meperidine,
    MeperidinePromethazine, Mephobarbital, Meprobamate, Metaxalone, Methocarbamol, Methyldopa,
    NaloxonePentazocine, Nifedipine, NonbenzodiazepineHypnotics, OfficeVisit, OncAdministrativeSex,
    OphthalmologicOutpatientVisit, Orphenadrine, Payer, Pentazocine, Pentobarbital, Phenobarbital,
    PhenylephrinePromethazine, PhenylephrineTriprolidine,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, PromethazineHydrochloride,
    PseudoephedrineTriprolidine, Race, Secobarbital, Thioridazine, Ticlopidine, Trihexyphenidyl,
    Trimethobenzamide, Trimipramine, Triprolidine)


class ClinicalQualityMeasure156v6(ClinicalQualityMeasure):
    """
    Use of High-Risk Medications in the Elderly

    Description: Percentage of patients 65 years of age and older who were ordered high-risk
    medications. Two rates are reported.
    a. Percentage of patients who were ordered at least one high-risk medication.
    b. Percentage of patients who were ordered at least two of the same high-risk medications.

    Definition: A high-risk medication is identified by either of the following:
         a. A prescription for medications classified as high risk at any dose and for any duration
         b. Prescriptions for medications classified as high risk at any dose with greater than a
    90 day supply

    Rationale: Seniors receiving inappropriate medications are more likely to report poorer health
    status at follow-up, compared to seniors who receive appropriate medications (Fu, Liu, and
    Christensen 2004. A study of the prevalence of potentially inappropriate medication use in
    older adults found that 40 percent of individuals 65 and older filled at least one prescription
    for a potentially inappropriate medication and 13 percent filled two or more (Fick et al.
    2008). While some adverse drug events are not preventable, studies estimate that between 30 and
    80 percent of adverse drug events in the elderly are preventable (MacKinnon and Hepler 2003).

    Reducing the number of inappropriate prescriptions can lead to improved patient safety and
    significant cost savings.  Conservative estimates of extra costs due to potentially
    inappropriate medications in the elderly average $7.2 billion a year (Fu et al. 2007).
    Medication use by older adults will likely increase further as the U.S. population ages, new
    drugs are developed, and new therapeutic and preventive uses for medications are discovered
    (Rothberg et al. 2008). The annual direct costs of preventable adverse drug events (ADEs) in
    the Medicare population have been estimated to exceed $800 million (IOM, 2007). By the year
    2030, nearly one in five U.S. residents is expected to be aged 65 years or older; this age
    group is projected to more than double in number from 38.7 million in 2008 to more than 88.5
    million in 2050.  Likewise, the population aged 85 years or older is expected to increase
    almost four-fold, from 5.4 million to 19 million between 2008 and 2050.  As the elderly
    population continues to grow, the number of older adults who present with multiple medical
    conditions for which several medications are prescribed continues to increase, resulting in
    polypharmacy (Gray and Gardner 2009).

    Guidance: The intent of Numerator 1 is to assess if the patient has been prescribed at least
    one high-risk medication.

    The intent of Numerator 2 is to assess if the patient has either:
         - Been prescribed at least two of the same high-risk medications.
         - Received two or more prescriptions, where the sum of days supply exceeds 90 days, for
    medications in the same medication class.

    The intent of the measure is to assess if the reporting provider ordered the high-risk
    medication(s). If the patient had a high-risk medication previously prescribed by another
    provider, they would not be counted towards the numerator unless the reporting provider also
    ordered a high-risk medication for them.

    CUMULATIVE MEDICATION DURATION is an individual's total number of medication days over a
    specific period; the period counts multiple prescriptions with gaps in between, but does not
    count the gaps during which a medication was not dispensed.

    To determine the cumulative medication duration, determine first the number of the Medication
    Days for each prescription in the period: the number of doses divided by the dose frequency per
    day. Then add the Medication Days for each prescription without counting any days between the
    prescriptions.

    For example, there is an original prescription for 30 days with 2 refills for thirty days each.
    After a gap of 3 months, the medication was prescribed again for 60 days with 1 refill for 60
    days. The cumulative medication duration is (30 x 3) + (60 x 2) = 210 days over the 10 month
    period.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms156v6
    """

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'Campanelli, Christine M. 2012. "American Geriatrics Society Updated Beers Criteria for Potentially Inappropriate Medication Use in Older Adults: the American Geriatrics Society 2012 Beers Criteria Update Expert Panel." Journal of the American Geriatrics Society 60(4): 616.',
        'American Geriatrics Society 2015 Beers Criteria Update Expert Panel. 2015. "American Geriatrics Society 2015 Updated Beers Criteria for Potentially Inappropriate Medication Use in Older Adults." Journal of the American Geriatrics Society. 63(11): 2227-2246.',
        'Zhan, C, et al. Potentially inappropriate medication use in the community-dwelling elderly. JAMA 2001; 286(22):2823-2868.',
        'Beers, M.H. Explicit criteria for determining potentially inappropriate medication use by the elderly. Arch Intern Med 1997; 157:1531-1536.',
        'Fick, DM, et al. Updating the Beers criteria for potentially inappropriate medication use in older adults. Arch Intern Med 2003; 163:2716-2724.',
        'Fu, A.Z., J.Z. Jiang, J.H. Reeves, J.E. Funcham, G.G. Liu, M. Perri. 2007. "Potentially Inappropriate Medication Use and Healthcare Expenditures in the US Community-Dwelling Elderly." Medical Care 45: 472-6.',
        'Gray, C.L, and C. Gardner. 2009. "Adverse Drug Events in the Elderly: An Ongoing Problem." J Manag Care Pharm 15(7):568-71.',
        'Fick, D.M., L.C. Mion, M.H. Beers, J.L. Waller. 2008. "Health Outcomes Associated with Potentially Inappropriate Medication Use in Older Adults." Research in Nursing & Health. 31(1): 42-51.',
        'AHRQ, "Use of High-Risk Medications in the Elderly: Percentage of Medicare Members 65 years of Age and Older who Received at least two different High-Risk Medications." National Quality Measures Clearinghouse. http://www.qualitymeasures.ahrq.gov/popups/printView.aspx?id=24003 (Accessed Web page: December 14, 2015).',
        'Institute of Medicine (IOM). 2007. Preventing Medication Errors/Committee on Identifying and Preventing Medication Errors. Ed. Aspden P., J.A. Wolcott, J.L. Bootman, L.R. Cronenwatt LR. Quality Chasm Series. Washington, DC: National Academy Press.',
        'MacKinnon, N.J. and C.D. Hepler. 2003. "Indicators of Preventable Drug-related Morbidity in Older Adults: Use Within a Managed Care Organization." J Managed Care Pharm 9:134-41.',
        'Kaufman MB, et al. Effect of Prescriber Education on the Use of Medications Contraindicated in Older Adults in a Managed Medicare Population. J Manag Care Pharm 2005 April/May; 11(3):211-219.',
        'Rothberg, M.B., P.S. Perkow, F. Liu, B. Korc-Grodzicki, M.J. Brennan, S. Bellantonio, M. Heelon, P.K. Lindenauer. 2008. "Potentially Inappropriate Medication Use in Hospitalized Elders." J Hosp Med 3:91-102.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Patients 65 years and older who had a visit during the measurement
        period
        """
        age = self.patient.age_at(self.timeframe.end)
        if age < 65:
            return False

        # FIX: check for a visit within the period when we have note data loaded

        return True

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Exclude patients who were in hospice care during the measurement year

        Exceptions: None
        """

        # FIX: detect hospice

        return self.in_initial_population()

    def in_numerator(self, population=1):
        """
        Numerator: Numerator 1: Patients with an order for at least one high-risk medication during
        the measurement period

        Numerator 2: Patients with at least two orders for the same high-risk medication during the
        measurement period

        Exclusions: Not Applicable
        """
        if population == 1:
            if self.high_risk_medications():
                return True

        elif population == 2:
            if len(self.high_risk_medications()) >= 2:
                return True

        else:
            raise Exception(f'Unknown population "{population}"')

    def high_risk_medications(self):
        """ find medication orders matching the high risk classification """
        meds = self.patient.medications.within_one_year(self.timeframe)

        # these are high-risk at any dosage
        high_risk = meds.find(HighRiskMedicationsForTheElderly)

        # FIX: these we need to evaluate dosage to decide if they
        # constitute high-risk medications but the medications
        # endpoint isn't returning enough info yet to do that, so
        # we'll err on the side of caution and assume they're high
        # risk too
        high_risk_dosage = meds.find(HighRiskMedicationsWithDaysSupplyCriteria)

        return high_risk + high_risk_dosage

    def compute_results(self):
        """
        Clinical recommendation: The measure is based on recommendations from the American
        Geriatrics Society Beers Criteria for Potentially Inappropriate Medication Use in Older
        Adults. The criteria were developed through key clinical expert consensus processes by
        Beers in 1997, Zahn in 2001 and an updated process by Fick in 2003, 2012 and 2015. The
        Beers Criteria identifies lists of drugs that are potentially inappropriate for all older
        adults and drugs that are potentially inappropriate in the elderly based on various high-
        risk factors such as dosage, days supply and underlying diseases or conditions. NCQA's
        Medication Management expert panel selected a subset of drugs that should be used with
        caution in the elderly for inclusion in the proposed measure based upon the recommendations
        in the Beers Criteria.

        Certain medications (MacKinnon 2003) are associated with increased risk of harm from drug
        side-effects and drug toxicity and pose a concern for patient safety. There is clinical
        consensus that these drugs pose increased risks in the elderly (Kaufman 2005). Studies link
        prescription drug use by the elderly with adverse drug events that contribute to
        hospitalization, increased length of hospital stay, increased duration of illness, nursing
        home placement and falls and fractures that are further associated with physical,
        functional and social decline in the elderly (AHRQ 2009).
        """
        patient = self.patient

        recommendations = []
        status = 'not_applicable'
        narrative = ''

        high_risk = self.high_risk_medications()
        if high_risk:
            names = [med['text'] for med in high_risk]
            narrative = f'{patient.first_name} is elderly and has been prescribed high-risk medication{"s" if len(names) > 1 else ""}: {", ".join(names)}.  The nursing team should perform a medication reconciliation.'

            status = 'due'
            rec = TaskRecommendation(
                patient, narrative=narrative, title='Task: Medication Reconciliation')
            recommendations.append(rec)

        return {'status': status, 'narrative': narrative, 'recommendations': recommendations}
