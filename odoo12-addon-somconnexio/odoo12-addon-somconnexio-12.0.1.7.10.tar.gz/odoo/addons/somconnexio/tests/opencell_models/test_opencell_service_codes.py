from ..sc_test_case import SCTestCase
from ...opencell_models.services import ServicesFromContract
from ..factories import ContractFactory, ContractLineFactory


class TestOpenCellServiceCodes(SCTestCase):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

        self.contract = ContractFactory()

        self.service = self.browse_ref('somconnexio.150Min1GB')

        self.contract.contract_line_ids[0].product_id = self.service

        self.expected_services = [{
            "code": self.service.default_code,
            "quantity": 1,
            "subscriptionDate": (
                self.contract.contract_line_ids[0].date_start.strftime("%Y-%m-%d")
            ),
        }]

    def test_services_to_activate(self):
        services_from_contract, _ = ServicesFromContract(
            self.contract
        ).services_to_activate()

        self.assertEquals(services_from_contract, self.expected_services)

    def test_services_to_activate_with_one_shot(self):
        self.one_shot = self.browse_ref('somconnexio.EnviamentSIM')

        one_shot_contract_line = ContractLineFactory()
        one_shot_contract_line.product_id = self.one_shot

        self.contract.contract_line_ids.append(one_shot_contract_line)

        expected_one_shots = [self.one_shot.default_code]

        _, one_shots_from_contract = ServicesFromContract(
            self.contract
        ).services_to_activate()

        self.assertEquals(one_shots_from_contract, expected_one_shots)
