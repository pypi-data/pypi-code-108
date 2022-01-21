r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MaxdataOnSanApplicationComponentsMetadata", "MaxdataOnSanApplicationComponentsMetadataSchema"]
__pdoc__ = {
    "MaxdataOnSanApplicationComponentsMetadataSchema.resource": False,
    "MaxdataOnSanApplicationComponentsMetadata": False,
}


class MaxdataOnSanApplicationComponentsMetadataSchema(ResourceSchema):
    """The fields of the MaxdataOnSanApplicationComponentsMetadata object"""

    key = fields.Str(data_key="key")
    r""" Key to look up metadata associated with an application component. """

    value = fields.Str(data_key="value")
    r""" Value associated with the key. """

    @property
    def resource(self):
        return MaxdataOnSanApplicationComponentsMetadata

    gettable_fields = [
        "key",
        "value",
    ]
    """key,value,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "key",
        "value",
    ]
    """key,value,"""


class MaxdataOnSanApplicationComponentsMetadata(Resource):

    _schema = MaxdataOnSanApplicationComponentsMetadataSchema
