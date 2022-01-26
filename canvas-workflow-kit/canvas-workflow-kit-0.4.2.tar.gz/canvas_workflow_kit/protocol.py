"""
Influence Types and Use Case Examples

1. Sorts/Searches: Define choice set sortings under specific conditions
2. Defaults: Set order field value defaults under specific conditions
3. Recommendations: Suggest documentation, orders, analyses, and patient engagements
4. Rationales: Request or require rationales when behavior diverges from protocols
5. Tasks: Assign a task to a user

Below is a small sample of the 200+ events in charting and coordination available for subscription.

Charting Events

CHART_OPENED, CHART_QUERIED, PRESCRIPTION_ORIGINATED, PRESCRIPTION_COMMITTED, REFERRAL_ORIGINATED,
REFERRAL_COMMITTED, NOTE_LOCKED, ...

Care Coordination Events

APPOINTMENT_SCHEDULED, PATIENT_ARRIVED, PATIENT_ROOMED, REFILL_REQUEST_RECEIVED,
REFERRAL_LOOP_CLOSED, POPULATION_QUERIED, MULTIPATIENT_ACTION_ORIGINATED, ...
"""

import importlib
import pkgutil
import re

from collections import defaultdict
from typing import Dict, List, Optional, Type, TypeVar

import arrow
import requests

from cached_property import cached_property
from canvas_workflow_kit import settings

from memoization import cached
from requests.auth import HTTPDigestAuth

from . import events
from .constants import CHANGE_TYPE
from .internal.attrdict import AttrDict
from .internal.string import snakecase
from .metaclass import DeclarativeFieldsMetaclass
from .patient import Patient
from .recommendation import (
    Recommendation, LabRecommendation, PlanRecommendation,
    TaskRecommendation, ReferRecommendation, ImagingRecommendation,
    PerformRecommendation, HyperlinkRecommendation, InterviewRecommendation,
    PrescribeRecommendation, VitalSignRecommendation, InstructionRecommendation,
    ImmunizationRecommendation, StructuredAssessmentRecommendation
)
from .timeframe import Timeframe

STATUS_DUE = 'due'
STATUS_SNOOZED = 'snoozed'
STATUS_NOT_APPLICABLE = 'not_applicable'
STATUS_PENDING = 'pending'
STATUS_SATISFIED = 'satisfied'
STATUS_NOT_RELEVANT = 'not_relevant'

PROTOCOL_STATUS_CHOICES = (
    (STATUS_DUE, 'Due'),
    (STATUS_NOT_APPLICABLE, 'Not Applicable'),
    (STATUS_PENDING, 'Pending'),
    (STATUS_NOT_RELEVANT, 'Not Relevant'),
)

# regex to find source URLs in protocol reference data
PROTOCOL_SOURCE_URL_RE = re.compile(r'(?i)(.*)\s((?:https?://)?(?:\S+/\S*))\.?$')

CONTEXT_GUIDANCE = 'guidance'
CONTEXT_REPORT = 'report'

session = requests.Session()

try:
    EXTERNAL_PROTOCOLS_URL = (
        f'{settings.INTEGRATION_SERVICE_ENDPOINT}/retrieve-external-protocols/')

    session.auth = HTTPDigestAuth(settings.INTEGRATION_SERVICE_USERNAME,
                                  settings.INTEGRATION_SERVICE_PASSWORD)

    EXTERNAL_PROTOCOLS_ENABLED = all((
        settings.INTEGRATION_SERVICE_ENDPOINT,
        settings.INTEGRATION_SERVICE_USERNAME,
        settings.INTEGRATION_SERVICE_PASSWORD,
    ))
except:
    EXTERNAL_PROTOCOLS_ENABLED = False
    EXTERNAL_PROTOCOLS_URL = ''


@cached(ttl=60)
def get_external_protocols(protocol_patient):
    """
    {
        "protocols": [
            {
                "identifier" : "CMS131v7"
                "status" : "due",
                "externalNarrative" : "Claims as of Jun 11 2020 suggest this patient has ..."
            },

            ...
        ]
    }
    """
    if not EXTERNAL_PROTOCOLS_ENABLED:
        return []

    response = session.post(EXTERNAL_PROTOCOLS_URL, json=protocol_patient)
    response.raise_for_status()

    response_json = response.json()

    if 'error' in response_json:
        return []

    if 'protocols' not in response_json:
        return []

    return response_json['protocols']


