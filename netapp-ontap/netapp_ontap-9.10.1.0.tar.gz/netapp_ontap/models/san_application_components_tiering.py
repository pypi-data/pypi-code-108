r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SanApplicationComponentsTiering", "SanApplicationComponentsTieringSchema"]
__pdoc__ = {
    "SanApplicationComponentsTieringSchema.resource": False,
    "SanApplicationComponentsTiering": False,
}


class SanApplicationComponentsTieringSchema(ResourceSchema):
    """The fields of the SanApplicationComponentsTiering object"""

    control = fields.Str(data_key="control")
    r""" Storage tiering placement rules for the container(s)

Valid choices:

* required
* best_effort
* disallowed """

    object_stores = fields.List(fields.Nested("netapp_ontap.models.maxdata_on_san_application_components_tiering_object_stores.MaxdataOnSanApplicationComponentsTieringObjectStoresSchema", unknown=EXCLUDE), data_key="object_stores")
    r""" The object_stores field of the san_application_components_tiering. """

    policy = fields.Str(data_key="policy")
    r""" The storage tiering type of the application component.

Valid choices:

* all
* auto
* none
* snapshot_only """

    @property
    def resource(self):
        return SanApplicationComponentsTiering

    gettable_fields = [
        "policy",
    ]
    """policy,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "control",
        "object_stores",
        "policy",
    ]
    """control,object_stores,policy,"""


class SanApplicationComponentsTiering(Resource):

    _schema = SanApplicationComponentsTieringSchema
