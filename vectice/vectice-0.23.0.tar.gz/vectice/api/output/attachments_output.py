from dataclasses import dataclass


@dataclass
class __Output:
    fileId: int
    fileName: str
    contentType: str
    entityId: int
    entityType: str


@dataclass
class AttachmentOutput(__Output):
    pass