RECOMMENDATION_CLASSES = (
    LabRecommendation, PlanRecommendation,
    TaskRecommendation, ReferRecommendation, ImagingRecommendation,
    PerformRecommendation, HyperlinkRecommendation, InterviewRecommendation,
    PrescribeRecommendation, VitalSignRecommendation, InstructionRecommendation,
    ImmunizationRecommendation, StructuredAssessmentRecommendation
)


def add_recommendation_factory(recommendation_class):
    """
    Generate generic add_*_recommendation methods.
    Eg: add_lab_recommendation(*args, **kwargs)
    """
    def add_recommendation_class(result, *args, **kwargs):
        recommendation = recommendation_class(*args, **kwargs)
        result.recommendations.append(recommendation)
    return add_recommendation_class


class ProtocolResult:
    recommendations: List[Recommendation]
    status: str
    narratives: List[str]
    due_in: Optional[int]
    days_of_notice: int
    next_review: arrow

    def __init__(self):
        self.recommendations = []
        self.status = STATUS_NOT_APPLICABLE
        self.narratives = []
        self.due_in = None
        self.days_of_notice = 30
        self.next_review = None

        # Create add_*_recommendation methods
        for recommendation_class in RECOMMENDATION_CLASSES:
            dynamic_class = add_recommendation_factory(recommendation_class)
            snake_case_type = snakecase(recommendation_class.__name__)
            setattr(self.__class__, f'add_{snake_case_type}', dynamic_class)

    def add_recommendation(self, *args, **kwargs):
        """
        Add a recommendation to the recommendations list.
        """
        if len(args) > 0 and isinstance(args[0], Recommendation):
            recommendation = args[0]
        else:
            recommendation = Recommendation(*args, **kwargs)

        self.recommendations.append(recommendation)

    def add_narrative(self, narrative: str):
        self.narratives.append(narrative)

    @property
    def narrative(self) -> str:
        return '\n'.join(self.narratives)


class ProtocolSource(object):

    def __init__(self, text: str, url: Optional[str] = None) -> None:
        self.text = text
        self.url = url


class Protocol(metaclass=DeclarativeFieldsMetaclass):

    class Meta:
        title: str = ''
        compute_on_change_types: List[str] = []
        responds_to_event_types: List[str] = []
        identifiers: List[str] = []
        description: str = ''
        information: str = ''
        references: List[str] = []

    def __init__(self, patient: Patient, **kwargs):
        self.patient = patient

    @property
    def identifier(self) -> str:
        identifiers = self._meta.identifiers
        if len(identifiers):
            return identifiers[0]
        return ""

    @classmethod
    def protocol_key(cls) -> str:
        """
        External key used to identify the protocol.
        """
        return cls.__name__

    @staticmethod
    def relative_float(value: str) -> float:
        try:
            sigma = 0.0
            if value[0] == '<' and value[1] != '=':
                sigma = -1e-6
            elif value[0] == '>' and value[1] != '=':
                sigma = +1e-6
            return float(value.strip('<≤=≥>')) + sigma
        except (ValueError, IndexError):
            return 0

    def sources(self) -> List[ProtocolSource]:
        """
        Returns a list of ProtocolSource objects with reference text and URLs. Not all sources have
        URLs.
        """
        sources = []

        for ref in self._meta.references:
            # look for URL at the end of the text
            match = PROTOCOL_SOURCE_URL_RE.search(ref)

            text = ref
            url = None

            if match:
                text = match.group(1)
                url = match.group(2)

            sources.append(ProtocolSource(text, url))

        return sources

    def status(self) -> str:
        raise NotImplementedError('status must be overridden')

    def snoozed(self) -> bool:
        return (self.patient.protocol_overrides.all_switched_off or
                self.patient.protocol_overrides.is_snoozed([self.protocol_key()]))

    @classmethod
    def enabled(cls) -> bool:
        """
        Protocols which return False from this method will be skipped.
        """
        return True


