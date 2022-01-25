"""
These models are accepted and returned by the views_docs
service, and are returned by various services that
expose documentation through the service.
"""

import datetime
from typing import List,Optional,Dict,Any
import pydantic

class DocumentationEntry(pydantic.BaseModel):
    """
    Services that expose endpoints that return documentation entries
    can be documented through the views_docs service.

    Note that the entry is recursive: entries can refer to child
    entries, such as tables > columns.
    """
    name: str
    path: str = "."
    entries: List["DocumentationEntry"] = []
    data: Dict[str,Any] = {}

DocumentationEntry.update_forward_refs()

class PostedDocumentationPage(pydantic.BaseModel):
    """
    The schema for posting a documentationentry to
    the views_docs service.
    """
    content: str

class DocumentationPageListEntry(pydantic.BaseModel):
    """
    The schema used when listing documentationentries.
    """
    name: str
    category: str
    last_edited: datetime.datetime
    author: str = ""

DocumentationPageList = List[DocumentationPageListEntry]

class DocumentationPageDetail(DocumentationPageListEntry, PostedDocumentationPage):
    """
    The schema for showing a full documentation entry, with both content and metadata
    """

class ViewsDoc(pydantic.BaseModel):
    """
    The data returned by views_docs, combining a remote entry with
    an optional documentation page.
    """
    entry: DocumentationEntry
    page: Optional[DocumentationPageDetail] = None
