r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ConsistencyGroupNamespaceStatus", "ConsistencyGroupNamespaceStatusSchema"]
__pdoc__ = {
    "ConsistencyGroupNamespaceStatusSchema.resource": False,
    "ConsistencyGroupNamespaceStatus": False,
}


class ConsistencyGroupNamespaceStatusSchema(ResourceSchema):
    """The fields of the ConsistencyGroupNamespaceStatus object"""

    container_state = fields.Str(data_key="container_state")
    r""" The state of the volume and aggregate that contain the NVMe namespace. Namespaces are only available when their containers are available.


Valid choices:

* online
* aggregate_offline
* volume_offline """

    mapped = fields.Boolean(data_key="mapped")
    r""" Reports if the NVMe namespace is mapped to an NVMe subsystem.<br/>
There is an added cost to retrieving this property's value. It is not populated for either a collection GET or an instance GET unless it is explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more. """

    read_only = fields.Boolean(data_key="read_only")
    r""" Reports if the NVMe namespace allows only read access. """

    state = fields.Str(data_key="state")
    r""" The state of the NVMe namespace. Normal states for a namespace are _online_ and _offline_. Other states indicate errors.


Valid choices:

* nvfail
* offline
* online
* space_error """

    @property
    def resource(self):
        return ConsistencyGroupNamespaceStatus

    gettable_fields = [
        "container_state",
        "mapped",
        "read_only",
        "state",
    ]
    """container_state,mapped,read_only,state,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ConsistencyGroupNamespaceStatus(Resource):

    _schema = ConsistencyGroupNamespaceStatusSchema
