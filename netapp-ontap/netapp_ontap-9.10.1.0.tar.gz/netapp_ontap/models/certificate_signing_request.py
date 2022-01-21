r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["CertificateSigningRequest", "CertificateSigningRequestSchema"]
__pdoc__ = {
    "CertificateSigningRequestSchema.resource": False,
    "CertificateSigningRequest": False,
}


class CertificateSigningRequestSchema(ResourceSchema):
    """The fields of the CertificateSigningRequest object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the certificate_signing_request. """

    algorithm = fields.Str(data_key="algorithm")
    r""" Asymmetric Encryption Algorithm.

Valid choices:

* rsa
* ecc """

    csr = fields.Str(data_key="csr")
    r""" A Certificate Signing Request (CSR) provided to a CA for obtaining a CA-signed certificate. """

    extended_key_usages = fields.List(fields.Str, data_key="extended_key_usages")
    r""" A list of extended key usage extensions. """

    generated_private_key = fields.Str(data_key="generated_private_key")
    r""" Private key generated for the CSR. """

    hash_function = fields.Str(data_key="hash_function")
    r""" Hashing function.

Valid choices:

* sha256
* sha224
* sha384
* sha512 """

    key_usages = fields.List(fields.Str, data_key="key_usages")
    r""" A list of key usage extensions. """

    security_strength = Size(data_key="security_strength")
    r""" Security strength of the certificate in bits. """

    subject_alternatives = fields.Nested("netapp_ontap.models.subject_alternate_name.SubjectAlternateNameSchema", unknown=EXCLUDE, data_key="subject_alternatives")
    r""" The subject_alternatives field of the certificate_signing_request. """

    subject_name = fields.Str(data_key="subject_name")
    r""" Subject name details of the certificate. The format is a list of comma separated key=value pairs.

Example: C=US,O=NTAP,CN=test.domain.com """

    @property
    def resource(self):
        return CertificateSigningRequest

    gettable_fields = [
        "links",
        "algorithm",
        "csr",
        "extended_key_usages",
        "generated_private_key",
        "hash_function",
        "key_usages",
        "security_strength",
        "subject_alternatives",
        "subject_name",
    ]
    """links,algorithm,csr,extended_key_usages,generated_private_key,hash_function,key_usages,security_strength,subject_alternatives,subject_name,"""

    patchable_fields = [
        "extended_key_usages",
        "key_usages",
    ]
    """extended_key_usages,key_usages,"""

    postable_fields = [
        "algorithm",
        "extended_key_usages",
        "hash_function",
        "key_usages",
        "security_strength",
        "subject_alternatives",
        "subject_name",
    ]
    """algorithm,extended_key_usages,hash_function,key_usages,security_strength,subject_alternatives,subject_name,"""


class CertificateSigningRequest(Resource):

    _schema = CertificateSigningRequestSchema
