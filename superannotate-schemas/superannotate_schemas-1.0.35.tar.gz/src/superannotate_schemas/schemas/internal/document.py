from typing import List
from typing import Optional

from superannotate_schemas.schemas.base import BaseAttribute
from superannotate_schemas.schemas.base import BaseInstance
from superannotate_schemas.schemas.base import BaseMetadata as Metadata
from superannotate_schemas.schemas.base import Tag
from superannotate_schemas.schemas.base import NotEmptyStr

from superannotate_schemas.schemas.base import BaseModel

from pydantic import Field
from pydantic import StrictStr


class Attribute(BaseAttribute):
    name: NotEmptyStr
    group_name: NotEmptyStr = Field(alias="groupName")


class DocumentInstance(BaseInstance):
    start: int
    end: int
    attributes: Optional[List[Attribute]] = Field(list())


class DocumentAnnotation(BaseModel):
    metadata: Metadata
    instances: Optional[List[DocumentInstance]] = Field(list())
    tags: Optional[List[Tag]] = Field(list())
    free_text: Optional[StrictStr] = Field(None, alias="freeText")
