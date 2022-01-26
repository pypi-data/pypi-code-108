import re

from typing import Dict, List

import arrow
from datetime import datetime

from canvas_workflow_kit.timeframe import Timeframe


def get_by_path(dic, keys):
    """Access a nested object in root by item sequence."""
    for key in keys:
        dic = dic.get(key, None)
        if dic is None:
            break
    return dic


URL_CPT = 'http://www.ama-assn.org/go/cpt'
URL_HCPCS = 'https://coder.aapc.com/hcpcs-codes'
URL_CVX = 'http://hl7.org/fhir/sid/cvx'
URL_LOINC = 'http://loinc.org'
URL_SNOMED = 'http://snomed.info/sct'
URL_FDB = 'http://www.fdbhealth.com/'
URL_RXNORM = 'http://www.nlm.nih.gov/research/umls/rxnorm'
URL_ICD10 = 'ICD-10'
URL_NUCC = 'http://www.nucc.org/'
URL_CANVAS = 'CANVAS'
URL_INTERNAL = 'INTERNAL'

CODE_SYSTEM_MAPPING = {
    'cpt': URL_CPT,
    'hcpcs': URL_HCPCS,
    'cvx': URL_CVX,
    'loinc': URL_LOINC,
    'snomedct': URL_SNOMED,
    'fdb': URL_FDB,
    'rxnorm': URL_RXNORM,
    'icd10cm': URL_ICD10,
    'icd10pcs': URL_ICD10,
    'nucc': URL_NUCC,
    'canvas': URL_CANVAS,
    'internal': URL_INTERNAL,
}

SYSTEM_CODE_MAPPING = {
    URL_CPT: ['cpt', 'hcpcs'],
    URL_CVX: ['cvx'],
    URL_LOINC: ['loinc'],
    URL_SNOMED: ['snomedct'],
    URL_FDB: ['fdb'],
    URL_RXNORM: ['rxnorm'],
    URL_ICD10: ['icd10cm', 'icd10pcs'],
    URL_NUCC: ['nucc'],
    URL_CANVAS: ['canvas'],
    URL_INTERNAL: ['internal'],
}


