r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FileInfoQosPolicy", "FileInfoQosPolicySchema"]
__pdoc__ = {
    "FileInfoQosPolicySchema.resource": False,
    "FileInfoQosPolicy": False,
}


class FileInfoQosPolicySchema(ResourceSchema):
    """The fields of the FileInfoQosPolicy object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the file_info_qos_policy. """

    name = fields.Str(data_key="name")
    r""" The name of the QoS policy. To remove the file from a QoS policy, set this property to an empty string "" or set it to "none" in a PATCH request.


Example: qos1 """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the QoS policy. Valid in PATCH.


Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return FileInfoQosPolicy

    gettable_fields = [
        "links",
        "name",
        "uuid",
    ]
    """links,name,uuid,"""

    patchable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    postable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""


class FileInfoQosPolicy(Resource):

    _schema = FileInfoQosPolicySchema
