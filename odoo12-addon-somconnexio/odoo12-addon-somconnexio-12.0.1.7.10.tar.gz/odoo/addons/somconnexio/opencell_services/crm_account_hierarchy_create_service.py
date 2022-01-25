from pyopencell.resources.customer import Customer
from pyopencell.resources.crm_account_hierarchy import CRMAccountHierarchy
from pyopencell.resources.subscription import Subscription
from pyopencell.resources.access import Access
from odoo import _

from ..opencell_models.customer import CustomerFromPartner
from ..opencell_models.crm_account_hierarchy import CRMAccountHierarchyFromContract
from ..opencell_models.subscription import SubscriptionFromContract
from ..opencell_models.access import AccessFromContract

from .opencell_exceptions import PyOpenCellException
from .crm_account_hierarchy_create_strategies import CRMAccountHierarchyCreateStrategies


class CRMAccountHierarchyFromContractCreateService(object):
    def __init__(self, contract, opencell_configuration):
        self.contract = contract
        self.partner = contract.partner_id
        self.create_OC_subscription_by_strategy = {
            "customer_hierarchy": self._from_customer_to_subscription,
            "customer_account_hierarchy": self._from_customer_account_to_subscription,  # noqa
            "subscription": self._subscription,
            "fallback": self._fallback,
        }
        self.opencell_configuration = opencell_configuration

    def run(self):
        strategy, kwargs = CRMAccountHierarchyCreateStrategies(
            self.contract).strategies()
        try:
            self.create_OC_subscription_by_strategy[strategy](**kwargs)
        except Exception as e:
            raise PyOpenCellException(str(e))

    def _from_customer_to_subscription(self, crm_account_hierarchy_code):
        customer_from_partner = CustomerFromPartner(
            self.partner,
            self.opencell_configuration
        )
        Customer.create(**customer_from_partner.to_dict())
        self._from_customer_account_to_subscription(crm_account_hierarchy_code)

    def _from_customer_account_to_subscription(
            self, crm_account_hierarchy_code):
        crm_account_hierarchy_from_contract = CRMAccountHierarchyFromContract(
            self.contract,
            crm_account_hierarchy_code)
        CRMAccountHierarchy.create(**crm_account_hierarchy_from_contract.to_dict())

        self._subscription(crm_account_hierarchy_code=crm_account_hierarchy_code)

    def _subscription(self, crm_account_hierarchy_code):
        subscription_from_contract = SubscriptionFromContract(
            self.contract,
            crm_account_hierarchy_code)
        Subscription.create(**subscription_from_contract.to_dict())

        access_from_contract = AccessFromContract(self.contract)
        Access.create(**access_from_contract.to_dict())

    def _fallback(self, customer_code):
        raise PyOpenCellException(
            _("Customer with code {} found with no customer accounts associated").format(  # noqa
                customer_code)
            )
