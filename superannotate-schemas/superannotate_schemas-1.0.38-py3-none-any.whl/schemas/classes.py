from typing import Optional
from typing import List

from superannotate_schemas.schemas.base import BaseModel
from superannotate_schemas.schemas.base import TimedBaseModel
from superannotate_schemas.schemas.base import StrictInt
from superannotate_schemas.schemas.base import StrictStr
from superannotate_schemas.schemas.base import HexColor
from superannotate_schemas.schemas.enums import ClassTypeEnum


class Attribute(TimedBaseModel):
    id: Optional[StrictInt]
    group_id: Optional[StrictInt]
    project_id: Optional[StrictInt]
    name: StrictStr
    count: Optional[StrictInt]

    def __hash__(self):
        return hash(f"{self.id}{self.group_id}{self.name}")


class AttributeGroup(TimedBaseModel):
    id: Optional[StrictInt]
    class_id: Optional[StrictInt]
    name: StrictStr
    is_multiselect: Optional[bool]
    attributes: List[Attribute]

    def __hash__(self):
        return hash(f"{self.id}{self.class_id}{self.name}")


class AnnotationClass(TimedBaseModel):
    id: Optional[StrictInt]
    project_id: Optional[StrictInt]
    type: ClassTypeEnum = ClassTypeEnum.OBJECT
    name: StrictStr
    color: HexColor
    count: Optional[StrictInt]
    attribute_groups: List[AttributeGroup]

    def __hash__(self):
        return hash(f"{self.id}{self.type}{self.name}")


class AnnotationClasses(BaseModel):
    __root__: List[AnnotationClass]
