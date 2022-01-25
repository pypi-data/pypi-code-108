from otrs_somconnexio.otrs_models.customer_data import CustomerData


class CustomerDataFromResPartner:

    def __init__(self, partner):
        self.partner = partner

    def build(self):
        return CustomerData(
            id=self.partner.ref,
            vat_number=self.partner.vat,
            phone=self.partner.mobile or self.partner.phone,
            name=self.partner.lastname,
            first_name=self.partner.firstname,
            street=self.partner.full_street,
            zip=self.partner.zip,
            city=self.partner.city,
            subdivision="{}-{}".format(
                self.partner.country_id.code,
                self.partner.state_id.code
            ),
        )
