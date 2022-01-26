from odoo.tests.common import TransactionCase
from ...opencell_models.subscription import SubscriptionFromContract
from ..factories import PartnerFactory, ContractFactory
from datetime import datetime


class SubscriptionFromContractTestCase(TransactionCase):

    def setUp(self):
        self.crm_account_code = "1234"

        self.contract = ContractFactory()
        self.contract.code = 1234
        self.contract.phone_number = "666666666"
        self.contract.service_type = "vodafone"
        self.contract.date_start = datetime.strptime("2020-03-11", "%Y-%m-%d")

    @staticmethod
    def _custom_fields_to_dict(custom_fields):
        custom_fields_dict = {}
        for field in custom_fields:
            custom_fields_dict[field["code"]] = field["stringValue"]

        return custom_fields_dict

    def test_mobile_subscription_construct_ok(self):
        self.contract.service_contract_type = "mobile"

        subscription_from_contract = SubscriptionFromContract(
            self.contract, self.crm_account_code
        )

        self.assertEqual(subscription_from_contract.code, 1234)
        self.assertEqual(subscription_from_contract.description, "666666666")
        self.assertEqual(subscription_from_contract.offerTemplate, "OF_SC_TEMPLATE_MOB")
        self.assertEqual(subscription_from_contract.subscriptionDate, "2020-03-11")
        self.assertEqual(subscription_from_contract.customFields, {})

    def test_broadband_subscription_construct_ok(self):
        self.contract.service_contract_type = "vodafone"
        internet_address = PartnerFactory()
        self.contract.service_partner_id = internet_address

        subscription_from_contract = SubscriptionFromContract(
            self.contract, self.crm_account_code
        )

        self.assertEqual(subscription_from_contract.code, 1234)
        self.assertEqual(subscription_from_contract.description, "666666666")
        self.assertEqual(subscription_from_contract.offerTemplate, "OF_SC_TEMPLATE_BA")
        self.assertEqual(subscription_from_contract.subscriptionDate, "2020-03-11")

        custom_fields_dict = self._custom_fields_to_dict(
            subscription_from_contract.customFields["customField"]
        )

        self.assertEqual(
            custom_fields_dict["CF_OF_SC_SUB_SERVICE_ADDRESS"],
            internet_address.full_street
        )
        self.assertEqual(
            custom_fields_dict["CF_OF_SC_SUB_SERVICE_CP"],
            internet_address.zip
        )
        self.assertEqual(
            custom_fields_dict["CF_OF_SC_SUB_SERVICE_CITY"],
            internet_address.city
        )
        self.assertEqual(
            custom_fields_dict["CF_OF_SC_SUB_SERVICE_SUBDIVISION"],
            internet_address.state_id.name
        )

    def test_orange_subscription_construct_ok(self):
        self.contract.service_contract_type = "orange"
        internet_address = PartnerFactory()
        self.contract.service_partner_id = internet_address

        subscription_from_contract = SubscriptionFromContract(
            self.contract, self.crm_account_code
        )

        self.assertEqual(subscription_from_contract.code, 1234)
        self.assertEqual(subscription_from_contract.description, "666666666")
        self.assertEqual(subscription_from_contract.offerTemplate, "OF_SC_TEMPLATE_BA")
        self.assertEqual(subscription_from_contract.subscriptionDate, "2020-03-11")

        custom_fields_dict = self._custom_fields_to_dict(
            subscription_from_contract.customFields["customField"]
        )

        self.assertEqual(
            custom_fields_dict["CF_OF_SC_SUB_SERVICE_ADDRESS"],
            internet_address.full_street
        )
        self.assertEqual(
            custom_fields_dict["CF_OF_SC_SUB_SERVICE_CP"],
            internet_address.zip
        )
        self.assertEqual(
            custom_fields_dict["CF_OF_SC_SUB_SERVICE_CITY"],
            internet_address.city
        )
        self.assertEqual(
            custom_fields_dict["CF_OF_SC_SUB_SERVICE_SUBDIVISION"],
            internet_address.state_id.name
        )
