from typing import Union
from logging import Logger
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from featurestorebundle.db.TableNames import TableNames
from featurestorebundle.entity.Entity import Entity
from featurestorebundle.delta.TableExistenceChecker import TableExistenceChecker
from featurestorebundle.delta.EmptyDataFrameCreator import EmptyDataFrameCreator
from featurestorebundle.feature.reader.FeaturesReaderInterface import FeaturesReaderInterface
from featurestorebundle.delta.feature.schema import get_feature_store_initial_schema


class DeltaTableFeaturesReader(FeaturesReaderInterface):
    def __init__(
        self,
        logger: Logger,
        spark: SparkSession,
        table_names: TableNames,
        table_existence_checker: TableExistenceChecker,
        empty_dataframe_creator: EmptyDataFrameCreator,
    ):
        self.__logger = logger
        self.__spark = spark
        self.__table_names = table_names
        self.__table_existence_checker = table_existence_checker
        self.__empty_dataframe_creator = empty_dataframe_creator

    def read(self, entity: Union[Entity, str]) -> DataFrame:
        if isinstance(entity, Entity):
            entity = entity.name

        full_table_name = self.__table_names.get_features_full_table_name(entity)

        self.__logger.info(f"Reading features from table {full_table_name}")

        return self.__spark.read.table(full_table_name)

    def read_safe(self, entity: Entity) -> DataFrame:
        full_table_name = self.__table_names.get_features_full_table_name(entity.name)

        if not self.exists(entity):
            return self.__empty_dataframe_creator.create(get_feature_store_initial_schema(entity))

        return self.__spark.read.table(full_table_name)

    def exists(self, entity: Union[Entity, str]) -> bool:
        if isinstance(entity, Entity):
            entity = entity.name

        full_table_name = self.__table_names.get_features_full_table_name(entity)

        return self.__table_existence_checker.exists(full_table_name)
