from enum import Enum


class CorrelationMethod(str, Enum):
    MUTUAL_INFO = "mutual_info"
    SPEARMAN = "spearman"
    PEARSON = "pearson"
    KENDALL = "kendall"

    def __str__(self) -> str:
        return str(self.value)
