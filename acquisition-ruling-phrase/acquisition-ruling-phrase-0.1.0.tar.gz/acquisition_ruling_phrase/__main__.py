from typing import Callable, Optional

from bs4 import BeautifulSoup

from .cues import ruling_cue
from .dispositive.phrases import Phrase
from .tags import (
    center_next_string,
    center_next_tag,
    p_space_strong,
    p_strong,
    proper_words,
)


def recipe(func: Callable, raw: str) -> Optional[str]:
    """Sanitize and use specific function"""
    soup = BeautifulSoup(raw, "html5lib")
    results = soup(func)
    if not results:
        return None
    return str(results[-1])  # the last one has the least tags


def fetch(text: str) -> Optional[str]:
    """Attempt either (1) tagged phrase via recipe; or (2) textual cues"""
    return (
        recipe(center_next_tag, text)
        or recipe(center_next_string, text)
        or recipe(p_strong, text)
        or recipe(p_space_strong, text)
        or recipe(proper_words, text)
        or ruling_cue(text)
    )


def wherefore_clause(context: str) -> Optional[str]:
    return Phrase("WHEREFORE", context).get_clause or None


def ordered_clause(context: str) -> Optional[str]:
    return Phrase("ORDERED", context).get_clause or None
