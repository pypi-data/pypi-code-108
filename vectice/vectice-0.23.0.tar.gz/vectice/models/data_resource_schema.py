from typing import List, Optional
from dataclasses import dataclass
from enum import Enum


class DataType(Enum):
    String = "Text"
    Integer = "Integer"
    Float = "RealNumber"
    Float64 = "RealNumber"
    Boolean = "Boolean"
    Spacial = "Spacial"
    Binary = "Binary"
    Timestamp = "Timestamp"
    DateTime = "DateTime"
    Complex = "Complex"
    Unknown = "Unknown"


@dataclass
class SchemaColumn:
    name: Optional[str] = None
    description: Optional[str] = None
    dataType: Optional[DataType] = None
    length: Optional[int] = 0
    precision: Optional[int] = None
    scale: Optional[int] = 0
    isUnique: Optional[bool] = False
    default: Optional[str] = None
    nullable: Optional[bool] = True
    isPrimaryKey: Optional[bool] = False
    isForeignKey: Optional[bool] = False


@dataclass
class DataResourceSchema:
    type: str
    name: str
    description: str
    fileFormat: str
    columns: Optional[List[SchemaColumn]] = None
