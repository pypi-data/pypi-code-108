from ..factories import ContractFactory, PartnerFactory
from mock import Mock, patch
from ..sc_test_case import SCTestCase
from ...opencell_services.crm_account_hierarchy_update_service import (
    CRMAccountHierarchyFromContractUpdateService,
    CRMAccountHierarchyFromPartnerUpdateService,
)
from ...opencell_models.crm_account_hierarchy import (
    CRMAccountHierarchyFromContractToChangeEmail,
    CRMAccountHierarchyFromContractToChangeIBAN,
    CRMAccountHierarchyFromPartner
)
from ...opencell_services.opencell_exceptions import PyOpenCellException


class PartnerFake:
    def __init__(self, email):
        self.email = email


class CRMAccountHierarchyFromContractUpdateServiceTests(SCTestCase):

    def setUp(self):
        super().setUp()
        self.contracts = [ContractFactory()]
        self.contracts[0].email_ids = [PartnerFake('hello@example.com')]
        self.contracts[0].invoice_partner_id.mobile = False
        self.customer_account_code = "1234"

    @patch("odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_update_service.CRMAccountHierarchyUpdateStrategies")  # noqa
    @patch("odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_update_service.CRMAccountHierarchy")  # noqa
    def test_crm_account_hierarchy_update_service_email(self, CRMAccountHierarchyMock,
                                                        MockUpdateStrategies):
        """ Call to CRMAccountHierarchy when updating an OC subscription """
        MockUpdateStrategies.return_value = Mock(spec=['strategies'])
        MockUpdateStrategies.return_value.strategies.return_value = "email", {
            "customer_account_code": self.customer_account_code
        }

        crm_account_hierarchy_from_contract = CRMAccountHierarchyFromContractToChangeEmail(  # noqa
            self.contracts[0], self.customer_account_code
        )
        CRMAccountHierarchyFromContractUpdateService(self.contracts, "email").run()
        CRMAccountHierarchyMock.update.assert_called_with(
            **crm_account_hierarchy_from_contract.to_dict()
        )

    @patch("odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_update_service.CRMAccountHierarchyUpdateStrategies")  # noqa
    @patch("odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_update_service.CRMAccountHierarchy")  # noqa
    def test_crm_account_hierarchy_update_service_iban(self, CRMAccountHierarchyMock, MockUpdateStrategies):  # noqa
        """ Call to CRMAccountHierarchy when updating an OC subscription """
        MockUpdateStrategies.return_value = Mock(spec=['strategies'])
        MockUpdateStrategies.return_value.strategies.return_value = "iban", {
            "customer_account_code": self.customer_account_code
        }

        crm_account_hierarchy_from_contract = CRMAccountHierarchyFromContractToChangeIBAN(  # noqa
            self.contracts[0], self.customer_account_code
        )
        CRMAccountHierarchyFromContractUpdateService(self.contracts, "iban").run()
        CRMAccountHierarchyMock.update.assert_called_with(
            **crm_account_hierarchy_from_contract.to_dict()
        )

    @patch("odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_update_service.CRMAccountHierarchyUpdateStrategies")  # noqa
    @patch("odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_update_service.CRMAccountHierarchy")  # noqa
    def test_crm_account_hierarchy_update_service_address(self, CRMAccountHierarchyMock, MockUpdateStrategies):  # noqa
        """ Call to CRMAccountHierarchy when updating an OC subscription """
        partner = PartnerFactory()
        customer_account_code = "1234_1"
        MockUpdateStrategies.return_value = Mock(spec=['strategies'])
        MockUpdateStrategies.return_value.strategies.return_value = "address", {
            "customer_account_code": customer_account_code,
        }

        crm_account_hierarchy_from_contract = CRMAccountHierarchyFromPartner(
            partner, customer_account_code
        )
        CRMAccountHierarchyFromPartnerUpdateService(
            partner, "address", customer_account_code
        ).run()
        CRMAccountHierarchyMock.update.assert_called_with(
            **crm_account_hierarchy_from_contract.to_dict()
        )

    @patch("odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_update_service.CRMAccountHierarchyUpdateStrategies")  # noqa
    @patch("odoo.addons.somconnexio.opencell_services.crm_account_hierarchy_update_service.CRMAccountHierarchy")  # noqa
    def test_crm_account_hierarchy_update_service_fallback(self, CRMAccountHierarchyMock, MockUpdateStrategies):  # noqa
        """ Call to CRMAccountHierarchy when updating an OC subscription """
        MockUpdateStrategies.return_value = Mock(spec=['strategies'])
        MockUpdateStrategies.return_value.strategies.return_value = "fallback", {
            "fallback_message": "Error message"
        }

        self.assertRaisesRegex(
            PyOpenCellException,
            "Error message",
            CRMAccountHierarchyFromContractUpdateService(self.contracts, "iban").run,
        )
