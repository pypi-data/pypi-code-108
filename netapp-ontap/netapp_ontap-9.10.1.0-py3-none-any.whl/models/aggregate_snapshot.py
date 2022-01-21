r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AggregateSnapshot", "AggregateSnapshotSchema"]
__pdoc__ = {
    "AggregateSnapshotSchema.resource": False,
    "AggregateSnapshot": False,
}


class AggregateSnapshotSchema(ResourceSchema):
    """The fields of the AggregateSnapshot object"""

    files_total = Size(data_key="files_total")
    r""" Total files allowed in Snapshot copies

Example: 10 """

    files_used = Size(data_key="files_used")
    r""" Total files created in Snapshot copies

Example: 3 """

    max_files_available = Size(data_key="max_files_available")
    r""" Maximum files available for Snapshot copies

Example: 5 """

    max_files_used = Size(data_key="max_files_used")
    r""" Files in use by Snapshot copies

Example: 50 """

    @property
    def resource(self):
        return AggregateSnapshot

    gettable_fields = [
        "files_total",
        "files_used",
        "max_files_available",
        "max_files_used",
    ]
    """files_total,files_used,max_files_available,max_files_used,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AggregateSnapshot(Resource):

    _schema = AggregateSnapshotSchema
