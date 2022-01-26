from .opencell_resource import OpenCellResource


class ServicesFromContract(OpenCellResource):
    def __init__(self, contract):
        self.contract = contract
        self.one_shot_category = "OneShot Service"

    def services_to_activate(self):
        """
        Return a list of dicts with the OpenCell service code
        and the start date of the contract line.

        To construct the dict, you need to get the service code
        form the product and the date from the
        start date of the contract line.

        :returns 2 elements:
            - services: List of dictionaries with the service code and the start date.
            - one_shots: List of one-shot service codes
        """
        services = []
        one_shots = []
        for line in self.contract.contract_line_ids:
            if line.product_id.product_tmpl_id.categ_id.name == self.one_shot_category:
                one_shots.append(line.product_id.default_code)
            else:
                opencell_service_dict = ContractLineToOCServiceDict(line).convert()
                services.append(opencell_service_dict)
        return services, one_shots


class ContractLineToOCServiceDict:
    """
    Presenter parsing OpenCell service and
    returning an OpenCell compliant service
    """

    def __init__(self, contract_line):
        self.contract_line = contract_line

    @staticmethod
    def service_dict(service_code, subscription_date):
        return {
            "code": service_code,
            "quantity": 1,
            "subscriptionDate": subscription_date,
        }

    def convert(self):
        return self.service_dict(
            self.contract_line.product_id.default_code,
            self.contract_line.date_start.strftime("%Y-%m-%d")
        )
