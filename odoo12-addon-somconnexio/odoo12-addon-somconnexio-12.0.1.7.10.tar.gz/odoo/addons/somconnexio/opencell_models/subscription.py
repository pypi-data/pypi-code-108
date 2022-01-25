from .opencell_resource import OpenCellResource
from .opencell_types.custom_field import CustomField


class SubscriptionFromContract(OpenCellResource):
    white_list = [
        'code', 'description', 'userAccount',
        'offerTemplate', 'subscriptionDate', 'customFields'
    ]
    offer_template_code = {
        'mobile': 'OF_SC_TEMPLATE_MOB',
        'adsl': 'OF_SC_TEMPLATE_BA',
        'vodafone': 'OF_SC_TEMPLATE_BA',
        'masmovil': 'OF_SC_TEMPLATE_BA',
        'orange': 'OF_SC_TEMPLATE_BA',
        'xoln': 'OF_SC_TEMPLATE_BA',
        'router4G': 'OF_SC_TEMPLATE_BA',
    }

    def __init__(self, contract, crm_account_hierarchy_code):
        self.contract = contract
        self.userAccount = crm_account_hierarchy_code

    @property
    def code(self):
        return self.contract.code

    @property
    def description(self):
        return self.contract.phone_number

    @property
    def offerTemplate(self):
        """
        Returns offer template code for current contract's service type.

        :return: offer template code (string)
        """
        return self.offer_template_code[self.contract.service_contract_type]

    @property
    def subscriptionDate(self):
        return self.contract.date_start.strftime("%Y-%m-%d")

    @property
    def customFields(self):
        if self.contract.service_contract_type == 'mobile':
            return {}
        internet_address = self.contract.service_partner_id
        return {
            "customField": [
                CustomField(
                    "CF_OF_SC_SUB_SERVICE_ADDRESS",
                    internet_address.full_street
                ).to_dict(),
                CustomField(
                    "CF_OF_SC_SUB_SERVICE_CP",
                    internet_address.zip
                ).to_dict(),
                CustomField(
                    "CF_OF_SC_SUB_SERVICE_CITY",
                    internet_address.city
                ).to_dict(),
                CustomField(
                    "CF_OF_SC_SUB_SERVICE_SUBDIVISION",
                    internet_address.state_id.name
                ).to_dict(),
            ]
        }
