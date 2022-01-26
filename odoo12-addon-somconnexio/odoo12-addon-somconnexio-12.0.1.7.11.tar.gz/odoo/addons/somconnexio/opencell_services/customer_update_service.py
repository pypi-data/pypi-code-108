from pyopencell.resources.customer import Customer
from ..opencell_models.customer import (
    CustomerFromPartner
)
from .opencell_exceptions import PyOpenCellException


class CustomerFromPartnerUpdateService:
    """
    Manage the Open Cell synchronization of the Contract model of Odoo.
    """

    def __init__(self, partner, opencell_configuration):
        self.partner = partner
        self.opencell_configuration = opencell_configuration

    def run(self):
        customer_from_partner = CustomerFromPartner(
            self.partner,
            self.opencell_configuration
        )
        try:
            Customer.update(**customer_from_partner.to_dict())
        except Exception as e:
            raise PyOpenCellException(str(e))
