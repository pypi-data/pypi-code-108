from pyopencell.resources.subscription import Subscription

from ..opencell_models.services import ContractLineToOCServiceDict


class SubscriptionService:
    """
    Model to execute the bussines logic of Som Connexio
    working with the Subscription model of PyOpenCell
    """

    def __init__(self, contract):
        self.contract = contract
        subscription_response = Subscription.get(self.contract.code)
        self.subscription = subscription_response.subscription

    def terminate(self):
        self.subscription.terminate(self.contract.terminate_date.strftime("%Y-%m-%d"))

    def create_one_shot(
        self, one_shot_default_code, amount=None,
        description=None, operation_date=None
    ):
        if not one_shot_default_code:
            return
        if operation_date:
            operation_date = operation_date.strftime("%Y-%m-%d")
        self.subscription.applyOneShotCharge(
            one_shot_default_code, amount,
            description=description, operationDate=operation_date
        )

    def create_service(self, contract_line):
        opencell_service_dict = ContractLineToOCServiceDict(
            contract_line,
        ).convert()
        self.subscription.activate([opencell_service_dict])

    def terminate_service(self, product, termination_date):
        termination_date = termination_date.strftime("%Y-%m-%d")

        for service in self.subscription.services["serviceInstance"]:
            service_needs_update = service["code"] == product.default_code and \
                not service.get("terminationDate")
            if service_needs_update:
                self.subscription.terminateServices(termination_date, [service["code"]])
