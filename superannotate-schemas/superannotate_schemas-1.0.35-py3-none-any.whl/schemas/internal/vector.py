from typing import List
from typing import Optional
from typing import Union

from superannotate_schemas.schemas.base import BaseVectorInstance
from superannotate_schemas.schemas.base import BboxPoints
from superannotate_schemas.schemas.base import BaseAttribute
from superannotate_schemas.schemas.base import Comment
from superannotate_schemas.schemas.base import BaseImageMetadata as Metadata
from superannotate_schemas.schemas.base import Tag
from superannotate_schemas.schemas.base import AxisPoint
from superannotate_schemas.schemas.base import VectorAnnotationTypeEnum
from superannotate_schemas.schemas.base import StrictNumber
from superannotate_schemas.schemas.base import INVALID_DICT_MESSAGE
from superannotate_schemas.schemas.base import BaseModel

from pydantic import StrictInt
from pydantic import StrictFloat
from pydantic import conlist
from pydantic import Field
from pydantic import validate_model
from pydantic import ValidationError
from pydantic import validator
from pydantic.error_wrappers import ErrorWrapper


class Attribute(BaseAttribute):
    id: StrictInt
    group_id: StrictInt = Field(alias="groupId")


class VectorInstance(BaseVectorInstance):
    attributes: Optional[List[Attribute]] = Field(list())


class Point(VectorInstance, AxisPoint):
    pass


class PolyLine(VectorInstance):
    points: List[Union[StrictFloat, StrictInt]]


class Polygon(VectorInstance):
    points: conlist(Union[StrictFloat, StrictInt], min_items=3)


class Bbox(VectorInstance):
    points: BboxPoints


class RotatedBoxPoints(BaseModel):
    x1: StrictNumber
    y1: StrictNumber
    x2: StrictNumber
    y2: StrictNumber
    x3: StrictNumber
    y3: StrictNumber
    x4: StrictNumber
    y4: StrictNumber


class RotatedBox(VectorInstance):
    points: RotatedBoxPoints


class Ellipse(VectorInstance):
    cx: StrictNumber
    cy: StrictNumber
    rx: StrictNumber
    ry: StrictNumber
    angle: StrictNumber


class TemplatePoint(BaseModel):
    id: StrictInt
    x: StrictNumber
    y: StrictNumber


class TemplateConnection(BaseModel):
    id: StrictInt
    from_connection: StrictInt = Field(alias="from")
    to_connection: StrictInt = Field(alias="to")


class Template(VectorInstance):
    points: conlist(TemplatePoint, min_items=1)
    connections: List[TemplateConnection]
    template_id: StrictInt = Field(alias="templateId")


class CuboidPoint(BaseModel):
    f1: AxisPoint
    f2: AxisPoint
    r1: AxisPoint
    r2: AxisPoint


class Cuboid(VectorInstance):
    points: CuboidPoint


ANNOTATION_TYPES = {
    VectorAnnotationTypeEnum.BBOX: Bbox,
    VectorAnnotationTypeEnum.TEMPLATE: Template,
    VectorAnnotationTypeEnum.CUBOID: Cuboid,
    VectorAnnotationTypeEnum.POLYGON: Polygon,
    VectorAnnotationTypeEnum.POINT: Point,
    VectorAnnotationTypeEnum.POLYLINE: PolyLine,
    VectorAnnotationTypeEnum.ELLIPSE: Ellipse,
    VectorAnnotationTypeEnum.RBBOX: RotatedBox,
}

class AnnotationInstance(BaseModel):
    __root__: Union[
        Template, Cuboid, Point, PolyLine, Polygon, Bbox, Ellipse, RotatedBox
    ]

    @classmethod
    def __get_validators__(cls):
        yield cls.return_action

    @classmethod
    def return_action(cls, values):
        try:
            try:
                instance_type = values["type"]
            except KeyError:
                raise ValidationError(
                    [ErrorWrapper(ValueError("field required"), "type")], cls
                )
            return ANNOTATION_TYPES[instance_type](**values)
        except KeyError:
            raise ValidationError(
                [
                    ErrorWrapper(
                        ValueError(
                            f"invalid type, valid types are {', '.join(ANNOTATION_TYPES.keys())}"
                        ),
                        "type",
                    )
                ],
                cls,
            )
        except TypeError as e:
            raise TypeError(INVALID_DICT_MESSAGE) from e


class VectorAnnotation(BaseModel):
    metadata: Metadata
    comments: Optional[List[Comment]] = Field(list())
    tags: Optional[List[Tag]] = Field(list())
    instances: Optional[
        List[
            Union[Template, Cuboid, Point, PolyLine, Polygon, Bbox, Ellipse, RotatedBox]
        ]
    ] = Field(list())

    @validator("instances", pre=True, each_item=True)
    def check_instances(cls, instance):
        annotation_type = instance.get("type")
        if not annotation_type:
            raise ValidationError(
                [
                    ErrorWrapper(
                        ValueError(
                            f"type field required"
                        ),
                        "type",
                    )
                ],
                model=BaseModel
            )
        model_type = ANNOTATION_TYPES.get(annotation_type)
        if not model_type:
            raise ValidationError(
                [
                    ErrorWrapper(
                        ValueError(
                            f"invalid value"
                        ),
                        "type",
                    )
                ],
                model=BaseModel
            )
        result = validate_model(ANNOTATION_TYPES[annotation_type], instance)
        if result[2]:
            raise ValidationError(
                result[2].raw_errors, model=ANNOTATION_TYPES[annotation_type]
            )
        return instance

