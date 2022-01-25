from dataclasses import dataclass
from pathlib import Path
from typing import List, TypeVar, Generic, Union, Callable

from sm.misc import deserialize_json, get_latest_path
from sm.outputs import SemanticModel

T = TypeVar("T")


@dataclass
class Example(Generic[T]):
    sms: List[SemanticModel]
    table: T


def load(
    data_dir: Union[str, Path], table_deser: Callable[[dict], T]
) -> List[Example[T]]:
    """Load dataset from a folder. Assuming the following structure:
    - descriptions: (containing semantic descriptions of tables)
        - <table_fs_id>
            - version.01.json
            - version.02.json
            - ...
        - ...
    - tables: (containing list of tables, the type of table depends on )
        - <table_fs_id>.json
        - ...

    Args:
        data_dir:
        table_deser: deserialize the table from dictionary

    Returns:

    """
    data_dir = Path(data_dir)
    examples = []
    for infile in sorted((data_dir / "tables").iterdir()):
        if infile.name.startswith("."):
            continue
        assert infile.name.endswith(".json")
        example_id = infile.stem

        table = table_deser(deserialize_json(infile))
        raw_sms = deserialize_json(
            get_latest_path(data_dir / f"descriptions/{example_id}/version.json")
        )
        sms = [SemanticModel.from_dict(sm) for sm in raw_sms]

        examples.append(Example(sms=sms, table=table))
    return examples
