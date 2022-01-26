from typing import List

import arrow

from canvas_workflow_kit import events
from canvas_workflow_kit.protocol import ClinicalQualityMeasure
from canvas_workflow_kit.recommendation import InterviewRecommendation, InstructionRecommendation, Recommendation
from canvas_workflow_kit.value_set.v2018 import (
    AdditionalEvaluationForDepressionAdolescent, AdditionalEvaluationForDepressionAdult,
    AdolescentDepressionScreening, AdultDepressionScreening, BipolarDiagnosis, DepressionDiagnosis,
    DepressionMedicationsAdolescent, DepressionMedicationsAdult, DepressionScreeningEncounterCodes,
    Ethnicity, FollowUpForDepressionAdolescent, FollowUpForDepressionAdult,
    NegativeDepressionScreening, OncAdministrativeSex, Payer, PositiveDepressionScreening, Race,
    ReferralForDepressionAdolescent, ReferralForDepressionAdult,
    SuicideRiskAssessment_559)  # flake8: noqa


class ClinicalQualityMeasure2v7(ClinicalQualityMeasure):
    """
    Preventive Care and Screening: Screening for Depression and Follow-Up Plan

    Description: Percentage of patients aged 12 years and older screened for depression on the date
    of the encounter using an age appropriate standardized depression screening tool AND if
    positive, a follow-up plan is documented on the date of the positive screen

    Definition: Screening:
    Completion of a clinical or diagnostic tool used to identify people at risk of developing or
    having a certain disease or condition, even in the absence of symptoms.
    Standardized Depression Screening Tool - A normalized and validated depression screening tool
    developed  for the patient population in which it is being utilized

    Examples of depression screening tools include but are not limited to:
    *  Adolescent Screening Tools (12-17 years)
       *  Patient Health Questionnaire for Adolescents (PHQ-A)
       *  Beck Depression Inventory-Primary Care Version (BDI-PC)
       *  Mood Feeling Questionnaire(MFQ)
       *  Center for Epidemiologic Studies Depression Scale (CES-D)
       *  Patient Health Questionnaire (PHQ-9)
       *  Pediatric Symptom Checklist (PSC-17)
       *  PRIME MD-PHQ2
    *  Adult Screening Tools (18 years and older)
       *  Patient Health Questionnaire (PHQ9)
       *  Beck Depression Inventory (BDI or BDI-II)
       *  Center for Epidemiologic Studies Depression Scale (CES-D)
       *  Depression Scale (DEPS)
       *  Duke Anxiety-Depression Scale (DADS)
       *  Geriatric Depression Scale (GDS)
       *  Cornell Scale for Depression in Dementia (CSDD)
       *  PRIME MD-PHQ2
       * Hamilton Rating Scale for Depression (HAM-D)
       * Quick Inventory of Depressive Symptomatology Self-Report (QID-SR)
    * Perinatal Screening Tools
       *  Edinburgh Postnatal Depression Scale
       *  Postpartum Depression Screening Scale
       *  Patient Health Questionnaire 9 (PHQ-9)
       *  Beck Depression Inventory
       *  Beck Depression Inventory-II
       *  Center for Epidemiologic Studies Depression Scale
       *  Zung Self-rating Depression Scale

    Follow-Up Plan:
    Documented follow-up for a positive depression screening must include one or more of the
    following:
     *  Additional evaluation for depression
     *  Suicide Risk Assessment
     *  Referral to a practitioner who is qualified to diagnose and treat depression
     *  Pharmacological interventions
     *  Other interventions or follow-up for the diagnosis or treatment of depression

    Rationale: 2014 U.S. survey data indicate that 2.8 million (11.4 percent) adolescents aged 12
    to 17 had a major depressive episode (MDE) in the past year and that 15.7 million (6.6 percent)
    adults aged 18 or older had at least one MDE in the past year, with 10.2 million adults (4.3
    percent) having one MDE with severe impairment in the past year (Center for Behavioral Health
    Statistics and Quality, 2015). The World Health Organization (WHO), as cited by Pratt & Brody
    (2008), found that major depression was the leading cause of disability worldwide. Data
    indicate that approximately 80% of people diagnosed with depression report some level of
    difficulty in functioning because of their depressive symptoms. For example, 35% of males and
    22% of females with depression reported that their depressive symptoms make it extremely
    difficult for them to work, get things done at home, or get along with other people.
    Additionally, more than one-half of all persons with mild depressive symptoms also reported
    some difficulty in daily functioning attributable to their depressive symptoms (Pratt & Brody,
    2008). In young adulthood, major depressive disorder (MDD) has been found to be associated with
    early pregnancy, decreased school performance, and impaired work, social, and family
    functioning (Williams et al., 2009, p. e716). In the perinatal period, depression and other
    mood disorders, such as bipolar disorder and anxiety disorders, can have devastating effects on
    women, infants, and families. Maternal suicide rates rise over hemorrhage and hypertensive
    disorders as a cause of maternal mortality (American College of Obstetricians and
    Gynecologists, 2015).

    Negative outcomes associated with depression make it crucial to screen in order to identify and
    treat depression in its early stages. While Primary Care Providers (PCPs) serve as the first
    line of defense in the detection of depression, studies show that PCPs fail to recognize up to
    50% of depressed patients (Borner, 2010, p. 948). 'Coyle et al. (2003), suggested that the
    picture is more grim for adolescents, and that more than 70% of children and adolescents
    suffering from serious mood disorders go unrecognized or inadequately treated' (Borner, 2010,
    p. 948). 'In nationally representative U.S. surveys, about 8% of adolescents reported having
    major depression in the past year. Only 36% to 44% of children and adolescents with depression
    receive treatment, suggesting that the majority of depressed youth are undiagnosed and
    untreated' (Sui, A. and USPSTF, 2016). Evidence supports that screening for depression in
    pregnant and postpartum women is of moderate net benefit and treatment options for positive
    depression screening should be available for patients twelve and older including pregnant and
    postpartum women.

    If preventing negative patient outcomes is not enough, the substantial economic burden of
    depression for individuals and society alike makes a case for screening for depression on a
    regular basis. Depression imposes economic burden through direct and indirect costs. 'In the
    United States, an estimated $22.8 billion was spent on depression treatment in 2009, and lost
    productivity cost an additional estimated $23 billion in 2011' (Sui, A. and USPSTF, 2016).

    This measure seeks to align with clinical guideline recommendations as well as the Healthy
    People 2020 recommendation for routine screening for mental health problems as a part of
    primary care for both children and adults (U.S. Department of Health and Human Services, 2014)
    and  makes an important contribution to the quality domain of community and population health.

    Guidance: A depression screen is completed on the date of the encounter using an age
    appropriate standardized depression screening tool AND if positive, either additional
    evaluation for depression, suicide risk assessment, referral to a practitioner who is qualified
    to diagnose and treat depression, pharmacological interventions, or other interventions or
    follow-up for the diagnosis or treatment of depression is documented on the date of the
    positive screen.

    Screening Tools:
     *  The name of the age appropriate standardized depression screening tool utilized must be
    documented in the medical record
     *  The depression screening must be reviewed and addressed in the office of the provider,
    filing the code, on the date of the encounter
     *  The screening should occur during a qualified encounter
     *  Standardized Depression Screening Tools should be normalized and validated for the age
    appropriate patient population in which they are used and must be documented in the medical
    record

    Follow-Up Plan:

    * The follow-up plan must be related to a positive depression screening, example: 'Patient
    referred for psychiatric evaluation due to positive depression screening.'

    * Pharmacologic treatment for depression is often indicated during pregnancy and/or lactation.
    Review and discussion of the risks of untreated versus treated depression is advised.
    Consideration of each patient's prior disease and treatment history, along with the risk
    profiles for individual pharmacologic agents, is important when selecting pharmacologic therapy
    with the greatest likelihood of treatment effect.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms2v7
    """

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'Quality Insights',
    ]

    references = [
        'American College of Obstetricians and Gynecologists (2015). Screening for perinatal depression. Committee Opinion No. 630. Obstet Gynecol 2015;125:1268-71. Retrieved from http://www.acog.org/Resources-And-Publications/Committee-Opinions/Committee-on-Obstetric-Practice/Screening-for-Perinatal-Depression',
        'Borner I, Braunstein JW, St. Victor, R, Pollack J (2010). Evaluation of a 2-question screening tool for detecting depression in adolescents in Primary Care. Clinical Pediatrics, 49, 947-995. doi: 10.1177/0009922810370203',
        'Center for Behavioral Health Statistics and Quality. (2015). Behavioral health trends in the United States:Results from the 2014 National Survey on Drug Use and Health (HHS Publication No. SMA 15-4927, NSDUH Series H-50). Retrieved from http://www.samhsa.gov/data/sites/default/files/NSDUH-FRR1-2014/NSDUH-FRR1-2014.pdf',
        'Coyle J T, Pine D.S, Charney D S, Lewis L, Nemeroff C B, Carlson G A, Joshi P T (2003). Depression and bipolar support alliance consensus development panel. Depression and bipolar support alliance consensus statement on the unmet needs in diagnosis and treatment of mood disorders in children and adolescents. Journal of the American Academy of Child and Adolescent Psychiatry, 42, 1494-1503.',
        'Pratt L.A, Brody DJ.(2008). Depression in the United States household population, 2005-2006. U.S. Department of Health and Human Services, Centers for Disease Control and Prevention National Center for Health Statistics. NCHS Data Brief No.7, 1-8.',
        'Siu AL, on behalf of the U.S. Preventive Services Task Force. Screening for Depression in Children and Adolescents: U.S. Preventive Services Task Force Recommendation Statement. Ann Intern Med. 2016;164:360-366. http://annals.org/article.aspx?articleid=2490528',
        'Siu AL, and the US Preventive Services Task Force (USPSTF). Screening for Depression in Adults: US Preventive Services Task Force Recommendation Statement. JAMA. 2016;315(4):380-387. doi:10.1001/jama.2015.18392. http://jama.jamanetwork.com/article.aspx?articleid=2484345',
        'Steinman LE, Frederick JT, Prohaska T, Satariano WA, Dornberg-Lee S, Fisher R, ...Snowden M (2007). Recommendations for treating depression in community-based older adults. American Journal of Preventive Medicine, 33(3), 175-81. Retrieved from: www.ajpm-online.net/article/S0749-3797%2807%2900330-3/abstract',
        'Trangle M, Gursky J, Haight R, Hardwig J, Hinnenkamp T, Kessler D, Mack N, Myszkowski M. Institute for Clinical Systems Improvement. Adult Depression in Primary Care. Updated March 2016. https://www.icsi.org/_asset/fnhdm3/Depr.pdf',
        'U.S. Department of Health and Human Services (2014). Healthy People 2020. Washington, DC: U.S. Department of Health and Human Services. Retrieved from: http://www.healthypeople.gov/2020/topicsobjectives2020/objectiveslist.aspx?topicId=28',
        'Wilkinson J, Bass C, Diem S, Gravley A, Harvey L, Maciosek M, McKeon K, Milteer L, Owens J, Rothe P, Snellman L, Solberg L, Vincent P. Institute for Clinical Systems Improvement. Preventive Services for Children and Adolescents. Updated September 2013. https://www.icsi.org/_asset/x1mnv1/PrevServKids.pdf',
        'Zalsman G, Brent DA & Weersing VR (2006). Depressive disorders in childhood and adolescence: an overview: epidemiology, clinical manifestation and risk factors. Child Adolesc Psychiatr Clin N Am. 2006;15:827-841',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: All patients aged 12 years and older before the beginning of the
        measurement period with at least one eligible encounter during the measurement period
        """
        age = self.patient.age_at(self.timeframe.end)
        if age >= 12:
            return True
        return False

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Patients with an active diagnosis for depression or a diagnosis of bipolar
        disorder

        Exceptions: Patient Reason(s)
        Patient refuses to participate
        OR
        Medical Reason(s)
        Patient is in an urgent or emergent situation where time is of the essence and to delay
        treatment would jeopardize the patient's health status
        OR
        Situations where the patient's functional capacity or motivation to improve may impact the
        accuracy of results of standardized depression assessment tools.  For example: certain
        court appointed cases or cases of delirium
        """
        if not self.in_initial_population():
            return False

        if self.patient.conditions.find(BipolarDiagnosis | DepressionDiagnosis):
            return False

        # FIX: how do we find refusal to participate?
        # FIX: how do we look for the medical reasons listed above?

        return True

    def in_numerator(self):
        """
        Numerator: Patients screened for depression on the date of the encounter  using an age
        appropriate standardized tool AND if positive, a follow-up plan is documented on the date
        of the positive screen

        Exclusions: Not Applicable
        """
        screening = self.patient.interviews.find(AdolescentDepressionScreening |
                                                 AdultDepressionScreening).within(
                                                     self.timeframe).last()
        if not screening:
            return False

        # FIX: what's the right way to see if the screening was
        # positive, given that there are many possible screening
        # interviews?  This works but depends on this wording being
        # used for all the narratives.
        if 'positive' in screening['results'][0]['narrative'].lower():
            if not self.patient.instructions.find(FollowUpForDepressionAdolescent |
                                                  FollowUpForDepressionAdult).within(
                                                      self.timeframe):
                return False

        return True

    def compute_results(self):
        """
        Clinical recommendation: Adolescent Recommendation (12-18 years):

        'The USPSTF recommends screening for MDD in adolescents aged 12 to 18 years. Screening
        should be implemented with adequate systems in place to ensure accurate diagnosis,
        effective treatment, and appropriate follow-up (B recommendation)' (Sui, A. and USPSTF,
        2016, p. 360).

        'Clinicians and health care systems should try to consistently screen adolescents, ages
        12-18,  for major depressive disorder, but only when systems are in place to ensure
        accurate diagnosis, careful selection of treatment, and close follow-up' (ICSI, 2013, p.
        16).

        Adult Recommendation (18 years and older):

        'The USPSTF recommends screening for depression in the general adult population, including
        pregnant and postpartum women. Screening should be implemented with adequate systems in
        place to ensure accurate diagnosis, effective treatment, and appropriate follow-up (B
        recommendation)' (Sui, A. and USPSTF, 2016, p. 380).

        The Institute for Clinical Systems Improvement (ICSI) health care guideline, Adult
        Depression in Primary Care, provides the following recommendations:
        1. 'Clinicians should routinely screen all adults for depression using a standardized
        instrument.'
        2. 'Clinicians should establish and maintain follow-up with patients.'
        3. 'Clinicians should screen and monitor depression in pregnant and post-partum women.'
        (Trangle, 2016 p.p. 9 - 10)
        """
        patient = self.patient
        age = self.patient.age_at(self.timeframe.end)

        recommendations: List[Recommendation] = []
        status = 'not_applicable'
        narrative = ''

        # FIX: is looking back one year correct?  The measure doesn't
        # say how often you should screen your patients.
        screening = (self.patient.interviews
                     .find(AdolescentDepressionScreening | AdultDepressionScreening)
                     .within_one_year(self.timeframe)
                     .last())  # yapf: disable

        if not screening:
            # should get a screening
            rec = InterviewRecommendation(
                patient=patient,
                questionnaire=(AdultDepressionScreening
                               if age >= 18 else AdultDepressionScreening))
            recommendations.append(rec)

            status = 'due'
            narrative = rec.narrative
            return {'status': status, 'narrative': narrative, 'recommendations': recommendations}

        # if they got the screening and they're negative we're done
        if 'positive' not in screening['results'][0]['narrative'].lower():
            status = 'current'
            narrative = f'{patient.first_name} was screened for depression with negative results.'
            return {'status': status, 'narrative': narrative, 'recommendations': recommendations}

        # they're screened and positive -- if they've gotten treatment then we're done
        if self.patient.instructions.find(FollowUpForDepressionAdolescent |
                                          FollowUpForDepressionAdult).after(
                                              arrow.get(screening['created'])):
            status = 'current'
            narrative = f'{patient.first_name} was screened for depression with positive results and a followup '\
                         'is documented.'
            return {'status': status, 'narrative': narrative, 'recommendations': recommendations}

        # recommend a followup
        recommendations.append(
            InstructionRecommendation(
                patient=patient,
                instruction=(FollowUpForDepressionAdult
                             if age >= 18 else FollowUpForDepressionAdolescent)))
        status = 'due'
        narrative = f'{patient.first_name} was screened for depression with positive results, a followup is recommended.'

        return {'status': status, 'narrative': narrative, 'recommendations': recommendations}
