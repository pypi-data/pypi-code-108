"""Contains all of magodo's default MagicTodo spell functions."""

from __future__ import annotations

from typing import Callable, Iterable, List, MutableSequence

from eris import ErisError, Err, Ok, Result

from ._shared import (
    CONTEXT_PREFIX,
    DEFAULT_PRIORITY,
    PROJECT_PREFIX,
    PUNCTUATION,
    TODO_PREFIXES,
    is_any_prefix_tag,
    is_any_tag,
    is_metadata_tag,
)
from .types import T, TodoSpell


def register_spell_factory(
    mut_spell_registry: MutableSequence[TodoSpell],
) -> Callable[[TodoSpell], TodoSpell]:
    """Factory for decorators used to register spell functions."""

    def register_spell(spell: TodoSpell) -> TodoSpell:
        mut_spell_registry.append(spell)
        return spell

    return register_spell


ALL_SPELLS: List[TodoSpell] = []
all_spells = register_spell_factory(ALL_SPELLS)


@all_spells
def handle_prefix(todo: T) -> Result[T, ErisError]:
    """Handles / validatees a magic todo's prefix.."""
    if todo.priority == DEFAULT_PRIORITY and not todo.desc.startswith(
        TODO_PREFIXES
    ):
        return Err(
            "Magic todos must satisfy one of; (1) Have a non-default"
            " (i.e. not 'O') priority set (2) Have been marked complete"
            " with an 'x' prefix (3) Have been marked open with an 'o'"
            f" prefix. todo={todo!r}"
        )

    if todo.desc.startswith("o "):
        return Ok(todo.new(desc=todo.desc[2:]))

    return Ok(todo)


@all_spells
def x_tag(todo: T) -> Result[T, ErisError]:
    """Handles tags of the form x:1234 where 1234 is the current time."""
    if todo.metadata is None or "x" not in todo.metadata:
        return Ok(todo)

    dtime = todo.metadata["x"]
    desc = " ".join(todo.desc.split(" ")[1:]) + f" dtime:{dtime}"

    new_todo = todo.new(desc=desc, done=True)
    line = new_todo.to_line()
    return type(todo).from_line(line)


@all_spells
def group_tags(todo: T) -> Result[T, ErisError]:
    """Groups all @ctxs, +projs, and meta:data at the end of the line."""
    if not (todo.contexts or todo.projects or todo.metadata):
        return Ok(todo)

    all_words = [w for w in todo.desc.split(" ") if w != "|"]
    new_words = []
    regular_words_found = False
    for i, word in enumerate(all_words[:]):
        all_prev_words_are_tags = _all_words_are_tags(all_words[:i])
        all_next_words_are_tags = _all_words_are_tags(all_words[i + 1 :])
        is_edge_tag = all_next_words_are_tags or all_prev_words_are_tags

        if is_metadata_tag(word) and word[-1] in PUNCTUATION:
            return Ok(todo)

        if is_any_prefix_tag(word) and (
            word[-1] in PUNCTUATION or not all_next_words_are_tags
        ):
            if regular_words_found:
                new_words.append(word[1:])
            continue

        if is_any_prefix_tag(word) and is_edge_tag:
            continue

        if is_metadata_tag(word):
            continue

        regular_words_found = True
        new_words.append(word)

    if not regular_words_found:
        return Ok(todo)

    desc = " ".join(new_words).strip()
    desc += " |"

    if todo.contexts:
        desc += " " + " ".join(
            CONTEXT_PREFIX + ctx for ctx in sorted(todo.contexts)
        )

    if todo.projects:
        desc += " " + " ".join(
            PROJECT_PREFIX + ctx for ctx in sorted(todo.projects)
        )

    if todo.metadata:
        desc += " " + " ".join(
            f"{k}:{v}" for (k, v) in sorted(todo.metadata.items())
        )

    return Ok(todo.new(desc=desc))


def _all_words_are_tags(words: Iterable[str]) -> bool:
    """Returns True if all `words` are special words."""
    return all(is_any_tag(w) for w in words)