class ClinicalQualityMeasure(Protocol):

    # The data sources that will invalidate this CQM; e.g. if this CQM uses interviews then if a
    # patient interview is committed we will need to re-run this CQM
    #
    # Deprecated - refer to constants.CHANGE_TYPE directly
    CHANGE_ALLERGY_INTOLERANCE = CHANGE_TYPE.ALLERGY_INTOLERANCE
    CHANGE_APPOINTMENT = CHANGE_TYPE.APPOINTMENT
    CHANGE_BILLING_LINE_ITEM = CHANGE_TYPE.BILLING_LINE_ITEM
    CHANGE_CONDITION = CHANGE_TYPE.CONDITION
    CHANGE_COVERAGE = CHANGE_TYPE.COVERAGE
    CHANGE_ENCOUNTER = CHANGE_TYPE.ENCOUNTER
    CHANGE_IMAGING_REPORT = CHANGE_TYPE.IMAGING_REPORT
    CHANGE_IMMUNIZATION = CHANGE_TYPE.IMMUNIZATION
    CHANGE_INSTRUCTION = CHANGE_TYPE.INSTRUCTION
    CHANGE_INTERVIEW = CHANGE_TYPE.INTERVIEW
    CHANGE_LAB_REPORT = CHANGE_TYPE.LAB_REPORT
    CHANGE_MEDICATION = CHANGE_TYPE.MEDICATION
    CHANGE_PATIENT = CHANGE_TYPE.PATIENT
    CHANGE_PROTOCOL_OVERRIDE = CHANGE_TYPE.PROTOCOL_OVERRIDE
    CHANGE_REFERRAL_REPORT = CHANGE_TYPE.REFERRAL_REPORT
    CHANGE_SUSPECT_HCC = CHANGE_TYPE.SUSPECT_HCC
    CHANGE_VITAL_SIGN = CHANGE_TYPE.VITAL_SIGN

    class Meta:
        responds_to_event_types = [
            events.HEALTH_MAINTENANCE,
        ]

    def __init__(self,
                 change_types: List = None,
                 timeframe: Timeframe = None,
                 now: arrow.Arrow = None,
                 context: str = CONTEXT_REPORT,
                 **kwargs):
        super().__init__(**kwargs)

        self.context = context if context == CONTEXT_GUIDANCE else CONTEXT_REPORT
        self._results: Optional[ProtocolResult] = None
        self.canvas_updates = []

        if not self.impacted_by_changes(change_types):
            self._results = ProtocolResult()
            self._results.status = STATUS_NOT_RELEVANT

            return

        self.now = now if now else arrow.utcnow()  # TODO now should be local time

        if timeframe:
            self.timeframe = timeframe
        else:
            end = self.now

            if self.snooze_adjustment:
                start = self.now.shift(days=self.snooze_adjustment['snoozedDays'])
                end = start.shift(years=1)
            elif self.period_adjustment:
                cycle = self.period_adjustment['cycleDays']
                start = end.shift(days=-1 * cycle)
            else:
                start = end.shift(years=-1)  # default duration is one year

            self.timeframe = Timeframe(start=start, end=end)

    def impacted_by_changes(self, change_types: Optional[List]) -> bool:
        # TODO: See if the calling process can select and compute only the protocols
        # that match change-types, instead of instantiating in order to check.
        # Will help reduce code, and speed things up.
        if not change_types or not self._meta.compute_on_change_types:
            return True

        for change in self._meta.compute_on_change_types:
            if change in change_types:
                return True

        return False

    @cached_property
    def snooze_adjustment(self) -> Optional[Dict]:
        override = self.patient.protocol_overrides.defined_for([self.protocol_key()])
        return override['snooze'] if override else None

    @cached_property
    def period_adjustment(self) -> Optional[Dict]:
        override = self.patient.protocol_overrides.defined_for([self.protocol_key()])
        return override['adjustment'] if override else None

    def in_initial_population(self) -> bool:
        """
        Protocols must return a boolean indicating whether a patient
        is in the initial population.
        """
        raise NotImplementedError('in_initial_population must be overridden')

    def in_denominator(self) -> bool:
        """
        Protocols must return a boolean indicating whether a patient
        is in the denominator.
        """
        raise NotImplementedError('in_denominator must be overridden')

    def in_numerator(self) -> bool:
        """
        Protocols must return a boolean indicating whether a patient
        is in the numerator.
        """
        raise NotImplementedError('in_numerator must be overridden')

    def compute_results(self) -> ProtocolResult:
        """
        Protocols must implement this method which returns:

           {
             'status': status,
             'narrative': narrative,
             'recommendations': recommendations
           }

        Status must be one of PROTOCOL_STATUS_CHOICES. Narrative must be an English description of
        recommended actions. Recommendations must be an array of Recommendation sub-class objects
        (LabRecommendation, VaccineRecommendation, etc.) or an empty array.
        """
        raise NotImplementedError('compute_results must be overridden')

    def results(self) -> ProtocolResult:
        """
        Calls compute_results and caches the result.
        """
        if not self._results:
            self._results = self.compute_results()

        return self._results

    def set_context(self, context: Dict = {}) -> None:
        self.context = AttrDict(context)

    def set_updates(self, canvas_updates: List[Dict]) -> None:
        self.canvas_updates = canvas_updates

    def updates(self) -> List[Dict]:
        return self.canvas_updates

    def recommendations(self) -> List[Recommendation]:
        return self.results().recommendations

    def narrative(self) -> str:
        return self.results().narrative

    def status(self) -> str:
        return self.results().status

    def due_in(self) -> Optional[int]:
        return self.results().due_in

    def days_of_notice(self) -> int:
        return self.results().days_of_notice

    def next_review(self) -> arrow:
        next_review = self.results().next_review
        due_in = self.results().due_in
        if due_in and due_in > 0 and next_review is None:
            next_review = arrow.utcnow().shift(days=due_in)
        return next_review

    def display_date(self, day: arrow.Arrow) -> str:
        return '%s on %s' % (day.humanize(other=self.now), day.format('M/D/YY'))

    @staticmethod
    def display_period(day_from: arrow.Arrow, day_to: arrow.Arrow) -> str:
        return 'between %s and %s' % (day_from.format('M/D/YY'), day_to.format('M/D/YY'))

    def screening_interval_context(self) -> str:
        try:
            abc = self.friendly_time_duration(self._meta.default_display_interval_in_days)
        except (AttributeError, KeyError):
            return ''

        if self.period_adjustment:
            abc = self.friendly_time_duration(self.period_adjustment['cycleDays'])
        return f'Current screening interval {abc}.'

    @staticmethod
    def friendly_time_duration(duration_in_days: int) -> str:
        friendly_duration = 'invalid duration'
        if duration_in_days >= 1:
            friendly_duration = f'{duration_in_days} days'
            if duration_in_days >= 365:
                years, days = divmod(duration_in_days, 365)
                plural = 's' if years > 1 else ''
                friendly_duration = f'{years} year{plural}'
                if days >= 30:
                    months = days // 30
                    plural = 's' if months > 1 else ''
                    friendly_duration = friendly_duration + f', {months} month{plural}'
            elif duration_in_days >= 30:
                months, days = divmod(duration_in_days, 30)
                plural = 's' if months > 1 else ''
                friendly_duration = f'{months} month{plural}'
                if days > 0:
                    plural = 's' if days > 1 else ''
                    friendly_duration = friendly_duration + f', {days} day{plural}'
        return friendly_duration

    @staticmethod
    def group_question_responses(interview: Dict) -> Dict:
        result: Dict = {}
        qr_id_2_code: Dict = {}
        for question in interview['questions']:
            qr_id_2_code[question['questionResponseId']] = question['code']

        for response in interview['responses']:
            question_code = qr_id_2_code[response['questionResponseId']]
            if question_code not in result:
                result[question_code] = []
            result[question_code].append(response['code'])

        return result

    # TODO move to ClinicalQualityMeasureReport class
    # def report(self):
    #     """
    #     Report aggregate statistical information on patients who are included or excluded from
    #     this protocol's criteria.
    #     """
    #     return {}

    # for Anthem we only actually know if a patient is in both the denominator AND NOT the
    # numerator, not both separately

    def format_external_protocols(self):
        return {
            'patientData': {
                'firstName': self.patient.first_name,
                'lastName': self.patient.last_name,
                'birthDate': self.patient.date_of_birth,
                'coverages': self.patient.coverages,
            }
        }


