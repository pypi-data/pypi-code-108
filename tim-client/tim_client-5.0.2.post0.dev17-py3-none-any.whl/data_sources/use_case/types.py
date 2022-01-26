from typing_extensions import TypedDict
from tim.types import Id


class UseCaseConfiguration(TypedDict):
  name: str
  workspace: Id
  dataset: Id


class CreateUseCaseResponse(TypedDict):
  id: str
  name: str
  description: str
  input: str
  output: str
  businessValue: str
  businessObjective: str
  businessKpi: str
  accuracyImpact: int
  workspace: Id
  dataset: Id
  isFavorite: bool
  createdAt: str
  createdBy: str
