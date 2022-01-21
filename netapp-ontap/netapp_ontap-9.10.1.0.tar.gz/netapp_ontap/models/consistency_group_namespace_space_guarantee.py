r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupNamespaceSpaceGuarantee", "ConsistencyGroupNamespaceSpaceGuaranteeSchema"]
__pdoc__ = {
    "ConsistencyGroupNamespaceSpaceGuaranteeSchema.resource": False,
    "ConsistencyGroupNamespaceSpaceGuarantee": False,
}


class ConsistencyGroupNamespaceSpaceGuaranteeSchema(ResourceSchema):
    """The fields of the ConsistencyGroupNamespaceSpaceGuarantee object"""

    requested = fields.Boolean(data_key="requested")
    r""" The requested space reservation policy for the NVMe namespace. If _true_, a space reservation is requested for the namespace; if _false_, the namespace is thin provisioned. Guaranteeing a space reservation request for a namespace requires that the volume in which the namespace resides also be space reserved and that the fractional reserve for the volume be 100%.<br/>
The space reservation policy for an NVMe namespace is determined by ONTAP. """

    reserved = fields.Boolean(data_key="reserved")
    r""" Reports if the NVMe namespace is space guaranteed.<br/>
This property is _true_ if a space guarantee is requested and the containing volume and aggregate support the request. This property is _false_ if a space guarantee is not requested or if a space guarantee is requested and either the containing volume and aggregate do not support the request. """

    @property
    def resource(self):
        return ConsistencyGroupNamespaceSpaceGuarantee

    gettable_fields = [
        "requested",
        "reserved",
    ]
    """requested,reserved,"""

    patchable_fields = [
        "requested",
    ]
    """requested,"""

    postable_fields = [
        "requested",
    ]
    """requested,"""


class ConsistencyGroupNamespaceSpaceGuarantee(Resource):

    _schema = ConsistencyGroupNamespaceSpaceGuaranteeSchema