class ExternallyAwareClinicalQualityMeasure:

    @property
    def external_protocol(self):
        if not EXTERNAL_PROTOCOLS_ENABLED:
            return {'externalNarrative': '', 'status': None}

        external_protocols = get_external_protocols(self.format_external_protocols())

        for protocol in external_protocols:
            if protocol['identifier'] == self.identifier:
                return protocol

        return {'externalNarrative': '', 'status': None}

    @property
    def external_narrative(self):
        return self.external_protocol['externalNarrative']

    def in_external_denominator(self):
        return self.external_protocol['status'] in ('due', 'satisfied')

    def in_external_numerator(self):
        return self.external_protocol['status'] == 'satisfied'

    # send soft close, since we think it is satisfied and external parties do
    # not
    def send_soft_close(self):
        # print('SOFT CLOSE: REPLACE ME WITH A CALL TO EXTERNAL PROTOCOL UPDATE ENDPOINT')
        pass

    # canvas does not think it applies, external does
    def applicable_externally_but_not_in_canvas(self):
        # for now, do nothing. In the future, if we have appropriate external
        # clinical context, try to capture the context within canvas.
        # Example: "claims suggest patient was diagnosed with xxx by xxx on
        # date xxx."
        # Options:
        # - Insert Past Medical History
        # - Request Records
        pass

    # protocol does not apply
    def craft_not_applicable_result(self):
        result = ProtocolResult()
        result.due_in = self.first_due_in()
        return result

    def compute_results(self) -> ProtocolResult:
        result: ProtocolResult

        if self.in_denominator():
            if self.in_numerator():
                result = self.craft_satisfied_result()

                if not self.in_external_numerator():
                    self.send_soft_close()
            else:
                result = self.craft_unsatisfied_result()

                if self.in_external_numerator():
                    # protocol satisfied externally, not in canvas
                    # talk to patient, request records, etc.
                    result.add_recommendation(
                        TaskRecommendation(
                            key=f'{self.identifier}_RECOMMEND_RECORDS_REQUEST',
                            button='Request Records',
                            patient=self.patient,
                            narrative=('An insurer believes this protocol has already been '
                                       'satisfied elsewhere. Request that records be retrieved to '
                                       'support this claim.'),
                            title='Request Records'))
                else:
                    # protocol unsatisfied in canvas and externally
                    # if external_narrative, use that narrative, otherwise our narrative
                    if self.external_narrative:
                        result.narratives = [self.external_narrative]
        else:
            result = self.craft_not_applicable_result()

            # if self.in_external_denominator():
            #     canvas does not think it applies, external does
            #     result = self.applicable_externally_but_not_in_canvas()

        return result


