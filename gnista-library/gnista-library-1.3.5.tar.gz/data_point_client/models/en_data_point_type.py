from enum import Enum


class EnDataPointType(str, Enum):
    IMPORTDATAPOINT = "ImportDataPoint"
    CALCULATIONDATAPOINT = "CalculationDataPoint"
    REMOTEDATAPOINT = "RemoteDataPoint"

    def __str__(self) -> str:
        return str(self.value)
