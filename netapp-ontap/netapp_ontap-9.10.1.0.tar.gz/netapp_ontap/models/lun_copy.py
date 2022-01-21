r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunCopy", "LunCopySchema"]
__pdoc__ = {
    "LunCopySchema.resource": False,
    "LunCopy": False,
}


class LunCopySchema(ResourceSchema):
    """The fields of the LunCopy object"""

    destinations = fields.List(fields.Nested("netapp_ontap.models.lun_copy_destinations.LunCopyDestinationsSchema", unknown=EXCLUDE), data_key="destinations")
    r""" An array of destination LUNs of LUN copy operations in which the containing LUN is the source of the copy. """

    source = fields.Nested("netapp_ontap.models.lun_copy_source.LunCopySourceSchema", unknown=EXCLUDE, data_key="source")
    r""" The source field of the lun_copy. """

    @property
    def resource(self):
        return LunCopy

    gettable_fields = [
        "destinations",
        "source",
    ]
    """destinations,source,"""

    patchable_fields = [
        "source",
    ]
    """source,"""

    postable_fields = [
        "source",
    ]
    """source,"""


class LunCopy(Resource):

    _schema = LunCopySchema
