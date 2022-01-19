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


class DashboardSpec(object):
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
        'categories': 'list[str]',
        'description': 'str',
        'html_file': 'str',
        'name': 'str'
    }

    attribute_map = {
        'categories': 'categories',
        'description': 'description',
        'html_file': 'html_file',
        'name': 'name'
    }

    def __init__(self, categories=None, description=None, html_file=None, name=None, local_vars_configuration=None):  # noqa: E501
        """DashboardSpec - a model defined in OpenAPI"""
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._categories = None
        self._description = None
        self._html_file = None
        self._name = None
        self.discriminator = None

        if categories is not None:
            self.categories = categories
        if description is not None:
            self.description = description
        if html_file is not None:
            self.html_file = html_file
        if name is not None:
            self.name = name

    @property
    def categories(self):
        """
        List of categories the dashboard belongs to

        :return: The categories of this DashboardSpec. 
        :rtype: list[str]
        """
        return self._categories

    @categories.setter
    def categories(self, categories):
        """
        List of categories the dashboard belongs to

        :param categories: The categories of this DashboardSpec.
        :type: list[str]
        """

        self._categories = categories

    @property
    def description(self):
        """
        Description of dashboard

        :return: The description of this DashboardSpec. 
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """
        Description of dashboard

        :param description: The description of this DashboardSpec.
        :type: str
        """

        self._description = description

    @property
    def html_file(self):
        """
        Server URL to dashboard HTML file

        :return: The html_file of this DashboardSpec. 
        :rtype: str
        """
        return self._html_file

    @html_file.setter
    def html_file(self, html_file):
        """
        Server URL to dashboard HTML file

        :param html_file: The html_file of this DashboardSpec.
        :type: str
        """

        self._html_file = html_file

    @property
    def name(self):
        """
        Name of dashboard

        :return: The name of this DashboardSpec. 
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Name of dashboard

        :param name: The name of this DashboardSpec.
        :type: str
        """

        self._name = name

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
        if not isinstance(other, DashboardSpec):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, DashboardSpec):
            return True

        return self.to_dict() != other.to_dict()
