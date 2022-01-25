from mock import Mock, patch
from pyopencell.exceptions import PyOpenCellAPIException
from odoo.tests import TransactionCase

from ...opencell_services.crm_account_hierarchy_update_strategies import CRMAccountHierarchyUpdateStrategies  # noqa
from ..factories import ContractFactory


class FakeSubscription:
    def __init__(self, user_account):
        self.userAccount = user_account


@patch(
    'odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_update_strategies.Customer',  # noqa
    spec=['get']
)
@patch(
    'odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_update_strategies.SubscriptionService'  # noqa
)
@patch(
    'odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_update_strategies.SubscriptionList',  # noqa
    spec=['get']
)
class CRMAccountHierarchyUpdateStrategiesTests(TransactionCase):
    def setUp(self):
        self.contracts = [ContractFactory()]
        self.customer_code = self.contracts[0].partner_id.ref

        self.mock_customer = Mock(spec=["customer"])
        self.mock_customer.customer = Mock(spec=["customerAccounts", "code"])
        self.mock_customer.customer.code = self.customer_code
        self.mock_customer.customer.customerAccounts = {
            "customerAccount": [
                {
                    "contactInformation": {
                        "email": "new_email@email.coop"
                    },
                    "methodOfPayment": [
                        {
                            "bankCoordinates": {
                                "iban": "ES9420805801101234567891"
                            }
                        }
                    ]
                }
            ]
        }

        self.user_account = "1234"
        self.mock_subscription_service = Mock(spec=["subscription"])
        self.mock_subscription_service.subscription = FakeSubscription(
            self.user_account)
        self.mock_subscription_list = Mock(spec=["subscriptions"])

    def _side_effect_customer_get(self, ref):
        if ref == self.customer_code:
            return self.mock_customer

    def _side_effect_subscription_service(self, contract):
        if contract == self.contracts[0]:
            return self.mock_subscription_service

    def _side_effect_subscription_list_get(self, **kwargs):
        expected_kwargs = {
            "query": "userAccount.code:{}|status:ACTIVE".format(self.user_account)
        }
        if kwargs == expected_kwargs:
            return self.mock_subscription_list

    def test_customer_hierarchy_update_email_strategy(self, SubscriptionListMock,
                                                      SubscriptionServiceMock,
                                                      CustomerMock):
        # Make sure '_all_contracts_to_change_in_customer_subscription_list' returns True  # noqa
        self.mock_subscription_list.subscriptions = self.contracts

        CustomerMock.get.side_effect = self._side_effect_customer_get
        SubscriptionServiceMock.side_effect = self._side_effect_subscription_service
        SubscriptionListMock.get.side_effect = self._side_effect_subscription_list_get

        strategy, params = CRMAccountHierarchyUpdateStrategies(
            self.contracts, "email").strategies()

        self.assertEqual(strategy, "email")
        self.assertEqual(
            params["customer_account_code"],
            "{}_0".format(self.customer_code)
        )

    def test_customer_hierarchy_update_iban_strategy(self, SubscriptionListMock,
                                                     SubscriptionServiceMock,
                                                     CustomerMock):
        # Make sure '_all_contracts_to_change_in_customer_subscription_list' returns True  # noqa
        self.mock_subscription_list.subscriptions = self.contracts

        CustomerMock.get.side_effect = self._side_effect_customer_get
        SubscriptionServiceMock.side_effect = self._side_effect_subscription_service
        SubscriptionListMock.get.side_effect = self._side_effect_subscription_list_get

        strategy, params = CRMAccountHierarchyUpdateStrategies(
            self.contracts, "iban").strategies()

        self.assertEqual(strategy, "iban")
        self.assertEqual(
            params["customer_account_code"],
            "{}_0".format(self.customer_code)
        )

    def test_customer_hierarchy_update_fallback_no_customer_strategy(
            self,
            SubscriptionListMock,
            SubscriptionServiceMock,
            CustomerMock):

        CustomerMock.get.side_effect = PyOpenCellAPIException(
            "GET", "url", "400", "error"
        )

        strategy, params = CRMAccountHierarchyUpdateStrategies(
            self.contracts, "email").strategies()

        self.assertEqual(strategy, "fallback")
        self.assertEqual(
            params["fallback_message"],
            "Customer with code {} not found in OC".format(
                self.customer_code)
        )

    def test_customer_hierarchy_update_fallback_customer_no_CA_strategy(
            self,
            SubscriptionListMock,
            SubscriptionServiceMock,
            CustomerMock):

        self.mock_customer.customer.customerAccounts["customerAccount"] = None

        strategy, params = CRMAccountHierarchyUpdateStrategies(
            self.contracts, "email").strategies()

        self.assertEqual(strategy, "fallback")
        self.assertEqual(
            params["fallback_message"],
            "Customer with code {} does not have any customer account hierachy.".format(  # noqa
                self.customer_code)
        )

    def test_customer_hierarchy_update_fallback_customer_multiple_CA_strategy(
            self,
            SubscriptionListMock,
            SubscriptionServiceMock,
            CustomerMock):

        self.mock_customer.customer.customerAccounts["customerAccount"] = [
            {
                "contactInformation": {
                    "email": "new_email@email.coop"
                },
                "methodOfPayment": [
                    {
                        "bankCoordinates": {
                            "iban": "ES9420805801101234567891"
                            }
                    }
                ]
            },
            {
                "contactInformation": {
                    "email": "new_email@email.coop"
                },
                "methodOfPayment": [
                    {
                        "bankCoordinates": {
                            "iban": "ES9420805801101234567891"
                            }
                    }
                ]
            },
        ]
        CustomerMock.get.side_effect = self._side_effect_customer_get

        strategy, params = CRMAccountHierarchyUpdateStrategies(
            self.contracts, "email").strategies()

        self.assertEqual(strategy, "fallback")
        self.assertEqual(
            params["fallback_message"],
            "Customer with code {} has more than one customer account hierachy. ".format(  # noqa
                self.customer_code) + "Please update OC manually."
        )

    def test_customer_hierarchy_update_partial_hierarchy_strategy(
            self,
            SubscriptionListMock,
            SubscriptionServiceMock,
            CustomerMock):
        # Make sure '_all_contracts_to_change_in_customer_subscription_list' returns False  # noqa
        self.mock_subscription_list.subscriptions = [
            self.contracts[0], self.contracts[0]]

        CustomerMock.get.side_effect = self._side_effect_customer_get
        SubscriptionServiceMock.side_effect = self._side_effect_subscription_service
        SubscriptionListMock.get.side_effect = self._side_effect_subscription_list_get

        strategy, params = CRMAccountHierarchyUpdateStrategies(
            self.contracts, "iban").strategies()

        self.assertEqual(strategy, "fallback")
        self.assertEqual(
            params["fallback_message"],
            "Trying to add changes that would need to divide the customer account " +
            "hierarchy from customer with code {} . ".format(self.customer_code) +
            "Please update OC manually."
        )

    def test_customer_hierarchy_fallback_unknown_strategy(
            self, SubscriptionListMock, SubscriptionServiceMock, CustomerMock):
        # Make sure '_all_contracts_to_change_in_customer_subscription_list' returns True  # noqa
        self.mock_subscription_list.subscriptions = self.contracts

        CustomerMock.get.side_effect = self._side_effect_customer_get
        SubscriptionServiceMock.side_effect = self._side_effect_subscription_service
        SubscriptionListMock.get.side_effect = self._side_effect_subscription_list_get

        strategy, params = CRMAccountHierarchyUpdateStrategies(
            self.contracts, "name").strategies()

        self.assertEqual(strategy, "fallback")
        self.assertEqual(
            params["fallback_message"],
            "Something went wrong, unable to choose a strategy"
        )


