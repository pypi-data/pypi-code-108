from mock import patch, Mock

from ..sc_test_case import SCTestCase


@patch("odoo.addons.somconnexio.models.contract.OpenCellConfiguration")
@patch("odoo.addons.somconnexio.models.contract.CRMAccountHierarchyFromContractCreateService")  # noqa
class TestContractForceOCIntegrationWizard(SCTestCase):

    def test_create_subscription(
        self,
        CRMAccountHierarchyFromContractCreateServiceMock,
        OpenCellConfigurationMock
    ):
        partner = self.browse_ref('base.partner_demo')
        service_partner = self.env['res.partner'].create({
            'parent_id': partner.id,
            'name': 'Partnér service OK',
            'type': 'service'
        })
        bank_b = self.env['res.partner.bank'].create({
            'acc_number': 'ES1720852066623456789011',
            'partner_id': partner.id
        })
        banking_mandate = self.env['account.banking.mandate'].create({
            'partner_bank_id': bank_b.id,
        })
        vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        vals_contract = {
            'name': 'Test Contract Broadband',
            'partner_id': partner.id,
            'service_partner_id': service_partner.id,
            'invoice_partner_id': partner.id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_fiber"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_vodafone"
            ),
            'vodafone_fiber_service_contract_info_id': (
                vodafone_fiber_contract_service_info.id
            ),
            'mandate_id': banking_mandate.id
        }

        CRMAccountHierarchyFromContractCreateServiceMock.return_value = Mock(spec=["run"])  # noqa
        OpenCellConfigurationMock.return_value = object

        contract = self.env['contract.contract'].create(vals_contract)

        wizard = self.env['contract.force.oc.integration.wizard'].with_context(
            active_id=contract.id
        ).create({})
        wizard.create_subscription()

        CRMAccountHierarchyFromContractCreateServiceMock.assert_called_once_with(
            contract,
            OpenCellConfigurationMock.return_value
        )
        CRMAccountHierarchyFromContractCreateServiceMock.return_value.run.assert_called_once()  # noqa
