from __future__ import annotations

from typing import List


class PythonCode:
    def __init__(self, indent_size: int):
        self.indent_size = indent_size
        self.indent: int = 0
        self.code_lines: List[str] = []

    def indent_left(self) -> None:
        self.indent -= self.indent_size
        
    def indent_right(self) -> None:
        self.indent += self.indent_size
        
    def add_line(self, line: str) -> None:
        self.code_lines.append(self.indent * ' ' + line + '\n')
        
    def add_newline(self) -> None:
        self.add_line('')
        
    def add_newlines(self, count: int) -> None:
        for _ in range(count):
            self.add_newline()
