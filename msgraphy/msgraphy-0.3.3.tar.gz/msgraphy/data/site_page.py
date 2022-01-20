from typing import List

from msgraphy.data import graphdataclass
from msgraphy.data.file import BaseItem


@graphdataclass
class ContentTypeInfo:
    id: str = None
    name: str = None


@graphdataclass
class WebPart:
    type: str = None
    data: dict = None


@graphdataclass
class PublicationFacet:
    level: str = None
    version_id: str = None


@graphdataclass
class SitePage(BaseItem):
    content_type: ContentTypeInfo = None

    title: str = None
    page_layout: str = None
    web_parts: List[WebPart] = None

    publishing_state: PublicationFacet = None



