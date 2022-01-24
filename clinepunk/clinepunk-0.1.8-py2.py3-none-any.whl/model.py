from dataclasses import dataclass, field
from typing import List


@dataclass(order=True)
class Word:
    length: int = field(compare=True)
    word: str


@dataclass
class WordCollection:
    words: List[Word] = field(default_factory=list)
