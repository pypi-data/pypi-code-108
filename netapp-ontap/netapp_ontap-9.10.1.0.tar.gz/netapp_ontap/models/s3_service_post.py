r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["S3ServicePost", "S3ServicePostSchema"]
__pdoc__ = {
    "S3ServicePostSchema.resource": False,
    "S3ServicePost": False,
}


class S3ServicePostSchema(ResourceSchema):
    """The fields of the S3ServicePost object"""

    num_records = Size(data_key="num_records")
    r""" Number of Records """

    records = fields.List(fields.Nested("netapp_ontap.models.s3_service_post_response_records.S3ServicePostResponseRecordsSchema", unknown=EXCLUDE), data_key="records")
    r""" The records field of the s3_service_post. """

    @property
    def resource(self):
        return S3ServicePost

    gettable_fields = [
        "num_records",
        "records",
    ]
    """num_records,records,"""

    patchable_fields = [
        "num_records",
        "records",
    ]
    """num_records,records,"""

    postable_fields = [
        "num_records",
        "records",
    ]
    """num_records,records,"""


class S3ServicePost(Resource):

    _schema = S3ServicePostSchema
