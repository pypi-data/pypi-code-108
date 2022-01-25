from typing import List, Optional
import re

import attrs
from attrs import frozen
import cattrs
from ftfy import fix_text


@frozen(slots=False)
class Card:
    # fields from mtgjson
    name: Optional[str] = attrs.field(default=None)
    mana_cost: Optional[str] = attrs.field(default=None, metadata={"alias": "manaCost"})
    mana_value: Optional[int] = attrs.field(
        default=None, metadata={"alias": "manaValue"}
    )
    types: Optional[List[str]] = attrs.field(default=None)
    printing: Optional[str] = attrs.field(default=None)
    rarity: Optional[str] = attrs.field(default=None)
    text: Optional[str] = attrs.field(default=None)
    power: Optional[str] = attrs.field(default=None)  # needs to be str because of `*`
    toughness: Optional[str] = attrs.field(
        default=None
    )  # needs to be str because of `*`

    def __str__(self):
        """Canonical string representation of a card:

        field1_name: field1_value | field2_name: field2_value | ..."""
        fields = []
        for f in attrs.fields(Card):
            if f.repr:
                value = getattr(self, f.name)
                if isinstance(value, list):
                    value = " ".join(value)
                if value:
                    fields.append((f.name, value))
        return fix_text(
            re.sub(r"\s+|_+", " ", " | ".join(f"{k}: {v}" for k, v in fields))
        )


@frozen(slots=False)
class CardStats:
    # fields from 17lands
    name: Optional[str] = attrs.field(default=None)
    stats_format: Optional[str] = attrs.field(default=None)
    stats_colors: Optional[str] = attrs.field(default=None)
    seen_count: Optional[int] = attrs.field(default=None)
    avg_seen: Optional[float] = attrs.field(default=None)
    avg_pick: Optional[float] = attrs.field(default=None)
    pick_count: Optional[int] = attrs.field(default=None)
    game_count: Optional[int] = attrs.field(default=None)
    win_rate: Optional[float] = attrs.field(default=None)
    sideboard_game_count: Optional[int] = attrs.field(default=None)
    sideboard_win_rate: Optional[float] = attrs.field(default=None)
    drawn_game_count: Optional[int] = attrs.field(default=None)
    drawn_win_rate: Optional[float] = attrs.field(default=None)
    ever_drawn_game_count: Optional[int] = attrs.field(default=None)
    drawn_game_count: Optional[int] = attrs.field(default=None)
    drawn_win_rate: Optional[float] = attrs.field(default=None)
    ever_drawn_game_count: Optional[int] = attrs.field(default=None)
    ever_drawn_win_rate: Optional[float] = attrs.field(default=None)
    never_drawn_game_count: Optional[int] = attrs.field(default=None)
    never_drawn_win_rate: Optional[float] = attrs.field(default=None)
    drawn_improvement_win_rate: Optional[float] = attrs.field(default=None)


@frozen(slots=False)
class CardWithStats(Card, CardStats):
    pass
