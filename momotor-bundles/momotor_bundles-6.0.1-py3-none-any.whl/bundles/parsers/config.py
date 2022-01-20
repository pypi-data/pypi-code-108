from dataclasses import dataclass
import typing
from pathlib import Path

from xsdata.formats.dataclass.parsers.config import ParserConfig


@dataclass
class BundleParserConfig(ParserConfig):
    huge_tree: bool = True
    process_xslt: bool = False
    validation_schema_path: typing.Union[str, Path, None] = None
