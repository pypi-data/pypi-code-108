from typing import List
from typing import Optional

from superannotate_schemas.schemas.base import BaseImageAnnotationInstance
from superannotate_schemas.schemas.base import BaseAttribute
from superannotate_schemas.schemas.base import BaseImageMetadata
from superannotate_schemas.schemas.base import NotEmptyStr
from superannotate_schemas.schemas.base import StrictStr
from superannotate_schemas.schemas.base import PixelColor
from superannotate_schemas.schemas.base import Tag
from superannotate_schemas.schemas.base import Comment

from superannotate_schemas.schemas.base import BaseModel
from pydantic import Field


class Attribute(BaseAttribute):
    name: NotEmptyStr
    group_name: NotEmptyStr = Field(alias="groupName")


class MetaData(BaseImageMetadata):
    is_segmented: Optional[bool] = Field(alias="isSegmented")
    is_predicted: Optional[bool] = Field(alias="isPredicted")


class AnnotationPart(BaseModel):
    color: PixelColor


class AnnotationInstance(BaseImageAnnotationInstance):
    parts: List[AnnotationPart]
    attributes: Optional[List[Attribute]] = Field(list())


class PixelAnnotation(BaseModel):
    metadata: MetaData
    instances: List[AnnotationInstance]
    tags: Optional[List[Tag]] = Field(list())
    comments: Optional[List[Comment]] = Field(list())
