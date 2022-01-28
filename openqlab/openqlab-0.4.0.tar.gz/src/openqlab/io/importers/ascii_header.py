import logging
import re
from pathlib import Path
from typing import List, Match, Optional

import pandas as pd

from openqlab._typing import FilepathOrBuffer
from openqlab.io.base_importer import StreamImporter
from openqlab.io.data_container import DataContainer
from openqlab.io.importers.utils import UnknownFileType

log = logging.getLogger(__name__)


class ASCII_Header(StreamImporter):
    PRIORITY = -5
    NAME = "ASCII_Header"
    AUTOIMPORTER = True
    STARTING_LINES: List[str] = []
    HEADER_ESCAPE: str = r"[#$%]"
    LINE_SPLIT: str = r"[,:;\s\t]"

    def __init__(self, stream: FilepathOrBuffer) -> None:
        super().__init__(stream)
        self._comment = ""
        self.prefix: Optional[str] = None
        self.header_line: Optional[int] = None

    def read(self) -> DataContainer:
        self._read_header()
        if self.header_line is None:
            self.prefix = f"{Path(self._stream.name).stem}_"
        try:
            log.debug(f"type of header: {type(self._header)}")
            return DataContainer(
                pd.read_csv(
                    self._stream,
                    sep=None,
                    engine="python",
                    prefix=self.prefix,
                    index_col=0,
                    comment="#",
                    header=self.header_line,
                ),
                header=self._header,
            )
        except Exception as e:
            raise UnknownFileType from e

    def _read_header(self) -> None:

        line = "True"
        while line:
            line_start_position = self._stream.tell()
            line = self._stream.readline()
            log.debug(rf"line:{repr(line)}")
            match: Optional[Match[str]] = re.match(
                rf"^{self.HEADER_ESCAPE}{{2}}\s*", line
            )
            if match:
                self._comment += line[match.end() :]
                continue
            match = re.match(rf"^{self.HEADER_ESCAPE}\s*", line)
            if match:
                keyword, value = re.split(
                    self.LINE_SPLIT, line[match.end() :], maxsplit=1
                )
                self._header[keyword] = value.strip()
                continue
            if not re.match(r"[-+]*\d+", line):
                self.header_line = 0
            break
        if self._comment and self._header:
            self._header["comment"] = self._comment.strip()
        log.info("line start cursor position: %s", line_start_position)
        self._stream.seek(line_start_position)
