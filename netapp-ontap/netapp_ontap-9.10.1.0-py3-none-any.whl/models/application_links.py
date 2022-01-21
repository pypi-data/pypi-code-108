r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationLinks", "ApplicationLinksSchema"]
__pdoc__ = {
    "ApplicationLinksSchema.resource": False,
    "ApplicationLinks": False,
}


class ApplicationLinksSchema(ResourceSchema):
    """The fields of the ApplicationLinks object"""

    self_ = fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="self")
    r""" The self_ field of the application_links. """

    snapshots = fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="snapshots")
    r""" The snapshots field of the application_links. """

    @property
    def resource(self):
        return ApplicationLinks

    gettable_fields = [
        "self_",
        "snapshots",
    ]
    """self_,snapshots,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationLinks(Resource):

    _schema = ApplicationLinksSchema
