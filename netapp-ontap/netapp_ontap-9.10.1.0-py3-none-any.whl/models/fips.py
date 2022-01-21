r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Fips", "FipsSchema"]
__pdoc__ = {
    "FipsSchema.resource": False,
    "Fips": False,
}


class FipsSchema(ResourceSchema):
    """The fields of the Fips object"""

    enabled = fields.Boolean(data_key="enabled")
    r""" Indicates whether or not the software FIPS mode is enabled on the cluster. Our FIPS compliance involves configuring the use of only approved algorithms in applicable contexts (for example TLS), as well as the use of formally validated cryptographic module software implementations, where applicable. The US government documents concerning FIPS 140-2 outline the relevant security policies in detail. """

    @property
    def resource(self):
        return Fips

    gettable_fields = [
        "enabled",
    ]
    """enabled,"""

    patchable_fields = [
        "enabled",
    ]
    """enabled,"""

    postable_fields = [
    ]
    """"""


class Fips(Resource):

    _schema = FipsSchema
