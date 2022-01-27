from enum import Enum


class TargetTransformType(str, Enum):
    DONOTHING = "DoNothing"
    HORIZONLAGDIFF = "HorizonLagDiff"
    HORIZONLAGDIFFRATIO = "HorizonLagDiffRatio"

    def __str__(self) -> str:
        return str(self.value)
