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


class CloneMediaSpec(object):
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
        'dest_project': 'int',
        'dest_section': 'str',
        'dest_type': 'int'
    }

    attribute_map = {
        'dest_project': 'dest_project',
        'dest_section': 'dest_section',
        'dest_type': 'dest_type'
    }

    def __init__(self, dest_project=None, dest_section=None, dest_type=None, local_vars_configuration=None):  # noqa: E501
        """CloneMediaSpec - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._dest_project = None
        self._dest_section = None
        self._dest_type = None
        self.discriminator = None

        self.dest_project = dest_project
        self.dest_section = dest_section
        self.dest_type = dest_type

    @property
    def dest_project(self):
        """
        Unique integer identyifying destination project.

        :return: The dest_project of this CloneMediaSpec. 
        :rtype: int
        """
        return self._dest_project

    @dest_project.setter
    def dest_project(self, dest_project):
        """
        Unique integer identyifying destination project.

        :param dest_project: The dest_project of this CloneMediaSpec.
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and dest_project is None:  # noqa: E501
            raise ValueError("Invalid value for `dest_project`, must not be `None`")  # noqa: E501

        self._dest_project = dest_project

    @property
    def dest_section(self):
        """
        Destination media section name.

        :return: The dest_section of this CloneMediaSpec. 
        :rtype: str
        """
        return self._dest_section

    @dest_section.setter
    def dest_section(self, dest_section):
        """
        Destination media section name.

        :param dest_section: The dest_section of this CloneMediaSpec.
        :type: str
        """

        self._dest_section = dest_section

    @property
    def dest_type(self):
        """
        Unique integer identifying destination media type. Use -1 to automatically select the media type if only one media type exists in the destination project.

        :return: The dest_type of this CloneMediaSpec. 
        :rtype: int
        """
        return self._dest_type

    @dest_type.setter
    def dest_type(self, dest_type):
        """
        Unique integer identifying destination media type. Use -1 to automatically select the media type if only one media type exists in the destination project.

        :param dest_type: The dest_type of this CloneMediaSpec.
        :type: int
        """
        if self.local_vars_configuration.client_side_validation and dest_type is None:  # noqa: E501
            raise ValueError("Invalid value for `dest_type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                dest_type is not None and dest_type < -1):  # noqa: E501
            raise ValueError("Invalid value for `dest_type`, must be a value greater than or equal to `-1`")  # noqa: E501

        self._dest_type = dest_type

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
        if not isinstance(other, CloneMediaSpec):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CloneMediaSpec):
            return True

        return self.to_dict() != other.to_dict()