@patch(
    'odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_update_strategies.Customer',  # noqa
    spec=['get']
)
class CRMAccountHierarchyFromPartnerUpdateStrategiesTests(TransactionCase):
    def setUp(self):
        self.contracts = [ContractFactory(), ContractFactory()]
        self.partner = self.contracts[0].partner_id
        self.contracts[1].partner_id = self.partner
        self.customer_code = self.contracts[0].partner_id.ref

        self.mock_customer = Mock(spec=["customer"])
        self.mock_customer.customer = Mock(spec=["customerAccounts", "code"])
        self.mock_customer.customer.code = self.customer_code
        self.mock_customer.customer.customerAccounts = {
            "customerAccount": [
                {
                    "code": str(self.customer_code) + "_1"
                },
                {
                    "code": str(self.customer_code) + "_2"
                },
            ]
        }

    def _side_effect_customer_get(self, ref):
        if ref == self.customer_code:
            return self.mock_customer

    def test_customer_hierarchy_update_address_strategy(self, CustomerMock):
        CustomerMock.get.side_effect = self._side_effect_customer_get

        strategy, params = CRMAccountHierarchyUpdateStrategies(
            None, "address", partner=self.partner,
            customer_account_code=str(self.customer_code)+"_1"
        ).strategies()

        self.assertEqual(strategy, "address")
        self.assertEqual(
            params["customer_account_code"],
            "{}_1".format(self.customer_code)
        )

    def test_customer_hierarchy_update_fallback_no_customer_strategy(
            self,
            CustomerMock):

        CustomerMock.get.side_effect = PyOpenCellAPIException(
            "GET", "url", "400", "error"
        )

        strategy, params = CRMAccountHierarchyUpdateStrategies(
            None, "address", partner=self.partner).strategies()

        self.assertEqual(strategy, "fallback")
        self.assertEqual(
            params["fallback_message"],
            "Customer with code {} not found in OC".format(
                self.customer_code)
        )

    def test_customer_hierarchy_update_fallback_customer_no_CA_strategy(
            self, CustomerMock):

        self.mock_customer.customer.customerAccounts["customerAccount"] = None

        strategy, params = CRMAccountHierarchyUpdateStrategies(
            None, "address", partner=self.partner).strategies()

        self.assertEqual(strategy, "fallback")
        self.assertEqual(
            params["fallback_message"],
            "Customer with code {} does not have any customer account hierachy.".format(  # noqa
                self.customer_code)
        )
