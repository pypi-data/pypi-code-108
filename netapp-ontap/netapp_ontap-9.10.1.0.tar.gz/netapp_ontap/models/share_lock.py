r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShareLock", "ShareLockSchema"]
__pdoc__ = {
    "ShareLockSchema.resource": False,
    "ShareLock": False,
}


class ShareLockSchema(ResourceSchema):
    """The fields of the ShareLock object"""

    mode = fields.Str(data_key="mode")
    r""" Types of share lock modes.

Valid choices:

* delete_on_close
* read_deny_read
* read_deny_write
* read_deny_all
* read_deny_delete
* read_deny_none
* read_deny_read_write
* read_deny_read_delete
* read_deny_write_delete
* write_deny_read
* write_deny_write
* write_deny_all
* write_deny_delete
* write_deny_none
* write_deny_read_write
* write_deny_read_delete
* write_deny_write_delete
* delete_deny_read
* delete_deny_write
* delete_deny_all
* delete_deny_delete
* delete_deny_none
* delete_deny_read_write
* delete_deny_read_delete
* delete_deny_write_delete
* read_write_deny_read
* read_write_deny_write
* read_write_deny_all
* read_write_deny_delete
* read_write_deny_none
* read_write_deny_read_write
* read_write_deny_read_delete
* read_write_deny_write_delete
* read_delete_deny_read
* read_delete_deny_write
* read_delete_deny_all
* read_delete_deny_delete
* read_delete_deny_none
* read_delete_deny_read_write
* read_delete_deny_read_delete
* read_delete_deny_write_delete
* write_delete_deny_read
* write_delete_deny_write
* write_delete_deny_all
* write_delete_deny_delete
* write_delete_deny_none
* write_delete_deny_read_write
* write_delete_deny_read_delete
* write_delete_deny_write_delete
* all_deny_read
* all_deny_write
* all_deny_all
* all_deny_delete
* all_deny_none
* all_deny_read_write
* all_deny_read_delete
* all_deny_write_delete
* none_deny_read
* none_deny_write
* none_deny_all
* none_deny_delete
* none_deny_none
* none_deny_read_write
* none_deny_read_delete
* none_deny_write_delete """

    soft = fields.Boolean(data_key="soft")
    r""" Indicates whether it is a soft share lock. """

    @property
    def resource(self):
        return ShareLock

    gettable_fields = [
        "mode",
        "soft",
    ]
    """mode,soft,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ShareLock(Resource):

    _schema = ShareLockSchema
