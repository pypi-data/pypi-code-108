r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SecurityAssociationIke", "SecurityAssociationIkeSchema"]
__pdoc__ = {
    "SecurityAssociationIkeSchema.resource": False,
    "SecurityAssociationIke": False,
}


class SecurityAssociationIkeSchema(ResourceSchema):
    """The fields of the SecurityAssociationIke object"""

    authentication = fields.Str(data_key="authentication")
    r""" Authentication method for internet key exchange protocol.

Valid choices:

* none
* psk
* cert """

    initiator_security_parameter_index = fields.Str(data_key="initiator_security_parameter_index")
    r""" Initiator's security parameter index for the IKE security association. """

    is_initiator = fields.Boolean(data_key="is_initiator")
    r""" Indicates whether or not IKE has been initiated by this node. """

    responder_security_parameter_index = fields.Str(data_key="responder_security_parameter_index")
    r""" Responder's security parameter index for the IKE security association. """

    state = fields.Str(data_key="state")
    r""" State of the IKE connection.

Valid choices:

* none
* connecting
* established
* dead_peer_probe """

    version = Size(data_key="version")
    r""" Internet key exchange protocol version. """

    @property
    def resource(self):
        return SecurityAssociationIke

    gettable_fields = [
        "authentication",
        "initiator_security_parameter_index",
        "is_initiator",
        "responder_security_parameter_index",
        "state",
        "version",
    ]
    """authentication,initiator_security_parameter_index,is_initiator,responder_security_parameter_index,state,version,"""

    patchable_fields = [
        "authentication",
        "initiator_security_parameter_index",
        "is_initiator",
        "responder_security_parameter_index",
        "state",
        "version",
    ]
    """authentication,initiator_security_parameter_index,is_initiator,responder_security_parameter_index,state,version,"""

    postable_fields = [
        "authentication",
        "initiator_security_parameter_index",
        "is_initiator",
        "responder_security_parameter_index",
        "state",
        "version",
    ]
    """authentication,initiator_security_parameter_index,is_initiator,responder_security_parameter_index,state,version,"""


class SecurityAssociationIke(Resource):

    _schema = SecurityAssociationIkeSchema
