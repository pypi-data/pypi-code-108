"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import os
from abc import ABCMeta
from typing import Any
from pathlib import Path
from weakref import ProxyType, proxy

# * Third Party Imports --------------------------------------------------------------------------------->
import pyparsing as pp

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class Token:

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(" + ', '.join(f"{k}={v!r}" for k, v in vars(self).items()) + ')'


class IniToken(Token, metaclass=ABCMeta):
    spec_data = None

    def add_comment(self, comment: "Comment") -> None:
        self.comments.append(comment.content)


class Comment(Token):
    def __init__(self, content: str) -> None:
        self.content = content.strip()
        self.comment_indicator: str = '#'

    def __str__(self) -> str:
        return self.content

    def as_text(self) -> str:
        return f"{self.comment_indicator} {self}"


class Section(IniToken):

    def __init__(self, name: str) -> None:
        self.name = name
        self.comments = []
        self.entries = {}

    def add_entry(self, entry: "Entry") -> None:
        entry.section = proxy(self)
        self.entries[entry.key] = entry

    def remove_entry(self, entry_key: str) -> None:
        del self.entries[entry_key]

    def __getitem__(self, key: str) -> "Entry":
        return self.entries[key]

    def get(self, key, default=None) -> Any:
        try:
            return self[key].get_value()
        except KeyError:
            return default

    def __len__(self) -> int:
        return len(self.entries)

    def as_dict(self) -> dict[str, dict[str, str]]:
        data = {self.name: {}}
        for entry in self.entries.values():
            data[self.name] |= entry.as_dict()
        return data

    def as_text(self,
                section_header_newlines: int = 1,
                extra_section_newlines: int = 2,
                extra_entry_newlines: int = 0) -> str:
        lines = []
        lines += [comment.as_text() for comment in self.comments]
        lines.append(f"[{self.name}]")
        lines += ['' for i in range(section_header_newlines)]
        lines += [entry.as_text(extra_entry_newlines=extra_entry_newlines) for entry in self.entries.values()]
        lines += ['' for i in range(extra_section_newlines)]
        return '\n'.join(lines)


class EnvSection(Section):
    # pylint: disable=super-init-not-called
    def __init__(self) -> None:
        self.name = "ENV"
        self.comments = None

    @property
    def entries(self) -> dict[str, "Entry"]:
        return {key: Entry(key, value) for key, value in os.environ.items()}


class Entry(IniToken):

    def __init__(self, key: str, value: str = None) -> None:
        self.key = key.strip()
        self.value = value.lstrip() if value is not None else value
        self.key_value_separator = '='
        self.comments = []
        self.section: ProxyType[Section] = None

    def as_dict(self) -> dict[str, str]:
        return {self.key: self.value}

    def as_text(self, extra_entry_newlines: int = 0) -> str:
        lines = [comment.as_text() for comment in self.comments]
        text_value = "" if self.value is None else self.value
        lines.append(f"{self.key} {self.key_value_separator} {text_value}")
        lines += ['' for i in range(extra_entry_newlines)]
        return '\n'.join(lines)


class TokenFactory:

    def __init__(self, token_map: dict[str, type] = None) -> None:
        self.token_map = {'comment': Comment,
                          'section_name': Section,
                          'entry': Entry}
        if token_map is not None:
            self.token_map |= token_map

    def parse_action(self, tokens: pp.ParseResults) -> Token:
        name = tokens.get_name()
        token_class = self.token_map[name]
        return token_class(*tokens)


# region[Main_Exec]

if __name__ == '__main__':
    pass
# endregion[Main_Exec]