T = TypeVar('T')


def get_subclasses(cls: Type[T]) -> List[Type[T]]:
    subclasses = []

    for subclass in cls.__subclasses__():
        subclasses.append(subclass)
        subclasses.extend(get_subclasses(subclass))

    return subclasses


def get_protocols(module) -> Dict[str, List[Type[Protocol]]]:
    for _, name, _ in pkgutil.iter_modules(module.__path__):
        importlib.import_module(f'{module.__name__}.{name}')

    subclasses = get_subclasses(Protocol)
    protocols_by_event_type: Dict[str, List[Type[Protocol]]] = defaultdict(list)

    for subclass in subclasses:
        # Ignore protocol subclasses that are not under the given module.
        if not subclass.__module__.startswith(module.__name__):
            continue

        # don't add the base classes themselves
        if subclass in (Protocol, ClinicalQualityMeasure):
            continue

        if not subclass.enabled():
            continue

        for event_type in subclass._meta.responds_to_event_types:
            protocols_by_event_type[event_type].append(subclass)

    return protocols_by_event_type


def protocols_for_patient(protocols: List[Type[Protocol]],
                          patient: Patient,
                          change_types: List = None,
                          context: str = CONTEXT_REPORT) -> List[ClinicalQualityMeasure]:
    """
    Return the set of protocols for this patient+event_type where the
    protocol is active for the patient and the protocol status is something
    other than Not Applicable.
    """

    def useful_cqm(cqm: ClinicalQualityMeasure) -> bool:
        if cqm.status() == STATUS_NOT_APPLICABLE:
            return bool(cqm.due_in())
        return True

    return [
        p for p in [
            protocol(patient=patient, change_types=change_types, context=context)
            for protocol in protocols
        ] if (isinstance(p, ClinicalQualityMeasure) and useful_cqm(p))
    ]


class CodingStruct:

    def __init__(self, code=None, system=None):
        self.code = code
        self.system = system
