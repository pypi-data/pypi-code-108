from typing import List, Callable, Union, Tuple, Dict, Any, Optional
import datetime
import decimal
import itertools
import re
import inspect

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models.fields import CharField as DjangoCharField
from django.db.models.enums import Choices
from django.db.models.functions import Concat
from django.db.models.query_utils import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.compat import coreapi, coreschema
from rest_framework.exceptions import ValidationError
from rest_framework.fields import get_error_detail

from drf_query_filter import mixins
from drf_query_filter.utils import ConnectorType, choices2help_text


class Empty:
    """ Dummy class just to represent a True None value """
    pass


class Node:
    internal_error_messages = {
        'value_error': 'cannot perform the operation with the given instance'
    }

    def __init__(self, children=None, connector=None):
        self.children: List[Node] = children or list()
        self.connector: ConnectorType = connector or ConnectorType.AND

    def __and__(self, other):
        if not isinstance(other, Node):
            raise ValueError(self.internal_error_messages['value_error'])

        if self.connector == ConnectorType.AND:
            self.children.append(other)
            return self
        else:
            node = Node(children=[self, other], connector=ConnectorType.AND)
            return node

    def __or__(self, other):
        if not isinstance(other, Node):
            raise ValueError(self.internal_error_messages['value_error'])

        if self.connector == ConnectorType.OR:
            self.children.append(other)
            return self
        else:
            node = Node(children=[self, other], connector=ConnectorType.OR)
            return node

    def __repr__(self):
        if self.children:
            return '(%(connector)s: [%(children)s])' % \
                   {
                       'connector': self.connector.value,
                       'children':  ', '.join(
                           [repr(child) for child in self.children]),
                   }
        return '`EMPTY NODE`'

    @property
    def errors(self) -> Dict:
        # Gather errors of all the nested children
        errors = {}
        for child in self.children:
            errors.update(child.errors)
        return errors

    def get_filter(self, data) -> Tuple[Q, Dict]:
        annotate = {}
        query = Q(_connector=self.connector.value)
        for child in self.children:
            _query, _annotate = child.get_filter(data)
            annotate.update(_annotate)
            if self.connector == ConnectorType.AND:
                query &= _query
            else:
                query |= _query
        return query, annotate

    def filter(self, queryset, data,
               raise_exceptions=False) -> Tuple[Any, Dict]:
        # This gets the query and annotate of all children and itself
        query, annotate = self.get_filter(data)

        # Check if there is no error if raise_exceptions is True
        errors = self.errors
        if errors and raise_exceptions:
            return queryset, errors

        if annotate:
            queryset = queryset.annotate(**annotate)
        if query:
            queryset = queryset.filter(query)

        return queryset, {}

    def get_coreapi_fields(self) -> list:
        # get all the children and return the results

        schema = list(itertools.chain.from_iterable(
            child.get_coreapi_fields() for child in self.children
        ))

        return schema

    def get_schema_operation_parameters(self) -> List[dict]:
        # get all the children and return the results

        schema = list(itertools.chain.from_iterable(
            child.get_schema_operation_parameters() for child in self.children
        ))

        return schema


