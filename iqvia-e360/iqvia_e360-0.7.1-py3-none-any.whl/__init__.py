__version__ = "0.7.1"

__all__ = ["E360Context", "Settings", "AnalyticDatasetModel",
           "AnalyticDatasetDefinitionModel", "Granularity",
           "AnalyticDatasetFormat", "ContainerAssetModel",
           "AdtReportAssetModel", "AssetModel", "ContainerModel",
           "AdtDefinitionAssetModel", "FileAssetModel", "VisualizationAssetModel", "ClientStoreAssetModel"]

try:
    # Attempts to import the client class
    # Allowed to fail importing so the package metadata can be read for building
    from workspace_clients.models import AssetModel, ContainerModel
    from adt_clients.models import AnalyticDatasetModel, AnalyticDatasetDefinitionModel, Granularity, AnalyticDatasetFormat

    from .settings import Settings
    from .e360_context import E360Context
    from .models import ContainerAssetModel, AdtReportAssetModel, AdtDefinitionAssetModel, FileAssetModel, VisualizationAssetModel, ClientStoreAssetModel

except (ImportError, ModuleNotFoundError):  # pragma: no cover
    pass  # pragma: no cover
