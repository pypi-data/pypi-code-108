# flake8: noqa
from canvas_workflow_kit import events
from canvas_workflow_kit.protocol import ClinicalQualityMeasure
from canvas_workflow_kit.timeframe import Timeframe
from canvas_workflow_kit.value_set.v2017 import (
    AcuteMyocardialInfarction, AnnualWellnessVisit, CoronaryArteryBypassGraft, Ethnicity,
    FaceToFaceInteraction, HdlCLaboratoryTest, HomeHealthcareServices, IschemicVascularDisease,
    LdlC, OfficeVisit, OncAdministrativeSex, Payer, PercutaneousCoronaryInterventions,
    PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, Race, TotalCholesterolLaboratoryTest,
    TriglyceridesLaboratoryTest)


# TODO Recommendations can have >1 action (more than one way to resolve a Recommendation)
# TODO Add Predicate class for rich "debugging"?
# TODO action-oriented 'tell me what to do view' vs. inverted 'tell me why' view
# TODO due/pending/etc. based on order committed/status
class ClinicalQualityMeasure182v6(ClinicalQualityMeasure):
    """
    Ischemic Vascular Disease (IVD): Complete Lipid Profile and LDL-C Control (<100 mg/dL)

    Description: Percentage of patients 18 years of age and older who were diagnosed with acute
    myocardial infarction (AMI), coronary artery bypass graft (CABG) or percutaneous coronary
    interventions (PCI) in the 12 months prior to the measurement period, or who had a diagnosis of
    ischemic vascular disease (IVD) during the measurement period, and who had a complete lipid
    profile performed during the measurement period and whose most recent Low-density Lipoprotein
    (LDL-C) was adequately controlled (< 100 mg/dL)

    Definition: None

    Rationale: A 10 percent decrease in total cholesterol levels (population wide) may result in an
    estimated 30 percent reduction in the incidence of coronary heart disease (CHD) (Centers for
    Disease Control and Prevention 2000). Based on data from the Third Report of the Expert Panel
    on Detection, Evaluation, and Treatment of High Blood Cholesterol in Adults:
    *Less than half of persons who qualify for any kind of lipid-modifying treatment for CHD risk
    reduction are receiving it
    *Less than half of even the highest-risk persons, those who have symptomatic CHD, are receiving
    lipid-lowering treatment
    *Only about a third of treated patients are achieving their LDL goal; less than 20 percent of
    CHD patients are at their LDL goal (National Cholesterol Education Program (NCEP) Expert Panel
    on Detection, Evaluation, and Treatment of High Blood Pressure 2002)

    According to data from the Behavioral Risk Factor Surveillance System (BRFSS) from 1991 - 2003,
    the prevalence of cholesterol screening during the preceding 5 years increased from 67.3
    percent in 1991 to 73.1 percent in 2003 (Centers for Disease Control and Prevention 2005).

    Between 1988-94 and 1999-2002, the age-adjusted mean total serum cholesterol level of adults 20
    years of age and  older decreased from 206 mg/dL to 203 mg/dL, and LDL cholesterol levels
    decreased from 129 mg/dL to 123 mg/dL. The mean level of LDL cholesterol for American adults
    age 20 and older is 123 mg/dL (Carroll et al. 2005). However, even given this decrease, there
    is still a significant amount of room for improvement.

    Guidance: Only patients who were diagnosed with acute myocardial infarction (AMI), coronary
    artery bypass graft (CABG) or percutaneous coronary interventions (PCI) are included in this
    measure

    More information: https://ecqi.healthit.gov/ecqm/measures/cms182v6
    """

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'Centers for Disease Control and Prevention (CDC). 2005. "Trends in cholesterol screening and awareness of high blood cholesterol - United States, 1991-2003." MMWR 54;865-870.',
        'Carroll, M.D., D.A. Lacher, P.D. Sorlie, J.I. Cleeman, D.J. Gordon, M. Wolz, S.M. Grundy, C.L. Johnson. 2005. "Trends in serum lipids and lipoproteins of adults. 1960-2002." JAMA 294:1773-1781.',
        'Centers for Disease Control and Prevention (CDC). 2000. "State-specific cholesterol screening trends - United States, 1991-1999." MMWR 49:750-755.',
        'National Cholesterol Education Program (NCEP) Expert Panel on Detection, Evaluation, and Treatment of High Blood Cholesterol in Adults (Adult Treatment Panel III). 2002. "Third Report of the National Cholesterol Education Program (NCEP) Expert Panel on Detection, Evaluation, and Treatment of High Blood Cholesterol in Adults (Adult Treatment Panel III) final report." Circulation 106(25):3143-421.',
        'Grundy SM, Cleeman JI, Merz CN, et al. Implications of recent clinical trials for the National Cholesterol Education Program Adult Treatment Panel III guidelines. Circulation 2004; 110: 227-39.',
        'U.S. Preventive Services Task Force. 2008. "Screening for lipid disorders in adults" (June) http://www.uspreventiveservicestaskforce.org/uspstf/uspschol.htm',
    ]

    funding_source = ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.one_year_before_start = Timeframe(
            start=self.timeframe.start.shift(months=-12), end=self.timeframe.start)

    def has_acute_myocardial_infarction(self):
        return self.patient.conditions.within(
            self.one_year_before_start).find(AcuteMyocardialInfarction)

    def has_ischemic_vascular_disease(self):
        return self.patient.conditions.within(self.timeframe).find(IschemicVascularDisease)

    def has_percutaneous_coronary_interventions(self):
        return self.patient.conditions.within(
            self.one_year_before_start).find(PercutaneousCoronaryInterventions)

    def has_coronary_artery_bypass_graft(self):
        return self.patient.conditions.within(
            self.one_year_before_start).find(CoronaryArteryBypassGraft)

    def has_all_four_tests_during_measurement_period(self):
        # XXX is checking for a result within the timeframe sufficient?
        return all([
            self.patient.lab_results.within(self.timeframe).find(HdlCLaboratoryTest),
            self.patient.lab_results.within(self.timeframe).find(LdlC),
            self.patient.lab_results.within(self.timeframe).find(TotalCholesterolLaboratoryTest),
            self.patient.lab_results.within(self.timeframe).find(TriglyceridesLaboratoryTest),
        ])

    def has_ldl_below_100mg_dl(self):
        most_recent_ldl_c = self.patient.lab_results.within(
            self.timeframe).find(LdlC).last_value(float)

        return most_recent_ldl_c is not None and float(most_recent_ldl_c['value']) < 100

    def in_initial_population(self):
        """
        Initial population: Patients 18 years of age and older with a visit during the measurement
        year who had an AMI, CABG, or PCI during the 12 months prior to the measurement year or who
        had a diagnosis of IVD during the measurement year
        """
        return any([
            self.has_acute_myocardial_infarction(),
            self.has_ischemic_vascular_disease(),
            all([
                self.has_percutaneous_coronary_interventions(),
                self.has_coronary_artery_bypass_graft(),
            ]),
        ])

    def in_denominator(self):
        """
        Denominator: Equals Initial Population
        """
        return self.in_initial_population()

    def in_numerator_1(self):
        """
        Numerator 1: Patients with a complete lipid profile performed during the measurement period
        """
        return self.has_all_four_tests_during_measurement_period()

    def in_numerator_2(self):
        """
        Numerator 2: Patients whose most recent LDL-C level performed during the measurement period
        is <100 mg/dL
        """
        return self.has_ldl_below_100mg_dl()

    def recommendations(self):
        """
        Clinical recommendation: Third report of the National Cholesterol Education Program (NCEP)
        Expert Panel on Detection, Evaluation, and Treatment of High Blood Cholesterol in Adults
        (Adult Treatment Panel III). (2002) AND Implications of recent clinical trials for the
        National Cholesterol Education Program Adult Treatment Panel III guidelines (2004)
        In high-risk persons, the recommended LDL-C goal is < 100 mg/dL.

        * An LDL-C goal of < 70 mg/dL is a therapeutic option on the basis of available clinical
          trial evidence, especially for patients at very high risk.

        * If LDL-C is > 100 mg/dL, an LDL-lowering drug is indicated simultaneously with lifestyle
          changes.

        * If baseline LDL-C is < 100 mg/dL, institution of an LDL-lowering drug to achieve an LDL-C
          level < 70 mg/dL is a therapeutic option on the basis of available clinical trial
          evidence.

        * If a high-risk person has high triglycerides or low HDL-C, consideration can be given to
          combining a fibrate or nicotinic acid with an LDL-lowering drug. When triglycerides are >
          200 mg/dL, non-HDL-C is a secondary target of therapy, with a goal 30 mg/dL higher than
          the identified LDL-C goal.

        The U.S. Preventive Services Task Force (USPSTF) strongly recommends screening men aged 35
        and older for lipid disorders and recommends screening men aged 20 to 35 for lipid
        disorders if they are at increased risk for coronary heart disease. The USPSTF also
        strongly recommends screening women aged 45 and older for lipid disorders if they are at
        increased risk for coronary heart disease and recommends screening women aged 20 to 45 for
        lipid disorders if they are at increased risk for coronary heart disease.
        """
        pass
