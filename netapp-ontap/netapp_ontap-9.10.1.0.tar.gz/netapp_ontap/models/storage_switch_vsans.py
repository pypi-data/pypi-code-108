r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["StorageSwitchVsans", "StorageSwitchVsansSchema"]
__pdoc__ = {
    "StorageSwitchVsansSchema.resource": False,
    "StorageSwitchVsans": False,
}


class StorageSwitchVsansSchema(ResourceSchema):
    """The fields of the StorageSwitchVsans object"""

    id = Size(data_key="id")
    r""" Storage switch VSAN ID """

    iod = fields.Boolean(data_key="iod")
    r""" Indicates whether in-order delivery is set for a zone. """

    load_balancing_types = fields.Str(data_key="load_balancing_types")
    r""" Storage switch VSAN load balancing type """

    name = fields.Str(data_key="name")
    r""" Storage switch VSAN name """

    state = fields.Str(data_key="state")
    r""" Storage switch VSAN Port state

Valid choices:

* ok
* error """

    @property
    def resource(self):
        return StorageSwitchVsans

    gettable_fields = [
        "id",
        "iod",
        "load_balancing_types",
        "name",
        "state",
    ]
    """id,iod,load_balancing_types,name,state,"""

    patchable_fields = [
        "id",
        "iod",
        "load_balancing_types",
        "name",
        "state",
    ]
    """id,iod,load_balancing_types,name,state,"""

    postable_fields = [
        "id",
        "iod",
        "load_balancing_types",
        "name",
        "state",
    ]
    """id,iod,load_balancing_types,name,state,"""


class StorageSwitchVsans(Resource):

    _schema = StorageSwitchVsansSchema
