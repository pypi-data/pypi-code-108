# coding: utf-8

"""
    Tator REST API

    Interface to the Tator backend.  # noqa: E501

    The version of the OpenAPI document: v1
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from ..configuration import Configuration


class FloatArrayQuery(object):
    """
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'center': 'list[float]',
        'lower_bound': 'float',
        'metric': 'str',
        'name': 'str',
        'order': 'str',
        'upper_bound': 'float'
    }

    attribute_map = {
        'center': 'center',
        'lower_bound': 'lower_bound',
        'metric': 'metric',
        'name': 'name',
        'order': 'order',
        'upper_bound': 'upper_bound'
    }

    def __init__(self, center=None, lower_bound=0, metric='l2norm', name=None, order='asc', upper_bound=None, local_vars_configuration=None):  # noqa: E501
        """FloatArrayQuery - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._center = None
        self._lower_bound = None
        self._metric = None
        self._name = None
        self._order = None
        self._upper_bound = None
        self.discriminator = None

        self.center = center
        if lower_bound is not None:
            self.lower_bound = lower_bound
        if metric is not None:
            self.metric = metric
        self.name = name
        if order is not None:
            self.order = order
        if upper_bound is not None:
            self.upper_bound = upper_bound

    @property
    def center(self):
        """
        Center of the query.

        :return: The center of this FloatArrayQuery. 
        :rtype: list[float]
        """
        return self._center

    @center.setter
    def center(self, center):
        """
        Center of the query.

        :param center: The center of this FloatArrayQuery.
        :type: list[float]
        """
        if self.local_vars_configuration.client_side_validation and center is None:  # noqa: E501
            raise ValueError("Invalid value for `center`, must not be `None`")  # noqa: E501

        self._center = center

    @property
    def lower_bound(self):
        """
        Return results with metric greater than this value.

        :return: The lower_bound of this FloatArrayQuery. 
        :rtype: float
        """
        return self._lower_bound

    @lower_bound.setter
    def lower_bound(self, lower_bound):
        """
        Return results with metric greater than this value.

        :param lower_bound: The lower_bound of this FloatArrayQuery.
        :type: float
        """

        self._lower_bound = lower_bound

    @property
    def metric(self):
        """
        Distance metric from center of query.

        :return: The metric of this FloatArrayQuery. 
        :rtype: str
        """
        return self._metric

    @metric.setter
    def metric(self, metric):
        """
        Distance metric from center of query.

        :param metric: The metric of this FloatArrayQuery.
        :type: str
        """
        allowed_values = ["l2norm", "l1norm"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and metric not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `metric` ({0}), must be one of {1}"  # noqa: E501
                .format(metric, allowed_values)
            )

        self._metric = metric

    @property
    def name(self):
        """
        Name of the attribute.

        :return: The name of this FloatArrayQuery. 
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Name of the attribute.

        :param name: The name of this FloatArrayQuery.
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def order(self):
        """
        Order in which results should be returned.

        :return: The order of this FloatArrayQuery. 
        :rtype: str
        """
        return self._order

    @order.setter
    def order(self, order):
        """
        Order in which results should be returned.

        :param order: The order of this FloatArrayQuery.
        :type: str
        """
        allowed_values = ["asc", "desc"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and order not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `order` ({0}), must be one of {1}"  # noqa: E501
                .format(order, allowed_values)
            )

        self._order = order

    @property
    def upper_bound(self):
        """
        Return results with metric less than this value.

        :return: The upper_bound of this FloatArrayQuery. 
        :rtype: float
        """
        return self._upper_bound

    @upper_bound.setter
    def upper_bound(self, upper_bound):
        """
        Return results with metric less than this value.

        :param upper_bound: The upper_bound of this FloatArrayQuery.
        :type: float
        """

        self._upper_bound = upper_bound

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, FloatArrayQuery):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, FloatArrayQuery):
            return True

        return self.to_dict() != other.to_dict()
