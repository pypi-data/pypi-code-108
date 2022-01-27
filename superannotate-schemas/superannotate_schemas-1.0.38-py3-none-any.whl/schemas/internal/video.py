from enum import Enum
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from superannotate_schemas.schemas.base import BaseAttribute
from superannotate_schemas.schemas.base import BaseInstance
from superannotate_schemas.schemas.base import BboxPoints
from superannotate_schemas.schemas.base import BaseMetadata
from superannotate_schemas.schemas.base import PointLabels
from superannotate_schemas.schemas.base import Tag
from superannotate_schemas.schemas.base import AnnotationStatusEnum

from superannotate_schemas.schemas.base import BaseModel
from pydantic import StrictFloat
from pydantic import constr
from pydantic import Field
from pydantic import StrictBool
from pydantic import StrictStr
from pydantic import StrictInt


class VideoType(str, Enum):
    EVENT = "event"
    BBOX = "bbox"


class Attribute(BaseAttribute):
    id: StrictInt
    group_id: StrictInt = Field(alias="groupId")


class MetaData(BaseMetadata):
    width: Optional[StrictInt]
    height: Optional[StrictInt]
    status: Optional[AnnotationStatusEnum]
    duration: Optional[StrictInt]
    error: Optional[StrictBool]


class BaseTimeStamp(BaseModel):
    active: Optional[bool]
    attributes: Optional[Dict[constr(regex=r"^[-|+]$"), List[Attribute]]]  # noqa: F722


class BboxTimeStamp(BaseTimeStamp):
    points: Optional[BboxPoints]


class BaseVideoInstance(BaseInstance):
    id: Optional[StrictStr]
    type: VideoType
    locked: Optional[StrictBool]
    timeline: Dict[StrictFloat, BaseTimeStamp]


class BboxInstance(BaseVideoInstance):
    point_labels: Optional[PointLabels] = Field(alias="pointLabels")
    timeline: Dict[StrictFloat, BboxTimeStamp]


class EventInstance(BaseVideoInstance):
    pass


class VideoAnnotation(BaseModel):
    metadata: MetaData
    instances: Optional[List[Union[EventInstance, BboxInstance]]] = Field(list())
    tags: Optional[List[Tag]] = Field(list())
