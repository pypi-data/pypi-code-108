from typing import List, Optional

from pydantic import validator
from pydantic.main import BaseModel

from cg_hermes.config.tags import ALL_TAGS, AVAILABLE_USAGES


class TagMap(BaseModel):
    tags: List[str]
    is_mandatory: bool
    used_by: List[str]
    bundle_id: Optional[bool] = False

    @validator("tags", each_item=True)
    def check_tags(cls, tag):
        assert tag in ALL_TAGS, f"{tag} not a valid tag"
        return tag

    @validator("used_by", each_item=True)
    def check_usage(cls, usage):
        assert usage in AVAILABLE_USAGES, f"{usage} not a valid usage"
        return usage


class CGTag(BaseModel):
    path: str
    tags: List[str]
    mandatory: bool
