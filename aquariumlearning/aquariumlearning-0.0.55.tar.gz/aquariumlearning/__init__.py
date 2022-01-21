# Only expose public API

from .util import check_if_update_needed

from .client import (
    Client as Client,
    LabeledDataset as LabeledDataset,
    LabeledFrame as LabeledFrame,
    Inferences as Inferences,
    InferencesFrame as InferencesFrame,
    LabelClassMap as LabelClassMap,
    ClassMapEntry as ClassMapEntry,
    ClassMapUpdateEntry as ClassMapUpdateEntry,
    CustomMetricsDefinition as CustomMetricsDefinition,
    StratifiedMetricsDefinition as StratifiedMetricsDefinition,
    orig_label_color_list as orig_label_color_list,
    tableau_colors as tableau_colors,
    turbo_rgb as turbo_rgb,
    viridis_rgb as viridis_rgb,
)
from .collection_client import CollectionClient as CollectionClient

from .issues import (
    IssueManager as IssueManager,
    Issue as Issue,
    IssueElement as IssueElement,
)
from .metrics_manager import MetricsManager as MetricsManager


# TODO: Avoid duplicating here while still getting nice autodoc?
__all__ = [
    "Client",
    "CollectionClient",
    "LabeledDataset",
    "LabeledFrame",
    "Inferences",
    "InferencesFrame",
    "LabelClassMap",
    "ClassMapEntry",
    "ClassMapUpdateEntry",
    "CustomMetricsDefinition",
    "StratifiedMetricsDefinition",
    "orig_label_color_list",
    "tableau_colors",
    "turbo_rgb",
    "viridis_rgb",
    "IssueManager",
    "Issue",
    "IssueElement",
    "MetricsManager",
]

check_if_update_needed()
