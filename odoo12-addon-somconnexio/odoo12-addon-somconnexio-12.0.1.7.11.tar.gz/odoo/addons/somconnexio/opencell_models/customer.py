from .account_hierarchy_resource import AccountHierarchyResource


class CustomerFromPartner(AccountHierarchyResource):

    def __init__(self, partner, opencell_configuration):
        self.opencell_configuration = opencell_configuration
        self.partner = partner
        self.white_list = ['seller', 'code', 'description', 'name',
                           'address', 'vatNo', 'contactInformation', 'customerCategory']

    @property
    def seller(self):
        return self.opencell_configuration.seller_code

    @property
    def code(self):
        return self.partner.ref

    @property
    def email(self):
        return self.partner.email

    @property
    def customerCategory(self):
        return self.opencell_configuration.customer_category_code

    @property
    def phone(self):
        return self.partner.mobile or self.partner.phone
