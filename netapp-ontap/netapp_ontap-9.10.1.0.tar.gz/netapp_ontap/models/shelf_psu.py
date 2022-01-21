r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ShelfPsu", "ShelfPsuSchema"]
__pdoc__ = {
    "ShelfPsuSchema.resource": False,
    "ShelfPsu": False,
}


class ShelfPsuSchema(ResourceSchema):
    """The fields of the ShelfPsu object"""

    crest_factor = Size(data_key="crest_factor")
    r""" The ratio of the peak voltage to the root-mean-square voltage

Example: 92 """

    model = fields.Str(data_key="model")
    r""" The model field of the shelf_psu.

Example: 00 """

    power_drawn = Size(data_key="power_drawn")
    r""" Power drawn, in watts

Example: 210 """

    power_rating = Size(data_key="power_rating")
    r""" Power rating, in watts

Example: 1600 """

    @property
    def resource(self):
        return ShelfPsu

    gettable_fields = [
        "crest_factor",
        "model",
        "power_drawn",
        "power_rating",
    ]
    """crest_factor,model,power_drawn,power_rating,"""

    patchable_fields = [
        "crest_factor",
        "model",
        "power_drawn",
        "power_rating",
    ]
    """crest_factor,model,power_drawn,power_rating,"""

    postable_fields = [
        "crest_factor",
        "model",
        "power_drawn",
        "power_rating",
    ]
    """crest_factor,model,power_drawn,power_rating,"""


class ShelfPsu(Resource):

    _schema = ShelfPsuSchema