class Field(Node):

    def __init__(self,
                 field_name: str,
                 target_fields: Optional[Union[str, List, Tuple]] = None,
                 validators: List[Callable] = None,
                 description: str = "",
                 connector: ConnectorType = ConnectorType.AND):
        """
        Base field or String Field.
        :param field_name: The name in the query params of the url.
        :param target_fields: The target fields in the queryset, This can be a
        string or a iterable of strings.
        :param validators: A list of class validators to call in the validation
        process.
        :param description: Description used in schema definition.
        :param connector: Type of connector in the target fields.
        """
        self.field_name: str = field_name
        assert self.field_name, (
            '%s.field_name cannot be empty.' % self.__class__.__name__)

        self.target_fields = target_fields or self.field_name

        assert isinstance(self.target_fields, (str, list, tuple)), (
            'given target_fields is a `%s`,'
            'expected a str or a list/tuple.' %
            type(self.target_fields)
        )

        if isinstance(self.target_fields, str):
            self.target_fields = [self.target_fields]

        self.validators: List[Callable] = validators

        # value got from the query param request
        self._raw_value: Any = Empty()
        self._value: Any = self._raw_value  # transformed value
        self.no_value: bool = True  # Flag to check if this
        self._errors: List = []  # the list of errors we got

        self.description = description

        super().__init__(None, connector=connector)

    def __call__(self, query_data: Dict) -> bool:
        """
        Try to find the value from the given field, if it doesn't find it then
        sets _raw_value as Empty()
        """

        if self.field_name in query_data:
            self._raw_value = query_data[self.field_name]
            return True
        else:
            self._raw_value = Empty()
            return False

    def __repr__(self):
        if self.children:
            return '(%(connector)s: [%(field_name)s, %(children)s])' % \
                   {
                       'connector':  self.connector.value,
                       'field_name': self.field_name,
                       'children':   ', '.join(
                           [repr(child) for child in self.children]),
                   }
        return '%(field_name)s' % {'field_name': self.field_name}

    @property
    def value(self) -> Any:
        assert not isinstance(self._value, Empty), (
            'you must call is_valid first')
        return self._value

    @property
    def errors(self) -> Dict:
        errors = {}
        if self._errors:
            errors.update({self.field_name: self._errors})
        for child in self.children:
            errors.update(child.errors)
        return errors

    def validate(self, value: Any) -> Any:
        """
        Function for custom validations, if there is any error it should throw
        a ValidationError Exception.
        This can also manipulate the value if required.
        """
        return value

    def run_validators(self, value: Any) -> None:
        """ This runs the validators like the fields in rest_framework """
        if self.validators:
            for validator in self.validators:
                # Run all the validators and gather all the errors raised by
                #  them
                try:
                    validator(value)
                except ValidationError as exc:
                    self._errors.extend(exc.detail)
                except DjangoValidationError as exc:
                    self._errors.extend(get_error_detail(exc))

    def is_valid(self) -> bool:
        self._errors = []  # Clean all the previous errors

        assert not isinstance(self._raw_value, Empty), \
            'you cannot call is_valid without giving a value first'

        try:
            self._value = self.validate(self._raw_value)
        except ValidationError as exc:
            self._errors.extend(exc.detail)
        except DjangoValidationError as exc:
            self._errors.extend(get_error_detail(exc))
        else:
            self.run_validators(self._value)

        return len(self._errors) == 0

    def get_value_query(self) -> Any:
        """
        This should be overwritten if the desire data needs to be manipulated
        for the query
        """
        return self.value

    def get_annotate(self) -> Dict:
        """
        This should be overwritten if the field requires to annotate custom
        fields in the query
        """
        return {}

    def get_query(self) -> Q:
        query = Q(_connector=self.connector.value)
        value = self.get_value_query()
        for field in self.target_fields:
            if self.connector == ConnectorType.AND:
                query &= Q(**{field: value})
            elif self.connector == ConnectorType.OR:
                query |= Q(**{field: value})

        return query

    def get_filter(self, data) -> Tuple[Q, Dict]:
        if self(data) and self.is_valid():
            annotate = self.get_annotate()
            query = self.get_query()
        else:
            annotate = {}
            query = Q(_connector=self.connector)
        for child in self.children:
            _query, _annotate = child.get_filter(data)
            annotate.update(_annotate)
            if self.connector == ConnectorType.AND:
                query &= _query
            else:
                query |= _query
        return query, annotate

    def get_description(self) -> str:
        return self.description

    def get_example(self) -> str:
        return ''

    def get_coreschema_field(self):
        # Cannot really write type definition of `coreschema` since
        # it will get evaluated when the coreschema it's not installed and the
        # target project does not require it.
        return coreschema.String()

    def get_coreapi_fields(self) -> list:
        # Cannot really write type definition of `coreapi.Field` since
        # it will get evaluated when the coreapi it's not installed and the
        # target project does not require it.
        schema = list(itertools.chain.from_iterable(
            child.get_coreapi_fields() for child in self.children
        ))

        return [coreapi.Field(
            name=self.field_name,
            required=False,  # for now there it's no requirement
            location='query',
            description=self.get_description(),
            schema=self.get_coreschema_field(),
            example=self.get_example(),
        )] + schema

    def get_schema(self) -> dict:
        return {'type': 'string'}

    def get_schema_operation_parameters(self) -> List[dict]:
        schema = list(itertools.chain.from_iterable(
            child.get_schema_operation_parameters() for child in self.children
        ))

        return [{
            'name':        self.field_name,
            'required':    False,
            'in':          'query',
            'description': self.get_description(),
            'schema':      self.get_schema(),
            'example':     self.get_example(),
        }] + schema


