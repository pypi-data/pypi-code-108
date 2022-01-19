# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.3898
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

from lusid_asyncio.configuration import Configuration


class ComplianceRun(object):
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
        'run_id': 'str',
        'as_at': 'datetime'
    }

    attribute_map = {
        'run_id': 'runId',
        'as_at': 'asAt'
    }

    required_map = {
        'run_id': 'required',
        'as_at': 'required'
    }

    def __init__(self, run_id=None, as_at=None, local_vars_configuration=None):  # noqa: E501
        """ComplianceRun - a model defined in OpenAPI"
        
        :param run_id:  The unique identifier of a compliance run (required)
        :type run_id: str
        :param as_at:  The date at time at which the compliance run was run (required)
        :type as_at: datetime

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._run_id = None
        self._as_at = None
        self.discriminator = None

        self.run_id = run_id
        self.as_at = as_at

    @property
    def run_id(self):
        """Gets the run_id of this ComplianceRun.  # noqa: E501

        The unique identifier of a compliance run  # noqa: E501

        :return: The run_id of this ComplianceRun.  # noqa: E501
        :rtype: str
        """
        return self._run_id

    @run_id.setter
    def run_id(self, run_id):
        """Sets the run_id of this ComplianceRun.

        The unique identifier of a compliance run  # noqa: E501

        :param run_id: The run_id of this ComplianceRun.  # noqa: E501
        :type run_id: str
        """
        if self.local_vars_configuration.client_side_validation and run_id is None:  # noqa: E501
            raise ValueError("Invalid value for `run_id`, must not be `None`")  # noqa: E501

        self._run_id = run_id

    @property
    def as_at(self):
        """Gets the as_at of this ComplianceRun.  # noqa: E501

        The date at time at which the compliance run was run  # noqa: E501

        :return: The as_at of this ComplianceRun.  # noqa: E501
        :rtype: datetime
        """
        return self._as_at

    @as_at.setter
    def as_at(self, as_at):
        """Sets the as_at of this ComplianceRun.

        The date at time at which the compliance run was run  # noqa: E501

        :param as_at: The as_at of this ComplianceRun.  # noqa: E501
        :type as_at: datetime
        """
        if self.local_vars_configuration.client_side_validation and as_at is None:  # noqa: E501
            raise ValueError("Invalid value for `as_at`, must not be `None`")  # noqa: E501

        self._as_at = as_at

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
        if not isinstance(other, ComplianceRun):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ComplianceRun):
            return True

        return self.to_dict() != other.to_dict()
