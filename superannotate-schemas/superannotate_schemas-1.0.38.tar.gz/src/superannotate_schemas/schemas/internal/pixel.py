from typing import List
from typing import Optional

from superannotate_schemas.schemas.base import BaseImageMetadata as Metadata
from superannotate_schemas.schemas.base import HexColor
from superannotate_schemas.schemas.base import BaseAttribute
from superannotate_schemas.schemas.base import BaseImageAnnotationInstance
from superannotate_schemas.schemas.base import Tag
from superannotate_schemas.schemas.base import Comment
from superannotate_schemas.schemas.base import BaseModel

from pydantic import StrictInt
from pydantic import Field


class Attribute(BaseAttribute):
    id: StrictInt
    group_id: StrictInt = Field(alias="groupId")


class AnnotationPart(BaseModel):
    color: HexColor


class AnnotationInstance(BaseImageAnnotationInstance):
    parts: List[AnnotationPart]
    class_id: StrictInt = Field(alias="classId")
    attributes: Optional[List[Attribute]] = Field(list())


class PixelAnnotation(BaseModel):
    metadata: Metadata
    instances: List[AnnotationInstance]
    tags: Optional[List[Tag]] = Field(list())
    comments: Optional[List[Comment]] = Field(list())
