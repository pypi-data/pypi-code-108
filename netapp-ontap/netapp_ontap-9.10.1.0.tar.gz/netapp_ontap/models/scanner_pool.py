r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ScannerPool", "ScannerPoolSchema"]
__pdoc__ = {
    "ScannerPoolSchema.resource": False,
    "ScannerPool": False,
}


class ScannerPoolSchema(ResourceSchema):
    """The fields of the ScannerPool object"""

    cluster = fields.Nested("netapp_ontap.resources.cluster.ClusterSchema", unknown=EXCLUDE, data_key="cluster")
    r""" The cluster field of the scanner_pool. """

    name = fields.Str(data_key="name")
    r""" Specifies the name of the scanner pool. Scanner pool name can be up to 256 characters long and is a string that can only contain any combination of ASCII-range alphanumeric characters a-z, A-Z, 0-9), "_", "-" and ".".

Example: scanner-1 """

    privileged_users = fields.List(fields.Str, data_key="privileged_users")
    r""" Specifies a list of privileged users. A valid form of privileged user-name is "domain-name\user-name". Privileged user-names are stored and treated as case-insensitive strings. Virus scanners must use one of the registered privileged users for connecting to clustered Data ONTAP for exchanging virus-scanning protocol messages and to access file for scanning, remedying and quarantining operations.

Example: ["cifs\\u1","cifs\\u2"] """

    role = fields.Str(data_key="role")
    r""" Specifies the role of the scanner pool. The possible values are:

  * primary   - Always active.
  * secondary - Active only when none of the primary external virus-scanning servers are connected.
  * idle      - Always inactive.


Valid choices:

* primary
* secondary
* idle """

    servers = fields.List(fields.Str, data_key="servers")
    r""" Specifies a list of IP addresses or FQDN for each Vscan server host names which are allowed to connect to clustered ONTAP.

Example: ["1.1.1.1","10.72.204.27","vmwin204-27.fsct.nb"] """

    @property
    def resource(self):
        return ScannerPool

    gettable_fields = [
        "cluster.links",
        "cluster.name",
        "cluster.uuid",
        "name",
        "privileged_users",
        "role",
        "servers",
    ]
    """cluster.links,cluster.name,cluster.uuid,name,privileged_users,role,servers,"""

    patchable_fields = [
        "cluster.name",
        "cluster.uuid",
        "privileged_users",
        "role",
        "servers",
    ]
    """cluster.name,cluster.uuid,privileged_users,role,servers,"""

    postable_fields = [
        "cluster.name",
        "cluster.uuid",
        "name",
        "privileged_users",
        "role",
        "servers",
    ]
    """cluster.name,cluster.uuid,name,privileged_users,role,servers,"""


class ScannerPool(Resource):

    _schema = ScannerPoolSchema
