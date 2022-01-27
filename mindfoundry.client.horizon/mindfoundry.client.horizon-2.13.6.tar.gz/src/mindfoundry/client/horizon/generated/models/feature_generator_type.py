from enum import Enum


class FeatureGeneratorType(str, Enum):
    AUTOLAG = "autolag"
    EWMA = "ewma"
    LAG = "lag"
    LOGARITHM = "logarithm"
    ROLLING_AVERAGE = "rolling_average"
    CALENDAR = "calendar"
    PERC_CHANGE = "perc_change"
    NUM_PEAKS = "num_peaks"
    ONE_HOT_ENCODE = "one_hot_encode"

    def __str__(self) -> str:
        return str(self.value)
