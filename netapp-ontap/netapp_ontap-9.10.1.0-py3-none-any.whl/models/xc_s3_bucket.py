r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["XcS3Bucket", "XcS3BucketSchema"]
__pdoc__ = {
    "XcS3BucketSchema.resource": False,
    "XcS3Bucket": False,
}


class XcS3BucketSchema(ResourceSchema):
    """The fields of the XcS3Bucket object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the xc_s3_bucket. """

    aggregates = fields.List(fields.Nested("netapp_ontap.resources.aggregate.AggregateSchema", unknown=EXCLUDE), data_key="aggregates")
    r""" A list of aggregates for FlexGroup volume constituents where the bucket is hosted. If this option is not specified, the bucket is auto-provisioned as a FlexGroup volume. """

    audit_event_selector = fields.Nested("netapp_ontap.models.s3_audit_event_selector.S3AuditEventSelectorSchema", unknown=EXCLUDE, data_key="audit_event_selector")
    r""" The audit_event_selector field of the xc_s3_bucket. """

    comment = fields.Str(data_key="comment")
    r""" Can contain any additional information about the bucket being created or modified.

Example: S3 bucket. """

    constituents_per_aggregate = Size(data_key="constituents_per_aggregate")
    r""" Specifies the number of constituents or FlexVol volumes per aggregate. A FlexGroup volume consisting of all such constituents across all specified aggregates is created. This option is used along with the aggregates option and cannot be used independently.

Example: 4 """

    encryption = fields.Nested("netapp_ontap.models.s3_bucket_encryption.S3BucketEncryptionSchema", unknown=EXCLUDE, data_key="encryption")
    r""" The encryption field of the xc_s3_bucket. """

    logical_used_size = Size(data_key="logical_used_size")
    r""" Specifies the bucket logical used size up to this point. """

    name = fields.Str(data_key="name")
    r""" Specifies the name of the bucket. Bucket name is a string that can only contain the following combination of ASCII-range alphanumeric characters 0-9, a-z, ".", and "-".

Example: bucket1 """

    policy = fields.Nested("netapp_ontap.models.s3_bucket_policy.S3BucketPolicySchema", unknown=EXCLUDE, data_key="policy")
    r""" The policy field of the xc_s3_bucket. """

    protection_status = fields.Nested("netapp_ontap.models.s3_bucket_protection_status.S3BucketProtectionStatusSchema", unknown=EXCLUDE, data_key="protection_status")
    r""" The protection_status field of the xc_s3_bucket. """

    qos_policy = fields.Nested("netapp_ontap.resources.qos_policy.QosPolicySchema", unknown=EXCLUDE, data_key="qos_policy")
    r""" The qos_policy field of the xc_s3_bucket. """

    role = fields.Str(data_key="role")
    r""" Specifies the role of the bucket.

Valid choices:

* standalone
* active
* passive """

    size = Size(data_key="size")
    r""" Specifies the bucket size in bytes; ranges from 80MB to 64TB.

Example: 1677721600 """

    storage_service_level = fields.Str(data_key="storage_service_level")
    r""" Specifies the storage service level of the FlexGroup volume on which the bucket should be created. Valid values are "value", "performance" or "extreme".

Valid choices:

* value
* performance
* extreme """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", unknown=EXCLUDE, data_key="svm")
    r""" The svm field of the xc_s3_bucket. """

    uuid = fields.Str(data_key="uuid")
    r""" Specifies the unique identifier of the bucket.

Example: 414b29a1-3b26-11e9-bd58-0050568ea055 """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", unknown=EXCLUDE, data_key="volume")
    r""" The volume field of the xc_s3_bucket. """

    @property
    def resource(self):
        return XcS3Bucket

    gettable_fields = [
        "links",
        "audit_event_selector",
        "comment",
        "encryption",
        "logical_used_size",
        "name",
        "policy",
        "protection_status",
        "qos_policy.links",
        "qos_policy.max_throughput_iops",
        "qos_policy.max_throughput_mbps",
        "qos_policy.min_throughput_iops",
        "qos_policy.min_throughput_mbps",
        "qos_policy.name",
        "qos_policy.uuid",
        "role",
        "size",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,audit_event_selector,comment,encryption,logical_used_size,name,policy,protection_status,qos_policy.links,qos_policy.max_throughput_iops,qos_policy.max_throughput_mbps,qos_policy.min_throughput_iops,qos_policy.min_throughput_mbps,qos_policy.name,qos_policy.uuid,role,size,svm.links,svm.name,svm.uuid,uuid,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "audit_event_selector",
        "comment",
        "encryption",
        "policy",
        "protection_status",
        "qos_policy.max_throughput_iops",
        "qos_policy.max_throughput_mbps",
        "qos_policy.min_throughput_iops",
        "qos_policy.min_throughput_mbps",
        "qos_policy.name",
        "qos_policy.uuid",
        "size",
        "volume.name",
        "volume.uuid",
    ]
    """audit_event_selector,comment,encryption,policy,protection_status,qos_policy.max_throughput_iops,qos_policy.max_throughput_mbps,qos_policy.min_throughput_iops,qos_policy.min_throughput_mbps,qos_policy.name,qos_policy.uuid,size,volume.name,volume.uuid,"""

    postable_fields = [
        "aggregates.name",
        "aggregates.uuid",
        "audit_event_selector",
        "comment",
        "constituents_per_aggregate",
        "encryption",
        "name",
        "policy",
        "protection_status",
        "qos_policy.max_throughput_iops",
        "qos_policy.max_throughput_mbps",
        "qos_policy.min_throughput_iops",
        "qos_policy.min_throughput_mbps",
        "qos_policy.name",
        "qos_policy.uuid",
        "size",
        "storage_service_level",
        "svm.name",
        "svm.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """aggregates.name,aggregates.uuid,audit_event_selector,comment,constituents_per_aggregate,encryption,name,policy,protection_status,qos_policy.max_throughput_iops,qos_policy.max_throughput_mbps,qos_policy.min_throughput_iops,qos_policy.min_throughput_mbps,qos_policy.name,qos_policy.uuid,size,storage_service_level,svm.name,svm.uuid,volume.name,volume.uuid,"""


class XcS3Bucket(Resource):

    _schema = XcS3BucketSchema
