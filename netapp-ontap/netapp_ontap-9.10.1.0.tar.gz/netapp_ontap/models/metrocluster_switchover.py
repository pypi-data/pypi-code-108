r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MetroclusterSwitchover", "MetroclusterSwitchoverSchema"]
__pdoc__ = {
    "MetroclusterSwitchoverSchema.resource": False,
    "MetroclusterSwitchover": False,
}


class MetroclusterSwitchoverSchema(ResourceSchema):
    """The fields of the MetroclusterSwitchover object"""

    force_on_disaster = fields.Boolean(data_key="force_on_disaster")
    r""" The force_on_disaster field of the metrocluster_switchover. """

    mount_volumes_readonly = fields.Boolean(data_key="mount_volumes_readonly")
    r""" The mount_volumes_readonly field of the metrocluster_switchover. """

    simulate = fields.Boolean(data_key="simulate")
    r""" The simulate field of the metrocluster_switchover. """

    @property
    def resource(self):
        return MetroclusterSwitchover

    gettable_fields = [
        "force_on_disaster",
        "mount_volumes_readonly",
        "simulate",
    ]
    """force_on_disaster,mount_volumes_readonly,simulate,"""

    patchable_fields = [
        "force_on_disaster",
        "mount_volumes_readonly",
        "simulate",
    ]
    """force_on_disaster,mount_volumes_readonly,simulate,"""

    postable_fields = [
        "force_on_disaster",
        "mount_volumes_readonly",
        "simulate",
    ]
    """force_on_disaster,mount_volumes_readonly,simulate,"""


class MetroclusterSwitchover(Resource):

    _schema = MetroclusterSwitchoverSchema
