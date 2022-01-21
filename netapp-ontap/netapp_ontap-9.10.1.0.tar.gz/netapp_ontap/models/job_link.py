r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["JobLink", "JobLinkSchema"]
__pdoc__ = {
    "JobLinkSchema.resource": False,
    "JobLink": False,
}


class JobLinkSchema(ResourceSchema):
    """The fields of the JobLink object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the job_link. """

    uuid = fields.Str(data_key="uuid")
    r""" The UUID of the asynchronous job that is triggered by a POST, PATCH, or DELETE operation. """

    @property
    def resource(self):
        return JobLink

    gettable_fields = [
        "links",
        "uuid",
    ]
    """links,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class JobLink(Resource):

    _schema = JobLinkSchema
