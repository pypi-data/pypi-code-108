r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupReplicationRelationship", "ConsistencyGroupReplicationRelationshipSchema"]
__pdoc__ = {
    "ConsistencyGroupReplicationRelationshipSchema.resource": False,
    "ConsistencyGroupReplicationRelationship": False,
}


class ConsistencyGroupReplicationRelationshipSchema(ResourceSchema):
    """The fields of the ConsistencyGroupReplicationRelationship object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the consistency_group_replication_relationship. """

    is_source = fields.Boolean(data_key="is_source")
    r""" Indicates whether or not this consistency group is the source for replication. """

    uuid = fields.Str(data_key="uuid")
    r""" The unique identifier of the SnapMirror relationship.


Example: 02c9e252-41be-11e9-81d5-00a0986138f7 """

    @property
    def resource(self):
        return ConsistencyGroupReplicationRelationship

    gettable_fields = [
        "links",
        "is_source",
        "uuid",
    ]
    """links,is_source,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ConsistencyGroupReplicationRelationship(Resource):

    _schema = ConsistencyGroupReplicationRelationshipSchema
