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


class BookmarkSpec(object):
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
        'name': 'str',
        'uri': 'str'
    }

    attribute_map = {
        'name': 'name',
        'uri': 'uri'
    }

    def __init__(self, name=None, uri=None, local_vars_configuration=None):  # noqa: E501
        """BookmarkSpec - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._name = None
        self._uri = None
        self.discriminator = None

        if name is not None:
            self.name = name
        if uri is not None:
            self.uri = uri

    @property
    def name(self):
        """
        Name of the bookmark.

        :return: The name of this BookmarkSpec. 
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Name of the bookmark.

        :param name: The name of this BookmarkSpec.
        :type: str
        """

        self._name = name

    @property
    def uri(self):
        """
        URI to the saved link.

        :return: The uri of this BookmarkSpec. 
        :rtype: str
        """
        return self._uri

    @uri.setter
    def uri(self, uri):
        """
        URI to the saved link.

        :param uri: The uri of this BookmarkSpec.
        :type: str
        """

        self._uri = uri

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
        if not isinstance(other, BookmarkSpec):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, BookmarkSpec):
            return True

        return self.to_dict() != other.to_dict()
