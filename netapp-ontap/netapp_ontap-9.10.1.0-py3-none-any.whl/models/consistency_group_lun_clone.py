r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupLunClone", "ConsistencyGroupLunCloneSchema"]
__pdoc__ = {
    "ConsistencyGroupLunCloneSchema.resource": False,
    "ConsistencyGroupLunClone": False,
}


class ConsistencyGroupLunCloneSchema(ResourceSchema):
    """The fields of the ConsistencyGroupLunClone object"""

    source = fields.Nested("netapp_ontap.models.consistency_group_lun_clone_source.ConsistencyGroupLunCloneSourceSchema", unknown=EXCLUDE, data_key="source")
    r""" The source field of the consistency_group_lun_clone. """

    @property
    def resource(self):
        return ConsistencyGroupLunClone

    gettable_fields = [
    ]
    """"""

    patchable_fields = [
        "source",
    ]
    """source,"""

    postable_fields = [
        "source",
    ]
    """source,"""


class ConsistencyGroupLunClone(Resource):

    _schema = ConsistencyGroupLunCloneSchema
