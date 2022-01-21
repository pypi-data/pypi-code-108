r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationStatisticsSpace1", "ApplicationStatisticsSpace1Schema"]
__pdoc__ = {
    "ApplicationStatisticsSpace1Schema.resource": False,
    "ApplicationStatisticsSpace1": False,
}


class ApplicationStatisticsSpace1Schema(ResourceSchema):
    """The fields of the ApplicationStatisticsSpace1 object"""

    available = Size(data_key="available")
    r""" The available amount of space left in the application. Note that this field has limited meaning for SAN applications. Space may be considered used from ONTAP's perspective while the host filesystem still considers it available. """

    logical_used = Size(data_key="logical_used")
    r""" The amount of space that would currently be used if no space saving features were enabled. For example, if compression were the only space saving feature enabled, this field would represent the uncompressed amount of space used. """

    provisioned = Size(data_key="provisioned")
    r""" The originally requested amount of space that was provisioned for the application. """

    reserved_unused = Size(data_key="reserved_unused")
    r""" The amount of space reserved for system features such as Snapshot copies that has not yet been used. """

    savings = Size(data_key="savings")
    r""" The amount of space saved by all enabled space saving features. """

    used = Size(data_key="used")
    r""" The amount of space that is currently being used by the application. Note that this includes any space reserved by the system for features such as Snapshot copies. """

    used_excluding_reserves = Size(data_key="used_excluding_reserves")
    r""" The amount of space that is currently being used, excluding any space that is reserved by the system for features such as Snapshot copies. """

    used_percent = Size(data_key="used_percent")
    r""" The percentage of the originally provisioned space that is currently being used by the application. """

    @property
    def resource(self):
        return ApplicationStatisticsSpace1

    gettable_fields = [
        "available",
        "logical_used",
        "provisioned",
        "reserved_unused",
        "savings",
        "used",
        "used_excluding_reserves",
        "used_percent",
    ]
    """available,logical_used,provisioned,reserved_unused,savings,used,used_excluding_reserves,used_percent,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationStatisticsSpace1(Resource):

    _schema = ApplicationStatisticsSpace1Schema
