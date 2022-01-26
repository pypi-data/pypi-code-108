from pyopencell.resources.crm_account_hierarchy import CRMAccountHierarchy
from ..opencell_models.crm_account_hierarchy import (
    CRMAccountHierarchyFromContractToChangeEmail,
    CRMAccountHierarchyFromContractToChangeIBAN,
    CRMAccountHierarchyFromPartner,
)
from .opencell_exceptions import PyOpenCellException
from .crm_account_hierarchy_update_strategies import CRMAccountHierarchyUpdateStrategies


class CRMAccountHierarchyFromContractUpdateService:
    """
    Manage the Open Cell synchronization of the Contract model of Odoo.
    """

    def __init__(self, contracts, updated_field):
        self.contracts = contracts
        self.updated_field = updated_field
        self.update_OC_subscription_by_strategy = {
            "email": self._change_crm_account_hierarchy_email,
            "iban": self._change_crm_account_hierarchy_iban,
            "fallback": self._fallback,
        }

    def run(self):
        try:
            strategy, kwargs = CRMAccountHierarchyUpdateStrategies(
                self.contracts, self.updated_field).strategies()
            self.update_OC_subscription_by_strategy[strategy](**kwargs)

        except Exception as e:
            raise PyOpenCellException(str(e))

    def _change_crm_account_hierarchy_email(self, customer_account_code):
        crm_account_hierarchy_from_contract = \
            CRMAccountHierarchyFromContractToChangeEmail(
                self.contracts[0], customer_account_code
            )
        CRMAccountHierarchy.update(**crm_account_hierarchy_from_contract.to_dict())

    def _change_crm_account_hierarchy_iban(self, customer_account_code):
        crm_account_hierarchy_from_contract = \
            CRMAccountHierarchyFromContractToChangeIBAN(
                self.contracts[0], customer_account_code
            )
        CRMAccountHierarchy.update(**crm_account_hierarchy_from_contract.to_dict())

    def _fallback(self, fallback_message):
        raise PyOpenCellException(fallback_message)


class CRMAccountHierarchyFromPartnerUpdateService:
    """
    Manage the Open Cell synchronization of the Partner model of Odoo.
    """

    def __init__(self, partner, updated_field, customer_account_code):
        self.partner = partner
        self.updated_field = updated_field
        self.customer_account_code = customer_account_code
        self.update_OC_subscription_by_strategy = {
            "address": self._change_crm_account_hierarchies_address,
            "fallback": self._fallback,
        }

    def run(self):
        try:
            strategy, kwargs = CRMAccountHierarchyUpdateStrategies(
                None, self.updated_field,
                partner=self.partner,
                customer_account_code=self.customer_account_code
            ).strategies()
            self.update_OC_subscription_by_strategy[strategy](**kwargs)

        except Exception as e:
            raise PyOpenCellException(str(e))

    def _change_crm_account_hierarchies_address(self, customer_account_code):
        crm_account_hierarchy_from_partner = \
            CRMAccountHierarchyFromPartner(
                self.partner, customer_account_code
            )
        CRMAccountHierarchy.update(**crm_account_hierarchy_from_partner.to_dict())

    def _fallback(self, fallback_message):
        raise PyOpenCellException(fallback_message)
