r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AdvancedRights", "AdvancedRightsSchema"]
__pdoc__ = {
    "AdvancedRightsSchema.resource": False,
    "AdvancedRights": False,
}


class AdvancedRightsSchema(ResourceSchema):
    """The fields of the AdvancedRights object"""

    append_data = fields.Boolean(data_key="append_data")
    r""" Append DAta """

    delete = fields.Boolean(data_key="delete")
    r""" Delete """

    delete_child = fields.Boolean(data_key="delete_child")
    r""" Delete Child """

    execute_file = fields.Boolean(data_key="execute_file")
    r""" Execute File """

    full_control = fields.Boolean(data_key="full_control")
    r""" Full Control """

    read_attr = fields.Boolean(data_key="read_attr")
    r""" Read Attributes """

    read_data = fields.Boolean(data_key="read_data")
    r""" Read Data """

    read_ea = fields.Boolean(data_key="read_ea")
    r""" Read Extended Attributes """

    read_perm = fields.Boolean(data_key="read_perm")
    r""" Read Permissions """

    synchronize = fields.Boolean(data_key="synchronize")
    r""" Synchronize """

    write_attr = fields.Boolean(data_key="write_attr")
    r""" Write Attributes """

    write_data = fields.Boolean(data_key="write_data")
    r""" Write Data """

    write_ea = fields.Boolean(data_key="write_ea")
    r""" Write Extended Attributes """

    write_owner = fields.Boolean(data_key="write_owner")
    r""" Write Owner """

    write_perm = fields.Boolean(data_key="write_perm")
    r""" Write Permission """

    @property
    def resource(self):
        return AdvancedRights

    gettable_fields = [
        "append_data",
        "delete",
        "delete_child",
        "execute_file",
        "full_control",
        "read_attr",
        "read_data",
        "read_ea",
        "read_perm",
        "synchronize",
        "write_attr",
        "write_data",
        "write_ea",
        "write_owner",
        "write_perm",
    ]
    """append_data,delete,delete_child,execute_file,full_control,read_attr,read_data,read_ea,read_perm,synchronize,write_attr,write_data,write_ea,write_owner,write_perm,"""

    patchable_fields = [
        "append_data",
        "delete",
        "delete_child",
        "execute_file",
        "full_control",
        "read_attr",
        "read_data",
        "read_ea",
        "read_perm",
        "write_attr",
        "write_data",
        "write_ea",
        "write_owner",
        "write_perm",
    ]
    """append_data,delete,delete_child,execute_file,full_control,read_attr,read_data,read_ea,read_perm,write_attr,write_data,write_ea,write_owner,write_perm,"""

    postable_fields = [
        "append_data",
        "delete",
        "delete_child",
        "execute_file",
        "full_control",
        "read_attr",
        "read_data",
        "read_ea",
        "read_perm",
        "write_attr",
        "write_data",
        "write_ea",
        "write_owner",
        "write_perm",
    ]
    """append_data,delete,delete_child,execute_file,full_control,read_attr,read_data,read_ea,read_perm,write_attr,write_data,write_ea,write_owner,write_perm,"""


class AdvancedRights(Resource):

    _schema = AdvancedRightsSchema
