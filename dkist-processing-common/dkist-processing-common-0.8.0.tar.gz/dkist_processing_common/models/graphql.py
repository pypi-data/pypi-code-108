"""
GraphQL Data models for the metadata store api
"""
from dataclasses import dataclass
from os import environ

AUTH_TOKEN = environ.get("GQL_AUTH_TOKEN")


@dataclass
class RecipeRunMutation:
    recipeRunId: int
    recipeRunStatusId: int
    authToken: str = AUTH_TOKEN


@dataclass
class RecipeRunStatusResponse:
    recipeRunStatusId: int


@dataclass
class RecipeRunStatusQuery:
    recipeRunStatusName: str


@dataclass
class CreateRecipeRunStatusResponse:
    recipeRunStatus: RecipeRunStatusResponse


@dataclass
class RecipeRunStatusMutation:
    recipeRunStatusName: str
    isComplete: bool
    recipeRunStatusDescription: str
    authToken: str = AUTH_TOKEN


@dataclass
class InputDatasetResponse:
    inputDatasetId: int
    isActive: bool
    inputDatasetDocument: str


@dataclass
class RecipeInstanceResponse:
    inputDataset: InputDatasetResponse
    recipeId: int


@dataclass
class RecipeRunResponse:
    recipeInstance: RecipeInstanceResponse
    recipeInstanceId: int
    configuration: str = None


@dataclass
class RecipeRunQuery:
    recipeRunId: int


@dataclass
class DatasetCatalogReceiptAccountMutation:
    """
    Dataclass used to write the dataset_catalog_receipt_account record for the run.
    It sets an expected object count for a dataset so that dataset inventory creation
    doesn't happen until all objects are transferred and inventoried.
    """

    datasetId: str
    expectedObjectCount: int
    authToken: str = AUTH_TOKEN


@dataclass
class RecipeRunProvenanceMutation:
    inputDatasetId: int
    isTaskManual: bool
    recipeRunId: int
    taskName: str
    libraryVersions: str
    workflowVersion: str
    codeVersion: str = None
    authToken: str = AUTH_TOKEN


@dataclass
class QualityReportMutation:
    datasetId: str
    qualityReport: str  # JSON
    authToken: str = AUTH_TOKEN
