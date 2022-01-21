r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationComponentSnapshotComponent", "ApplicationComponentSnapshotComponentSchema"]
__pdoc__ = {
    "ApplicationComponentSnapshotComponentSchema.resource": False,
    "ApplicationComponentSnapshotComponent": False,
}


class ApplicationComponentSnapshotComponentSchema(ResourceSchema):
    """The fields of the ApplicationComponentSnapshotComponent object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the application_component_snapshot_component. """

    name = fields.Str(data_key="name")
    r""" Component Name """

    uuid = fields.Str(data_key="uuid")
    r""" Component UUID """

    @property
    def resource(self):
        return ApplicationComponentSnapshotComponent

    gettable_fields = [
        "links",
        "name",
        "uuid",
    ]
    """links,name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationComponentSnapshotComponent(Resource):

    _schema = ApplicationComponentSnapshotComponentSchema
