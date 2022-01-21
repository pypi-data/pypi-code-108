r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationRpoRpo", "ApplicationRpoRpoSchema"]
__pdoc__ = {
    "ApplicationRpoRpoSchema.resource": False,
    "ApplicationRpoRpo": False,
}


class ApplicationRpoRpoSchema(ResourceSchema):
    """The fields of the ApplicationRpoRpo object"""

    local = fields.Nested("netapp_ontap.models.application_rpo_rpo_local.ApplicationRpoRpoLocalSchema", unknown=EXCLUDE, data_key="local")
    r""" The local field of the application_rpo_rpo. """

    remote = fields.Nested("netapp_ontap.models.application_rpo_rpo_remote.ApplicationRpoRpoRemoteSchema", unknown=EXCLUDE, data_key="remote")
    r""" The remote field of the application_rpo_rpo. """

    @property
    def resource(self):
        return ApplicationRpoRpo

    gettable_fields = [
        "local",
        "remote",
    ]
    """local,remote,"""

    patchable_fields = [
        "local",
        "remote",
    ]
    """local,remote,"""

    postable_fields = [
        "local",
        "remote",
    ]
    """local,remote,"""


class ApplicationRpoRpo(Resource):

    _schema = ApplicationRpoRpoSchema