class IntegerField(Field):
    """
    Field that only accepts integers as values
    """
    error_messages = {
        'invalid': _('“%(value)s” value must be an integer.'),
    }

    def validate(self, value):
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValidationError(
                self.error_messages['invalid'] % {'value': value},
                code='invalid')

    def get_coreschema_field(self):
        return coreschema.Integer()

    def get_schema(self) -> dict:
        return {
            'type':   'number',
            'format': 'int32',
        }


class RangeIntegerField(mixins.Range,
                        IntegerField):
    """
    Accepts two integer values in the string and generate a
    query with greater than and/or lesser than in the target fields.
    """
    pass


class FloatField(Field):
    """
    Field that only accepts floats values
    """
    error_messages = {
        'invalid': _('“%(value)s” value must be a float.'),
    }

    def validate(self, value):
        """ Try to parse the value into a float """
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ValidationError(
                self.error_messages['invalid'] % {'value': value},
                code='invalid')

    def get_coreschema_field(self):
        return coreschema.Number()

    def get_schema(self) -> dict:
        return {
            'type':   'number',
            'format': 'float',
        }


class RangeFloatField(mixins.Range,
                      FloatField):
    """
    Accepts two float values in the string and generate a query with
    greater than and/or lesser than in the target fields.
    """
    pass


class DecimalField(Field):
    """
    Field that only accepts Decimal values
    """
    error_messages = {
        'invalid': _('“%(value)s” value must be a double.'),
    }

    def validate(self, value):
        try:
            value = decimal.Decimal(value)
        except (decimal.InvalidOperation, TypeError, ValueError):
            raise ValidationError(
                self.error_messages['invalid'] % {'value': value},
                code='invalid')

        if value.is_nan():
            raise ValidationError(
                self.error_messages['invalid'] % {'value': value},
                code='invalid')

        if value in (decimal.Decimal('Inf'), decimal.Decimal('-Inf')):
            raise ValidationError(
                self.error_messages['invalid'] % {'value': value},
                code='invalid')

        return value

    def get_coreschema_field(self):
        return coreschema.Number()

    def get_schema(self) -> dict:
        return {
            'type':   'number',
            'format': 'double',
        }


class RangeDecimalField(mixins.Range,
                        DecimalField):
    """
    Accepts two Decimal values in the string and generate a query with greater
    than or lesser than in the target fields.
    """
    pass


def default_timezone():
    return timezone.get_current_timezone() if settings.USE_TZ else None


class DateTimeField(Field):
    """
    Field that only accepts values that can be parsed into datetime
    """
    error_messages = {
        'wrong_format': 'Value %(value)s does not have the correct format,'
                        ' should be %(date_format)s'
    }
    default_date_format = '%Y-%m-%dT%H:%M:%SZ'

    def __init__(self, *args, date_format: str = None, **kwargs):
        self.date_format = date_format or self.default_date_format
        super().__init__(*args, **kwargs)

    def validate(self, value):
        try:
            date = datetime.datetime.strptime(value, self.date_format)
            _timezone = default_timezone()
            if _timezone and (
                    date.tzinfo is None
                    or date.tzinfo.utcoffset(date) is None):
                return timezone.make_aware(date, _timezone)
            return date
        except ValueError:
            raise ValidationError(
                self.error_messages['wrong_format'] % {
                    'value': value, 'date_format': self.date_format
                }, code='wrong_format')

    def get_coreschema_field(self):
        return coreschema.String(
            format='date-time'
        )

    def get_schema(self) -> dict:
        return {
            'type':   'string',
            'format': 'date-time',
        }


class RangeDateTimeField(mixins.Range,
                         DateTimeField):
    """
    Accepts two datetime values in the string and generate a query with greater
    than and/or lesser than in the target fields.
    """
    pass


