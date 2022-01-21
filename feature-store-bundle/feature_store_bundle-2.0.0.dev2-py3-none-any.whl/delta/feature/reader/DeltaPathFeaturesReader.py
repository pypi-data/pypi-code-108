from typing import Union
from logging import Logger
from pyspark.sql import SparkSession
from pyspark.sql import DataFrame
from featurestorebundle.db.TableNames import TableNames
from featurestorebundle.entity.Entity import Entity
from featurestorebundle.delta.PathExistenceChecker import PathExistenceChecker
from featurestorebundle.delta.EmptyDataFrameCreator import EmptyDataFrameCreator
from featurestorebundle.feature.reader.FeaturesReaderInterface import FeaturesReaderInterface
from featurestorebundle.delta.feature.schema import get_feature_store_initial_schema


class DeltaPathFeaturesReader(FeaturesReaderInterface):
    def __init__(
        self,
        logger: Logger,
        spark: SparkSession,
        table_names: TableNames,
        path_existence_checker: PathExistenceChecker,
        empty_dataframe_creator: EmptyDataFrameCreator,
    ):
        self.__logger = logger
        self.__spark = spark
        self.__table_names = table_names
        self.__path_existence_checker = path_existence_checker
        self.__empty_dataframe_creator = empty_dataframe_creator

    def read(self, entity: Union[Entity, str]) -> DataFrame:
        if isinstance(entity, Entity):
            entity = entity.name

        path = self.__table_names.get_features_path(entity)

        self.__logger.info(f"Reading features from path {path}")

        return self.__spark.read.format("delta").load(path)

    def read_safe(self, entity: Entity) -> DataFrame:
        path = self.__table_names.get_features_path(entity.name)

        if not self.exists(entity):
            return self.__empty_dataframe_creator.create(get_feature_store_initial_schema(entity))

        return self.__spark.read.format("delta").load(path)

    def exists(self, entity: Union[Entity, str]) -> bool:
        if isinstance(entity, Entity):
            entity = entity.name

        path = self.__table_names.get_features_path(entity)

        return self.__path_existence_checker.exists(path)
