r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeEncryption", "VolumeEncryptionSchema"]
__pdoc__ = {
    "VolumeEncryptionSchema.resource": False,
    "VolumeEncryption": False,
}


class VolumeEncryptionSchema(ResourceSchema):
    """The fields of the VolumeEncryption object"""

    enabled = fields.Boolean(data_key="enabled")
    r""" Creates an encrypted or an unencrypted volume. For POST, when set to 'true', a new key is generated and used to encrypt the given volume. In that case, the underlying SVM must be configured with the key manager. When set to 'false', the volume created will be unencrypted. For PATCH, when set to 'true', it encrypts an unencrypted volume. Specifying the parameter as 'false' in a PATCH operation for an encrypted volume is only supported when moving the volume to another aggregate. """

    key_id = fields.Str(data_key="key_id")
    r""" The key ID used for creating encrypted volume. A new key-id is generated for creating an encrypted volume. This key-id is associated with the generated key. """

    key_manager_attribute = fields.Str(data_key="key_manager_attribute")
    r""" Specifies an additional key manager attribute that is an identifier-value pair, separated by '='. For example, CRN=unique-value. This parameter is required when using the POST method and an IBM Key Lore key manager is configured on the SVM.

Example: CRN=v1:bluemix:public:containers-kubernetes:us-south:a/asdfghjkl1234:asdfghjkl1234:worker:kubernetes-asdfghjkl-worker1 """

    rekey = fields.Boolean(data_key="rekey")
    r""" If set to 'true', re-encrypts the volume with a new key. Valid in PATCH. """

    state = fields.Str(data_key="state")
    r""" Volume encryption state.<br>encrypted &dash; The volume is completely encrypted.<br>encrypting &dash; Encryption operation is in progress.<br>partial &dash; Some constituents are encrypted and some are not. Applicable only for FlexGroup volume.<br>rekeying. Encryption of volume with a new key is in progress.<br>unencrypted &dash; The volume is a plain-text one.

Valid choices:

* encrypted
* encrypting
* partial
* rekeying
* unencrypted """

    status = fields.Nested("netapp_ontap.models.volume_encryption_status.VolumeEncryptionStatusSchema", unknown=EXCLUDE, data_key="status")
    r""" The status field of the volume_encryption. """

    type = fields.Str(data_key="type")
    r""" Volume encryption type.<br>none &dash; The volume is a plain-text one.<br>volume &dash; The volume is encrypted with NVE (NetApp Volume Encryption).<br>aggregate &dash; The volume is encrypted with NAE (NetApp Aggregate Encryption).

Valid choices:

* none
* volume
* aggregate """

    @property
    def resource(self):
        return VolumeEncryption

    gettable_fields = [
        "enabled",
        "key_id",
        "rekey",
        "state",
        "status",
        "type",
    ]
    """enabled,key_id,rekey,state,status,type,"""

    patchable_fields = [
        "enabled",
        "rekey",
        "status",
    ]
    """enabled,rekey,status,"""

    postable_fields = [
        "enabled",
        "key_manager_attribute",
        "status",
    ]
    """enabled,key_manager_attribute,status,"""


class VolumeEncryption(Resource):

    _schema = VolumeEncryptionSchema
