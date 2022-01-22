"""A module for handling the information the player receives each round."""

from dataclasses import dataclass, field

@dataclass
class Hint:
    """A summary of the information the player receives each round."""

    correct: dict[str, set[int]] = field(default_factory=dict)
    inverse_correct: dict[int, str] = field(default_factory=dict, init=False)

    misplaced: dict[str, set[int]] = field(default_factory=dict)
    inverse_misplaced: dict[int, set[str]] = field(default_factory=dict, init=False)

    absent: set[str] = field(default_factory=set)

    def __post_init__(self):
        """Initialize inverse mappings."""
        for letter, indices in self.correct.items():
            for index in indices:
                self.inverse_correct[index] = letter

        for letter, indices in self.misplaced.items():
            for index in indices:
                self.inverse_misplaced.setdefault(index, set()).add(letter)
