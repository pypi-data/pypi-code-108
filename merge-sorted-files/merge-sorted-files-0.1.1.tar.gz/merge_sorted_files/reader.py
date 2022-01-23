from __future__ import annotations

from typing import TextIO
import logging

class IntReader:
    def __init__(self, fp: TextIO):
        self.fp = fp

    def __iter__(self) -> IntReader:
        return self

    def __next__(self):
        while True:
            line = self.fp.readline()
            if not line:
                self.fp.close()
                raise StopIteration

            try:
                return int(line.rstrip("\n\r"))
            except ValueError:
                logging.error(f"Non-int line ignored: {line}")

        
