# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""The base class to hold all the HTS events."""
from typing import Any, Dict, Optional

from azureml.automl.core.shared._diagnostics.automl_events import AutoMLBaseEvent


class PartitionTabularDatasetStart(AutoMLBaseEvent):
    """Events for HTS partition tabular dataset start."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(PartitionTabularDatasetStart, self).__init__(additional_fields)


class PartitionTabularDatasetPartition(AutoMLBaseEvent):
    """Events for HTS partition tabular dataset partition."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(PartitionTabularDatasetPartition, self).__init__(additional_fields)


class PartitionTabularDatasetEnd(AutoMLBaseEvent):
    """Events for HTS partition tabular dataset end."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(PartitionTabularDatasetEnd, self).__init__(additional_fields)


class HierarchyBuilderDriverStart(AutoMLBaseEvent):
    """Events for HTS hierarchy builder start."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HierarchyBuilderDriverStart, self).__init__(additional_fields)


class HierarchyBuilderValidateData(AutoMLBaseEvent):
    """Events for HTS hierarchy builder validate data."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HierarchyBuilderValidateData, self).__init__(additional_fields)


class HierarchyBuilderCollectData(AutoMLBaseEvent):
    """Events for HTS hierarchy builder collect data."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HierarchyBuilderCollectData, self).__init__(additional_fields)


class HierarchyBuilderUpload(AutoMLBaseEvent):
    """Events for HTS hierarchy builder upload."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HierarchyBuilderUpload, self).__init__(additional_fields)


class HierarchyBuilderEnd(AutoMLBaseEvent):
    """Events for HTS hierarchy builder end."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HierarchyBuilderEnd, self).__init__(additional_fields)


class DataAggStart(AutoMLBaseEvent):
    """Events for HTS data agg start."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(DataAggStart, self).__init__(additional_fields)


class DataAggAggData(AutoMLBaseEvent):
    """Events for HTS data agg script data agg."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(DataAggAggData, self).__init__(additional_fields)


class DataAggUpload(AutoMLBaseEvent):
    """Events for HTS data agg upload."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(DataAggUpload, self).__init__(additional_fields)


class DataAggPropCalc(AutoMLBaseEvent):
    """Events for HTS data agg proportion calculation."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(DataAggPropCalc, self).__init__(additional_fields)


class DataAggEnd(AutoMLBaseEvent):
    """Events for HTS data agg proportion calculation."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(DataAggEnd, self).__init__(additional_fields)


class HTSAutoMLTrainStart(AutoMLBaseEvent):
    """Events for HTS automl train start."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSAutoMLTrainStart, self).__init__(additional_fields)


class HTSAutoMLTrainSaveMetadata(AutoMLBaseEvent):
    """Events for HTS automl train start."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSAutoMLTrainSaveMetadata, self).__init__(additional_fields)


class HTSAutoMLTrainEnd(AutoMLBaseEvent):
    """Events for HTS automl train end."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSAutoMLTrainEnd, self).__init__(additional_fields)


class HTSForecastStart(AutoMLBaseEvent):
    """Events for HTS forecast start."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSForecastStart, self).__init__(additional_fields)


class HTSForecastGroupBy(AutoMLBaseEvent):
    """Events for HTS forecast group by."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSForecastGroupBy, self).__init__(additional_fields)


class HTSForecastEnd(AutoMLBaseEvent):
    """Events for HTS forecast end."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSForecastEnd, self).__init__(additional_fields)


class HTSPropCalcStart(AutoMLBaseEvent):
    """Events for HTS proportions calculation start."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSPropCalcStart, self).__init__(additional_fields)


class HTSPropCalcProcessFile(AutoMLBaseEvent):
    """Events for HTS proportions calculation start."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSPropCalcProcessFile, self).__init__(additional_fields)


class HTSPropCalcTimeSum(AutoMLBaseEvent):
    """Events for HTS proportions calculation start."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSPropCalcTimeSum, self).__init__(additional_fields)


class HTSPropCalcUpload(AutoMLBaseEvent):
    """Events for HTS proportions calculation start."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSPropCalcUpload, self).__init__(additional_fields)


class HTSPropCalcEnd(AutoMLBaseEvent):
    """Events for HTS proportions calculation start."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSPropCalcEnd, self).__init__(additional_fields)


class HTSAllocationStart(AutoMLBaseEvent):
    """Events for HTS allocation start."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSAllocationStart, self).__init__(additional_fields)


class HTSAllocationProcess(AutoMLBaseEvent):
    """Events for HTS allocation process raw data file."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSAllocationProcess, self).__init__(additional_fields)


class HTSAllocationPredict(AutoMLBaseEvent):
    """Events for HTS allocation predict allocation."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSAllocationPredict, self).__init__(additional_fields)


class HTSAllocationEnd(AutoMLBaseEvent):
    """Events for HTS allocation end."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSAllocationEnd, self).__init__(additional_fields)


class HTSExplAllocationStart(AutoMLBaseEvent):
    """Events for HTS explaination allocation start."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSExplAllocationStart, self).__init__(additional_fields)


class HTSExplAllocationAllocation(AutoMLBaseEvent):
    """Events for HTS explaination allocation script allocation."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSExplAllocationAllocation, self).__init__(additional_fields)


class HTSExplAllocationEnd(AutoMLBaseEvent):
    """Events for HTS explaination allocation end."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSExplAllocationEnd, self).__init__(additional_fields)


class HTSExplAllocationRawData(AutoMLBaseEvent):
    """Events for HTS explaination allocation process raw data."""
    def __init__(self, additional_fields: Optional[Dict[str, Any]] = None) -> None:
        super(HTSExplAllocationRawData, self).__init__(additional_fields)
