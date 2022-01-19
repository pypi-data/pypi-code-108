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


class Organization(object):
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
        'id': 'int',
        'name': 'str',
        'permission': 'str'
    }

    attribute_map = {
        'id': 'id',
        'name': 'name',
        'permission': 'permission'
    }

    def __init__(self, id=None, name=None, permission=None, local_vars_configuration=None):  # noqa: E501
        """Organization - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._name = None
        self._permission = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if name is not None:
            self.name = name
        if permission is not None:
            self.permission = permission

    @property
    def id(self):
        """
        Unique integer identifying the organization.

        :return: The id of this Organization. 
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Unique integer identifying the organization.

        :param id: The id of this Organization.
        :type: int
        """

        self._id = id

    @property
    def name(self):
        """
        Name of the organization.

        :return: The name of this Organization. 
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Name of the organization.

        :param name: The name of this Organization.
        :type: str
        """

        self._name = name

    @property
    def permission(self):
        """
        Permission level of user making request.

        :return: The permission of this Organization. 
        :rtype: str
        """
        return self._permission

    @permission.setter
    def permission(self, permission):
        """
        Permission level of user making request.

        :param permission: The permission of this Organization.
        :type: str
        """

        self._permission = permission

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
        if not isinstance(other, Organization):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Organization):
            return True

        return self.to_dict() != other.to_dict()