class DateField(DateTimeField):
    """
    Field that only accepts values that can be parsed into date
    """
    default_date_format = '%Y-%m-%d'

    def validate(self, value):
        try:
            date = datetime.datetime.strptime(value, self.date_format).date()
            return date
        except ValueError:
            raise ValidationError(self.error_messages['wrong_format'] % {
                'value': value, 'date_format': self.date_format},
                code='wrong_format')

    def get_coreschema_field(self):
        return coreschema.String(
            format='date'
        )

    def get_schema(self) -> dict:
        return {
            'type':   'string',
            'format': 'date',
        }


class RangeDateField(mixins.Range,
                     DateField):
    """
    Accepts two date values in the string and generate a query with greater
    than and/or lesser than in the target fields.
    """
    pass


class ChoicesField(Field):
    """
    Field made to support multiple options.
    This can handle custom messages for the error raised
    """

    default_choices = []
    default_validate_message = 'Value `%(value)s` is not a valid option,' \
                               'Options are: %(choices)s '

    def __init__(self, *args,
                 choices: Union[
                     Choices,
                     List[Tuple[str, str]],
                     List[str],
                 ] = None,
                 validate_message: str = "",
                 **kwargs):

        self.choices = self.sanitize_choices(choices or self.default_choices)

        self.validate_message = validate_message or self.default_validate_message
        super().__init__(*args, **kwargs)

    def sanitize_choices(self, choices) -> List[Tuple[str, str]]:
        """Makes sure that choices it's a valid type."""
        if inspect.isclass(choices) and issubclass(choices, Choices):
            return choices.choices
        return [
            (str(choice[0]), str(choice[1]))
            if isinstance(choice, tuple) else (choice, Empty())
            for choice in choices
        ]

    def validate(self, value):
        if not any(value == choice[0] for choice in self.choices):
            raise ValidationError(detail=self.validate_message % {
                'value': value, 'choices': [
                    choice[0] for choice in self.choices
                ]
            }, code='not_in_choices')
        return value

    def get_description(self) -> str:
        return '%s%s' % (
            self.description + '  \n' if self.description else '',
            choices2help_text(self.choices)
        )

    def get_choices_for_schema(self):
        return [choice[0] for choice in self.choices]

    def get_coreschema_field(self):
        return coreschema.Enum(self.get_choices_for_schema())

    def get_schema(self):
        return {
            'type': 'string',
            'enum': self.get_choices_for_schema()
        }


class BooleanField(ChoicesField):
    """
    Field that only accepts boolean related strings
    """

    def __init__(self, *args, invert=False, **kwargs):
        # ignore the kwargs of choices
        kwargs['choices'] = [
            'true', 'True', 't', 'T', '1',
            'false', 'False', 'f', 'F', '0'
        ]
        self.invert = invert
        kwargs['validate_message'] = 'Value `%(value)s` is not a valid ' \
            'boolean. Options are: %(choices)s '
        super().__init__(*args, **kwargs)

    def validate(self, value):
        value = super().validate(value)
        return (value in ['true', 'True', 't', 'T', '1']) ^ self.invert


class ExistsField(Field):
    """
    Field that returns a set value if the field exists in the Query params.
    This Field doesn't care for the value given
    """

    def __init__(self, *args, return_value=None, **kwargs):
        self.return_value = return_value
        super().__init__(*args, **kwargs)

    def get_value_query(self):
        return self.return_value


class ConcatField(Field):
    """
    Concatenate Fields and query from that result
    """
    invalid_characters = r'[\( \)\\/]'

    def __init__(self, *args, **kwargs):
        self.lookup = kwargs.pop('lookup', '')
        self.target_field_name = kwargs.pop('target_field_name', '')
        self.output_field = kwargs.pop('output_field', DjangoCharField())
        super().__init__(*args, **kwargs)
        if not self.target_field_name:
            self.target_field_name = re.sub(
                r'__+', '_', re.sub(
                    self.invalid_characters, '_',
                    '_'.join([str(value) for value in self.target_fields])
                )
            )

    def get_lookup(self):
        return '__%s' % self.lookup if self.lookup else ''

    def get_query(self):
        query = Q(**{
            '%s%s' % (
                self.target_field_name, self.get_lookup()
            ): self.get_value_query()
        })
        return query

    def get_annotate(self):
        # concat values here
        concat = Concat(*self.target_fields, output_field=self.output_field)
        return {self.target_field_name: concat}
