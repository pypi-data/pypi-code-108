from enum import Enum
from pydantic import BaseModel, Field

class Frameworks(str,Enum):
    sklearn = "SKLEARN"

    @staticmethod
    def has_value(item):
        return item in [v.value for v in Frameworks.__members__.values()]