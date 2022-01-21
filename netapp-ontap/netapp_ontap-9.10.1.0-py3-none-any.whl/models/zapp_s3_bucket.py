r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ZappS3Bucket", "ZappS3BucketSchema"]
__pdoc__ = {
    "ZappS3BucketSchema.resource": False,
    "ZappS3Bucket": False,
}


class ZappS3BucketSchema(ResourceSchema):
    """The fields of the ZappS3Bucket object"""

    application_components = fields.List(fields.Nested("netapp_ontap.models.zapp_s3_bucket_application_components.ZappS3BucketApplicationComponentsSchema", unknown=EXCLUDE), data_key="application_components")
    r""" The list of application components to be created. """

    @property
    def resource(self):
        return ZappS3Bucket

    gettable_fields = [
        "application_components",
    ]
    """application_components,"""

    patchable_fields = [
        "application_components",
    ]
    """application_components,"""

    postable_fields = [
        "application_components",
    ]
    """application_components,"""


class ZappS3Bucket(Resource):

    _schema = ZappS3BucketSchema
