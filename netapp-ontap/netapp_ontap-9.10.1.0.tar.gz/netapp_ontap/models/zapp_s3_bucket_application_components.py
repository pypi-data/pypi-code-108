r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ZappS3BucketApplicationComponents", "ZappS3BucketApplicationComponentsSchema"]
__pdoc__ = {
    "ZappS3BucketApplicationComponentsSchema.resource": False,
    "ZappS3BucketApplicationComponents": False,
}


class ZappS3BucketApplicationComponentsSchema(ResourceSchema):
    """The fields of the ZappS3BucketApplicationComponents object"""

    access_policies = fields.List(fields.Nested("netapp_ontap.models.zapp_s3_bucket_application_components_access_policies.ZappS3BucketApplicationComponentsAccessPoliciesSchema", unknown=EXCLUDE), data_key="access_policies")
    r""" The list of S3 objectstore policies to be created. """

    capacity_tier = fields.Boolean(data_key="capacity_tier")
    r""" Prefer lower latency storage under similar media costs. """

    comment = fields.Str(data_key="comment")
    r""" Object Store Server Bucket Description Usage: &lt;(size 1..256)&gt; """

    exclude_aggregates = fields.List(fields.Nested("netapp_ontap.models.nas_exclude_aggregates.NasExcludeAggregatesSchema", unknown=EXCLUDE), data_key="exclude_aggregates")
    r""" The exclude_aggregates field of the zapp_s3_bucket_application_components. """

    name = fields.Str(data_key="name")
    r""" The name of the application component. """

    qos = fields.Nested("netapp_ontap.models.nas_qos.NasQosSchema", unknown=EXCLUDE, data_key="qos")
    r""" The qos field of the zapp_s3_bucket_application_components. """

    size = Size(data_key="size")
    r""" The total size of the S3 Bucket, split across the member components. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    storage_service = fields.Nested("netapp_ontap.models.nas_storage_service.NasStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the zapp_s3_bucket_application_components. """

    uuid = fields.Str(data_key="uuid")
    r""" Object Store Server Bucket UUID Usage: &lt;UUID&gt; """

    @property
    def resource(self):
        return ZappS3BucketApplicationComponents

    gettable_fields = [
        "access_policies",
        "capacity_tier",
        "comment",
        "exclude_aggregates",
        "name",
        "qos",
        "size",
        "storage_service",
        "uuid",
    ]
    """access_policies,capacity_tier,comment,exclude_aggregates,name,qos,size,storage_service,uuid,"""

    patchable_fields = [
        "name",
        "size",
        "storage_service",
    ]
    """name,size,storage_service,"""

    postable_fields = [
        "access_policies",
        "capacity_tier",
        "comment",
        "exclude_aggregates",
        "name",
        "qos",
        "size",
        "storage_service",
    ]
    """access_policies,capacity_tier,comment,exclude_aggregates,name,qos,size,storage_service,"""


class ZappS3BucketApplicationComponents(Resource):

    _schema = ZappS3BucketApplicationComponentsSchema
