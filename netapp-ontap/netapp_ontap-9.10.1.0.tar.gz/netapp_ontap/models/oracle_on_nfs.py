r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["OracleOnNfs", "OracleOnNfsSchema"]
__pdoc__ = {
    "OracleOnNfsSchema.resource": False,
    "OracleOnNfs": False,
}


class OracleOnNfsSchema(ResourceSchema):
    """The fields of the OracleOnNfs object"""

    archive_log = fields.Nested("netapp_ontap.models.oracle_on_nfs_archive_log.OracleOnNfsArchiveLogSchema", unknown=EXCLUDE, data_key="archive_log")
    r""" The archive_log field of the oracle_on_nfs. """

    db = fields.Nested("netapp_ontap.models.oracle_on_nfs_db.OracleOnNfsDbSchema", unknown=EXCLUDE, data_key="db")
    r""" The db field of the oracle_on_nfs. """

    nfs_access = fields.List(fields.Nested("netapp_ontap.models.app_nfs_access.AppNfsAccessSchema", unknown=EXCLUDE), data_key="nfs_access")
    r""" The list of NFS access controls. You must provide either 'host' or 'access' to enable NFS access. """

    ora_home = fields.Nested("netapp_ontap.models.oracle_on_nfs_ora_home.OracleOnNfsOraHomeSchema", unknown=EXCLUDE, data_key="ora_home")
    r""" The ora_home field of the oracle_on_nfs. """

    protection_type = fields.Nested("netapp_ontap.models.mongo_db_on_san_protection_type.MongoDbOnSanProtectionTypeSchema", unknown=EXCLUDE, data_key="protection_type")
    r""" The protection_type field of the oracle_on_nfs. """

    redo_log = fields.Nested("netapp_ontap.models.oracle_on_nfs_redo_log.OracleOnNfsRedoLogSchema", unknown=EXCLUDE, data_key="redo_log")
    r""" The redo_log field of the oracle_on_nfs. """

    @property
    def resource(self):
        return OracleOnNfs

    gettable_fields = [
        "archive_log",
        "db",
        "nfs_access",
        "ora_home",
        "protection_type",
        "redo_log",
    ]
    """archive_log,db,nfs_access,ora_home,protection_type,redo_log,"""

    patchable_fields = [
        "archive_log",
        "db",
        "ora_home",
        "protection_type",
        "redo_log",
    ]
    """archive_log,db,ora_home,protection_type,redo_log,"""

    postable_fields = [
        "archive_log",
        "db",
        "nfs_access",
        "ora_home",
        "protection_type",
        "redo_log",
    ]
    """archive_log,db,nfs_access,ora_home,protection_type,redo_log,"""


class OracleOnNfs(Resource):

    _schema = OracleOnNfsSchema
