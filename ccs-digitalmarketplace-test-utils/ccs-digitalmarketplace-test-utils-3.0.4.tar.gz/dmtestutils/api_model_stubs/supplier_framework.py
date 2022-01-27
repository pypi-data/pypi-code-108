from .base import BaseAPIModelStub


class SupplierFrameworkStub(BaseAPIModelStub):
    resource_name = 'frameworkInterest'
    default_data = {
        "agreementId": None,
        "agreementPath": None,
        "agreementReturned": False,
        "agreementReturnedAt": None,
        "agreementStatus": None,
        "allowDeclarationReuse": True,
        "applicationCompanyDetailsConfirmed": None,
        "countersigned": False,
        "countersignedAt": None,
        "countersignedDetails": None,
        "countersignedPath": None,
        "frameworkFamily": "g-cloud",
        "frameworkFramework": "g-cloud",
        "frameworkSlug": "g-cloud-13",
        "onFramework": False,
        "prefillDeclarationFromFrameworkSlug": None,
        "supplierId": 886665,
        "supplierName": "Kev's Pies"
    }
    optional_keys = [
        ('supplierId', 'supplier_id'),
        ('frameworkSlug', 'framework_slug'),
        ('onFramework', 'on_framework'),
        ('prefillDeclarationFromFrameworkSlug', 'prefill_declaration_from_slug'),
        ('applicationCompanyDetailsConfirmed', 'application_company_details_confirmed')
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if kwargs.get('agreed_variations'):
            self.response_data['agreedVariations'] = {
                "1": {
                    "agreedAt": "2018-05-04T16:58:52.362855Z",
                    "agreedUserEmail": "stub@example.com",
                    "agreedUserId": 123,
                    "agreedUserName": "Test user"
                }
            }
        else:
            self.response_data['agreedVariations'] = {}

        if kwargs.get('with_declaration'):
            self.response_data['declaration'] = {
                "nameOfOrganisation": "My Little Company",
                "organisationSize": "micro",
                "primaryContactEmail": "supplier@example.com",
                "status": kwargs.get('declaration_status', 'unstarted'),
            }
        else:
            self.response_data['declaration'] = {}

        if kwargs.get('with_agreement'):
            agreement_data = {
                "agreementId": 9876,
                "agreementReturned": True,
                "agreementReturnedAt": "2017-05-17T14:31:27.118905Z",
                "agreementDetails": {
                    "frameworkAgreementVersion": "RM1557ix",
                    "signerName": "A. Nonymous",
                    "signerRole": "The Boss",
                    "uploaderUserId": 443333,
                    "uploaderUserName": "Test user",
                    "uploaderUserEmail": "supplier@example.com",
                },
                "agreementPath": "not/the/real/path.pdf",
                "countersigned": True,
                "countersignedAt": "2017-06-15T08:41:46.390992Z",
                "countersignedDetails": {
                    "approvedByUserId": 123,
                },
                "agreementStatus": "countersigned",
            }
            if kwargs.get('with_users'):
                agreement_data['agreementDetails'].update({
                    "uploaderUserEmail": "stub@example.com",
                    "uploaderUserName": "Test user",
                })
                agreement_data['countersignedDetails'].update({
                    "approvedByUserEmail": "stub@example.com",
                    "approvedByUserName": "Test user",
                })
            self.response_data.update(agreement_data)
        else:
            self.response_data['agreementDetails'] = {}

        for snakecase_key in [
            'agreed_variations', 'with_declaration', 'with_agreement', 'with_users', 'declaration_status'
        ]:
            if kwargs.get(snakecase_key):
                del self.response_data[snakecase_key]
