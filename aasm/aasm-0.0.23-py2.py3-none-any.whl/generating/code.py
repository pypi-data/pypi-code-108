from __future__ import annotations

from typing import List


class Code:
    def __init__(self, agent_code_lines: List[str], graph_code_lines: List[str]):
        self.agent_code_lines: List[str] = agent_code_lines
        self.graph_code_lines: List[str] = graph_code_lines
        self._iter_code_lines: List[str] | None = None
        self._iter_idx: int | None = None
        self._iter_num_code_lines: int | None = None

    def __iter__(self) -> Code:
        self._iter_code_lines = self.agent_code_lines + ["\n"] + self.graph_code_lines
        self._iter_num_code_lines = len(self._iter_code_lines)
        self._iter_idx = -1
        return self

    def __next__(self):
        self._iter_idx += 1
        if self._iter_idx < self._iter_num_code_lines:
            return self._iter_code_lines[self._iter_idx]
        raise StopIteration
