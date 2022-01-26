from typing import List

from canvas_workflow_kit import events
from canvas_workflow_kit.protocol import ClinicalQualityMeasure
from canvas_workflow_kit.recommendation import Recommendation

# flake8: noqa
from canvas_workflow_kit.value_set.v2018 import (
    ConsultantReport, Ethnicity, FaceToFaceInteraction, OfficeVisit, OncAdministrativeSex,
    OphthalmologicalServices, Payer, PreventiveCareEstablishedOfficeVisit0To17,
    PreventiveCareInitialOfficeVisit0To17, PreventiveCareServicesEstablishedOfficeVisit18AndUp,
    PreventiveCareServicesInitialOfficeVisit18AndUp, Race, Referral)


class ClinicalQualityMeasure50v6(ClinicalQualityMeasure):
    """
    Closing the Referral Loop: Receipt of Specialist Report

    Description: Percentage of patients with referrals, regardless of age, for which the referring
    provider receives a report from the provider to whom the patient was referred

    Definition: Referral: A request from one physician or other eligible provider to another
    practitioner for evaluation, treatment, or co-management of a patient's condition. This term
    encompasses referral and consultation as defined by Centers for Medicare and Medicaid Services.

    Rationale: Problems in the outpatient referral and consultation process have been documented,
    including lack of timeliness of information and inadequate provision of information between the
    specialist and the requesting physician (Gandhi, 2000; Forrest, 2000; Stille, 2005). In a study
    of physician satisfaction with the outpatient referral process, Gandhi et al. (2000) found that
    68% of specialists reported receiving no information from the primary care provider prior to
    referral visits, and 25% of primary care providers had still not received any information from
    specialists 4 weeks after referral visits. In another study of 963 referrals (Forrest, 2000),
    pediatricians scheduled appointments with specialists for only 39% and sent patient information
    to the specialists in only 51% of the time.

    In a 2006 report to Congress, MedPAC found that care coordination programs improved quality of
    care for patients, reduced hospitalizations, and improved adherence to evidence-based care
    guidelines, especially among patients with diabetes and CHD. Associations with cost-savings
    were less clear; this was attributed to how well the intervention group was chosen and defined,
    as well as the intervention put in place. Additionally, cost-savings were usually calculated in
    the short-term, while some argue that the greatest cost-savings accrue over time (MedPAC,
    2006).

    Improved mechanisms for information exchange could facilitate communication between providers,
    whether for time-limited referrals or consultations, on-going co-management, or during care
    transitions. For example, a study by Branger et al. (1999) found that an electronic
    communication network that linked the computer-based patient records of physicians who had
    shared care of patients with diabetes significantly increased frequency of communications
    between physicians and availability of important clinical data. There was a 3-fold increase in
    the likelihood that the specialist provided written communication of results if the primary
    care physician scheduled appointments and sent patient information to the specialist (Forrest,
    2000).

    Care coordination is a focal point in the current health care reform and our nation's
    ambulatory health information technology (HIT) framework. The National Priorities Partnership
    recently highlighted care coordination as one of the most critical areas for development of
    quality measurement and improvement (NPP, 2008).

    Guidance: The provider who refers the patient to another provider is the provider who should be
    held accountable for the performance of this measure.

    The provider to whom the patient was referred should be the same provider that sends the
    report.

    If there are multiple referrals for a patient during the measurement period, use the first
    referral.

    The consultant report that will fulfill the referral should be completed after the referral,
    and should be related to the referral for which it is attributed. If there are multiple
    consultant reports received by the referring provider which pertain to a particular referral,
    use the first consultant report to satisfy the measure. Eligible professionals or eligible
    clinicians reporting on this measure should note that all data for the reporting year is to be
    submitted by the deadline established by CMS. Therefore, eligible professionals or eligible
    clinicians who see patients towards the end of the reporting period (ie, December in
    particular), should communicate the consultant report as soon as possible in order for those
    patients to be counted in the measure numerator. Communicating the report as soon as possible
    will ensure the data is included in the submission to CMS.

    More information: https://ecqi.healthit.gov/ecqm/measures/cms50v6
    """

    responds_to_event_types = [
        events.HEALTH_MAINTENANCE,
    ]

    authors = [
        'National Committee for Quality Assurance',
    ]

    references = [
        'Branger, P. J., Van\'t Hooft, A., Van Der Wouden, J. C., Moorman, P. W., and Van Bemmel, J. H. (1999). Shared care for diabetes: supporting communication between primary and secondary care. International Journal of Medical Informatics 53(2-3), 133-142.',
        'Forrest, C. B., Glade, G. B., Baker, A. E., Bocian, A., Von Schrader, S., and Starfield, B. (2000). Coordination of specialty referrals and physician satisfaction with referral care. Archives of Pediatrics and Adolescent Medicine 154(5), 499-506.',
        'Gandhi, T. K., Sittig, D. F., Franklin, M., Sussman, A. J., Fairchild, D. G., and Bates, D. W. (2000). Communication breakdown in the outpatient referral process. Journal of General Internal Medicine 15(9), 626-631.',
        'Medicare Payment Advisory Commission (MedPAC) Report to the Congress: Medicare Payment Policy.March, 2006. Retrieved February 22, 2017, from http://medpac.gov/docs/default-source/reports/Mar06_EntireReport.pdf?sfvrsn=0',
        'National Priorities Partnership. National Priorities and Goals: Aligning Our Efforts to Transform America\'s Healthcare. Washington, DC: National Quality Forum; 2008.',
        'Stille, C. J., Jerant, A., Bell, D., Meltzer, D., and Elmore, J. G. (2005). Coordinating care across diseases, settings, and clinicians: a key role for the generalist in practice. Annals of Internal Medicine 142(8), 700-708.',
    ]

    funding_source = ''

    def in_initial_population(self):
        """
        Initial population: Number of patients, regardless of age, who were referred by one
        provider to another provider, and who had a visit during the measurement period
        """
        if self.patient.referrals.within_one_year(self.timeframe):
            return True

    def in_denominator(self):
        """
        Denominator: Equals Initial Population

        Exclusions: None

        Exceptions: None
        """
        return self.in_initial_population()

    def in_numerator(self):
        """
        Numerator: Number of patients with a referral, for which the referring provider received a
        report from the provider to whom the patient was referred

        Exclusions: Not Applicable
        """
        # FIX: how do we find reports and match them back to referrals?

        return False

    def compute_results(self):
        """
        Clinical recommendation: None
        """
        # FIX: how do we find reports and match them back to referrals?

        recommendations: List[Recommendation] = []
        status = 'not_applicable'
        narrative = ''

        return {'status': status, 'narrative': narrative, 'recommendations': recommendations}
