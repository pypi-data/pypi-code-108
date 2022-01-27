from .base import BaseAPIModelStub


class SupplierStub(BaseAPIModelStub):
    resource_name = 'suppliers'
    contact_information = {
        "address1": "123 Fake Road",
        "city": "Madeupolis",
        "contactName": "Mr E Man",
        "email": "mre@company.com",
        "id": 4321,
        "links": {
            "self": "http://localhost:5000/suppliers/1234/contact-information/4321"
        },
        "phoneNumber": "01234123123",
        "postcode": "A11 1AA",
        "website": "https://www.mre.company"
    }
    default_data = {
        "companiesHouseNumber": "12345678",
        "companyDetailsConfirmed": True,
        "contactInformation": [contact_information],
        "description": "I'm a supplier.",
        "dunsNumber": "123456789",
        "id": 1234,
        "links": {
            "self": "http://localhost:5000/suppliers/1234"
        },
        "name": "My Little Company",
        "organisationSize": "micro",
        "registeredName": "My Little Registered Company",
        "registrationCountry": "country:GB",
        "tradingStatus": "limited company",
        "vatNumber": "111222333"
    }
    optional_keys = [
        ("otherCompanyRegistrationNumber", "other_company_registration_number"),
        ("companyDetailsConfirmed", "company_details_confirmed"),
    ]

    def single_result_response(self):
        # Include service_counts in API response only - this key isn't present in Supplier.serialize()
        self.response_data['service_counts'] = {
            "G-Cloud 9": 109,
            "G-Cloud 8": 108,
            "G-Cloud 7": 107,
            "G-Cloud 6": 106,
            "G-Cloud 5": 105,
            "G-Cloud 13": 113
        }
        return {
            self.resource_name: self.response_data
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if kwargs.get('id'):
            self.response_data["links"]["self"] = "http://localhost:5000/suppliers/{id}".format(id=kwargs.get('id'))

        if kwargs.get('contact_id'):
            self.contact_information['id'] = kwargs.get('contact_id')
            self.contact_information['links']['self'] = \
                "http://localhost:5000/suppliers/{id}/contact-information/{contact_id}".format(
                    id=self.response_data['id'], contact_id=kwargs.get('contact_id')
                )
            self.response_data["contactInformation"] = [self.contact_information]
            # Don't include the kwarg in response
            del self.response_data['contact_id']

        if self.response_data.get('otherCompanyRegistrationNumber'):
            # We allow one or other of these registration numbers, but not both
            del self.response_data['companiesHouseNumber']
            # Companies without a Companies House number aren't necessarily overseas, but they might well be
            self.response_data['registrationCountry'] = 'country:NZ'
