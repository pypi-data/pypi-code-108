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


class AttributeTypeSpec(object):
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
        'addition': 'AttributeType',
        'entity_type': 'str'
    }

    attribute_map = {
        'addition': 'addition',
        'entity_type': 'entity_type'
    }

    def __init__(self, addition=None, entity_type=None, local_vars_configuration=None):  # noqa: E501
        """AttributeTypeSpec - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._addition = None
        self._entity_type = None
        self.discriminator = None

        if addition is not None:
            self.addition = addition
        if entity_type is not None:
            self.entity_type = entity_type

    @property
    def addition(self):
        """

        :return: The addition of this AttributeTypeSpec. 
        :rtype: AttributeType
        """
        return self._addition

    @addition.setter
    def addition(self, addition):
        """

        :param addition: The addition of this AttributeTypeSpec.
        :type: AttributeType
        """

        self._addition = addition

    @property
    def entity_type(self):
        """
        The entity type containing the attribute to rename.

        :return: The entity_type of this AttributeTypeSpec. 
        :rtype: str
        """
        return self._entity_type

    @entity_type.setter
    def entity_type(self, entity_type):
        """
        The entity type containing the attribute to rename.

        :param entity_type: The entity_type of this AttributeTypeSpec.
        :type: str
        """

        self._entity_type = entity_type

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
        if not isinstance(other, AttributeTypeSpec):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, AttributeTypeSpec):
            return True

        return self.to_dict() != other.to_dict()
