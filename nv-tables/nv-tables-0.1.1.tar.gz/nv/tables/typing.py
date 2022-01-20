from typing import Dict, Any, Mapping, List, Iterable, Tuple

from nv.utils.typing import DataClass


# Generic data structures
DataRow = Mapping[str, Any] | DataClass
DataTable = Iterable[DataRow]
DataStructure = Iterable[Tuple[str, DataTable]] | Mapping[str, DataTable]


# Output data structures
ParsedDataRow = Dict[str, Any] | DataClass
ParsedDataTable = List[ParsedDataRow]
ParsedDataStructure = Mapping[str, ParsedDataTable]
