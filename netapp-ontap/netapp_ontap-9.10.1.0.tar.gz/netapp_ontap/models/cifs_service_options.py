r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["CifsServiceOptions", "CifsServiceOptionsSchema"]
__pdoc__ = {
    "CifsServiceOptionsSchema.resource": False,
    "CifsServiceOptions": False,
}


class CifsServiceOptionsSchema(ResourceSchema):
    """The fields of the CifsServiceOptions object"""

    admin_to_root_mapping = fields.Boolean(data_key="admin_to_root_mapping")
    r""" Specifies whether or not Administrator can be mapped to the UNIX user "root". """

    advanced_sparse_file = fields.Boolean(data_key="advanced_sparse_file")
    r""" Specifies whether or not the CIFS server supports the advanced sparse file capabilities. This allows
CIFS clients to query the allocated ranges of a file and to write zeroes or free data blocks for ranges
of a file. """

    copy_offload = fields.Boolean(data_key="copy_offload")
    r""" Specifies whether or not to enable the Copy Offload feature. This feature enables direct
data transfers within or between compatible storage devices without transferring the data
through the host computer.<br/>
Note that this will also enable/disable the direct copy feature accordingly. """

    fake_open = fields.Boolean(data_key="fake_open")
    r""" Specifies whether or not fake open support is enabled. This parameter allows you to optimize the
open and close requests coming from SMB 2 clients. """

    fsctl_trim = fields.Boolean(data_key="fsctl_trim")
    r""" Specifies whether or not the trim requests (FSCTL_FILE_LEVEL_TRIM) are supported on the CIFS server. """

    junction_reparse = fields.Boolean(data_key="junction_reparse")
    r""" Specifies whether or not the reparse point support is enabled. When enabled the CIFS server
exposes junction points to Windows clients as reparse points. This parameter is only active
if the client has negotiated use of the SMB 2 or SMB 3 protocol. This parameter is not supported
for SVMs with Infinite Volume. """

    large_mtu = fields.Boolean(data_key="large_mtu")
    r""" Specifies whether or not SMB clients can send reads up to 1 MB in size. """

    multichannel = fields.Boolean(data_key="multichannel")
    r""" Specifies whether or not the CIFS server supports Multichannel. """

    null_user_windows_name = fields.Str(data_key="null_user_windows_name")
    r""" Specifies a Windows User or Group name that should be mapped in case of a NULL user
value. """

    path_component_cache = fields.Boolean(data_key="path_component_cache")
    r""" Specifies whether or not the path component cache is enabled on the CIFS server. """

    referral = fields.Boolean(data_key="referral")
    r""" Specifies whether or not to refer clients to more optimal LIFs. When enabled, it automatically
refers clients to a data LIF local to the node which hosts the root of the requested share. """

    smb_credits = Size(data_key="smb_credits")
    r""" Specifies the maximum number of outstanding requests on a CIFS connection.

Example: 128 """

    widelink_reparse_versions = fields.List(fields.Str, data_key="widelink_reparse_versions")
    r""" Specifies the CIFS protocol versions for which the widelink is reported as reparse point. """

    @property
    def resource(self):
        return CifsServiceOptions

    gettable_fields = [
        "admin_to_root_mapping",
        "advanced_sparse_file",
        "copy_offload",
        "fake_open",
        "fsctl_trim",
        "junction_reparse",
        "large_mtu",
        "multichannel",
        "null_user_windows_name",
        "path_component_cache",
        "referral",
        "smb_credits",
        "widelink_reparse_versions",
    ]
    """admin_to_root_mapping,advanced_sparse_file,copy_offload,fake_open,fsctl_trim,junction_reparse,large_mtu,multichannel,null_user_windows_name,path_component_cache,referral,smb_credits,widelink_reparse_versions,"""

    patchable_fields = [
        "admin_to_root_mapping",
        "advanced_sparse_file",
        "copy_offload",
        "fake_open",
        "fsctl_trim",
        "junction_reparse",
        "large_mtu",
        "multichannel",
        "null_user_windows_name",
        "path_component_cache",
        "referral",
        "smb_credits",
        "widelink_reparse_versions",
    ]
    """admin_to_root_mapping,advanced_sparse_file,copy_offload,fake_open,fsctl_trim,junction_reparse,large_mtu,multichannel,null_user_windows_name,path_component_cache,referral,smb_credits,widelink_reparse_versions,"""

    postable_fields = [
        "admin_to_root_mapping",
        "advanced_sparse_file",
        "copy_offload",
        "fake_open",
        "fsctl_trim",
        "junction_reparse",
        "large_mtu",
        "multichannel",
        "null_user_windows_name",
        "path_component_cache",
        "referral",
        "smb_credits",
        "widelink_reparse_versions",
    ]
    """admin_to_root_mapping,advanced_sparse_file,copy_offload,fake_open,fsctl_trim,junction_reparse,large_mtu,multichannel,null_user_windows_name,path_component_cache,referral,smb_credits,widelink_reparse_versions,"""


class CifsServiceOptions(Resource):

    _schema = CifsServiceOptionsSchema
