import enum
from typing import List, Dict, Optional

from pydantic import BaseModel


class DatasetType(str, enum.Enum):
    """type of Dataset"""

    raw = "raw"
    derived = "derived"


class Ownable(BaseModel):
    """Many objects in SciCat are ownable"""

    ownerGroup: str
    accessGroups: List[str]


class MongoQueryable(BaseModel):
    """Many objects in SciCat are mongo queryable"""

    createdBy: Optional[str]
    updatedBy: Optional[str]
    updatedAt: Optional[str]
    createdAt: Optional[str]


class Dataset(Ownable, MongoQueryable):
    """
    A dataset in SciCat
    """

    pid: Optional[str]
    owner: str
    ownerEmail: Optional[str]
    orcidOfOwner: Optional[str]
    contactEmail: str
    creationLocation: str
    creationTime: str
    datasetName: Optional[str]
    type: DatasetType
    instrumentId: Optional[str]
    proposalId: str
    dataFormat: str
    principalInvestigator: str
    sourceFolder: str
    sourceFolderHost: Optional[str]
    size: Optional[int]
    packedSize: Optional[int]
    numberOfFiles: Optional[int]
    numberOfFilesArchived: Optional[int]
    scientificMetadata: Dict
    sampleId: str
    isPublished: str
    description: Optional[str]
    validationStatus: Optional[str]
    keywords: Optional[List[str]]
    datasetName: Optional[str]
    classification: Optional[str]
    license: Optional[str]
    version: Optional[str]
    isPublished: Optional[bool] = False


class DataFile(MongoQueryable):
    """
    A reference to a file in SciCat. Path is relative
    to the Dataset's sourceFolder parameter

    """

    path: str
    size: int
    time: Optional[str]
    uid: Optional[str] = None
    gid: Optional[str] = None
    perm: Optional[str] = None


class Datablock(Ownable):
    """
    A Datablock maps between a Dataset and contains DataFiles
    """

    id: Optional[str]
    # archiveId: str = None  listed in catamel model, but comes back invalid?
    size: int
    packedSize: Optional[int]
    chkAlg: Optional[int]
    version: str = None
    dataFileList: List[DataFile]
    datasetId: str


class Attachment(Ownable):
    """
    Attachments can be any base64 encoded string...thumbnails are attachments
    """

    id: Optional[str]
    thumbnail: str
    caption: Optional[str]
    datasetId: str
