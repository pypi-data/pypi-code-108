from typing import List, Optional
from datetime import date
from pyspark.sql import DataFrame
from featurestorebundle.feature.reader.FeaturesReaderInterface import FeaturesReaderInterface
from featurestorebundle.metadata.reader.MetadataReaderInterface import MetadataReaderInterface
from featurestorebundle.target.reader.TargetsReaderInterface import TargetsReaderInterface
from featurestorebundle.delta.feature.DeltaRainbowTableManager import DeltaRainbowTableManager
from featurestorebundle.delta.feature.FeaturesFilteringManager import FeaturesFilteringManager
from featurestorebundle.delta.target.TargetsFilteringManager import TargetsFilteringManager


class FeatureStore:
    def __init__(
        self,
        features_reader: FeaturesReaderInterface,
        metadata_reader: MetadataReaderInterface,
        targets_reader: TargetsReaderInterface,
        rainbow_table_manager: DeltaRainbowTableManager,
        features_filtering_manager: FeaturesFilteringManager,
        targets_filtering_manager: TargetsFilteringManager,
    ):
        self.__features_reader = features_reader
        self.__metadata_reader = metadata_reader
        self.__targets_reader = targets_reader
        self.__rainbow_table_manager = rainbow_table_manager
        self.__features_filtering_manager = features_filtering_manager
        self.__targets_filtering_manager = targets_filtering_manager

    def get_latest(self, entity: str, features: Optional[List[str]] = None) -> DataFrame:
        features = features or []
        feature_store = self.__features_reader.read(entity)
        rainbow_table = self.__rainbow_table_manager.read(entity)

        return self.__features_filtering_manager.get_latest(feature_store, rainbow_table, features)

    def get_for_target(
        self,
        entity: str,
        target: str,
        target_date_from: Optional[date] = None,
        target_date_to: Optional[date] = None,
        time_diff: Optional[str] = None,
        features: Optional[List[str]] = None,
        skip_incomplete_rows: bool = False,
    ) -> DataFrame:
        features = features or []
        feature_store = self.__features_reader.read(entity)
        target_store = self.__targets_reader.read(entity)
        rainbow_table = self.__rainbow_table_manager.read(entity)
        targets = self.__targets_filtering_manager.get_targets(target_store, target, target_date_from, target_date_to, time_diff)

        return self.__features_filtering_manager.get_for_target(feature_store, rainbow_table, targets, features, skip_incomplete_rows)

    def get_metadata(
        self,
        entity: Optional[str] = None,
    ) -> DataFrame:
        return self.__metadata_reader.read(entity)

    def get_targets(
        self,
        entity: str,
        target: str,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        time_diff: Optional[str] = None,
    ) -> DataFrame:
        target_store = self.__targets_reader.read(entity)

        return self.__targets_filtering_manager.get_targets(target_store, target, date_from, date_to, time_diff)
