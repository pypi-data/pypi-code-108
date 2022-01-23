from pathlib import Path, PurePath
from typing import List, TypeVar

# Convenient typedefs
#
StringList = List[str]
PathList = List[Path]
PurePathList = List[PurePath]

# A type variable so function types can vary.
#
T = TypeVar("T")
