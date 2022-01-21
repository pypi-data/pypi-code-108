r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeNvram", "NodeNvramSchema"]
__pdoc__ = {
    "NodeNvramSchema.resource": False,
    "NodeNvram": False,
}


class NodeNvramSchema(ResourceSchema):
    """The fields of the NodeNvram object"""

    battery_state = fields.Str(data_key="battery_state")
    r""" Specifies status of the NVRAM battery. Possible values:

* <i>battery_ok</i>
* <i>battery_partially_discharged</i>
* <i>battery_fully_discharged</i>
* <i>battery_not_present</i>
* <i>battery_near_end_of_life</i>
* <i>battery_at_end_of_life</i>
* <i>battery_unknown</i>
* <i>battery_over_charged</i>
* <i>battery_fully_charged</i>


Valid choices:

* battery_ok
* battery_partially_discharged
* battery_fully_discharged
* battery_not_present
* battery_near_end_of_life
* battery_at_end_of_life
* battery_unknown
* battery_over_charged
* battery_fully_charged """

    id = Size(data_key="id")
    r""" Vendor specific NVRAM ID of the node. """

    @property
    def resource(self):
        return NodeNvram

    gettable_fields = [
        "battery_state",
        "id",
    ]
    """battery_state,id,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NodeNvram(Resource):

    _schema = NodeNvramSchema
