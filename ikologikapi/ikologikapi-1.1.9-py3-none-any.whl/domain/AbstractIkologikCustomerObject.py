from ikologikapi.domain.AbstractIkologikObject import AbstractIkologikObject


class AbstractIkologikCustomerObject(AbstractIkologikObject):

    def __init__(self, customer: str):
        super().__init__()
        self.customer = customer
