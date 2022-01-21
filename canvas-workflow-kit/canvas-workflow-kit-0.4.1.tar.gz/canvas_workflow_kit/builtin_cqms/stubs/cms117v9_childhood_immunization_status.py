from protocols import events
from protocols.protocol import ClinicalQualityMeasure
from protocols.value_set.v2021 import (
    AnaphylacticReactionToCommonBakersYeast, AnaphylacticReactionToDtapVaccine,
    AnaphylacticReactionToHepatitisAVaccine, AntiHepatitisAIggAntigenTest,
    AntiHepatitisBVirusSurfaceAb, DisordersOfTheImmuneSystem, DtapVaccine,
    EncephalopathyDueToChildhoodVaccination, EncounterInpatient, Ethnicity, HepatitisA,
    HepatitisAVaccine, HepatitisB, HepatitisBVaccine, HibVaccine3DoseSchedule,
    HibVaccine4DoseSchedule, Hiv, HomeHealthcareServices, HospiceCareAmbulatory,
    InactivatedPolioVaccineIpv, InfluenzaVaccine, Intussusception,
    MalignantNeoplasmOfLymphaticAndHematopoieticTissue, Measles,
    MeaslesAntibodyTestIggAntibodyPresence, MeaslesAntibodyTestIggAntibodyTiter,
    MeaslesMumpsAndRubellaMmrVaccine, Mumps, MumpsAntibodyTestIggAntibodyPresence,
    MumpsAntibodyTestIggAntibodyTiter, OfficeVisit, OncAdministrativeSex, Payer,
    PneumococcalConjugateVaccine, PreventiveCareEstablishedOfficeVisit0To17,
    PreventiveCareServicesInitialOfficeVisit0To17, Race, RotavirusVaccine3DoseSchedule, Rubella,
    RubellaAntibodyTestIggAntibodyPresence, RubellaAntibodyTestIggAntibodyTiter,
    SevereCombinedImmunodeficiency, VaricellaZoster,
    VaricellaZosterAntibodyTestIggAntibodyPresence, VaricellaZosterAntibodyTestIggAntibodyTiter,
    VaricellaZosterVaccineVzv)