class PatientRecordSet:
    """
    Base class representing sorted sets of records (conditions, immunizations,
    etc) for a patient.  You can iterate through them and get at the
    record data:

        for condition in patient.conditions:
            print(f'Sorry, you have {condition['name']}')

    To filter on objects use filters:
        patient.referrals.filter(order=None)  # find referrals where `"order": null`
        patient.referrals.filter(timestamp__lt=arrow.now())

    Filters can use any of the following appended to the property name:
        exact, iexact, contains, icontains,
        gt, gte, lt, lte,
        startswith, endswith, istartswith, iendswith

    If not specified, exact will be used by default.

    To filter on a nested objects, use double underscore.
        patient.referral.filter(report__status='NEW')

    You can find records by value set:

        patient.conditions.find(Diabetes)

    Filter by date in various ways:

        patient.conditions.within(timeframe)
        patient.conditions.before(now)
        patient.conditions.after(yesterday)

    Methods are chainable:

        patient.conditions.find(Diabetes).within(timeframe)

    Except these, which pick the last record and extract a value from it:

        patient.conditions.find(Diabetes).within(timeframe).last()
        patient.lab_reports.find(Hba1CLaboratoryTest).within(timeframe).last_value()

    """
    API_KEY_FIELD = 'patient__key'
    API_UPDATE_FIELD = None
    VALID_SYSTEMS = None
    DATE_FIELD = 'date'

    operators = {
        'exact': lambda x, y: x == y,
        'iexact': lambda x, y: x.lower() == y.lower(),
        'contains': lambda x, y: x in y,
        'icontains': lambda x, y: x.lower() in y.lower(),
        'gt': lambda x, y: x > y,
        'gte': lambda x, y: x >= y,
        'lt': lambda x, y: x < y,
        'lte': lambda x, y: x <= y,
        'startswith': lambda x, y: False if not isinstance(x, str) else x.startswith(y),
        'endswith': lambda x, y: False if not isinstance(x, str) else x.endswith(y),
        'istartswith': lambda x, y: False if not isinstance(x, str) else x.lower().startswith(y.lower()),
        'iendswith': lambda x, y: False if not isinstance(x, str) else x.lower().endswith(y.lower()),
    }

    def __init__(self, records):
        self.records = records

    def __str__(self):
        return f'<{self.__class__.__name__}: {len(self.records)} records>'

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return self.records.__iter__()

    def __getitem__(self, index):
        return self.records[index]

    def __bool__(self):
        return True if self.records else False

    def __len__(self):
        return len(self.records)

    def __add__(self, other):
        if self.__class__ != other.__class__:
            raise Exception(f'Illegal attempt to add a {self.__class__} and a {other.__class__}.')

        return self.__class__(self.records + other.records)

    @classmethod
    def new_from(cls, records: List[Dict]):
        return cls(records)

    @staticmethod
    def item_to_codes(item) -> List:
        """
        Internal method used to find the codes in a given record
        object, should be overriden by sub-classes as needed.
        """
        if 'code' in item:
            return item['code']['coding']

        if 'coding' in item:
            return item['coding']

        return []

    def validated(self):
        """
        Filter records that have been committed, not deleted or enter by error.
        Returns a PatientRecordSet object of the same sub-class, enabling chaining of calls.
        """
        items = []
        for item in self.records:
            if item.get('deleted'):
                continue

            if item.get('entered_in_error') or item.get('enteredInError'):
                continue

            if not item.get('committer'):
                continue

            items.append(item)

        return self.__class__(items)

    def _enumerate_system_list_codes(self, value_set):
        # not all patient record data has codes, ex: referrals
        if not self.VALID_SYSTEMS:
            raise Exception('Invalid call to find() on non-coded patient data.')

        values = value_set.values
        systems = [key for key in values.keys() if key in self.VALID_SYSTEMS]

        for item in self.records:
            for coding in self.item_to_codes(item):
                coding_systems = [
                    sys for sys in SYSTEM_CODE_MAPPING.get(coding['system'], []) if sys in systems
                ]

                for coding_system in coding_systems:
                    yield item, coding, values[coding_system]

    def _parse_shorthand_filter(self, key):
        tokens = key.split("__")

        operator_name = 'exact'
        operator_method = self.operators['exact']
        if tokens[-1] in self.operators:
            operator_name = tokens.pop()
            operator_method = self.operators.get(operator_name)

        def left_side(item):
            left_side_value = get_by_path(item, tokens)
            return left_side_value

        def filter_fn(x, y):
            left_val = left_side(x)

            # Modify types so they cna be compared
            # TODO: do date conversion in the record object itself
            if isinstance(y, (arrow.Arrow, datetime)) and isinstance(left_val, str):
                left_val = arrow.get(left_val)

            elif isinstance(y, (arrow.Arrow, datetime)) and left_val is None:
                return False

            return operator_method(left_val, y)
        return filter_fn

    def filter(self, **kwargs):
        """
        Filter a queryset.
        To filter on a nested objects, use double underscore.
          Ex: .filter(report__status='NEW')
        Django operators can also be used.
          Ex: .filter(report__status__istartswith='ne', report__status__icontains='w')
        """
        queryset = self.__class__(self.records)

        for kwarg_key, value in kwargs.items():
            filter_fn = self._parse_shorthand_filter(kwarg_key)
            queryset.records = [
                item for item in queryset if filter_fn(item, value)
            ]
        return queryset

    def exclude(self, **kwargs):
        """
        Exclude values in a queryset using the same method as filter()
        """

        queryset = self.__class__(self.records)

        for kwarg_key, value in kwargs.items():
            filter_fn = self._parse_shorthand_filter(kwarg_key)
            queryset.records = [
                item for item in queryset if not filter_fn(item, value)
            ]
        return queryset

    def find(self, value_set):
        """
        Find records that match a given value_set based on exact code. Returns a
        PatientRecordSet object of the same sub-class, enabling chaining
        of calls.
        """
        items = []
        for item, coding, list_codes in self._enumerate_system_list_codes(value_set):
            if coding['code'] in list_codes:
                items.append(item)

        return self.__class__(items)

    def find_class(self, value_set):
        """
        Find records that match a given value_set based on regular expression. Returns a
        PatientRecordSet object of the same sub-class, enabling chaining
        of calls.
        """
        items = []
        for item, coding, list_codes in self._enumerate_system_list_codes(value_set):
            for code_re in list_codes:
                if re.search(code_re, coding['code']):
                    items.append(item)
                    break

        return self.__class__(items)


