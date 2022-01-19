# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.3899
    Contact: info@finbourne.com
    Generated by: https://openapi-generator.tech
"""


try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec
import pprint
import re  # noqa: F401
import six

from lusid.configuration import Configuration


class FlowConventions(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
      required_map (dict): The key is attribute name
                           and the value is whether it is 'required' or 'optional'.
    """
    openapi_types = {
        'currency': 'str',
        'payment_frequency': 'str',
        'day_count_convention': 'str',
        'roll_convention': 'str',
        'payment_calendars': 'list[str]',
        'reset_calendars': 'list[str]',
        'settle_days': 'int',
        'reset_days': 'int',
        'leap_days_included': 'bool',
        'scope': 'str',
        'code': 'str'
    }

    attribute_map = {
        'currency': 'currency',
        'payment_frequency': 'paymentFrequency',
        'day_count_convention': 'dayCountConvention',
        'roll_convention': 'rollConvention',
        'payment_calendars': 'paymentCalendars',
        'reset_calendars': 'resetCalendars',
        'settle_days': 'settleDays',
        'reset_days': 'resetDays',
        'leap_days_included': 'leapDaysIncluded',
        'scope': 'scope',
        'code': 'code'
    }

    required_map = {
        'currency': 'required',
        'payment_frequency': 'required',
        'day_count_convention': 'required',
        'roll_convention': 'required',
        'payment_calendars': 'required',
        'reset_calendars': 'required',
        'settle_days': 'required',
        'reset_days': 'required',
        'leap_days_included': 'optional',
        'scope': 'optional',
        'code': 'optional'
    }

    def __init__(self, currency=None, payment_frequency=None, day_count_convention=None, roll_convention=None, payment_calendars=None, reset_calendars=None, settle_days=None, reset_days=None, leap_days_included=None, scope=None, code=None, local_vars_configuration=None):  # noqa: E501
        """FlowConventions - a model defined in OpenAPI"
        
        :param currency:  Currency of the flow convention. (required)
        :type currency: str
        :param payment_frequency:  When generating a multiperiod flow, or when the maturity of the flow is not given but the start date is,  the tenor is the time-step from the anchor-date to the nominal maturity of the flow prior to any adjustment. (required)
        :type payment_frequency: str
        :param day_count_convention:  when calculating the fraction of a year between two dates, what convention is used to represent the number of days in a year  and difference between them.  Supported string (enumeration) values are: [Actual360, Act360, MoneyMarket, Actual365, Act365, Thirty360, ThirtyU360, Bond, ThirtyE360, EuroBond, ActualActual, ActAct, ActActIsda, ActActIsma, ActActIcma, OneOne, Act364, Act365F, Act365L, Act365_25, Act252, Bus252, NL360, NL365, ActActAFB, Act365Cad, ThirtyActIsda, Thirty365Isda, ThirtyEActIsda, ThirtyE360Isda, ThirtyE365Isda, ThirtyU360EOM]. (required)
        :type day_count_convention: str
        :param roll_convention:  When generating a set of dates, what convention should be used for adjusting dates that coincide with a non-business day.  Supported string (enumeration) values are: [NoAdjustment, Previous, P, Following, F, ModifiedPrevious, MP, ModifiedFollowing, MF, EndOfMonth, EOM, EndOfMonthPrevious, EOMP, EndOfMonthFollowing, EOMF, HalfMonthModifiedFollowing]. (required)
        :type roll_convention: str
        :param payment_calendars:  An array of strings denoting holiday calendars that apply to generation of payment schedules. (required)
        :type payment_calendars: list[str]
        :param reset_calendars:  An array of strings denoting holiday calendars that apply to generation of reset schedules. (required)
        :type reset_calendars: list[str]
        :param settle_days:  Number of Good Business Days between the trade date and the effective or settlement date of the instrument. (required)
        :type settle_days: int
        :param reset_days:  The number of Good Business Days between determination and payment of reset. (required)
        :type reset_days: int
        :param leap_days_included:  If this flag is set to true, the 29th of February is included in the date schedule when the business roll convention is applied.  If this flag is set to false, the business roll convention ignores February 29 for date schedules, cash flow payments etc.  This flag defaults to true if not specified, i.e., leap days are included in a date schedule generation.
        :type leap_days_included: bool
        :param scope:  The scope used when updating or inserting the convention.
        :type scope: str
        :param code:  The code of the convention.
        :type code: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._currency = None
        self._payment_frequency = None
        self._day_count_convention = None
        self._roll_convention = None
        self._payment_calendars = None
        self._reset_calendars = None
        self._settle_days = None
        self._reset_days = None
        self._leap_days_included = None
        self._scope = None
        self._code = None
        self.discriminator = None

        self.currency = currency
        self.payment_frequency = payment_frequency
        self.day_count_convention = day_count_convention
        self.roll_convention = roll_convention
        self.payment_calendars = payment_calendars
        self.reset_calendars = reset_calendars
        self.settle_days = settle_days
        self.reset_days = reset_days
        self.leap_days_included = leap_days_included
        self.scope = scope
        self.code = code

    @property
    def currency(self):
        """Gets the currency of this FlowConventions.  # noqa: E501

        Currency of the flow convention.  # noqa: E501

        :return: The currency of this FlowConventions.  # noqa: E501
        :rtype: str
        """
        return self._currency

    @currency.setter
    def currency(self, currency):
        """Sets the currency of this FlowConventions.

        Currency of the flow convention.  # noqa: E501

        :param currency: The currency of this FlowConventions.  # noqa: E501
        :type currency: str
        """
        if self.local_vars_configuration.client_side_validation and currency is None:  # noqa: E501
            raise ValueError("Invalid value for `currency`, must not be `None`")  # noqa: E501

        self._currency = currency

    @property
    def payment_frequency(self):
        """Gets the payment_frequency of this FlowConventions.  # noqa: E501

        When generating a multiperiod flow, or when the maturity of the flow is not given but the start date is,  the tenor is the time-step from the anchor-date to the nominal maturity of the flow prior to any adjustment.  # noqa: E501

        :return: The payment_frequency of this FlowConventions.  # noqa: E501
        :rtype: str
        """
        return self._payment_frequency

    @payment_frequency.setter
    def payment_frequency(self, payment_frequency):
        """Sets the payment_frequency of this FlowConventions.

        When generating a multiperiod flow, or when the maturity of the flow is not given but the start date is,  the tenor is the time-step from the anchor-date to the nominal maturity of the flow prior to any adjustment.  # noqa: E501

        :param payment_frequency: The payment_frequency of this FlowConventions.  # noqa: E501
        :type payment_frequency: str
        """
        if self.local_vars_configuration.client_side_validation and payment_frequency is None:  # noqa: E501
            raise ValueError("Invalid value for `payment_frequency`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                payment_frequency is not None and len(payment_frequency) > 50):
            raise ValueError("Invalid value for `payment_frequency`, length must be less than or equal to `50`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                payment_frequency is not None and len(payment_frequency) < 0):
            raise ValueError("Invalid value for `payment_frequency`, length must be greater than or equal to `0`")  # noqa: E501

        self._payment_frequency = payment_frequency

    @property
    def day_count_convention(self):
        """Gets the day_count_convention of this FlowConventions.  # noqa: E501

        when calculating the fraction of a year between two dates, what convention is used to represent the number of days in a year  and difference between them.  Supported string (enumeration) values are: [Actual360, Act360, MoneyMarket, Actual365, Act365, Thirty360, ThirtyU360, Bond, ThirtyE360, EuroBond, ActualActual, ActAct, ActActIsda, ActActIsma, ActActIcma, OneOne, Act364, Act365F, Act365L, Act365_25, Act252, Bus252, NL360, NL365, ActActAFB, Act365Cad, ThirtyActIsda, Thirty365Isda, ThirtyEActIsda, ThirtyE360Isda, ThirtyE365Isda, ThirtyU360EOM].  # noqa: E501

        :return: The day_count_convention of this FlowConventions.  # noqa: E501
        :rtype: str
        """
        return self._day_count_convention

    @day_count_convention.setter
    def day_count_convention(self, day_count_convention):
        """Sets the day_count_convention of this FlowConventions.

        when calculating the fraction of a year between two dates, what convention is used to represent the number of days in a year  and difference between them.  Supported string (enumeration) values are: [Actual360, Act360, MoneyMarket, Actual365, Act365, Thirty360, ThirtyU360, Bond, ThirtyE360, EuroBond, ActualActual, ActAct, ActActIsda, ActActIsma, ActActIcma, OneOne, Act364, Act365F, Act365L, Act365_25, Act252, Bus252, NL360, NL365, ActActAFB, Act365Cad, ThirtyActIsda, Thirty365Isda, ThirtyEActIsda, ThirtyE360Isda, ThirtyE365Isda, ThirtyU360EOM].  # noqa: E501

        :param day_count_convention: The day_count_convention of this FlowConventions.  # noqa: E501
        :type day_count_convention: str
        """
        if self.local_vars_configuration.client_side_validation and day_count_convention is None:  # noqa: E501
            raise ValueError("Invalid value for `day_count_convention`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                day_count_convention is not None and len(day_count_convention) > 50):
            raise ValueError("Invalid value for `day_count_convention`, length must be less than or equal to `50`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                day_count_convention is not None and len(day_count_convention) < 0):
            raise ValueError("Invalid value for `day_count_convention`, length must be greater than or equal to `0`")  # noqa: E501

        self._day_count_convention = day_count_convention

    @property
    def roll_convention(self):
        """Gets the roll_convention of this FlowConventions.  # noqa: E501

        When generating a set of dates, what convention should be used for adjusting dates that coincide with a non-business day.  Supported string (enumeration) values are: [NoAdjustment, Previous, P, Following, F, ModifiedPrevious, MP, ModifiedFollowing, MF, EndOfMonth, EOM, EndOfMonthPrevious, EOMP, EndOfMonthFollowing, EOMF, HalfMonthModifiedFollowing].  # noqa: E501

        :return: The roll_convention of this FlowConventions.  # noqa: E501
        :rtype: str
        """
        return self._roll_convention

    @roll_convention.setter
    def roll_convention(self, roll_convention):
        """Sets the roll_convention of this FlowConventions.

        When generating a set of dates, what convention should be used for adjusting dates that coincide with a non-business day.  Supported string (enumeration) values are: [NoAdjustment, Previous, P, Following, F, ModifiedPrevious, MP, ModifiedFollowing, MF, EndOfMonth, EOM, EndOfMonthPrevious, EOMP, EndOfMonthFollowing, EOMF, HalfMonthModifiedFollowing].  # noqa: E501

        :param roll_convention: The roll_convention of this FlowConventions.  # noqa: E501
        :type roll_convention: str
        """
        if self.local_vars_configuration.client_side_validation and roll_convention is None:  # noqa: E501
            raise ValueError("Invalid value for `roll_convention`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                roll_convention is not None and len(roll_convention) > 50):
            raise ValueError("Invalid value for `roll_convention`, length must be less than or equal to `50`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                roll_convention is not None and len(roll_convention) < 0):
            raise ValueError("Invalid value for `roll_convention`, length must be greater than or equal to `0`")  # noqa: E501

        self._roll_convention = roll_convention

    @property
    def payment_calendars(self):
        """Gets the payment_calendars of this FlowConventions.  # noqa: E501

        An array of strings denoting holiday calendars that apply to generation of payment schedules.  # noqa: E501

        :return: The payment_calendars of this FlowConventions.  # noqa: E501
        :rtype: list[str]
        """
        return self._payment_calendars

    @payment_calendars.setter
    def payment_calendars(self, payment_calendars):
        """Sets the payment_calendars of this FlowConventions.

        An array of strings denoting holiday calendars that apply to generation of payment schedules.  # noqa: E501

        :param payment_calendars: The payment_calendars of this FlowConventions.  # noqa: E501
        :type payment_calendars: list[str]
        """
        if self.local_vars_configuration.client_side_validation and payment_calendars is None:  # noqa: E501
            raise ValueError("Invalid value for `payment_calendars`, must not be `None`")  # noqa: E501

        self._payment_calendars = payment_calendars

    @property
    def reset_calendars(self):
        """Gets the reset_calendars of this FlowConventions.  # noqa: E501

        An array of strings denoting holiday calendars that apply to generation of reset schedules.  # noqa: E501

        :return: The reset_calendars of this FlowConventions.  # noqa: E501
        :rtype: list[str]
        """
        return self._reset_calendars

    @reset_calendars.setter
    def reset_calendars(self, reset_calendars):
        """Sets the reset_calendars of this FlowConventions.

        An array of strings denoting holiday calendars that apply to generation of reset schedules.  # noqa: E501

        :param reset_calendars: The reset_calendars of this FlowConventions.  # noqa: E501
        :type reset_calendars: list[str]
        """
        if self.local_vars_configuration.client_side_validation and reset_calendars is None:  # noqa: E501
            raise ValueError("Invalid value for `reset_calendars`, must not be `None`")  # noqa: E501

        self._reset_calendars = reset_calendars

    @property
    def settle_days(self):
        """Gets the settle_days of this FlowConventions.  # noqa: E501

        Number of Good Business Days between the trade date and the effective or settlement date of the instrument.  # noqa: E501

        :return: The settle_days of this FlowConventions.  # noqa: E501
        :rtype: int
        """
        return self._settle_days

    @settle_days.setter
    def settle_days(self, settle_days):
        """Sets the settle_days of this FlowConventions.

        Number of Good Business Days between the trade date and the effective or settlement date of the instrument.  # noqa: E501

        :param settle_days: The settle_days of this FlowConventions.  # noqa: E501
        :type settle_days: int
        """
        if self.local_vars_configuration.client_side_validation and settle_days is None:  # noqa: E501
            raise ValueError("Invalid value for `settle_days`, must not be `None`")  # noqa: E501

        self._settle_days = settle_days

    @property
    def reset_days(self):
        """Gets the reset_days of this FlowConventions.  # noqa: E501

        The number of Good Business Days between determination and payment of reset.  # noqa: E501

        :return: The reset_days of this FlowConventions.  # noqa: E501
        :rtype: int
        """
        return self._reset_days

    @reset_days.setter
    def reset_days(self, reset_days):
        """Sets the reset_days of this FlowConventions.

        The number of Good Business Days between determination and payment of reset.  # noqa: E501

        :param reset_days: The reset_days of this FlowConventions.  # noqa: E501
        :type reset_days: int
        """
        if self.local_vars_configuration.client_side_validation and reset_days is None:  # noqa: E501
            raise ValueError("Invalid value for `reset_days`, must not be `None`")  # noqa: E501

        self._reset_days = reset_days

    @property
    def leap_days_included(self):
        """Gets the leap_days_included of this FlowConventions.  # noqa: E501

        If this flag is set to true, the 29th of February is included in the date schedule when the business roll convention is applied.  If this flag is set to false, the business roll convention ignores February 29 for date schedules, cash flow payments etc.  This flag defaults to true if not specified, i.e., leap days are included in a date schedule generation.  # noqa: E501

        :return: The leap_days_included of this FlowConventions.  # noqa: E501
        :rtype: bool
        """
        return self._leap_days_included

    @leap_days_included.setter
    def leap_days_included(self, leap_days_included):
        """Sets the leap_days_included of this FlowConventions.

        If this flag is set to true, the 29th of February is included in the date schedule when the business roll convention is applied.  If this flag is set to false, the business roll convention ignores February 29 for date schedules, cash flow payments etc.  This flag defaults to true if not specified, i.e., leap days are included in a date schedule generation.  # noqa: E501

        :param leap_days_included: The leap_days_included of this FlowConventions.  # noqa: E501
        :type leap_days_included: bool
        """

        self._leap_days_included = leap_days_included

    @property
    def scope(self):
        """Gets the scope of this FlowConventions.  # noqa: E501

        The scope used when updating or inserting the convention.  # noqa: E501

        :return: The scope of this FlowConventions.  # noqa: E501
        :rtype: str
        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        """Sets the scope of this FlowConventions.

        The scope used when updating or inserting the convention.  # noqa: E501

        :param scope: The scope of this FlowConventions.  # noqa: E501
        :type scope: str
        """
        if (self.local_vars_configuration.client_side_validation and
                scope is not None and len(scope) > 256):
            raise ValueError("Invalid value for `scope`, length must be less than or equal to `256`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                scope is not None and len(scope) < 1):
            raise ValueError("Invalid value for `scope`, length must be greater than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                scope is not None and not re.search(r'^[a-zA-Z0-9\-_]+$', scope)):  # noqa: E501
            raise ValueError(r"Invalid value for `scope`, must be a follow pattern or equal to `/^[a-zA-Z0-9\-_]+$/`")  # noqa: E501

        self._scope = scope

    @property
    def code(self):
        """Gets the code of this FlowConventions.  # noqa: E501

        The code of the convention.  # noqa: E501

        :return: The code of this FlowConventions.  # noqa: E501
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets the code of this FlowConventions.

        The code of the convention.  # noqa: E501

        :param code: The code of this FlowConventions.  # noqa: E501
        :type code: str
        """
        if (self.local_vars_configuration.client_side_validation and
                code is not None and len(code) > 256):
            raise ValueError("Invalid value for `code`, length must be less than or equal to `256`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                code is not None and len(code) < 1):
            raise ValueError("Invalid value for `code`, length must be greater than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                code is not None and not re.search(r'^[a-zA-Z0-9\-_]+$', code)):  # noqa: E501
            raise ValueError(r"Invalid value for `code`, must be a follow pattern or equal to `/^[a-zA-Z0-9\-_]+$/`")  # noqa: E501

        self._code = code

    def to_dict(self, serialize=False):
        """Returns the model properties as a dict"""
        result = {}

        def convert(x):
            if hasattr(x, "to_dict"):
                args = getfullargspec(x.to_dict).args
                if len(args) == 1:
                    return x.to_dict()
                else:
                    return x.to_dict(serialize)
            else:
                return x

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            attr = self.attribute_map.get(attr, attr) if serialize else attr
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: convert(x),
                    value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], convert(item[1])),
                    value.items()
                ))
            else:
                result[attr] = convert(value)

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, FlowConventions):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FlowConventions):
            return True

        return self.to_dict() != other.to_dict()
