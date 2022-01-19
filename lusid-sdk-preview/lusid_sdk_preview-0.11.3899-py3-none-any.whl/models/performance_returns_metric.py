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


class PerformanceReturnsMetric(object):
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
        'type': 'str',
        'window': 'str',
        'allow_partial': 'bool',
        'annualised': 'bool',
        'with_fee': 'bool',
        'seed_amount': 'str',
        'alias': 'str'
    }

    attribute_map = {
        'type': 'type',
        'window': 'window',
        'allow_partial': 'allowPartial',
        'annualised': 'annualised',
        'with_fee': 'withFee',
        'seed_amount': 'seedAmount',
        'alias': 'alias'
    }

    required_map = {
        'type': 'optional',
        'window': 'optional',
        'allow_partial': 'optional',
        'annualised': 'optional',
        'with_fee': 'optional',
        'seed_amount': 'optional',
        'alias': 'optional'
    }

    def __init__(self, type=None, window=None, allow_partial=None, annualised=None, with_fee=None, seed_amount=None, alias=None, local_vars_configuration=None):  # noqa: E501
        """PerformanceReturnsMetric - a model defined in OpenAPI"
        
        :param type:  The type of the metric. Default to Return
        :type type: str
        :param window:  The given metric for the calculation i.e. 1Y, 1D.
        :type window: str
        :param allow_partial:  Bool if the metric is allowed partial results. Deafult to false.
        :type allow_partial: bool
        :param annualised:  Bool if the metric is annualized. Default to false.
        :type annualised: bool
        :param with_fee:  Bool if the metric should consider the fees when is calculated. Default to false.
        :type with_fee: bool
        :param seed_amount:  The given seed amount for the calculation of the indicative amount metrics.
        :type seed_amount: str
        :param alias:  The alias for the metric.
        :type alias: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._type = None
        self._window = None
        self._allow_partial = None
        self._annualised = None
        self._with_fee = None
        self._seed_amount = None
        self._alias = None
        self.discriminator = None

        self.type = type
        self.window = window
        if allow_partial is not None:
            self.allow_partial = allow_partial
        if annualised is not None:
            self.annualised = annualised
        if with_fee is not None:
            self.with_fee = with_fee
        self.seed_amount = seed_amount
        self.alias = alias

    @property
    def type(self):
        """Gets the type of this PerformanceReturnsMetric.  # noqa: E501

        The type of the metric. Default to Return  # noqa: E501

        :return: The type of this PerformanceReturnsMetric.  # noqa: E501
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type):
        """Sets the type of this PerformanceReturnsMetric.

        The type of the metric. Default to Return  # noqa: E501

        :param type: The type of this PerformanceReturnsMetric.  # noqa: E501
        :type type: str
        """

        self._type = type

    @property
    def window(self):
        """Gets the window of this PerformanceReturnsMetric.  # noqa: E501

        The given metric for the calculation i.e. 1Y, 1D.  # noqa: E501

        :return: The window of this PerformanceReturnsMetric.  # noqa: E501
        :rtype: str
        """
        return self._window

    @window.setter
    def window(self, window):
        """Sets the window of this PerformanceReturnsMetric.

        The given metric for the calculation i.e. 1Y, 1D.  # noqa: E501

        :param window: The window of this PerformanceReturnsMetric.  # noqa: E501
        :type window: str
        """

        self._window = window

    @property
    def allow_partial(self):
        """Gets the allow_partial of this PerformanceReturnsMetric.  # noqa: E501

        Bool if the metric is allowed partial results. Deafult to false.  # noqa: E501

        :return: The allow_partial of this PerformanceReturnsMetric.  # noqa: E501
        :rtype: bool
        """
        return self._allow_partial

    @allow_partial.setter
    def allow_partial(self, allow_partial):
        """Sets the allow_partial of this PerformanceReturnsMetric.

        Bool if the metric is allowed partial results. Deafult to false.  # noqa: E501

        :param allow_partial: The allow_partial of this PerformanceReturnsMetric.  # noqa: E501
        :type allow_partial: bool
        """

        self._allow_partial = allow_partial

    @property
    def annualised(self):
        """Gets the annualised of this PerformanceReturnsMetric.  # noqa: E501

        Bool if the metric is annualized. Default to false.  # noqa: E501

        :return: The annualised of this PerformanceReturnsMetric.  # noqa: E501
        :rtype: bool
        """
        return self._annualised

    @annualised.setter
    def annualised(self, annualised):
        """Sets the annualised of this PerformanceReturnsMetric.

        Bool if the metric is annualized. Default to false.  # noqa: E501

        :param annualised: The annualised of this PerformanceReturnsMetric.  # noqa: E501
        :type annualised: bool
        """

        self._annualised = annualised

    @property
    def with_fee(self):
        """Gets the with_fee of this PerformanceReturnsMetric.  # noqa: E501

        Bool if the metric should consider the fees when is calculated. Default to false.  # noqa: E501

        :return: The with_fee of this PerformanceReturnsMetric.  # noqa: E501
        :rtype: bool
        """
        return self._with_fee

    @with_fee.setter
    def with_fee(self, with_fee):
        """Sets the with_fee of this PerformanceReturnsMetric.

        Bool if the metric should consider the fees when is calculated. Default to false.  # noqa: E501

        :param with_fee: The with_fee of this PerformanceReturnsMetric.  # noqa: E501
        :type with_fee: bool
        """

        self._with_fee = with_fee

    @property
    def seed_amount(self):
        """Gets the seed_amount of this PerformanceReturnsMetric.  # noqa: E501

        The given seed amount for the calculation of the indicative amount metrics.  # noqa: E501

        :return: The seed_amount of this PerformanceReturnsMetric.  # noqa: E501
        :rtype: str
        """
        return self._seed_amount

    @seed_amount.setter
    def seed_amount(self, seed_amount):
        """Sets the seed_amount of this PerformanceReturnsMetric.

        The given seed amount for the calculation of the indicative amount metrics.  # noqa: E501

        :param seed_amount: The seed_amount of this PerformanceReturnsMetric.  # noqa: E501
        :type seed_amount: str
        """

        self._seed_amount = seed_amount

    @property
    def alias(self):
        """Gets the alias of this PerformanceReturnsMetric.  # noqa: E501

        The alias for the metric.  # noqa: E501

        :return: The alias of this PerformanceReturnsMetric.  # noqa: E501
        :rtype: str
        """
        return self._alias

    @alias.setter
    def alias(self, alias):
        """Sets the alias of this PerformanceReturnsMetric.

        The alias for the metric.  # noqa: E501

        :param alias: The alias of this PerformanceReturnsMetric.  # noqa: E501
        :type alias: str
        """

        self._alias = alias

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
        if not isinstance(other, PerformanceReturnsMetric):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, PerformanceReturnsMetric):
            return True

        return self.to_dict() != other.to_dict()