class PatientEventRecordSet(PatientRecordSet):

    def __init__(self, records):
        super().__init__(records)
        # filter out records with no date attached - they're useless
        # for protocols since everything is constrained by timeframe
        records = [r for r in records if r[self.DATE_FIELD] is not None]
        self.records = sorted(records, key=lambda rec: rec[self.DATE_FIELD])

    def filter_function(self, filter_fn):
        """
        Filter records by date, pass in a function and it will be
        applied to each date.  Returns a PatientRecordSet object of the
        same sub-class, enabling chaining of calls.
        """
        return self.__class__([
            item for item in self.records
            if item[self.DATE_FIELD] and filter_fn(arrow.get(item[self.DATE_FIELD]))
        ])

    def within(self, timeframe: Timeframe):
        """
        Find records within a timeframe.  Returns a PatientRecordSet
        object of the same sub-class, enabling chaining of calls.
        """

        def filter_fn(onset) -> bool:
            return timeframe.start <= onset <= timeframe.end

        return self.filter_function(filter_fn)

    def before(self, end: arrow):
        """
        Find records before an arrow datetime.  Returns a
        PatientRecordSet object of the same sub-class, enabling chaining
        of calls.
        """
        return self.filter_function(lambda onset: onset <= end)

    def after(self, start: arrow):
        """
        Find records after an arrow datetime.  Returns a
        PatientRecordSet object of the same sub-class, enabling chaining
        of calls.
        """
        return self.filter_function(lambda onset: onset >= start)

    # TODO_REPORTING the "Measurement Period" is defined as the period from
    # Jan 1st to Dec 31st of a specified year
    def within_one_year(self, timeframe: Timeframe):
        """
        Find records within the year before the timeframe end. Returns a
        PatientRecordSet object of the same sub-class, enabling chaining
        of calls.
        """
        return self.within(Timeframe(start=timeframe.end.shift(years=-1), end=timeframe.end))

    # TODO_REPORTING the "Measurement Period" is defined as the period from
    # Jan 1st to Dec 31st of a specified year
    def within_two_years(self, timeframe: Timeframe):
        """
        Find records within the 2 years before the timeframe end. Returns a
        PatientRecordSet object of the same sub-class, enabling chaining
        of calls.
        """
        return self.within(Timeframe(start=timeframe.end.shift(years=-2), end=timeframe.end))

    def first(self):
        """
        Returns the first (less recent) record.
        """
        if self.records:
            return self.records[0]
        return None

    def last(self):
        """
        Returns the last (most recent) record.
        """
        if self.records:
            return self.records[-1]
        return None

    def last_value(self, cast=None):
        """
        Returns the last (most recent) record.
        """
        record = self.last()

        if record is None:
            return None

        if cast:
            try:
                return cast(record['value'])
            except (ValueError, TypeError):
                return None
        else:
            return record['value']


class PatientPeriodRecordSet(PatientRecordSet):

    def __init__(self, records):
        super().__init__(records)
        self.records = [r for r in records if len(r['periods']) > 0]

    def intersects(self, timeframe: Timeframe, still_active: bool):
        """
        Search all records with a period overlapping with the provided period
        Returns a PatientRecordSet object of the same sub-class, enabling chaining of calls.

        still_active is used in regard of the end date of the record (period['to']) when
        it is known (i.e. not None)
        The record is validating the criteria
         - when still_active==False, this means that the record is active during the period
         - when still_active==True , this means that the record is still active after the
         end of the period
        """
        result = []
        for item in self.records:
            for period in item['periods']:
                if (arrow.get(period['from']) <= timeframe.end and
                        (period['to'] is None or
                         ((not still_active and
                           timeframe.start <= arrow.get(period['to'])) or
                          (still_active and
                           timeframe.end <= arrow.get(period['to']))))):  # yapf: disable
                    result.append(item)
                    break

        return self.__class__(result)

    def starts_before(self, on_date: arrow):
        """
        Search all records with a still active period starting before the end of
        the provided period
        Returns a PatientRecordSet object of the same sub-class, enabling chaining of calls.
        """
        result = []
        for item in self.records:
            for period in item['periods']:
                if arrow.get(period['from']) <= on_date and period['to'] is None:
                    result.append(item)

        return self.__class__(result)


class BillingLineItemRecordSet(PatientEventRecordSet):
    VALID_SYSTEMS = ['cpt', 'hcpcs']
    DATE_FIELD = 'created'
    PATIENT_FIELD = 'billing_line_items'
    API_UPDATE_FIELD = 'billingLineItems'

    @staticmethod
    def item_to_codes(item) -> List:
        return [{'code': item['cpt'], 'system': URL_CPT}]


