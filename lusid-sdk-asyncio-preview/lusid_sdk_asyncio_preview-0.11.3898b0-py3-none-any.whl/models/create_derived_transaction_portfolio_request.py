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


class CreateDerivedTransactionPortfolioRequest(object):
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
        'display_name': 'str',
        'description': 'str',
        'code': 'str',
        'parent_portfolio_id': 'ResourceId',
        'created': 'datetime',
        'corporate_action_source_id': 'ResourceId',
        'accounting_method': 'str',
        'sub_holding_keys': 'list[str]',
        'instrument_scopes': 'list[str]'
    }

    attribute_map = {
        'display_name': 'displayName',
        'description': 'description',
        'code': 'code',
        'parent_portfolio_id': 'parentPortfolioId',
        'created': 'created',
        'corporate_action_source_id': 'corporateActionSourceId',
        'accounting_method': 'accountingMethod',
        'sub_holding_keys': 'subHoldingKeys',
        'instrument_scopes': 'instrumentScopes'
    }

    required_map = {
        'display_name': 'required',
        'description': 'optional',
        'code': 'required',
        'parent_portfolio_id': 'required',
        'created': 'optional',
        'corporate_action_source_id': 'optional',
        'accounting_method': 'optional',
        'sub_holding_keys': 'optional',
        'instrument_scopes': 'optional'
    }

    def __init__(self, display_name=None, description=None, code=None, parent_portfolio_id=None, created=None, corporate_action_source_id=None, accounting_method=None, sub_holding_keys=None, instrument_scopes=None, local_vars_configuration=None):  # noqa: E501
        """CreateDerivedTransactionPortfolioRequest - a model defined in OpenAPI"
        
        :param display_name:  The name of the derived transaction portfolio. (required)
        :type display_name: str
        :param description:  A description for the derived transaction portfolio.
        :type description: str
        :param code:  The code of the derived transaction portfolio. Together with the scope this uniquely identifies the derived transaction portfolio. (required)
        :type code: str
        :param parent_portfolio_id:  (required)
        :type parent_portfolio_id: lusid_asyncio.ResourceId
        :param created:  The effective datetime at which to create the derived transaction portfolio. No transactions can be added to the derived transaction portfolio before this date. Defaults to the current LUSID system datetime if not specified.
        :type created: datetime
        :param corporate_action_source_id: 
        :type corporate_action_source_id: lusid_asyncio.ResourceId
        :param accounting_method:  Determines the accounting treatment given to the transaction portfolio's tax lots. The available values are: Default, AverageCost, FirstInFirstOut, LastInFirstOut, HighestCostFirst, LowestCostFirst
        :type accounting_method: str
        :param sub_holding_keys:  A set of unique transaction properties to group the derived transaction portfolio's holdings by, perhaps for strategy tagging. Each property must be from the 'Transaction' domain and identified by a key in the format {domain}/{scope}/{code}, for example 'Transaction/strategies/quantsignal'. Note that sub-holding keys cannot currently be added after the transaction portfolio has been created; see https://support.lusid.com/knowledgebase/article/KA-01879/en-us for more information.
        :type sub_holding_keys: list[str]
        :param instrument_scopes:  The resolution strategy used to resolve instruments of transactions/holdings upserted to this derived portfolio.
        :type instrument_scopes: list[str]

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._display_name = None
        self._description = None
        self._code = None
        self._parent_portfolio_id = None
        self._created = None
        self._corporate_action_source_id = None
        self._accounting_method = None
        self._sub_holding_keys = None
        self._instrument_scopes = None
        self.discriminator = None

        self.display_name = display_name
        self.description = description
        self.code = code
        self.parent_portfolio_id = parent_portfolio_id
        self.created = created
        if corporate_action_source_id is not None:
            self.corporate_action_source_id = corporate_action_source_id
        if accounting_method is not None:
            self.accounting_method = accounting_method
        self.sub_holding_keys = sub_holding_keys
        self.instrument_scopes = instrument_scopes

    @property
    def display_name(self):
        """Gets the display_name of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501

        The name of the derived transaction portfolio.  # noqa: E501

        :return: The display_name of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :rtype: str
        """
        return self._display_name

    @display_name.setter
    def display_name(self, display_name):
        """Sets the display_name of this CreateDerivedTransactionPortfolioRequest.

        The name of the derived transaction portfolio.  # noqa: E501

        :param display_name: The display_name of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
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
    def description(self):
        """Gets the description of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501

        A description for the derived transaction portfolio.  # noqa: E501

        :return: The description of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this CreateDerivedTransactionPortfolioRequest.

        A description for the derived transaction portfolio.  # noqa: E501

        :param description: The description of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :type description: str
        """
        if (self.local_vars_configuration.client_side_validation and
                description is not None and len(description) > 1024):
            raise ValueError("Invalid value for `description`, length must be less than or equal to `1024`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                description is not None and len(description) < 0):
            raise ValueError("Invalid value for `description`, length must be greater than or equal to `0`")  # noqa: E501
        if (self.local_vars_configuration.client_side_validation and
                description is not None and not re.search(r'^[\s\S]*$', description)):  # noqa: E501
            raise ValueError(r"Invalid value for `description`, must be a follow pattern or equal to `/^[\s\S]*$/`")  # noqa: E501

        self._description = description

    @property
    def code(self):
        """Gets the code of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501

        The code of the derived transaction portfolio. Together with the scope this uniquely identifies the derived transaction portfolio.  # noqa: E501

        :return: The code of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """Sets the code of this CreateDerivedTransactionPortfolioRequest.

        The code of the derived transaction portfolio. Together with the scope this uniquely identifies the derived transaction portfolio.  # noqa: E501

        :param code: The code of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
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
    def parent_portfolio_id(self):
        """Gets the parent_portfolio_id of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501


        :return: The parent_portfolio_id of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :rtype: lusid_asyncio.ResourceId
        """
        return self._parent_portfolio_id

    @parent_portfolio_id.setter
    def parent_portfolio_id(self, parent_portfolio_id):
        """Sets the parent_portfolio_id of this CreateDerivedTransactionPortfolioRequest.


        :param parent_portfolio_id: The parent_portfolio_id of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :type parent_portfolio_id: lusid_asyncio.ResourceId
        """
        if self.local_vars_configuration.client_side_validation and parent_portfolio_id is None:  # noqa: E501
            raise ValueError("Invalid value for `parent_portfolio_id`, must not be `None`")  # noqa: E501

        self._parent_portfolio_id = parent_portfolio_id

    @property
    def created(self):
        """Gets the created of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501

        The effective datetime at which to create the derived transaction portfolio. No transactions can be added to the derived transaction portfolio before this date. Defaults to the current LUSID system datetime if not specified.  # noqa: E501

        :return: The created of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :rtype: datetime
        """
        return self._created

    @created.setter
    def created(self, created):
        """Sets the created of this CreateDerivedTransactionPortfolioRequest.

        The effective datetime at which to create the derived transaction portfolio. No transactions can be added to the derived transaction portfolio before this date. Defaults to the current LUSID system datetime if not specified.  # noqa: E501

        :param created: The created of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :type created: datetime
        """

        self._created = created

    @property
    def corporate_action_source_id(self):
        """Gets the corporate_action_source_id of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501


        :return: The corporate_action_source_id of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :rtype: lusid_asyncio.ResourceId
        """
        return self._corporate_action_source_id

    @corporate_action_source_id.setter
    def corporate_action_source_id(self, corporate_action_source_id):
        """Sets the corporate_action_source_id of this CreateDerivedTransactionPortfolioRequest.


        :param corporate_action_source_id: The corporate_action_source_id of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :type corporate_action_source_id: lusid_asyncio.ResourceId
        """

        self._corporate_action_source_id = corporate_action_source_id

    @property
    def accounting_method(self):
        """Gets the accounting_method of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501

        Determines the accounting treatment given to the transaction portfolio's tax lots. The available values are: Default, AverageCost, FirstInFirstOut, LastInFirstOut, HighestCostFirst, LowestCostFirst  # noqa: E501

        :return: The accounting_method of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :rtype: str
        """
        return self._accounting_method

    @accounting_method.setter
    def accounting_method(self, accounting_method):
        """Sets the accounting_method of this CreateDerivedTransactionPortfolioRequest.

        Determines the accounting treatment given to the transaction portfolio's tax lots. The available values are: Default, AverageCost, FirstInFirstOut, LastInFirstOut, HighestCostFirst, LowestCostFirst  # noqa: E501

        :param accounting_method: The accounting_method of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :type accounting_method: str
        """
        allowed_values = ["Default", "AverageCost", "FirstInFirstOut", "LastInFirstOut", "HighestCostFirst", "LowestCostFirst"]  # noqa: E501
        if self.local_vars_configuration.client_side_validation and accounting_method not in allowed_values:  # noqa: E501
            raise ValueError(
                "Invalid value for `accounting_method` ({0}), must be one of {1}"  # noqa: E501
                .format(accounting_method, allowed_values)
            )

        self._accounting_method = accounting_method

    @property
    def sub_holding_keys(self):
        """Gets the sub_holding_keys of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501

        A set of unique transaction properties to group the derived transaction portfolio's holdings by, perhaps for strategy tagging. Each property must be from the 'Transaction' domain and identified by a key in the format {domain}/{scope}/{code}, for example 'Transaction/strategies/quantsignal'. Note that sub-holding keys cannot currently be added after the transaction portfolio has been created; see https://support.lusid.com/knowledgebase/article/KA-01879/en-us for more information.  # noqa: E501

        :return: The sub_holding_keys of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._sub_holding_keys

    @sub_holding_keys.setter
    def sub_holding_keys(self, sub_holding_keys):
        """Sets the sub_holding_keys of this CreateDerivedTransactionPortfolioRequest.

        A set of unique transaction properties to group the derived transaction portfolio's holdings by, perhaps for strategy tagging. Each property must be from the 'Transaction' domain and identified by a key in the format {domain}/{scope}/{code}, for example 'Transaction/strategies/quantsignal'. Note that sub-holding keys cannot currently be added after the transaction portfolio has been created; see https://support.lusid.com/knowledgebase/article/KA-01879/en-us for more information.  # noqa: E501

        :param sub_holding_keys: The sub_holding_keys of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :type sub_holding_keys: list[str]
        """

        self._sub_holding_keys = sub_holding_keys

    @property
    def instrument_scopes(self):
        """Gets the instrument_scopes of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501

        The resolution strategy used to resolve instruments of transactions/holdings upserted to this derived portfolio.  # noqa: E501

        :return: The instrument_scopes of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :rtype: list[str]
        """
        return self._instrument_scopes

    @instrument_scopes.setter
    def instrument_scopes(self, instrument_scopes):
        """Sets the instrument_scopes of this CreateDerivedTransactionPortfolioRequest.

        The resolution strategy used to resolve instruments of transactions/holdings upserted to this derived portfolio.  # noqa: E501

        :param instrument_scopes: The instrument_scopes of this CreateDerivedTransactionPortfolioRequest.  # noqa: E501
        :type instrument_scopes: list[str]
        """

        self._instrument_scopes = instrument_scopes

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
        if not isinstance(other, CreateDerivedTransactionPortfolioRequest):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, CreateDerivedTransactionPortfolioRequest):
            return True

        return self.to_dict() != other.to_dict()
