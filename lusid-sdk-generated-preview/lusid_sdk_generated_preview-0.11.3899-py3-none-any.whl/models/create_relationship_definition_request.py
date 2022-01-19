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


class CreateRelationshipDefinitionRequest(object):
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
        'scope': 'str',
        'code': 'str',
        'source_entity_type': 'str',
        'target_entity_type': 'str',
        'display_name': 'str',
        'outward_description': 'str',
        'inward_description': 'str',
        'life_time': 'str',
        'relationship_cardinality': 'str'
    }

    attribute_map = {
        'scope': 'scope',
        'code': 'code',
        'source_entity_type': 'sourceEntityType',
        'target_entity_type': 'targetEntityType',
        'display_name': 'displayName',
        'outward_description': 'outwardDescription',
        'inward_description': 'inwardDescription',
        'life_time': 'lifeTime',
        'relationship_cardinality': 'relationshipCardinality'
    }

    required_map = {
        'scope': 'required',
        'code': 'required',
        'source_entity_type': 'required',
        'target_entity_type': 'required',
        'display_name': 'required',
        'outward_description': 'required',
        'inward_description': 'required',
        'life_time': 'optional',
        'relationship_cardinality': 'optional'
    }

    def __init__(self, scope=None, code=None, source_entity_type=None, target_entity_type=None, display_name=None, outward_description=None, inward_description=None, life_time=None, relationship_cardinality=None, local_vars_configuration=None):  # noqa: E501
        """CreateRelationshipDefinitionRequest - a model defined in OpenAPI"
        
        :param scope:  The scope that the relationship definition exists in. (required)
        :type scope: str
        :param code:  The code of the relationship definition. Together with the scope this uniquely defines the relationship definition. (required)
        :type code: str
        :param source_entity_type:  The entity type of the source entity object. Allowed values are 'Portfolio', 'PortfolioGroup', 'Person', 'LegalEntity' or a custom entity type prefixed with '~'. (required)
        :type source_entity_type: str
        :param target_entity_type:  The entity type of the target entity object. Allowed values are 'Portfolio', 'PortfolioGroup', 'Person', 'LegalEntity' or a custom entity type prefixed with '~'. (required)
        :type target_entity_type: str
        :param display_name:  The display name of the relationship definition. (required)
        :type display_name: str
        :param outward_description:  The description to relate source entity object and target entity object. (required)
        :type outward_description: str
        :param inward_description:  The description to relate target entity object and source entity object. (required)
        :type inward_description: str
        :param life_time:  Describes how the relationships can change over time. Allowed values are 'Perpetual' and 'TimeVariant', defaults to 'Perpetual' if not specified.
        :type life_time: str
        :param relationship_cardinality:  Describes the cardinality of the relationship with a specific source entity object and relationships under this definition. Allowed values are 'ManyToMany' and 'OneToMany', defaults to 'ManyToMany' if not specified.
        :type relationship_cardinality: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._scope = None
        self._code = None
        self._source_entity_type = None
        self._target_entity_type = None
        self._display_name = None
        self._outward_description = None
        self._inward_description = None
        self._life_time = None
        self._relationship_cardinality = None
        self.discriminator = None

        self.scope = scope
        self.code = code
        self.source_entity_type = source_entity_type
        self.target_entity_type = target_entity_type
        self.display_name = display_name
        self.outward_description = outward_description
        self.inward_description = inward_description
        self.life_time = life_time
        self.relationship_cardinality = relationship_cardinality

    @property
    def scope(self):
        """Gets the scope of this CreateRelationshipDefinitionRequest.  # noqa: E501

        The scope that the relationship definition exists in.  # noqa: E501

        :return: The scope of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :rtype: str
        """
        return self._scope

    @scope.setter
    def scope(self, scope):
        """Sets the scope of this CreateRelationshipDefinitionRequest.

        The scope that the relationship definition exists in.  # noqa: E501

        :param scope: The scope of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :type scope: str
        """
        if self.local_vars_configuration.client_side_validation and scope is None:  # noqa: E501
            raise ValueError("Invalid value for `scope`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                scope is not None and len(scope) > 64):
            raise ValueError("Invalid value for `scope`, length must be less than or equal to `64`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                scope is not None and len(scope) < 1):
            raise ValueError("Invalid value for `scope`, length must be greater than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                scope is not None and not re.search(r'^[a-zA-Z0-9\-_]+$', scope)):  # noqa: E501
            raise ValueError(r"Invalid value for `scope`, must be a follow pattern or equal to `/^[a-zA-Z0-9\-_]+$/`")  # noqa: E501

        self._scope = scope

    @property
    def code(self):
        """Gets the code of this CreateRelationshipDefinitionRequest.  # noqa: E501

        The code of the relationship definition. Together with the scope this uniquely defines the relationship definition.  # noqa: E501

        :return: The code of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets the code of this CreateRelationshipDefinitionRequest.

        The code of the relationship definition. Together with the scope this uniquely defines the relationship definition.  # noqa: E501

        :param code: The code of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :type code: str
        """
        if self.local_vars_configuration.client_side_validation and code is None:  # noqa: E501
            raise ValueError("Invalid value for `code`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                code is not None and len(code) > 64):
            raise ValueError("Invalid value for `code`, length must be less than or equal to `64`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                code is not None and len(code) < 1):
            raise ValueError("Invalid value for `code`, length must be greater than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                code is not None and not re.search(r'^[a-zA-Z0-9\-_]+$', code)):  # noqa: E501
            raise ValueError(r"Invalid value for `code`, must be a follow pattern or equal to `/^[a-zA-Z0-9\-_]+$/`")  # noqa: E501

        self._code = code

    @property
    def source_entity_type(self):
        """Gets the source_entity_type of this CreateRelationshipDefinitionRequest.  # noqa: E501

        The entity type of the source entity object. Allowed values are 'Portfolio', 'PortfolioGroup', 'Person', 'LegalEntity' or a custom entity type prefixed with '~'.  # noqa: E501

        :return: The source_entity_type of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :rtype: str
        """
        return self._source_entity_type

    @source_entity_type.setter
    def source_entity_type(self, source_entity_type):
        """Sets the source_entity_type of this CreateRelationshipDefinitionRequest.

        The entity type of the source entity object. Allowed values are 'Portfolio', 'PortfolioGroup', 'Person', 'LegalEntity' or a custom entity type prefixed with '~'.  # noqa: E501

        :param source_entity_type: The source_entity_type of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :type source_entity_type: str
        """
        if self.local_vars_configuration.client_side_validation and source_entity_type is None:  # noqa: E501
            raise ValueError("Invalid value for `source_entity_type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                source_entity_type is not None and len(source_entity_type) > 64):
            raise ValueError("Invalid value for `source_entity_type`, length must be less than or equal to `64`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                source_entity_type is not None and len(source_entity_type) < 1):
            raise ValueError("Invalid value for `source_entity_type`, length must be greater than or equal to `1`")  # noqa: E501

        self._source_entity_type = source_entity_type

    @property
    def target_entity_type(self):
        """Gets the target_entity_type of this CreateRelationshipDefinitionRequest.  # noqa: E501

        The entity type of the target entity object. Allowed values are 'Portfolio', 'PortfolioGroup', 'Person', 'LegalEntity' or a custom entity type prefixed with '~'.  # noqa: E501

        :return: The target_entity_type of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :rtype: str
        """
        return self._target_entity_type

    @target_entity_type.setter
    def target_entity_type(self, target_entity_type):
        """Sets the target_entity_type of this CreateRelationshipDefinitionRequest.

        The entity type of the target entity object. Allowed values are 'Portfolio', 'PortfolioGroup', 'Person', 'LegalEntity' or a custom entity type prefixed with '~'.  # noqa: E501

        :param target_entity_type: The target_entity_type of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :type target_entity_type: str
        """
        if self.local_vars_configuration.client_side_validation and target_entity_type is None:  # noqa: E501
            raise ValueError("Invalid value for `target_entity_type`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                target_entity_type is not None and len(target_entity_type) > 64):
            raise ValueError("Invalid value for `target_entity_type`, length must be less than or equal to `64`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                target_entity_type is not None and len(target_entity_type) < 1):
            raise ValueError("Invalid value for `target_entity_type`, length must be greater than or equal to `1`")  # noqa: E501

        self._target_entity_type = target_entity_type

    @property
    def display_name(self):
        """Gets the display_name of this CreateRelationshipDefinitionRequest.  # noqa: E501

        The display name of the relationship definition.  # noqa: E501

        :return: The display_name of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """Sets the display_name of this CreateRelationshipDefinitionRequest.

        The display name of the relationship definition.  # noqa: E501

        :param display_name: The display_name of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :type display_name: str
        """
        if self.local_vars_configuration.client_side_validation and display_name is None:  # noqa: E501
            raise ValueError("Invalid value for `display_name`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                display_name is not None and len(display_name) > 512):
            raise ValueError("Invalid value for `display_name`, length must be less than or equal to `512`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                display_name is not None and len(display_name) < 1):
            raise ValueError("Invalid value for `display_name`, length must be greater than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                display_name is not None and not re.search(r'^[\s\S]*$', display_name)):  # noqa: E501
            raise ValueError(r"Invalid value for `display_name`, must be a follow pattern or equal to `/^[\s\S]*$/`")  # noqa: E501

        self._display_name = display_name

    @property
    def outward_description(self):
        """Gets the outward_description of this CreateRelationshipDefinitionRequest.  # noqa: E501

        The description to relate source entity object and target entity object.  # noqa: E501

        :return: The outward_description of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :rtype: str
        """
        return self._outward_description

    @outward_description.setter
    def outward_description(self, outward_description):
        """Sets the outward_description of this CreateRelationshipDefinitionRequest.

        The description to relate source entity object and target entity object.  # noqa: E501

        :param outward_description: The outward_description of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :type outward_description: str
        """
        if self.local_vars_configuration.client_side_validation and outward_description is None:  # noqa: E501
            raise ValueError("Invalid value for `outward_description`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                outward_description is not None and len(outward_description) > 512):
            raise ValueError("Invalid value for `outward_description`, length must be less than or equal to `512`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                outward_description is not None and len(outward_description) < 1):
            raise ValueError("Invalid value for `outward_description`, length must be greater than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                outward_description is not None and not re.search(r'^[\s\S]*$', outward_description)):  # noqa: E501
            raise ValueError(r"Invalid value for `outward_description`, must be a follow pattern or equal to `/^[\s\S]*$/`")  # noqa: E501

        self._outward_description = outward_description

    @property
    def inward_description(self):
        """Gets the inward_description of this CreateRelationshipDefinitionRequest.  # noqa: E501

        The description to relate target entity object and source entity object.  # noqa: E501

        :return: The inward_description of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :rtype: str
        """
        return self._inward_description

    @inward_description.setter
    def inward_description(self, inward_description):
        """Sets the inward_description of this CreateRelationshipDefinitionRequest.

        The description to relate target entity object and source entity object.  # noqa: E501

        :param inward_description: The inward_description of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :type inward_description: str
        """
        if self.local_vars_configuration.client_side_validation and inward_description is None:  # noqa: E501
            raise ValueError("Invalid value for `inward_description`, must not be `None`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                inward_description is not None and len(inward_description) > 512):
            raise ValueError("Invalid value for `inward_description`, length must be less than or equal to `512`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                inward_description is not None and len(inward_description) < 1):
            raise ValueError("Invalid value for `inward_description`, length must be greater than or equal to `1`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                inward_description is not None and not re.search(r'^[\s\S]*$', inward_description)):  # noqa: E501
            raise ValueError(r"Invalid value for `inward_description`, must be a follow pattern or equal to `/^[\s\S]*$/`")  # noqa: E501

        self._inward_description = inward_description

    @property
    def life_time(self):
        """Gets the life_time of this CreateRelationshipDefinitionRequest.  # noqa: E501

        Describes how the relationships can change over time. Allowed values are 'Perpetual' and 'TimeVariant', defaults to 'Perpetual' if not specified.  # noqa: E501

        :return: The life_time of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :rtype: str
        """
        return self._life_time

    @life_time.setter
    def life_time(self, life_time):
        """Sets the life_time of this CreateRelationshipDefinitionRequest.

        Describes how the relationships can change over time. Allowed values are 'Perpetual' and 'TimeVariant', defaults to 'Perpetual' if not specified.  # noqa: E501

        :param life_time: The life_time of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :type life_time: str
        """

        self._life_time = life_time

    @property
    def relationship_cardinality(self):
        """Gets the relationship_cardinality of this CreateRelationshipDefinitionRequest.  # noqa: E501

        Describes the cardinality of the relationship with a specific source entity object and relationships under this definition. Allowed values are 'ManyToMany' and 'OneToMany', defaults to 'ManyToMany' if not specified.  # noqa: E501

        :return: The relationship_cardinality of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :rtype: str
        """
        return self._relationship_cardinality

    @relationship_cardinality.setter
    def relationship_cardinality(self, relationship_cardinality):
        """Sets the relationship_cardinality of this CreateRelationshipDefinitionRequest.

        Describes the cardinality of the relationship with a specific source entity object and relationships under this definition. Allowed values are 'ManyToMany' and 'OneToMany', defaults to 'ManyToMany' if not specified.  # noqa: E501

        :param relationship_cardinality: The relationship_cardinality of this CreateRelationshipDefinitionRequest.  # noqa: E501
        :type relationship_cardinality: str
        """

        self._relationship_cardinality = relationship_cardinality

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
        if not isinstance(other, CreateRelationshipDefinitionRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateRelationshipDefinitionRequest):
            return True

        return self.to_dict() != other.to_dict()
