from enum import Enum


class MbsAgency(str, Enum):
    NULL_AGENCY = "NULL_AGENCY"
    FNM = "FNM"
    FHL = "FHL"
    GNM = "GNM"

    def __str__(self) -> str:
        return str(self.value)
