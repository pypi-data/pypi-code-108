# coding: utf-8

"""
    Pulp 3 API

    Fetch, Upload, Organize, and Distribute Software Packages  # noqa: E501

    The version of the OpenAPI document: v3
    Contact: pulp-list@redhat.com
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six

from pulpcore.client.pulp_container.configuration import Configuration


class ContainerContainerPushRepositoryResponse(object):
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
    """
    openapi_types = {
        'versions_href': 'str',
        'pulp_labels': 'object',
        'description': 'str',
        'pulp_created': 'datetime',
        'name': 'str',
        'latest_version_href': 'str',
        'retain_repo_versions': 'int',
        'pulp_href': 'str'
    }

    attribute_map = {
        'versions_href': 'versions_href',
        'pulp_labels': 'pulp_labels',
        'description': 'description',
        'pulp_created': 'pulp_created',
        'name': 'name',
        'latest_version_href': 'latest_version_href',
        'retain_repo_versions': 'retain_repo_versions',
        'pulp_href': 'pulp_href'
    }

    def __init__(self, versions_href=None, pulp_labels=None, description=None, pulp_created=None, name=None, latest_version_href=None, retain_repo_versions=None, pulp_href=None, local_vars_configuration=None):  # noqa: E501
        """ContainerContainerPushRepositoryResponse - a model defined in OpenAPI"""  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration()
        self.local_vars_configuration = local_vars_configuration

        self._versions_href = None
        self._pulp_labels = None
        self._description = None
        self._pulp_created = None
        self._name = None
        self._latest_version_href = None
        self._retain_repo_versions = None
        self._pulp_href = None
        self.discriminator = None

        if versions_href is not None:
            self.versions_href = versions_href
        if pulp_labels is not None:
            self.pulp_labels = pulp_labels
        self.description = description
        if pulp_created is not None:
            self.pulp_created = pulp_created
        self.name = name
        if latest_version_href is not None:
            self.latest_version_href = latest_version_href
        self.retain_repo_versions = retain_repo_versions
        if pulp_href is not None:
            self.pulp_href = pulp_href

    @property
    def versions_href(self):
        """Gets the versions_href of this ContainerContainerPushRepositoryResponse.  # noqa: E501


        :return: The versions_href of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :rtype: str
        """
        return self._versions_href

    @versions_href.setter
    def versions_href(self, versions_href):
        """Sets the versions_href of this ContainerContainerPushRepositoryResponse.


        :param versions_href: The versions_href of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :type: str
        """

        self._versions_href = versions_href

    @property
    def pulp_labels(self):
        """Gets the pulp_labels of this ContainerContainerPushRepositoryResponse.  # noqa: E501


        :return: The pulp_labels of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :rtype: object
        """
        return self._pulp_labels

    @pulp_labels.setter
    def pulp_labels(self, pulp_labels):
        """Sets the pulp_labels of this ContainerContainerPushRepositoryResponse.


        :param pulp_labels: The pulp_labels of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :type: object
        """

        self._pulp_labels = pulp_labels

    @property
    def description(self):
        """Gets the description of this ContainerContainerPushRepositoryResponse.  # noqa: E501

        An optional description.  # noqa: E501

        :return: The description of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this ContainerContainerPushRepositoryResponse.

        An optional description.  # noqa: E501

        :param description: The description of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :type: str
        """

        self._description = description

    @property
    def pulp_created(self):
        """Gets the pulp_created of this ContainerContainerPushRepositoryResponse.  # noqa: E501

        Timestamp of creation.  # noqa: E501

        :return: The pulp_created of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :rtype: datetime
        """
        return self._pulp_created

    @pulp_created.setter
    def pulp_created(self, pulp_created):
        """Sets the pulp_created of this ContainerContainerPushRepositoryResponse.

        Timestamp of creation.  # noqa: E501

        :param pulp_created: The pulp_created of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :type: datetime
        """

        self._pulp_created = pulp_created

    @property
    def name(self):
        """Gets the name of this ContainerContainerPushRepositoryResponse.  # noqa: E501

        A unique name for this repository.  # noqa: E501

        :return: The name of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this ContainerContainerPushRepositoryResponse.

        A unique name for this repository.  # noqa: E501

        :param name: The name of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :type: str
        """
        if self.local_vars_configuration.client_side_validation and name is None:  # noqa: E501
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def latest_version_href(self):
        """Gets the latest_version_href of this ContainerContainerPushRepositoryResponse.  # noqa: E501


        :return: The latest_version_href of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :rtype: str
        """
        return self._latest_version_href

    @latest_version_href.setter
    def latest_version_href(self, latest_version_href):
        """Sets the latest_version_href of this ContainerContainerPushRepositoryResponse.


        :param latest_version_href: The latest_version_href of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :type: str
        """

        self._latest_version_href = latest_version_href

    @property
    def retain_repo_versions(self):
        """Gets the retain_repo_versions of this ContainerContainerPushRepositoryResponse.  # noqa: E501

        Retain X versions of the repository. Default is null which retains all versions. This is provided as a tech preview in Pulp 3 and may change in the future.  # noqa: E501

        :return: The retain_repo_versions of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :rtype: int
        """
        return self._retain_repo_versions

    @retain_repo_versions.setter
    def retain_repo_versions(self, retain_repo_versions):
        """Sets the retain_repo_versions of this ContainerContainerPushRepositoryResponse.

        Retain X versions of the repository. Default is null which retains all versions. This is provided as a tech preview in Pulp 3 and may change in the future.  # noqa: E501

        :param retain_repo_versions: The retain_repo_versions of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :type: int
        """
        if (self.local_vars_configuration.client_side_validation and
                retain_repo_versions is not None and retain_repo_versions < 1):  # noqa: E501
            raise ValueError("Invalid value for `retain_repo_versions`, must be a value greater than or equal to `1`")  # noqa: E501

        self._retain_repo_versions = retain_repo_versions

    @property
    def pulp_href(self):
        """Gets the pulp_href of this ContainerContainerPushRepositoryResponse.  # noqa: E501


        :return: The pulp_href of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :rtype: str
        """
        return self._pulp_href

    @pulp_href.setter
    def pulp_href(self, pulp_href):
        """Sets the pulp_href of this ContainerContainerPushRepositoryResponse.


        :param pulp_href: The pulp_href of this ContainerContainerPushRepositoryResponse.  # noqa: E501
        :type: str
        """

        self._pulp_href = pulp_href

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
        if not isinstance(other, ContainerContainerPushRepositoryResponse):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, ContainerContainerPushRepositoryResponse):
            return True

        return self.to_dict() != other.to_dict()
