from enum import Enum
from typing_extensions import TypedDict


class Id(TypedDict):
  id: str


class Origin(Enum):
  REGISTRATION = 'Registration'
  EXECUTION = 'Executed'
  VALIDATION = 'Validation'


class MessageType(Enum):
  INFO = 'Info'
  WARNING = 'Warning'
  ERROR = 'Error'


class Logs(TypedDict):
  createdAt: str
  origin: Origin
  message: str
  messageType: MessageType


class Status(Enum):
  REGISTERED = 'Registered'
  RUNNING = 'Running'
  FINISHED = 'Finished'
  FINISHED_WITH_WARNING = 'FinishedWithWarning'
  FAILED = 'Failed'
  QUEUED = 'Queued'


class StatusResponse(TypedDict):
  createdAt: str
  status: Status
  progress: float
  memory: int
  CPU: int


class ObjId(TypedDict):
  id: str


class SortDirection(Enum):
  CREATED_AT_DESC = '-createdAt'
  CREATED_AT_ASC = '+createdAt'
  UPDATED_AT_DESC = '-updatedAt'
  UPDATED_AT_ASC = '+updatedAt'
  TITLE_DESC = '-title'
  TITLE_ASC = '+title'


class ExecuteResponse(TypedDict):
  message: str
  code: str


class Version(TypedDict):
  version: Id
