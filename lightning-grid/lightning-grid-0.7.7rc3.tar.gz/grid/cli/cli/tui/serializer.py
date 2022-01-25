import csv
from dataclasses import asdict
from enum import Enum
import io
import json
from typing import Any, Dict, List, Union

from rich.console import Console
from rich.table import Table
from rich.text import Text

from grid.cli.sdk_record import Record


class SerializationFormat(Enum):
    """Formats used to serialize Record objects."""
    JSON = "json"
    CSV = "csv"
    TABLE = "table"


class Serializer:
    """
    Record parser will serialize Grid API results into desired formats.
    This is used in the context of a TUI where we may want to output the format
    of data into different formats, such as JSON, CSV, etc.

    Parameters
    ----------
    records: List[Record]
        List of Record objects
    """
    def __init__(self, records: List[Record]):
        self.records = records
        self.header = self.dict_records[0].keys()

    @property
    def dict_records(self) -> List[Dict[str, Any]]:
        """Dict[str, Any] representation of Record"""
        return [asdict(record) for record in self.records]

    def to_table(self) -> Table:
        """Serializes Record object to rich Table"""
        table = Table(*self.header, show_header=True, header_style="bold green")
        for record in self.dict_records:
            values = [Text(v) for v in record.values()]
            table.add_row(*values)
        return table

    def to_json(self) -> str:
        """Serializes Record objects to JSON."""
        return json.dumps(self.dict_records)

    def to_csv(self) -> str:
        """Serializes Record objects to CSV."""
        output = io.StringIO()
        writer = csv.DictWriter(output, quoting=csv.QUOTE_NONNUMERIC, fieldnames=self.header)
        writer.writeheader()
        for record in self.dict_records:
            writer.writerow(record)

        return output.getvalue()

    def generate(self, format: SerializationFormat = SerializationFormat.TABLE) -> Union[str]:
        """
        Serializes output in desired format.

        Parameters
        ----------
        format: SerializationFormat
            Type of output format to generate output in.
        """
        if format == SerializationFormat.TABLE:
            pass
        elif format == SerializationFormat.CSV:
            return self.to_csv()
        elif format == SerializationFormat.JSON:
            return self.to_json()

    def print(self, format: SerializationFormat = SerializationFormat.TABLE) -> None:
        console = Console()
        data = self.generate()
        console.print(data, highlight=False)
