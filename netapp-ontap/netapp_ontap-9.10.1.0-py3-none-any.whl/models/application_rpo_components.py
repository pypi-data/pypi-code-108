r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationRpoComponents", "ApplicationRpoComponentsSchema"]
__pdoc__ = {
    "ApplicationRpoComponentsSchema.resource": False,
    "ApplicationRpoComponents": False,
}


class ApplicationRpoComponentsSchema(ResourceSchema):
    """The fields of the ApplicationRpoComponents object"""

    name = fields.Str(data_key="name")
    r""" Component Name. """

    rpo = fields.Nested("netapp_ontap.models.application_rpo_rpo.ApplicationRpoRpoSchema", unknown=EXCLUDE, data_key="rpo")
    r""" The rpo field of the application_rpo_components. """

    uuid = fields.Str(data_key="uuid")
    r""" Component UUID. """

    @property
    def resource(self):
        return ApplicationRpoComponents

    gettable_fields = [
        "name",
        "rpo",
        "uuid",
    ]
    """name,rpo,uuid,"""

    patchable_fields = [
        "rpo",
    ]
    """rpo,"""

    postable_fields = [
        "rpo",
    ]
    """rpo,"""


class ApplicationRpoComponents(Resource):

    _schema = ApplicationRpoComponentsSchema
