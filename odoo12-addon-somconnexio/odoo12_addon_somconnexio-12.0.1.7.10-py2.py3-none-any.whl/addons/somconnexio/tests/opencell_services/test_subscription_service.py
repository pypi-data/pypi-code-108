from datetime import date

from odoo.tests import TransactionCase
from mock import Mock, patch
from ...opencell_services.subscription_service import SubscriptionService

from ..factories import ContractFactory


class SubscriptionServiceTests(TransactionCase):

    def setUp(self):
        super().setUp()
        self.contract = ContractFactory()

    @patch(
        'odoo.addons.somconnexio.opencell_services.subscription_service.Subscription',
        spec=['get']
    )
    def test_terminate_subscription(
        self,
        MockSubscription
    ):
        MockSubscription.get.return_value = Mock(spec=['subscription'])
        MockSubscription.get.return_value.subscription = Mock(spec=['terminate'])

        SubscriptionService(
            self.contract,
        ).terminate()

        MockSubscription.get.assert_called_once_with(self.contract.code)

        MockSubscription.get.return_value.subscription.terminate.assert_called_once_with(  # noqa
            self.contract.terminate_date.strftime("%Y-%m-%d")
        )

    @patch(
        'odoo.addons.somconnexio.opencell_services.subscription_service.Subscription',
        spec=['get']
    )
    def test_create_one_shot_with_cost(self, MockSubscription):
        MockSubscription.get.return_value = Mock(spec=['subscription'])
        MockSubscription.get.return_value.subscription = Mock(spec=['applyOneShotCharge'])  # noqa

        one_shot_default_code = "TEST_DEFAULT_CODE"

        SubscriptionService(
            self.contract,
        ).create_one_shot(one_shot_default_code)

        MockSubscription.get.assert_called_once_with(self.contract.code)
        MockSubscription.get.return_value.subscription.applyOneShotCharge.assert_called_once_with(  # noqa
            one_shot_default_code, None, description=None, operationDate=None
        )

    @patch(
        'odoo.addons.somconnexio.opencell_services.subscription_service.Subscription',
        spec=['get']
    )
    def test_create_one_shot_with_amount(self, MockSubscription):
        MockSubscription.get.return_value = Mock(spec=['subscription'])
        MockSubscription.get.return_value.subscription = Mock(spec=['applyOneShotCharge'])  # noqa

        one_shot_default_code = "TEST_DEFAULT_CODE"
        one_shot_amount = -123.4567

        SubscriptionService(
            self.contract,
        ).create_one_shot(one_shot_default_code, one_shot_amount)

        MockSubscription.get.assert_called_once_with(self.contract.code)
        MockSubscription.get.return_value.subscription.applyOneShotCharge.assert_called_once_with(  # noqa
            one_shot_default_code, one_shot_amount,
            description=None, operationDate=None
        )

    @patch(
        'odoo.addons.somconnexio.opencell_services.subscription_service.Subscription',
        spec=['get']
    )
    def test_create_one_shot_with_description(self, MockSubscription):
        MockSubscription.get.return_value = Mock(spec=['subscription'])
        MockSubscription.get.return_value.subscription = Mock(spec=['applyOneShotCharge'])  # noqa

        one_shot_default_code = "TEST_DEFAULT_CODE"
        one_shot_amount = -123.4567
        description = "Fake compensation"

        SubscriptionService(
            self.contract,
        ).create_one_shot(
            one_shot_default_code, one_shot_amount,
            description=description
        )

        MockSubscription.get.assert_called_once_with(self.contract.code)
        MockSubscription.get.return_value.subscription.applyOneShotCharge.assert_called_once_with(  # noqa
            one_shot_default_code, one_shot_amount,
            description=description, operationDate=None
        )

    @patch(
        'odoo.addons.somconnexio.opencell_services.subscription_service.Subscription',
        spec=['get']
    )
    def test_create_one_shot_with_operation_date(self, MockSubscription):
        MockSubscription.get.return_value = Mock(spec=['subscription'])
        MockSubscription.get.return_value.subscription = Mock(spec=['applyOneShotCharge'])  # noqa

        one_shot_default_code = "TEST_DEFAULT_CODE"
        one_shot_amount = -123.4567
        operation_date = date(2021, 5, 15)

        SubscriptionService(
            self.contract,
        ).create_one_shot(
            one_shot_default_code, one_shot_amount,
            operation_date=operation_date
        )

        MockSubscription.get.assert_called_once_with(self.contract.code)
        MockSubscription.get.return_value.subscription.applyOneShotCharge.assert_called_once_with(  # noqa
            one_shot_default_code, one_shot_amount,
            description=None, operationDate=operation_date.strftime("%Y-%m-%d")
        )

    @patch(
        'odoo.addons.somconnexio.opencell_services.subscription_service.Subscription',
        spec=['get']
    )
    def test_create_one_shot_free(self, MockSubscription):
        MockSubscription.get.return_value = Mock(spec=['subscription'])
        MockSubscription.get.return_value.subscription = Mock(spec=['applyOneShotCharge'])  # noqa

        one_shot_default_code = ""

        SubscriptionService(
            self.contract,
        ).create_one_shot(one_shot_default_code)

        MockSubscription.get.assert_called_once_with(self.contract.code)
        MockSubscription.get.return_value.subscription.applyOneShotCharge.assert_not_called()  # noqa

    @patch(
        'odoo.addons.somconnexio.opencell_services.subscription_service.Subscription',
        spec=['get']
    )
    @patch(
        'odoo.addons.somconnexio.opencell_services.subscription_service.ContractLineToOCServiceDict'  # noqa
    )
    def test_create_service(
        self,
        MockContractLineToOCServiceDict,
        MockSubscription
    ):
        expectec_oc_service_dict = Mock(spec=[])

        MockSubscription.get.return_value = Mock(spec=['subscription'])
        MockSubscription.get.return_value.subscription = Mock(spec=['activate'])
        contract_line = self.contract.contract_line_ids[0]

        MockContractLineToOCServiceDict.return_value = Mock(spec=['convert'])
        MockContractLineToOCServiceDict.return_value.convert.return_value = expectec_oc_service_dict  # noqa

        SubscriptionService(
            self.contract,
        ).create_service(contract_line)

        MockContractLineToOCServiceDict.assert_called_once_with(
            contract_line,
        )
        MockSubscription.get.assert_called_once_with(self.contract.code)
        MockSubscription.get.return_value.subscription.activate.assert_called_once_with(  # noqa
            [expectec_oc_service_dict]
        )

    @patch(
        'odoo.addons.somconnexio.opencell_services.subscription_service.Subscription',
        spec=['get']
    )
    def test_terminate_service(
        self,
        MockSubscription
    ):
        product = Mock(spec=['default_code'])
        product.default_code = "PRODUCT_CODE"
        MockSubscription.get.return_value = Mock(spec=['subscription'])
        MockSubscription.get.return_value.subscription = Mock(spec=[
            'services',
            'terminateServices'
        ])

        MockSubscription.get.return_value.subscription.services = {
            "serviceInstance": [
                {
                    "code": "PRODUCT_CODE"
                }
            ]
        }
        termination_date = date.today()

        SubscriptionService(
            self.contract,
        ).terminate_service(product, termination_date)

        MockSubscription.get.assert_called_once_with(self.contract.code)
        MockSubscription.get.return_value.subscription.terminateServices.assert_called_once_with(  # noqa
            termination_date.strftime("%Y-%m-%d"),
            [product.default_code]
        )
