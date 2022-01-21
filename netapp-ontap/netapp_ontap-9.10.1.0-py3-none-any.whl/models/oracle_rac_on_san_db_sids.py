r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["OracleRacOnSanDbSids", "OracleRacOnSanDbSidsSchema"]
__pdoc__ = {
    "OracleRacOnSanDbSidsSchema.resource": False,
    "OracleRacOnSanDbSids": False,
}


class OracleRacOnSanDbSidsSchema(ResourceSchema):
    """The fields of the OracleRacOnSanDbSids object"""

    igroup_name = fields.Str(data_key="igroup_name")
    r""" The name of the initiator group through which the contents of this application will be accessed. Modification of this parameter is a disruptive operation. All LUNs in the application component will be unmapped from the current igroup and re-mapped to the new igroup. """

    @property
    def resource(self):
        return OracleRacOnSanDbSids

    gettable_fields = [
        "igroup_name",
    ]
    """igroup_name,"""

    patchable_fields = [
        "igroup_name",
    ]
    """igroup_name,"""

    postable_fields = [
        "igroup_name",
    ]
    """igroup_name,"""


class OracleRacOnSanDbSids(Resource):

    _schema = OracleRacOnSanDbSidsSchema
