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


class A2BDataRecord(object):
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
        'portfolio_id': 'ResourceId',
        'holding_type': 'str',
        'instrument_scope': 'str',
        'instrument_uid': 'str',
        'sub_holding_keys': 'dict(str, PerpetualProperty)',
        'currency': 'str',
        'transaction_id': 'str',
        'start': 'A2BCategory',
        'flows': 'A2BCategory',
        'gains': 'A2BCategory',
        'carry': 'A2BCategory',
        'end': 'A2BCategory',
        'properties': 'dict(str, ModelProperty)',
        'group_id': 'str'
    }

    attribute_map = {
        'portfolio_id': 'portfolioId',
        'holding_type': 'holdingType',
        'instrument_scope': 'instrumentScope',
        'instrument_uid': 'instrumentUid',
        'sub_holding_keys': 'subHoldingKeys',
        'currency': 'currency',
        'transaction_id': 'transactionId',
        'start': 'start',
        'flows': 'flows',
        'gains': 'gains',
        'carry': 'carry',
        'end': 'end',
        'properties': 'properties',
        'group_id': 'groupId'
    }

    required_map = {
        'portfolio_id': 'optional',
        'holding_type': 'optional',
        'instrument_scope': 'optional',
        'instrument_uid': 'optional',
        'sub_holding_keys': 'optional',
        'currency': 'optional',
        'transaction_id': 'optional',
        'start': 'optional',
        'flows': 'optional',
        'gains': 'optional',
        'carry': 'optional',
        'end': 'optional',
        'properties': 'optional',
        'group_id': 'optional'
    }

    def __init__(self, portfolio_id=None, holding_type=None, instrument_scope=None, instrument_uid=None, sub_holding_keys=None, currency=None, transaction_id=None, start=None, flows=None, gains=None, carry=None, end=None, properties=None, group_id=None, local_vars_configuration=None):  # noqa: E501
        """A2BDataRecord - a model defined in OpenAPI"
        
        :param portfolio_id: 
        :type portfolio_id: lusid.ResourceId
        :param holding_type:  The type of the holding e.g. Position, Balance, CashCommitment, Receivable, ForwardFX etc.
        :type holding_type: str
        :param instrument_scope:  The unique Lusid Instrument Id (LUID) of the instrument that the holding is in.
        :type instrument_scope: str
        :param instrument_uid:  The unique Lusid Instrument Id (LUID) of the instrument that the holding is in.
        :type instrument_uid: str
        :param sub_holding_keys:  The sub-holding properties which identify the holding. Each property will be from the 'Transaction' domain. These are configured when a transaction portfolio is created.
        :type sub_holding_keys: dict[str, lusid.PerpetualProperty]
        :param currency:  The holding currency.
        :type currency: str
        :param transaction_id:  The unique identifier for the transaction.
        :type transaction_id: str
        :param start: 
        :type start: lusid.A2BCategory
        :param flows: 
        :type flows: lusid.A2BCategory
        :param gains: 
        :type gains: lusid.A2BCategory
        :param carry: 
        :type carry: lusid.A2BCategory
        :param end: 
        :type end: lusid.A2BCategory
        :param properties:  The properties which have been requested to be decorated onto the holding. These will be from the 'Instrument' domain.
        :type properties: dict[str, lusid.ModelProperty]
        :param group_id:  Arbitrary string that can be used to cross reference an entry in the A2B report with activity in the A2B-Movements. This should be used purely as a token. The content should not be relied upon.
        :type group_id: str

        """  # noqa: E501
        if local_vars_configuration is None:
            local_vars_configuration = Configuration.get_default_copy()
        self.local_vars_configuration = local_vars_configuration

        self._portfolio_id = None
        self._holding_type = None
        self._instrument_scope = None
        self._instrument_uid = None
        self._sub_holding_keys = None
        self._currency = None
        self._transaction_id = None
        self._start = None
        self._flows = None
        self._gains = None
        self._carry = None
        self._end = None
        self._properties = None
        self._group_id = None
        self.discriminator = None

        if portfolio_id is not None:
            self.portfolio_id = portfolio_id
        self.holding_type = holding_type
        self.instrument_scope = instrument_scope
        self.instrument_uid = instrument_uid
        self.sub_holding_keys = sub_holding_keys
        self.currency = currency
        self.transaction_id = transaction_id
        if start is not None:
            self.start = start
        if flows is not None:
            self.flows = flows
        if gains is not None:
            self.gains = gains
        if carry is not None:
            self.carry = carry
        if end is not None:
            self.end = end
        self.properties = properties
        self.group_id = group_id

    @property
    def portfolio_id(self):
        """Gets the portfolio_id of this A2BDataRecord.  # noqa: E501


        :return: The portfolio_id of this A2BDataRecord.  # noqa: E501
        :rtype: lusid.ResourceId
        """
        return self._portfolio_id

    @portfolio_id.setter
    def portfolio_id(self, portfolio_id):
        """Sets the portfolio_id of this A2BDataRecord.


        :param portfolio_id: The portfolio_id of this A2BDataRecord.  # noqa: E501
        :type portfolio_id: lusid.ResourceId
        """

        self._portfolio_id = portfolio_id

    @property
    def holding_type(self):
        """Gets the holding_type of this A2BDataRecord.  # noqa: E501

        The type of the holding e.g. Position, Balance, CashCommitment, Receivable, ForwardFX etc.  # noqa: E501

        :return: The holding_type of this A2BDataRecord.  # noqa: E501
        :rtype: str
        """
        return self._holding_type

    @holding_type.setter
    def holding_type(self, holding_type):
        """Sets the holding_type of this A2BDataRecord.

        The type of the holding e.g. Position, Balance, CashCommitment, Receivable, ForwardFX etc.  # noqa: E501

        :param holding_type: The holding_type of this A2BDataRecord.  # noqa: E501
        :type holding_type: str
        """

        self._holding_type = holding_type

    @property
    def instrument_scope(self):
        """Gets the instrument_scope of this A2BDataRecord.  # noqa: E501

        The unique Lusid Instrument Id (LUID) of the instrument that the holding is in.  # noqa: E501

        :return: The instrument_scope of this A2BDataRecord.  # noqa: E501
        :rtype: str
        """
        return self._instrument_scope

    @instrument_scope.setter
    def instrument_scope(self, instrument_scope):
        """Sets the instrument_scope of this A2BDataRecord.

        The unique Lusid Instrument Id (LUID) of the instrument that the holding is in.  # noqa: E501

        :param instrument_scope: The instrument_scope of this A2BDataRecord.  # noqa: E501
        :type instrument_scope: str
        """

        self._instrument_scope = instrument_scope

    @property
    def instrument_uid(self):
        """Gets the instrument_uid of this A2BDataRecord.  # noqa: E501

        The unique Lusid Instrument Id (LUID) of the instrument that the holding is in.  # noqa: E501

        :return: The instrument_uid of this A2BDataRecord.  # noqa: E501
        :rtype: str
        """
        return self._instrument_uid

    @instrument_uid.setter
    def instrument_uid(self, instrument_uid):
        """Sets the instrument_uid of this A2BDataRecord.

        The unique Lusid Instrument Id (LUID) of the instrument that the holding is in.  # noqa: E501

        :param instrument_uid: The instrument_uid of this A2BDataRecord.  # noqa: E501
        :type instrument_uid: str
        """

        self._instrument_uid = instrument_uid

    @property
    def sub_holding_keys(self):
        """Gets the sub_holding_keys of this A2BDataRecord.  # noqa: E501

        The sub-holding properties which identify the holding. Each property will be from the 'Transaction' domain. These are configured when a transaction portfolio is created.  # noqa: E501

        :return: The sub_holding_keys of this A2BDataRecord.  # noqa: E501
        :rtype: dict[str, lusid.PerpetualProperty]
        """
        return self._sub_holding_keys

    @sub_holding_keys.setter
    def sub_holding_keys(self, sub_holding_keys):
        """Sets the sub_holding_keys of this A2BDataRecord.

        The sub-holding properties which identify the holding. Each property will be from the 'Transaction' domain. These are configured when a transaction portfolio is created.  # noqa: E501

        :param sub_holding_keys: The sub_holding_keys of this A2BDataRecord.  # noqa: E501
        :type sub_holding_keys: dict[str, lusid.PerpetualProperty]
        """

        self._sub_holding_keys = sub_holding_keys

    @property
    def currency(self):
        """Gets the currency of this A2BDataRecord.  # noqa: E501

        The holding currency.  # noqa: E501

        :return: The currency of this A2BDataRecord.  # noqa: E501
        :rtype: str
        """
        return self._currency

    @currency.setter
    def currency(self, currency):
        """Sets the currency of this A2BDataRecord.

        The holding currency.  # noqa: E501

        :param currency: The currency of this A2BDataRecord.  # noqa: E501
        :type currency: str
        """

        self._currency = currency

    @property
    def transaction_id(self):
        """Gets the transaction_id of this A2BDataRecord.  # noqa: E501

        The unique identifier for the transaction.  # noqa: E501

        :return: The transaction_id of this A2BDataRecord.  # noqa: E501
        :rtype: str
        """
        return self._transaction_id

    @transaction_id.setter
    def transaction_id(self, transaction_id):
        """Sets the transaction_id of this A2BDataRecord.

        The unique identifier for the transaction.  # noqa: E501

        :param transaction_id: The transaction_id of this A2BDataRecord.  # noqa: E501
        :type transaction_id: str
        """

        self._transaction_id = transaction_id

    @property
    def start(self):
        """Gets the start of this A2BDataRecord.  # noqa: E501


        :return: The start of this A2BDataRecord.  # noqa: E501
        :rtype: lusid.A2BCategory
        """
        return self._start

    @start.setter
    def start(self, start):
        """Sets the start of this A2BDataRecord.


        :param start: The start of this A2BDataRecord.  # noqa: E501
        :type start: lusid.A2BCategory
        """

        self._start = start

    @property
    def flows(self):
        """Gets the flows of this A2BDataRecord.  # noqa: E501


        :return: The flows of this A2BDataRecord.  # noqa: E501
        :rtype: lusid.A2BCategory
        """
        return self._flows

    @flows.setter
    def flows(self, flows):
        """Sets the flows of this A2BDataRecord.


        :param flows: The flows of this A2BDataRecord.  # noqa: E501
        :type flows: lusid.A2BCategory
        """

        self._flows = flows

    @property
    def gains(self):
        """Gets the gains of this A2BDataRecord.  # noqa: E501


        :return: The gains of this A2BDataRecord.  # noqa: E501
        :rtype: lusid.A2BCategory
        """
        return self._gains

    @gains.setter
    def gains(self, gains):
        """Sets the gains of this A2BDataRecord.


        :param gains: The gains of this A2BDataRecord.  # noqa: E501
        :type gains: lusid.A2BCategory
        """

        self._gains = gains

    @property
    def carry(self):
        """Gets the carry of this A2BDataRecord.  # noqa: E501


        :return: The carry of this A2BDataRecord.  # noqa: E501
        :rtype: lusid.A2BCategory
        """
        return self._carry

    @carry.setter
    def carry(self, carry):
        """Sets the carry of this A2BDataRecord.


        :param carry: The carry of this A2BDataRecord.  # noqa: E501
        :type carry: lusid.A2BCategory
        """

        self._carry = carry

    @property
    def end(self):
        """Gets the end of this A2BDataRecord.  # noqa: E501


        :return: The end of this A2BDataRecord.  # noqa: E501
        :rtype: lusid.A2BCategory
        """
        return self._end

    @end.setter
    def end(self, end):
        """Sets the end of this A2BDataRecord.


        :param end: The end of this A2BDataRecord.  # noqa: E501
        :type end: lusid.A2BCategory
        """

        self._end = end

    @property
    def properties(self):
        """Gets the properties of this A2BDataRecord.  # noqa: E501

        The properties which have been requested to be decorated onto the holding. These will be from the 'Instrument' domain.  # noqa: E501

        :return: The properties of this A2BDataRecord.  # noqa: E501
        :rtype: dict[str, lusid.ModelProperty]
        """
        return self._properties

    @properties.setter
    def properties(self, properties):
        """Sets the properties of this A2BDataRecord.

        The properties which have been requested to be decorated onto the holding. These will be from the 'Instrument' domain.  # noqa: E501

        :param properties: The properties of this A2BDataRecord.  # noqa: E501
        :type properties: dict[str, lusid.ModelProperty]
        """

        self._properties = properties

    @property
    def group_id(self):
        """Gets the group_id of this A2BDataRecord.  # noqa: E501

        Arbitrary string that can be used to cross reference an entry in the A2B report with activity in the A2B-Movements. This should be used purely as a token. The content should not be relied upon.  # noqa: E501

        :return: The group_id of this A2BDataRecord.  # noqa: E501
        :rtype: str
        """
        return self._group_id

    @group_id.setter
    def group_id(self, group_id):
        """Sets the group_id of this A2BDataRecord.

        Arbitrary string that can be used to cross reference an entry in the A2B report with activity in the A2B-Movements. This should be used purely as a token. The content should not be relied upon.  # noqa: E501

        :param group_id: The group_id of this A2BDataRecord.  # noqa: E501
        :type group_id: str
        """

        self._group_id = group_id

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
        if not isinstance(other, A2BDataRecord):
            return False

        return self.to_dict() == other.to_dict()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        if not isinstance(other, A2BDataRecord):
            return True

        return self.to_dict() != other.to_dict()
