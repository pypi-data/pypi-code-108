from enum import Enum
from tim.types import Logs, Status, Id, Version
from typing import List, Union, NamedTuple, Optional
from typing_extensions import TypedDict
from pandas.core.frame import DataFrame


class BaseUnit(Enum):
  DAY = 'Day'
  HOUR = 'Hour'
  MINUTE = 'Minute'
  SECOND = 'Second'
  MONTH = 'Month'
  SAMPLE = 'Sample'


Range = TypedDict('Range', {'from': str, 'to': str})


class RelativeRange(TypedDict):
  baseUnit: BaseUnit
  value: int


class ImputationTypeEnum(Enum):
  LINEAR = 'Linear'
  LOCF = 'LOCF'
  NONE = 'None'


class BasicBaseUnitEnum(Enum):
  DAY = 'Day'
  HOUR = 'Hour'
  MINUTE = 'Minute'
  SECOND = 'Second'


class UpdateUntilBaseUnitEnum(Enum):
  DAY = 'Day'
  HOUR = 'Hour'
  SAMPLE = 'Sample'


class ImputationInput(TypedDict):
  type: ImputationTypeEnum
  maxGapLength: int


class TimeScaleInput(TypedDict):
  baseUnit: BasicBaseUnitEnum
  value: int


class Aggregation(Enum):
  MEAN = 'Mean'
  SUM = 'Sum'
  MINIMUM = 'Minumum'
  MAXIMUM = 'Maximum'


class UpdateTimeInput(TypedDict):
  type: BasicBaseUnitEnum
  value: str


class UpdateUntilInput(TypedDict):
  baseUnit: UpdateUntilBaseUnitEnum
  offset: int


class UpdatesInput(TypedDict):
  column: Union[str, int]
  updateTime: List[UpdateTimeInput]
  updateUntil: UpdateUntilInput


class Data(TypedDict):
  version: Id
  rows: Union[RelativeRange, List[Range]]
  columns: List[Union[str, int]]
  KPIColumn: Union[str, int]
  holidayColumn: Union[str, int]
  imputation: ImputationInput
  timeScale: TimeScaleInput
  aggregation: Aggregation
  updates: List[UpdatesInput]


class DetectData(TypedDict):
  version: Id
  rows: Union[RelativeRange, List[Range]]
  imputation: ImputationInput


class DomainSpecificsInput(TypedDict):
  perspective: str
  sensitivity: float
  minSensitivity: float
  maxSensitivity: float


class NormalBehaviorModelInput(TypedDict):
  useNormalBehaviorModel: bool
  normalization: bool
  maxModelComplexity: int
  features: List[str]
  dailyCycle: bool
  useKPIoffsets: bool
  allowOffsets: bool


class DetectionIntervalsInput:
  type: str
  value: str


class AnomalousBehaviorModelInput(TypedDict):
  maxModelComplexity: int
  detectionIntervals: List[DetectionIntervalsInput]


class Configuration(TypedDict):
  domainSpecifics: List[DomainSpecificsInput]
  normalBehaviorModel: NormalBehaviorModelInput
  anomalousBehaviorModel: AnomalousBehaviorModelInput


class AnomalyDetectionJobConfiguration(TypedDict, total=False):
  name: str
  useCase: Id
  data: Data
  configuration: Configuration


class AnomalyDetectionDetectConfiguration(TypedDict, total=False):
  name: str
  data: DetectData


class BuildModelResponse(TypedDict):
  id: str
  expectedResultsTableSize: float


class BuildAnomalyDetectionModelConfiguration(TypedDict):
  name: str
  configuration: Configuration
  data: Data


class AccuracyMetrics(TypedDict):
  mape: float
  rmse: float
  accuracy: str
  mae: float


class SampleMeasures(TypedDict):
  name: str
  inSample: AccuracyMetrics
  outOfSample: AccuracyMetrics


class ErrorMeasures(TypedDict):
  all: SampleMeasures
  bin: List[SampleMeasures]
  samplesAhead: List[SampleMeasures]


class AnomalyDetectionType(Enum):
  BUILD_MODEL = 'build-model'
  REBUILD_MODEL = 'rebuild-model'
  DETECT = 'detect'
  RCA = 'rca'


class JobLoad(Enum):
  LIGHT = 'Light'
  HEAVY = 'Heavy'


class AnomalyDetection(TypedDict):
  id: str
  name: str
  type: AnomalyDetectionType
  status: Status
  parentJob: Id
  sequenceId: str
  useCase: Id
  experiment: Id
  dataset: Version
  createdAt: str
  completedAt: str
  executedAt: str
  workerVersion: float
  registrationBody: AnomalyDetectionJobConfiguration
  jobLoad: JobLoad
  calculationTime: str


class Part(TypedDict):
  type: str
  predictor: str
  offset: int
  value: float
  window: int
  knot: float
  subtype: int
  period: int
  cosOrder: List[float]
  sinOrder: List[float]
  unit: str
  day: int
  month: int


class Term(TypedDict):
  importance: int
  parts: List[Part]


class VariableOffset(TypedDict):
  name: str
  dataFrom: int
  dataTo: int


class AnomalyDetectionJobNormalBehaviorModelModel(TypedDict):
  index: int
  dayTime: str
  terms: List[Term]
  variableOffsets: List[VariableOffset]


class VariableProperties(TypedDict):
  name: str
  importance: float
  dataFrom: int
  dataTo: int


class AnomalyDetectionJobNormalBehaviorModel(TypedDict):
  samplingPeriod: str
  models: List[AnomalyDetectionJobNormalBehaviorModelModel]
  variableProperties: List[VariableProperties]


class AnomalyDetectionJobModelResultModel(TypedDict):
  normalBehaviorModel: AnomalyDetectionJobNormalBehaviorModel


class AnomalyDetectionJobModelResult(TypedDict):
  modelVersion: str
  model: AnomalyDetectionJobModelResultModel
  signature: str


class AnomalyDetectionResultsResponse(NamedTuple):
  metadata: Optional[AnomalyDetection]
  model_result: Optional[AnomalyDetectionJobModelResult]
  table_result: Optional[DataFrame]
  logs: List[Logs]
