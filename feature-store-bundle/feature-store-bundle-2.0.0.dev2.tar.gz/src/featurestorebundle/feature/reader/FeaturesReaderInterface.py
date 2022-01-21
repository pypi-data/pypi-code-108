from abc import ABC, abstractmethod
from typing import Union
from pyspark.sql import DataFrame
from featurestorebundle.entity.Entity import Entity


class FeaturesReaderInterface(ABC):
    @abstractmethod
    def read(self, entity: Union[Entity, str]) -> DataFrame:
        pass

    @abstractmethod
    def read_safe(self, entity: Entity) -> DataFrame:
        pass

    @abstractmethod
    def exists(self, entity: Union[Entity, str]) -> bool:
        pass
