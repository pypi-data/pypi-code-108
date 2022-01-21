r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MongoDbOnSanNewIgroups", "MongoDbOnSanNewIgroupsSchema"]
__pdoc__ = {
    "MongoDbOnSanNewIgroupsSchema.resource": False,
    "MongoDbOnSanNewIgroups": False,
}


class MongoDbOnSanNewIgroupsSchema(ResourceSchema):
    """The fields of the MongoDbOnSanNewIgroups object"""

    comment = fields.Str(data_key="comment")
    r""" A comment available for use by the administrator. """

    igroups = fields.List(fields.Nested("netapp_ontap.models.maxdata_on_san_new_igroups_igroups.MaxdataOnSanNewIgroupsIgroupsSchema", unknown=EXCLUDE), data_key="igroups")
    r""" The igroups field of the mongo_db_on_san_new_igroups. """

    initiator_objects = fields.List(fields.Nested("netapp_ontap.models.maxdata_on_san_new_igroups_initiator_objects.MaxdataOnSanNewIgroupsInitiatorObjectsSchema", unknown=EXCLUDE), data_key="initiator_objects")
    r""" The initiator_objects field of the mongo_db_on_san_new_igroups. """

    initiators = fields.List(fields.Str, data_key="initiators")
    r""" The initiators field of the mongo_db_on_san_new_igroups. """

    name = fields.Str(data_key="name")
    r""" The name of the new initiator group. """

    os_type = fields.Str(data_key="os_type")
    r""" The name of the host OS accessing the application. The default value is the host OS that is running the application.

Valid choices:

* hyper_v
* linux
* solaris
* vmware
* windows
* xen """

    protocol = fields.Str(data_key="protocol")
    r""" The protocol of the new initiator group.

Valid choices:

* fcp
* iscsi
* mixed """

    @property
    def resource(self):
        return MongoDbOnSanNewIgroups

    gettable_fields = [
        "initiators",
    ]
    """initiators,"""

    patchable_fields = [
        "comment",
        "igroups",
        "initiator_objects",
        "initiators",
        "name",
        "os_type",
        "protocol",
    ]
    """comment,igroups,initiator_objects,initiators,name,os_type,protocol,"""

    postable_fields = [
        "comment",
        "igroups",
        "initiator_objects",
        "initiators",
        "name",
        "os_type",
        "protocol",
    ]
    """comment,igroups,initiator_objects,initiators,name,os_type,protocol,"""


class MongoDbOnSanNewIgroups(Resource):

    _schema = MongoDbOnSanNewIgroupsSchema
