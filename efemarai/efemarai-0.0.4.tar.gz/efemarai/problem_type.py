from enum import Enum

class ProblemType(Enum):
    Classification = "Classification"
    ObjectDetection = "ObjectDetection"
    SemanticSegmentation = "SemanticSegmentation"
    InstanceSegmentation = "InstanceSegmentation"

    @classmethod
    def has(cls, value):
        try:
            cls(value)
            return True
        except ValueError:
            return False
