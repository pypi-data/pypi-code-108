r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeVm", "NodeVmSchema"]
__pdoc__ = {
    "NodeVmSchema.resource": False,
    "NodeVm": False,
}


class NodeVmSchema(ResourceSchema):
    """The fields of the NodeVm object"""

    provider_type = fields.Str(data_key="provider_type")
    r""" Cloud provider where the VM is hosted.

Valid choices:

* GoogleCloud
* AWS_S3
* Azure_Cloud """

    @property
    def resource(self):
        return NodeVm

    gettable_fields = [
        "provider_type",
    ]
    """provider_type,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NodeVm(Resource):

    _schema = NodeVmSchema
