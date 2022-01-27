from enum import Enum


class ClassificationScoreMetric(str, Enum):
    PRECISION_AT_20 = "precision_at_20"
    ACCURACY = "accuracy"
    BALANCED_ACCURACY_SCORE = "balanced_accuracy_score"
    F1_SCORE = "f1_score"
    PRECISION_SCORE = "precision_score"

    def __str__(self) -> str:
        return str(self.value)
