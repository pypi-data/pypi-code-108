# coding: utf-8

"""
    LUSID API

    FINBOURNE Technology  # noqa: E501

    The version of the OpenAPI document: 0.11.3899
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

from lusid.configuration import Configuration


class Relation(object):
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
        'version': 'Version',
        'relation_definition_id': 'ResourceId',
        'related_entity_id': 'dict(str, str)',
        'traversal_direction': 'str',
        'traversal_description': 'str',
        'effective_from': 'datetime'
    }

    attribute_map = {
        'version': 'version',
        'relation_definition_id': 'relationDefinitionId',
        'related_entity_id': 'relatedEntityId',
        'traversal_direction': 'traversalDirection',
        'traversal_description': 'traversalDescription',
        'effective_from': 'effectiveFrom'
    }

    required_map = {
        'version': 'optional',
        'relation_definition_id': 'required',
        'related_entity_id': 'required',
        'traversal_direction': 'required',
        'traversal_description': 'required',
        'effective_from': 'optional'
    }

    def __init__(self, version=None, relation_definition_id=None, related_entity_id=None, traversal_direction=None, traversal_description=None, effective_from=None, local_vars_configuration=None):  # noqa: E501
        """Relation - a model defined in OpenAPI"
        
        :param version: 
        :type version: lusid.Version
        :param relation_definition_id:  (required)
        :type relation_definition_id: lusid.ResourceId
        :param related_entity_id:  (required)
        :type related_entity_id: dict(str, str)
        :param traversal_direction:  (required)
        :type traversal_direction: str
        :param traversal_description:  (required)
        :type traversal_description: str
        :param effective_from: 
        :type effective_from: datetime

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._version = None
        self._relation_definition_id = None
        self._related_entity_id = None
        self._traversal_direction = None
        self._traversal_description = None
        self._effective_from = None
        self.discriminator = None

        if version is not None:
            self.version = version
        self.relation_definition_id = relation_definition_id
        self.related_entity_id = related_entity_id
        self.traversal_direction = traversal_direction
        self.traversal_description = traversal_description
        if effective_from is not None:
            self.effective_from = effective_from

    @property
    def version(self):
        """Gets the version of this Relation.  # noqa: E501


        :return: The version of this Relation.  # noqa: E501
        :rtype: lusid.Version
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this Relation.


        :param version: The version of this Relation.  # noqa: E501
        :type version: lusid.Version
        """

        self._version = version

    @property
    def relation_definition_id(self):
        """Gets the relation_definition_id of this Relation.  # noqa: E501


        :return: The relation_definition_id of this Relation.  # noqa: E501
        :rtype: lusid.ResourceId
        """
        return self._relation_definition_id

    @relation_definition_id.setter
    def relation_definition_id(self, relation_definition_id):
        """Sets the relation_definition_id of this Relation.


        :param relation_definition_id: The relation_definition_id of this Relation.  # noqa: E501
        :type relation_definition_id: lusid.ResourceId
        """
        if self.local_vars_configuration.client_side_validation and relation_definition_id is None:  # noqa: E501
            raise ValueError("Invalid value for `relation_definition_id`, must not be `None`")  # noqa: E501

        self._relation_definition_id = relation_definition_id

    @property
    def related_entity_id(self):
        """Gets the related_entity_id of this Relation.  # noqa: E501


        :return: The related_entity_id of this Relation.  # noqa: E501
        :rtype: dict(str, str)
        """
        return self._related_entity_id

    @related_entity_id.setter
    def related_entity_id(self, related_entity_id):
        """Sets the related_entity_id of this Relation.


        :param related_entity_id: The related_entity_id of this Relation.  # noqa: E501
        :type related_entity_id: dict(str, str)
        """
        if self.local_vars_configuration.client_side_validation and related_entity_id is None:  # noqa: E501
            raise ValueError("Invalid value for `related_entity_id`, must not be `None`")  # noqa: E501

        self._related_entity_id = related_entity_id

    @property
    def traversal_direction(self):
        """Gets the traversal_direction of this Relation.  # noqa: E501


        :return: The traversal_direction of this Relation.  # noqa: E501
        :rtype: str
        """
        return self._traversal_direction

    @traversal_direction.setter
    def traversal_direction(self, traversal_direction):
        """Sets the traversal_direction of this Relation.


        :param traversal_direction: The traversal_direction of this Relation.  # noqa: E501
        :type traversal_direction: str
        """
        if self.local_vars_configuration.client_side_validation and traversal_direction is None:  # noqa: E501
            raise ValueError("Invalid value for `traversal_direction`, must not be `None`")  # noqa: E501

        self._traversal_direction = traversal_direction

    @property
    def traversal_description(self):
        """Gets the traversal_description of this Relation.  # noqa: E501


        :return: The traversal_description of this Relation.  # noqa: E501
        :rtype: str
        """
        return self._traversal_description

    @traversal_description.setter
    def traversal_description(self, traversal_description):
        """Sets the traversal_description of this Relation.


        :param traversal_description: The traversal_description of this Relation.  # noqa: E501
        :type traversal_description: str
        """
        if self.local_vars_configuration.client_side_validation and traversal_description is None:  # noqa: E501
            raise ValueError("Invalid value for `traversal_description`, must not be `None`")  # noqa: E501

        self._traversal_description = traversal_description

    @property
    def effective_from(self):
        """Gets the effective_from of this Relation.  # noqa: E501


        :return: The effective_from of this Relation.  # noqa: E501
        :rtype: datetime
        """
        return self._effective_from

    @effective_from.setter
    def effective_from(self, effective_from):
        """Sets the effective_from of this Relation.


        :param effective_from: The effective_from of this Relation.  # noqa: E501
        :type effective_from: datetime
        """

        self._effective_from = effective_from

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
        if not isinstance(other, Relation):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, Relation):
            return True

        return self.to_dict() != other.to_dict()
