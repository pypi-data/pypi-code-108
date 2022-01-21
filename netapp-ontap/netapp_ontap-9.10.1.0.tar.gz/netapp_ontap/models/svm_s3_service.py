r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SvmS3Service", "SvmS3ServiceSchema"]
__pdoc__ = {
    "SvmS3ServiceSchema.resource": False,
    "SvmS3Service": False,
}


class SvmS3ServiceSchema(ResourceSchema):
    """The fields of the SvmS3Service object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the svm_s3_service. """

    certificate = fields.Nested("netapp_ontap.resources.security_certificate.SecurityCertificateSchema", unknown=EXCLUDE, data_key="certificate")
    r""" The certificate field of the svm_s3_service. """

    enabled = fields.Boolean(data_key="enabled")
    r""" Specifies whether or not to enable S3. Setting this value to true creates a service if one is not yet created. """

    is_http_enabled = fields.Boolean(data_key="is_http_enabled")
    r""" Specifies whether HTTP is enabled on the S3 server. By default, HTTP is disabled on the S3 server. """

    is_https_enabled = fields.Boolean(data_key="is_https_enabled")
    r""" Specifies whether HTTPS is enabled on the S3 server. By default, HTTPS is enabled on the S3 server. """

    name = fields.Str(data_key="name")
    r""" Specifies the name of the S3 server. A server name length can range from 1 to 253 characters and can only contain the following combination of characters 0-9, A-Z, a-z, ".", and "-".

Example: s3-server-1 """

    port = Size(data_key="port")
    r""" Specifies the HTTP listener port for the S3 server. By default, HTTP is enabled on port 80. """

    secure_port = Size(data_key="secure_port")
    r""" Specifies the HTTPS listener port for the S3 server. By default, HTTPS is enabled on port 443. """

    @property
    def resource(self):
        return SvmS3Service

    gettable_fields = [
        "links",
        "certificate.links",
        "certificate.name",
        "certificate.uuid",
        "enabled",
        "is_http_enabled",
        "is_https_enabled",
        "name",
        "port",
        "secure_port",
    ]
    """links,certificate.links,certificate.name,certificate.uuid,enabled,is_http_enabled,is_https_enabled,name,port,secure_port,"""

    patchable_fields = [
        "certificate.name",
        "certificate.uuid",
        "enabled",
        "is_http_enabled",
        "is_https_enabled",
        "name",
        "port",
        "secure_port",
    ]
    """certificate.name,certificate.uuid,enabled,is_http_enabled,is_https_enabled,name,port,secure_port,"""

    postable_fields = [
        "certificate.name",
        "certificate.uuid",
        "enabled",
        "is_http_enabled",
        "is_https_enabled",
        "name",
        "port",
        "secure_port",
    ]
    """certificate.name,certificate.uuid,enabled,is_http_enabled,is_https_enabled,name,port,secure_port,"""


class SvmS3Service(Resource):

    _schema = SvmS3ServiceSchema
