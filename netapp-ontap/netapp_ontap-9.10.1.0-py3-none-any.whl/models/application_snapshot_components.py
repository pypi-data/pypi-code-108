r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationSnapshotComponents", "ApplicationSnapshotComponentsSchema"]
__pdoc__ = {
    "ApplicationSnapshotComponentsSchema.resource": False,
    "ApplicationSnapshotComponents": False,
}


class ApplicationSnapshotComponentsSchema(ResourceSchema):
    """The fields of the ApplicationSnapshotComponents object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the application_snapshot_components. """

    name = fields.Str(data_key="name")
    r""" Component name """

    uuid = fields.Str(data_key="uuid")
    r""" Component UUID """

    @property
    def resource(self):
        return ApplicationSnapshotComponents

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


class ApplicationSnapshotComponents(Resource):

    _schema = ApplicationSnapshotComponentsSchema