class ConditionRecordSet(PatientPeriodRecordSet):
    VALID_SYSTEMS = ['icd10cm', 'icd10pcs', 'snomedct']
    PATIENT_FIELD = 'conditions'
    API_UPDATE_FIELD = 'conditions'

    @staticmethod
    def item_to_codes(item) -> List:
        if item['clinicalStatus'] in ['active', 'resolved']:
            return item['coding']
        return []


class ImmunizationRecordSet(PatientEventRecordSet):
    VALID_SYSTEMS = ['cvx']
    DATE_FIELD = 'dateOrdered'
    PATIENT_FIELD = 'immunizations'
    API_UPDATE_FIELD = 'immunizations'

    @staticmethod
    def item_to_codes(item) -> List:
        return item['coding']


class VitalSignRecordSet(PatientEventRecordSet):
    VALID_SYSTEMS = ['loinc']
    DATE_FIELD = 'dateRecorded'
    PATIENT_FIELD = 'vital_signs'
    API_KEY_FIELD = 'reading__patient__key'
    API_UPDATE_FIELD = 'vitalSigns'

    @staticmethod
    def item_to_codes(item) -> List:
        return [{'code': item['loincNum'], 'system': URL_LOINC}]


class LabReportRecordSet(PatientEventRecordSet):
    VALID_SYSTEMS = ['loinc']
    DATE_FIELD = 'originalDate'
    PATIENT_FIELD = 'lab_reports'
    API_UPDATE_FIELD = 'labReports'

    @staticmethod
    def item_to_codes(item) -> List:
        codes = []
        for code in item['loincCodes']:
            codes.append({'system': URL_LOINC, **code})
        return codes

    @classmethod
    def new_from(cls, data: Dict):
        # lab reports come in a slightly weird structure - the records we
        # care about are the lab values but the date we need to filter on
        # is in the outer lab-report structure.  To use the
        # PatientRecordSet code we need to collapse them so we have a date
        # stamp and a set of codes in a single record hash.
        combined = []
        for report in data:
            for value in report['values']:
                combined.append({'originalDate': report['originalDate'], **value})

        return cls(combined)


class InstructionRecordSet(PatientEventRecordSet):
    VALID_SYSTEMS = ['icd10cm', 'icd10pcs', 'snomedct', 'cpt', 'hcpcs']
    DATE_FIELD = 'noteTimestamp'
    PATIENT_FIELD = 'instructions'
    API_UPDATE_FIELD = 'instructions'


class MedicationRecordSet(PatientPeriodRecordSet):
    VALID_SYSTEMS = [
        'rxnorm',
        'fdb',
    ]
    PATIENT_FIELD = 'medications'
    API_UPDATE_FIELD = 'medications'

    @staticmethod
    def item_to_codes(item) -> List:
        return item['coding']


class InterviewRecordSet(PatientEventRecordSet):
    VALID_SYSTEMS = ['loinc', 'snomedct', 'rxnorm', 'canvas', 'internal']
    DATE_FIELD = 'noteTimestamp'
    PATIENT_FIELD = 'interviews'
    API_UPDATE_FIELD = 'interviews'

    @staticmethod
    def item_to_codes(item) -> List:
        codes = []

        for result in item['results']:
            if result['code'] != '' and result['codeSystem'] != '':
                codes.append({
                    'code': result['code'],
                    'system': result['codeSystem'],
                    'question_id': None,
                })

        for coding in item.get('questionnaires', []):
            codes.append({
                'code': coding['code'],
                'system': coding['codeSystem'],
                'question_id': None,
            })
        for coding in item.get('questions', []):
            codes.append({
                'code': coding['code'],
                'system': coding['codeSystem'],
                'question_id': coding['questionResponseId'],
            })
        for coding in item.get('responses', []):
            codes.append({
                'code': coding['code'],
                'system': coding['codeSystem'],
                'question_id': coding['questionResponseId'],
            })
        # interviews.find(...)
        return codes

    def find_question_response(self, value_set_question, value_set_response):
        items = []
        questions = []

        for _, coding, list_codes in self._enumerate_system_list_codes(value_set_question):
            if coding['code'] in list_codes:
                questions.append(coding['question_id'])

        for item, coding, list_codes in self._enumerate_system_list_codes(value_set_response):
            if coding['code'] in list_codes and coding['question_id'] in questions:
                items.append(item)

        return self.__class__(items)


