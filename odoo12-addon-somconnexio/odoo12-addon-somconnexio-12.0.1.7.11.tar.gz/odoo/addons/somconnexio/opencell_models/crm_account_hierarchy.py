import time
import logging

from .account_hierarchy_resource import AccountHierarchyResource
from .opencell_types.description import Description

logger = logging.getLogger(__name__)


class CRMAccountHierarchyFromContract(AccountHierarchyResource):
    def __init__(self, contract, crm_account_hierarchy_code):
        self.contract = contract
        self.crm_account_hierarchy_code = crm_account_hierarchy_code
        self.partner = contract.partner_id
        self.white_list = [
            'address', 'billingCycle', 'code', 'contactInformation', 'country',
            'crmAccountType', 'crmParentCode', 'currency', 'customerCategory',
            'description', 'electronicBilling', 'language', 'methodOfPayment', 'name',
            'vatNo', 'email', 'mailingType', 'emailTemplate', 'ccedEmails']
        self.email_list = [email.email for email in self.contract.email_ids]

    @property
    def email(self):
        return self.email_list[0]

    @property
    def ccedEmails(self):
        if len(self.email_list) > 1:
            return ",".join(self.email_list[1:])
        else:
            return None

    @property
    def contactInformation(self):
        return {
            "email" : self.email,
            "phone" : self.contract.invoice_partner_id.phone or "",
            "mobile" : self.contract.invoice_partner_id.mobile or "",
            "fax" : ""
        }

    @property
    def code(self):
        return self.crm_account_hierarchy_code

    @property
    def crmAccountType(self):
        return "CA_UA"

    @property
    def phone(self):
        return self.partner.phone or self.partner.mobile

    @property
    def crmParentCode(self):
        return self.partner.ref

    @property
    def language(self):
        """
        A conversion has to be done:
            If Odoo language code is es_ES, ESP will be passed to Opencell.
            If Odoo language code is ca_ES, CAT will be passed to Opencell.
        """
        lang_code = self.partner.lang
        if lang_code == 'es_ES':
            return 'ESP'
        elif lang_code == 'ca_ES':
            return 'CAT'
        else:
            raise Exception("""
            Can't match Odoo's lang_code {} with an OpenCell language code
            """.format(lang_code))

    @property
    def methodOfPayment(self):
        # DTO in OC - https://api.opencellsoft.com/7.X/json_PaymentMethodDto.html
        partner_bank = self._contract_partner_bank()
        if not partner_bank:
            return []
        return [{
            "paymentMethodType": "DIRECTDEBIT",
            "disabled": False,
            "preferred": True,
            "customerAccountCode": self.code,
            "bankCoordinates": {
                "iban": partner_bank.sanitized_acc_number,
                "bic": partner_bank.bank_id.bic,
                "accountOwner": Description(
                    "{} {}".format(self.partner.firstname, self.partner.lastname)).text,
                "bankName": partner_bank.bank_id.name,
            },
            "alias": partner_bank.id,
            # TODO: Manage SEPA mandate
            "mandateIdentification": partner_bank.id,
            "mandateDate": int(time.mktime(partner_bank.create_date.timetuple())),
        }]

    def _contract_partner_bank(self):
        try:
            return self.contract.mandate_id.partner_bank_id
        except IndexError:
            logger.error("Can't find iban for contract {}".format(self.contract.code))

    @property
    def customerCategory(self):
        return 'CLIENT'

    @property
    def currency(self):
        return 'EUR'

    @property
    def billingCycle(self):
        return 'BC_SC_MONTHLY_1ST'

    @property
    def country(self):
        country = 'SP'
        if self.partner.state_id.code in ['TF', 'GC']:
            country = 'ES_CN'
        return country

    @property
    def electronicBilling(self):
        return True

    @property
    def mailingType(self):
        return 'Manual'

    @property
    def emailTemplate(self):
        return 'EMAIL_TEMPLATE_TEST'


class CRMAccountHierarchyFromPartner(CRMAccountHierarchyFromContract):
    def __init__(self, partner, crm_account_hierarchy_code):
        self.crm_account_hierarchy_code = crm_account_hierarchy_code
        self.partner = partner
        self.white_list = [
            'code', 'crmAccountType', 'currency', 'language', 'address', 'country'
        ]


class CRMAccountHierarchyFromContractToChangeEmail(CRMAccountHierarchyFromContract):
    def __init__(self, contract, crm_account_hierarchy_code):
        super().__init__(contract, crm_account_hierarchy_code)
        self.white_list = [
            'code', 'crmAccountType', 'currency', 'language', 'email', 'ccedEmails',
            'contactInformation'
        ]


class CRMAccountHierarchyFromContractToChangeIBAN(CRMAccountHierarchyFromContract):
    def __init__(self, contract, crm_account_hierarchy_code):
        super().__init__(contract, crm_account_hierarchy_code)
        self.white_list = [
            'code', 'crmAccountType', 'currency', 'language', 'methodOfPayment'
        ]
