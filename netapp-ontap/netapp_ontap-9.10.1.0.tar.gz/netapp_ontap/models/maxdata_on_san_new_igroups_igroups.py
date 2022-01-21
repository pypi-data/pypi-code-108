r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MaxdataOnSanNewIgroupsIgroups", "MaxdataOnSanNewIgroupsIgroupsSchema"]
__pdoc__ = {
    "MaxdataOnSanNewIgroupsIgroupsSchema.resource": False,
    "MaxdataOnSanNewIgroupsIgroups": False,
}


class MaxdataOnSanNewIgroupsIgroupsSchema(ResourceSchema):
    """The fields of the MaxdataOnSanNewIgroupsIgroups object"""

    name = fields.Str(data_key="name")
    r""" The name of an igroup to nest within a parent igroup. Mutually exclusive with initiators and initiator_objects. """

    uuid = fields.Str(data_key="uuid")
    r""" The UUID of an igroup to nest within a parent igroup Usage: &lt;UUID&gt; """

    @property
    def resource(self):
        return MaxdataOnSanNewIgroupsIgroups

    gettable_fields = [
    ]
    """"""

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


class MaxdataOnSanNewIgroupsIgroups(Resource):

    _schema = MaxdataOnSanNewIgroupsIgroupsSchema
