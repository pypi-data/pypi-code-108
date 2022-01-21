r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SwitchPortIdentity", "SwitchPortIdentitySchema"]
__pdoc__ = {
    "SwitchPortIdentitySchema.resource": False,
    "SwitchPortIdentity": False,
}


class SwitchPortIdentitySchema(ResourceSchema):
    """The fields of the SwitchPortIdentity object"""

    index = Size(data_key="index")
    r""" Interface Index. """

    name = fields.Str(data_key="name")
    r""" Interface Name. """

    number = Size(data_key="number")
    r""" Interface Number. """

    @property
    def resource(self):
        return SwitchPortIdentity

    gettable_fields = [
        "index",
        "name",
        "number",
    ]
    """index,name,number,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class SwitchPortIdentity(Resource):

    _schema = SwitchPortIdentitySchema
