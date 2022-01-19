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


class GetCdsFlowConventionsResponse(object):
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
        'href': 'str',
        'value': 'CdsFlowConventions',
        'failed': 'dict(str, ErrorDetail)',
        'links': 'list[Link]'
    }

    attribute_map = {
        'href': 'href',
        'value': 'value',
        'failed': 'failed',
        'links': 'links'
    }

    required_map = {
        'href': 'optional',
        'value': 'optional',
        'failed': 'optional',
        'links': 'optional'
    }

    def __init__(self, href=None, value=None, failed=None, links=None, local_vars_configuration=None):  # noqa: E501
        """GetCdsFlowConventionsResponse - a model defined in OpenAPI"
        
        :param href:  The specific Uniform Resource Identifier (URI) for this resource at the requested effective and asAt datetime.
        :type href: str
        :param value: 
        :type value: lusid_asyncio.CdsFlowConventions
        :param failed:  The identifiers that did not resolve to a conventions along with the nature of the failure.
        :type failed: dict[str, lusid_asyncio.ErrorDetail]
        :param links:  Collection of links.
        :type links: list[lusid_asyncio.Link]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._href = None
        self._value = None
        self._failed = None
        self._links = None
        self.discriminator = None

        self.href = href
        if value is not None:
            self.value = value
        self.failed = failed
        self.links = links

    @property
    def href(self):
        """Gets the href of this GetCdsFlowConventionsResponse.  # noqa: E501

        The specific Uniform Resource Identifier (URI) for this resource at the requested effective and asAt datetime.  # noqa: E501

        :return: The href of this GetCdsFlowConventionsResponse.  # noqa: E501
        :rtype: str
        """
        return self._href

    @href.setter
    def href(self, href):
        """Sets the href of this GetCdsFlowConventionsResponse.

        The specific Uniform Resource Identifier (URI) for this resource at the requested effective and asAt datetime.  # noqa: E501

        :param href: The href of this GetCdsFlowConventionsResponse.  # noqa: E501
        :type href: str
        """

        self._href = href

    @property
    def value(self):
        """Gets the value of this GetCdsFlowConventionsResponse.  # noqa: E501


        :return: The value of this GetCdsFlowConventionsResponse.  # noqa: E501
        :rtype: lusid_asyncio.CdsFlowConventions
        """
        return self._value

    @value.setter
    def value(self, value):
        """Sets the value of this GetCdsFlowConventionsResponse.


        :param value: The value of this GetCdsFlowConventionsResponse.  # noqa: E501
        :type value: lusid_asyncio.CdsFlowConventions
        """

        self._value = value

    @property
    def failed(self):
        """Gets the failed of this GetCdsFlowConventionsResponse.  # noqa: E501

        The identifiers that did not resolve to a conventions along with the nature of the failure.  # noqa: E501

        :return: The failed of this GetCdsFlowConventionsResponse.  # noqa: E501
        :rtype: dict[str, lusid_asyncio.ErrorDetail]
        """
        return self._failed

    @failed.setter
    def failed(self, failed):
        """Sets the failed of this GetCdsFlowConventionsResponse.

        The identifiers that did not resolve to a conventions along with the nature of the failure.  # noqa: E501

        :param failed: The failed of this GetCdsFlowConventionsResponse.  # noqa: E501
        :type failed: dict[str, lusid_asyncio.ErrorDetail]
        """

        self._failed = failed

    @property
    def links(self):
        """Gets the links of this GetCdsFlowConventionsResponse.  # noqa: E501

        Collection of links.  # noqa: E501

        :return: The links of this GetCdsFlowConventionsResponse.  # noqa: E501
        :rtype: list[lusid_asyncio.Link]
        """
        return self._links

    @links.setter
    def links(self, links):
        """Sets the links of this GetCdsFlowConventionsResponse.

        Collection of links.  # noqa: E501

        :param links: The links of this GetCdsFlowConventionsResponse.  # noqa: E501
        :type links: list[lusid_asyncio.Link]
        """

        self._links = links

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
        if not isinstance(other, GetCdsFlowConventionsResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, GetCdsFlowConventionsResponse):
            return True

        return self.to_dict() != other.to_dict()
