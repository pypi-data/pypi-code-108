from pydantic import (
    BaseModel, validator, root_validator, AnyUrl
)

from typing import Optional, Dict, List, Union


# def coord0_less_than_coord1(coord0, length):
#     if coord0 >= coord1:
#         return False
#     return True


class BoundingBox(BaseModel):
    x: float
    y: float
    w: float
    h: float
    value: str

    @root_validator
    def between_zero_and_one(cls, values):
        for key in values:
            if key != "name":
                if values[key] > 1 or values[key] < 0:
                    raise ValueError(
                        f"{key} must be greater or equal to zero and less than or equal to one."
                    )
        return values

    # @root_validator
    # def x0_less_than_x1(cls, values):
    #     if not coord0_less_than_coord1(values["x0"], values["x1"]):
    #         raise ValueError("x1 must be greater than x0")
    #     return values

    # @root_validator
    # def y0_less_than_y1(cls, values):
    #     if not coord0_less_than_coord1(values["y0"], values["y1"]):
    #         raise ValueError("y1 must be greater than y0")
    #     return values


class Polygon(BaseModel):
    pass


class Classification(BaseModel):
    name: str
    type: str
    value: str


class Objects(BaseModel):
    name: str
    type: str
    objects: Union[List[BoundingBox], List[Polygon]]


# {
#     "classifications": [],
#     "bounding_boxes": [],
#     "polygons": []
# }

# "models": [
#     "name": "scooter_parking_quality",
#     "data_labels": "bay_no_bay",
#     "exclude_classes": ["insufficient_information"]
# ],
# "data": [
#     {
#         "id": "test",
#         "url": "https://test.com/1.jpg",
#         "labels": [
#             {
#                 "name": "scooter_parking",
#                 "type": "classification",
#                 "value": "in_parking_bay"
#             },
#             {
#                 "name": "scooter_detection",
#                 "type": "bounding_box",
#                 "objects": []
#             }
#         ]
#     }
# ]


class Image(BaseModel):
    id: str
    uri: AnyUrl
    labels: Optional[List[Union[Classification, Objects]]]

    @ validator('uri')
    def check_valid_uri(cls, uri):
        legal_schemes = ['gs', 'http', 'https']
        if uri.scheme not in legal_schemes:
            raise ValueError(
                f'{uri} scheme must be one of {" ".join(legal_schemes)}'
            )

        return uri
