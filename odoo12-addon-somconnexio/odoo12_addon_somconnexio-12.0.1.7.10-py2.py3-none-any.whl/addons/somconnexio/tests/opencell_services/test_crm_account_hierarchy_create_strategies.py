from mock import Mock, patch
from odoo.tests import TransactionCase

from ...opencell_services.crm_account_hierarchy_create_strategies import CRMAccountHierarchyCreateStrategies  # noqa
from ..factories import ContractFactory
from .test_crm_account_hierarchy_update_service import PartnerFake


class CRMAccountHierarchyCreateStrategiesTests(TransactionCase):
    def setUp(self):
        self.contract = ContractFactory()
        self.contract.email_ids = [PartnerFake(
            self.contract.invoice_partner_id.email)]

    @patch(
        'odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_create_strategies.Customer',  # noqa
        spec=['get']
    )
    def test_customer_hierarchy_strategy(self, CustomerMock):  # noqa
        mock_customer = Mock(spec=["customer"])
        mock_customer.customer = None

        def _side_effect_customer_get(ref):
            if ref == self.contract.partner_id.ref:
                return mock_customer

        CustomerMock.get.side_effect = _side_effect_customer_get

        strategy, params = CRMAccountHierarchyCreateStrategies(
            self.contract).strategies()

        self.assertEqual(strategy, 'customer_hierarchy')
        self.assertEqual(
            params["crm_account_hierarchy_code"],
            "{}_0".format(self.contract.partner_id.ref)
        )

    @patch(
        'odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_create_strategies.Customer',  # noqa
        spec=['get']
    )
    def test_customer_account_hierarchy_strategy_different_email(self, CustomerMock):  # noqa
        iban = self.contract.mandate_id.partner_bank_id.sanitized_acc_number
        mock_customer = Mock(spec=["customer"])
        mock_customer.customer = Mock(spect=["customerAccounts", "code"])
        mock_customer.customer.code = self.contract.partner_id.ref
        mock_customer.customer.customerAccounts = {
            "customerAccount": [
                {
                    "contactInformation": {
                        "email": "new_email@email.coop"
                    },
                    "methodOfPayment": [
                        {
                            "bankCoordinates": {
                                "iban": iban
                            }
                        }
                    ]
                }
            ]
        }

        def _side_effect_customer_get(ref):
            if ref == self.contract.partner_id.ref:
                return mock_customer

        CustomerMock.get.side_effect = _side_effect_customer_get

        strategy, params = CRMAccountHierarchyCreateStrategies(
            self.contract).strategies()

        self.assertEqual(strategy, 'customer_account_hierarchy')
        self.assertEqual(
            params["crm_account_hierarchy_code"],
            "{}_1".format(self.contract.partner_id.ref)
        )

    @patch(
        'odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_create_strategies.Customer',  # noqa
        spec=['get']
    )
    def test_customer_account_hierarchy_strategy_different_iban(self, CustomerMock):  # noqa
        mock_customer = Mock(spec=["customer"])
        mock_customer.customer = Mock(spect=["customerAccounts", "code"])
        mock_customer.customer.code = self.contract.partner_id.ref
        mock_customer.customer.customerAccounts = {
            "customerAccount": [
                {
                    "contactInformation": {
                        "email": self.contract.invoice_partner_id.email,
                    },
                    "methodOfPayment": [
                        {
                            "bankCoordinates": {
                                "iban": "ES6621000418401234567822"
                            }
                        }
                    ]
                }
            ]
        }

        def _side_effect_customer_get(ref):
            if ref == self.contract.partner_id.ref:
                return mock_customer

        CustomerMock.get.side_effect = _side_effect_customer_get

        strategy, params = CRMAccountHierarchyCreateStrategies(
            self.contract).strategies()

        self.assertEqual(strategy, 'customer_account_hierarchy')
        self.assertEqual(
            params["crm_account_hierarchy_code"],
            "{}_1".format(self.contract.partner_id.ref)
        )

    @patch(
        'odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_create_strategies.Customer',  # noqa
        spec=['get']
    )
    def test_subscription_strategy(self, CustomerMock):  # noqa
        iban = self.contract.mandate_id.partner_bank_id.sanitized_acc_number
        mock_customer = Mock(spec=["customer"])
        mock_customer.customer = Mock(spect=["customerAccounts", "code"])
        mock_customer.customer.code = self.contract.partner_id.ref
        mock_customer.customer.customerAccounts = {
            "customerAccount": [
                {
                    "code": "{}_0".format(self.contract.partner_id.ref),
                    "contactInformation": {
                        "email": self.contract.invoice_partner_id.email,
                    },
                    "methodOfPayment": [
                        {
                            "bankCoordinates": {
                                "iban": iban,
                            }
                        }
                    ]
                }
            ]
        }

        def _side_effect_customer_get(ref):
            if ref == self.contract.partner_id.ref:
                return mock_customer

        CustomerMock.get.side_effect = _side_effect_customer_get

        strategy, params = CRMAccountHierarchyCreateStrategies(
            self.contract).strategies()

        self.assertEqual(strategy, 'subscription')
        self.assertEqual(
            params["crm_account_hierarchy_code"],
            "{}_0".format(self.contract.partner_id.ref)
        )

    @patch(
        'odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_create_strategies.Customer',  # noqa
        spec=['get']
    )
    def test_fallback_strategy(self, CustomerMock):
        mock_customer = Mock(spec=["customer"])
        mock_customer.customer = Mock(spect=["customerAccounts", "code"])
        mock_customer.customer.code = self.contract.partner_id.ref
        mock_customer.customer.customerAccounts = {'customerAccount': None}

        def _side_effect_customer_get(ref):
            if ref == self.contract.partner_id.ref:
                return mock_customer

        CustomerMock.get.side_effect = _side_effect_customer_get

        strategy, params = CRMAccountHierarchyCreateStrategies(
            self.contract).strategies()

        self.assertEqual(strategy, 'fallback')
        self.assertEqual(
            params["customer_code"],
            self.contract.partner_id.ref
        )