class ReferralReportRecordSet(PatientEventRecordSet):
    VALID_SYSTEMS: List[str] = [
        'snomedct',
        'loinc',
        'cpt',
    ]
    DATE_FIELD = 'originalDate'
    PATIENT_FIELD = 'referral_reports'
    API_UPDATE_FIELD = 'referralReports'

    @staticmethod
    def item_to_codes(item) -> List:
        codes = []

        for result in item['codings']:
            codes.append({
                'code': result['code'],
                'system': result['system'],
            })
        return codes


class ReferralRecordSet(PatientEventRecordSet):
    # TO BE DEVELOPED
    VALID_SYSTEMS: List[str] = [
        'snomedct',
        'loinc',
        'cpt',
    ]
    DATE_FIELD = 'timestamp'
    PATIENT_FIELD = 'referrals'
    API_UPDATE_FIELD = 'referrals'


class InpatientStayRecordSet(PatientEventRecordSet):
    # TO BE DEVELOPED
    VALID_SYSTEMS: List[str] = [
        'snomedct',
        'loinc',
        'cpt',
    ]
    DATE_FIELD = 'noteTimestamp'
    PATIENT_FIELD = 'inpatient_stays'
    API_UPDATE_FIELD = 'inpatientStay'


class ImagingReportRecordSet(PatientEventRecordSet):
    VALID_SYSTEMS: List[str] = [
        'snomedct',
        'loinc',
        'cpt',
    ]
    DATE_FIELD = 'originalDate'
    PATIENT_FIELD = 'imaging_reports'
    API_UPDATE_FIELD = 'imagingReports'

    @staticmethod
    def item_to_codes(item) -> List:
        codes = []

        for result in item['codings']:
            codes.append({
                'code': result['code'],
                'system': result['system'],
            })
        return codes


class ProtocolOverrideRecordSet(PatientRecordSet):
    VALID_SYSTEMS: List[str] = ['snomedct']
    PATIENT_FIELD = 'protocol_overrides'
    API_UPDATE_FIELD = 'protocolOverrides'

    def defined_for(self, protocol_keys: List[str]):
        for item in self.records:
            if item['protocolKey'] in protocol_keys:
                return item
        return None

    @property
    def all_switched_off(self) -> bool:
        for item in self.records:
            if item['protocolKey'] == '*':
                return True
        return False

    def is_snoozed(self, protocol_keys: List[str]) -> bool:

        def protocol_snoozed(item):
            if (item['protocolKey'] in protocol_keys and item['snooze'] and
                    arrow.now() < arrow.get(
                        item['snooze']['reference']).shift(days=item['snooze']['snoozedDays'])):
                return True

        return any(protocol_snoozed(override) for override in self.records)

    @staticmethod
    def item_to_codes(item) -> List:
        snooze = item.get("snooze", {})
        code = snooze.get("reasonCode")
        system = snooze.get("reasonCodeSystem")
        if code:
            return [{
                'code': code,
                'system': system,
            }]
        return []


class ReasonForVisitRecordSet(PatientEventRecordSet):
    # TO BE DEVELOPED
    VALID_SYSTEMS: List[str] = [
        'snomedct',
        'loinc',
        'cpt',
    ]
    DATE_FIELD = 'created'
    PATIENT_FIELD = 'reason_for_visits'
    API_UPDATE_FIELD = 'reasonForVisits'


class UpcomingAppointmentRecordSet(PatientRecordSet):
    VALID_SYSTEMS: List[str] = ['canvas', 'internal']
    PATIENT_FIELD = 'upcoming_appointments'
    API_UPDATE_FIELD = 'upcomingAppointments'
    DATE_FIELD = 'startTime'


class UpcomingAppointmentNoteRecordSet(PatientRecordSet):
    VALID_SYSTEMS: List[str] = ['canvas', 'internal']
    PATIENT_FIELD = 'upcoming_appointment_notes'
    API_UPDATE_FIELD = 'upcomingAppointmentNotes'


class MessageRecordSet(PatientRecordSet):
    VALID_SYSTEMS: List[str] = ['canvas', 'internal']
    PATIENT_FIELD = 'messages'
    API_UPDATE_FIELD = 'messages'


class AllergyIntoleranceRecordSet(PatientEventRecordSet):
    VALID_SYSTEMS: List[str] = ['fdb']
    PATIENT_FIELD = 'allergy_intolerances'
    API_UPDATE_FIELD = 'allergyIntolerances'
    DATE_FIELD = 'onsetDate'
