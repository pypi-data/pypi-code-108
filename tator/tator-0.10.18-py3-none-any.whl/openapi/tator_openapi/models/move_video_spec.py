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


class MoveVideoSpec(object):
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
        'media_files': 'MediaFiles'
    }

    attribute_map = {
        'media_files': 'media_files'
    }

    def __init__(self, media_files=None, local_vars_configuration=None):  # noqa: E501
        """MoveVideoSpec - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._media_files = None
        self.discriminator = None

        self.media_files = media_files

    @property
    def media_files(self):
        """

        :return: The media_files of this MoveVideoSpec. 
        :rtype: MediaFiles
        """
        return self._media_files

    @media_files.setter
    def media_files(self, media_files):
        """

        :param media_files: The media_files of this MoveVideoSpec.
        :type: MediaFiles
        """
        if self.local_vars_configuration.client_side_validation and media_files is None:  # noqa: E501
            raise ValueError("Invalid value for `media_files`, must not be `None`")  # noqa: E501

        self._media_files = media_files

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
        if not isinstance(other, MoveVideoSpec):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, MoveVideoSpec):
            return True

        return self.to_dict() != other.to_dict()
