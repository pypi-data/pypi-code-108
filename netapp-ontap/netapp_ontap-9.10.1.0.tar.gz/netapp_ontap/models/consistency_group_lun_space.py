r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupLunSpace", "ConsistencyGroupLunSpaceSchema"]
__pdoc__ = {
    "ConsistencyGroupLunSpaceSchema.resource": False,
    "ConsistencyGroupLunSpace": False,
}


class ConsistencyGroupLunSpaceSchema(ResourceSchema):
    """The fields of the ConsistencyGroupLunSpace object"""

    size = Size(data_key="size")
    r""" The total provisioned size of the LUN. The LUN size can be increased but not reduced using the REST interface.
The maximum and minimum sizes listed here are the absolute maximum and absolute minimum sizes, in bytes. The actual minimum and maxiumum sizes vary depending on the ONTAP version, ONTAP platform, and the available space in the containing volume and aggregate.
For more information, see _Size properties_ in the _docs_ section of the ONTAP REST API documentation.


Example: 1073741824 """

    used = Size(data_key="used")
    r""" The amount of space consumed by the main data stream of the LUN.<br/>
This value is the total space consumed in the volume by the LUN, including filesystem overhead, but excluding prefix and suffix streams. Due to internal filesystem overhead and the many ways SAN filesystems and applications utilize blocks within a LUN, this value does not necessarily reflect actual consumption/availability from the perspective of the filesystem or application. Without specific knowledge of how the LUN blocks are utilized outside of ONTAP, this property should not be used as an indicator for an out-of-space condition.<br/>
For more information, see _Size properties_ in the _docs_ section of the ONTAP REST API documentation. """

    @property
    def resource(self):
        return ConsistencyGroupLunSpace

    gettable_fields = [
        "size",
        "used",
    ]
    """size,used,"""

    patchable_fields = [
        "size",
    ]
    """size,"""

    postable_fields = [
        "size",
    ]
    """size,"""


class ConsistencyGroupLunSpace(Resource):

    _schema = ConsistencyGroupLunSpaceSchema