class ClinicalQualityMeasure117v9(ClinicalQualityMeasure):
    """
    Childhood Immunization Status

    Description: Percentage of children 2 years of age who had four diphtheria, tetanus and
    acellular pertussis (DTaP); three polio (IPV), one measles, mumps and rubella (MMR); three or
    four H influenza type B (Hib); three hepatitis B (Hep B); one chicken pox (VZV); four
    pneumococcal conjugate (PCV); one hepatitis A (Hep A); two or three rotavirus (RV); and two
    influenza (flu) vaccines by their second birthday

    Definition: Recommended vaccines: Vaccines and the schedule of vaccines as recommended by the
    Advisory Committee on Immunization Practices (ACIP) for children two years of age. The measure
    may differ slightly from the ACIP recommendations because the measure focuses on immunizations
    that are appropriate by age 2. Also, there may be small differences when there are shortages
    for a particular vaccine.

    Rationale: Infants and toddlers are particularly vulnerable to infectious diseases because
    their immune systems have not built up the necessary defenses to fight infection (Centers for
    Disease Control and Prevention (CDC, 2019). Most childhood vaccines are between 90 and 99
    percent effective in preventing diseases (American Academy of Pediatrics, 2013). Vaccination of
    each U.S. birth cohort with the current childhood immunization schedule prevents approximately
    42,000 deaths and 20 million cases of disease and saves nearly $14 billion in direct costs and
    $69 billion in societal costs each year (Zhou et al., 2014).

    Immunizing a child not only protects that child's health but also the health of the community,
    especially for those who are not immunized or are unable to be immunized due to other health
    complications (Centers for Disease Control and Prevention, 2018).

    Guidance: For the MMR, hepatitis B, VZV and hepatitis A vaccines, numerator inclusion criteria
    include: evidence of receipt of the recommended vaccine; documented history of the illness; or,
    a seropositive test result for the antigen. For the DTaP, IPV, Hib, pneumococcal, rotavirus,
    and influenza vaccines, numerator inclusion criteria include only evidence of receipt of the
    recommended vaccine.

    Patients may be included in the numerator for a particular antigen if they had an anaphylactic
    reaction to the vaccine. Patients may be included in the numerator for the DTaP vaccine if they
    have encephalopathy. Patients may be included in the numerator for the IPV vaccine if they have
    had an anaphylactic reaction to streptomycin, polymyxin B, or neomycin. Patients may be
    included in the numerator for the influenza, MMR, or varicella vaccines if they have cancer of
    lymphoreticular or histiocytic tissue, multiple myeloma, leukemia, have had an anaphylactic
    reaction to neomycin, have immunodeficiency, or have HIV. Patients may be included in the
    numerator for the hepatitis B vaccine if they have had an anaphylactic reaction to common
    baker's yeast.

    The measure allows a grace period by measuring compliance with these recommendations between
    birth and age two.

    This eCQM is a patient-based measure.

    This version of the eCQM uses QDM version 5.5. Please refer to the eCQI resource center
    (https://ecqi.healthit.gov/qdm) for more information on the QDM.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms117v9
    """

    title = 'Childhood Immunization Status'

    identifiers = ['CMS117v9']

    types = ['CQM']

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'Centers for Disease Control and Prevention (CDC). (2019). Common Questions About Vaccines. Retrieved October 17, 2019, from https://www.cdc.gov/vaccines/parents/FAQs.html',
        'American Academy of Pediatrics. (2013). Why Immunize Your Child. Retrieved October 17, 2019, from HealthyChildren.org website: http://www.healthychildren.org/english/safety-prevention/immunizations/Pages/Why-Immunize-Your-Child.aspx',
        'Zhou, F., Shefer, A., Wenger, J., Messonnier, M., Wang, L. Y., Lopez, A., … Rodewald, L. (2014). Economic evaluation of the routine childhood immunization program in the United States, 2009. Pediatrics, 133(4), 577–585. https://doi.org/10.1542/peds.2013-0698',
        'Centers for Disease Control and Prevention. (2019). Recommended Child and Adolescent Immunization Schedule for ages 18 years or younger. Retrieved October 22, 2019, from https://www.cdc.gov/vaccines/schedules/downloads/child/0-18yrs-child-combined-schedule.pdf',
        'Centers for Disease Control and Prevention. (2018). Why Are Childhood Vaccines So Important? Retrieved October 23, 2019, from https://www.cdc.gov/vaccines/vac-gen/howvpd.htm',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Children who turn 2 years of age during the measurement period and who
        have a visit during the measurement period
        """
        pass

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: Exclude patients whose hospice care overlaps the measurement period

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Children who have evidence showing they received recommended vaccines, had
        documented history of the illness, had a seropositive test result, or had an allergic
        reaction to the vaccine by their second birthday

        Exclusions: Not Applicable
        """
        pass


    def compute_results(self):
        """
        Clinical recommendation: Recommended Child and Adolescent Immunization Schedule
        for ages 18 years or younger, United States 2019 (Centers for Disease Control and
        Prevention, 2019)

        Hepatitis B (HepB)
        "(minimum age: birth)
        Birth dose (monovalent HepB vaccine only)
        -- Mother is HBsAg-negative: 1 dose within 24 hours of birth for all medically stable
        infants ?2,000 grams. Infants <2,000 grams: administer 1 dose at chronological age 1 month
        or hospital discharge.
        -- Mother is HBsAg-positive:
        - Administer HepB vaccine and 0.5 mL of hepatitis B immune globulin (HBIG) (at separate
        anatomic sites) within 12 hours of birth, regardless of birth weight. For infants <2,000
        grams, administer 3 additional doses of vaccine (total of 4 doses) beginning at age 1
        month.
        - Test for HBsAg and anti-HBs at age 9–12 months. If HepB series is delayed, test 1–2
        months after final dose.
        -- Mother’s HBsAg status is unknown:
        - Administer HepB vaccine within 12 hours of birth, regardless of birth weight.
        - For infants <2,000 grams, administer 0.5 mL of HBIG in addition to HepB vaccine within 12
        hours of birth. Administer 3 additional doses of vaccine (total of 4 doses) beginning at
        age 1 month.
        - Determine mother’s HBsAg status as soon as possible. If mother is HBsAg-positive,
        administer 0.5 mL of HBIG to infants ?2,000 grams as soon as possible, but no later than 7
        days of age.
        Routine series
        -- 3-dose series at 0, 1–2, 6–18 months (use monovalent HepB
        vaccine for doses administered before age 6 weeks)
        -- Infants who did not receive a birth dose should begin the
        series as soon as feasible (see Table 2).
        -- Administration of 4 doses is permitted when a combination
        vaccine containing HepB is used after the birth dose.
        -- Minimum age for the final (3rd or 4th ) dose: 24 weeks
        -- Minimum intervals: dose 1 to dose 2: 4 weeks / dose 2 to
        dose 3: 8 weeks / dose 1 to dose 3: 16 weeks (when 4 doses
        are administered, substitute "dose 4" for "dose 3" in these
        calculations) "

        Diphtheria, tetanus, acellular pertussis vaccinations (DTap)
        "(minimum age: 6 weeks [4 years for Kinrix or Quadracel])
        Routine vaccination
        -- 5-dose series at 2, 4, 6, 15–18 months, 4–6 years
        - Prospectively: Dose 4 may be given as early as age 12 months if at least 6 months have
        elapsed since dose 3.
        - Retrospectively: A 4th dose that was inadvertently given as early as 12 months may be
        counted if at least 4 months have elapsed since dose 3."

        Haemophilus influenzae type b (Hib)
        "(minimum age: 6 weeks)
        Routine vaccination
        -- ActHIB, Hiberix, or Pentacel: 4-dose series at 2, 4, 6, 12–15 months
        -- PedvaxHIB: 3-dose series at 2, 4, 12–15 months"

        Poliovirus (inactivated) (IPV)
        " (minimum age: 6 weeks)
        Routine vaccination
        -- 4-dose series at ages 2, 4, 6–18 months, 4–6 years; administer the final dose on or
        after the 4th birthday and at least 6 months after the previous dose.
        -- 4 or more doses of IPV can be administered before the 4th birthday when a combination
        vaccine containing IPV is used. However, a dose is still recommended after the 4th birthday
        and at least 6 months after the previous dose."

        Measles, mumps, and rubella (MMR)
        "(minimum age: 12 months for routine vaccination)
        Routine vaccination
        -- 2-dose series at 12–15 months, 4–6 years
         Dose 2 may be administered as early as 4 weeks after dose 1"

        Pneumococcal
        "(minimum age: 6 weeks [PCV13], 2 years [PPSV23])
        Routine vaccination with PCV13
        -- 4-dose series at 2, 4, 6, 12–15 months"

        Varicella (VAR)
        "(minimum age: 12 months)
        Routine vaccination
        -- 2-dose series: 12–15 months, 4–6 years
        -- Dose 2 may be administered as early as 3 months after dose 1 (a dose administered after
        a 4-week interval may be counted)."

        Hepatitis A (HepA)
        "(minimum age: 12 months for routine vaccination)
        Routine vaccination
        -- 2-dose series (Havrix 6–12 months apart or Vaqta 6–18 months apart, minimum interval 6
        months); a series begun before the 2nd birthday should be completed even if the child turns
        2 before the second dose is administered."

        Rotavirus (RV)
        "(minimum age: 6 weeks)
        Routine vaccination
        -- Rotarix: 2-dose series at 2 and 4 months.
        -- RotaTeq: 3-dose series at 2, 4, and 6 months.
        If any dose in the series is either RotaTeq or unknown, default
        to 3-dose series."

        Influenza (inactivated)  influenza vaccine (IIV)
        "(minimum age: 6 months [IIV], 2 years [LAIV  ], 18 years [RIV])
        Routine vaccination
        -- 1 dose any influenza vaccine appropriate for age and health status annually (2 doses
        separated by at least 4 weeks for children 6 months–8 years who did not receive at least 2
        doses of influenza vaccine before July 1, 2018)"
        """
        pass
