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


class Announcement(object):
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
        'message': 'str',
        'subject': 'str'
    }

    attribute_map = {
        'id': 'id',
        'message': 'message',
        'subject': 'subject'
    }

    def __init__(self, id=None, message=None, subject=None, local_vars_configuration=None):  # noqa: E501
        """Announcement - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._id = None
        self._message = None
        self._subject = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if message is not None:
            self.message = message
        if subject is not None:
            self.subject = subject

    @property
    def id(self):
        """
        Unique integer identifying an announcement.

        :return: The id of this Announcement. 
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id):
        """
        Unique integer identifying an announcement.

        :param id: The id of this Announcement.
        :type: int
        """

        self._id = id

    @property
    def message(self):
        """
        Message of the announcement.

        :return: The message of this Announcement. 
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """
        Message of the announcement.

        :param message: The message of this Announcement.
        :type: str
        """

        self._message = message

    @property
    def subject(self):
        """
        Subject of the announcement.

        :return: The subject of this Announcement. 
        :rtype: str
        """
        return self._subject

    @subject.setter
    def subject(self, subject):
        """
        Subject of the announcement.

        :param subject: The subject of this Announcement.
        :type: str
        """

        self._subject = subject

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
        if not isinstance(other, Announcement):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Announcement):
            return True

        return self.to_dict() != other.to_dict()
