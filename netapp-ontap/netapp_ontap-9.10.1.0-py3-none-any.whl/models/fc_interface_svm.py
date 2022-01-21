r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FcInterfaceSvm", "FcInterfaceSvmSchema"]
__pdoc__ = {
    "FcInterfaceSvmSchema.resource": False,
    "FcInterfaceSvm": False,
}


class FcInterfaceSvmSchema(ResourceSchema):
    """The fields of the FcInterfaceSvm object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the fc_interface_svm. """

    data_protocol = fields.Str(data_key="data_protocol")
    r""" The data protocol for which the Fibre Channel interface is configured.

Valid choices:

* fcp
* fc_nvme """

    location = fields.Nested("netapp_ontap.models.fc_interface_svm_location.FcInterfaceSvmLocationSchema", unknown=EXCLUDE, data_key="location")
    r""" The location field of the fc_interface_svm. """

    name = fields.Str(data_key="name")
    r""" The name of the Fibre Channel interface.

Example: lif1 """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the Fibre Channel interface.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return FcInterfaceSvm

    gettable_fields = [
        "links",
        "data_protocol",
        "name",
        "uuid",
    ]
    """links,data_protocol,name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "data_protocol",
        "location",
        "name",
    ]
    """data_protocol,location,name,"""


class FcInterfaceSvm(Resource):

    _schema = FcInterfaceSvmSchema
