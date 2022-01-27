from .base import BaseAPIModelStub


class FrameworkAgreementStub(BaseAPIModelStub):
    resource_name = 'agreement'
    default_data = {
        'id': 1234,
        'supplierId': 43333,
        'frameworkSlug': "digital-outcomes-and-specialists-3",
        'status': '',
    }
    optional_keys = [
        ('signedAgreementDetails', 'signed_agreement_details'),
        ('signedAgreementPath', 'signed_agreement_path'),
        ('signedAgreementReturnedAt', 'signed_agreement_returned_at'),
        ('countersignedAgreementDetails', 'countersigned_agreement_details'),
        ('countersignedAgreementReturnedAt', 'countersigned_agreement_returned_at'),
        ('countersignedAgreementPath', 'countersigned_agreement_path')
    ]
