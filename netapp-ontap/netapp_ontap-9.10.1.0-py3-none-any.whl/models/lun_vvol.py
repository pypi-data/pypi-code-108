r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunVvol", "LunVvolSchema"]
__pdoc__ = {
    "LunVvolSchema.resource": False,
    "LunVvol": False,
}


class LunVvolSchema(ResourceSchema):
    """The fields of the LunVvol object"""

    bindings = fields.List(fields.Nested("netapp_ontap.models.lun_vvol_bindings.LunVvolBindingsSchema", unknown=EXCLUDE), data_key="bindings")
    r""" Bindings between the LUN, which must be of class `protocol_endpoint` or `vvol`, and LUNs of the opposite class.<br/>
A class `vvol` LUN must be bound to a class `protocol_endpoint` LUN in order to be accessed. Class `protocol_endpoint` and `vvol` LUNs allow many-to-many bindings. A LUN of one class is allowed to be bound to zero or more LUNs of the opposite class. The binding between any two specific LUNs is reference counted. When a binding is created that already exists, the binding count is incremented. When a binding is deleted, the binding count is decremented, but the LUNs remain bound if the resultant reference count is greater than zero. When the binding count reaches zero, the binding is destroyed.<br/>
The bindings array contains LUNs of the opposite class of the containing LUN object.<br/>
There is an added cost to retrieving property values for `vvol.bindings`. They are not populated for either a collection GET or an instance GET unless explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. """

    is_bound = fields.Boolean(data_key="is_bound")
    r""" Reports if the LUN is part of a VMware virtual volume (vVol) bind relationship. This is `true` if the LUN is of class `protocol_endpoint` or `vvol` and has one or more bindings to a LUN of the opposite class. This is false if the LUN is of class `regular` or unbound. """

    @property
    def resource(self):
        return LunVvol

    gettable_fields = [
        "bindings",
        "is_bound",
    ]
    """bindings,is_bound,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class LunVvol(Resource):

    _schema = LunVvolSchema
