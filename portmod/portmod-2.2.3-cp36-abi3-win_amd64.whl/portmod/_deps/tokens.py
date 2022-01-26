# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

from typing import Any, List, NamedTuple, TypeVar, Union

from portmodlib.atom import Atom, FQAtom
from portmodlib.usestr import parse_usestr

_T = TypeVar("_T", bound="Token")


class Token(NamedTuple):
    """A formula token"""

    value: str
    polarity: bool = True

    def __str__(self) -> str:
        if self.polarity:
            return self.value
        else:
            return "-" + self.value

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Token):
            # Note: order is important to avoid unnecessary string comparisions
            return self.polarity == other.polarity and self.value == other.value
        return False

    def neg(self: _T) -> _T:
        return self.__class__(self.value, not self.polarity)


class AtomToken(Token):
    """Token descirbing a package"""

    value: FQAtom


class FlagToken(Token):
    """Token describing a use flag dependency on a package"""

    value: FQAtom

    def __str__(self) -> str:
        if self.polarity:
            return list(self.value.USE)[0]
        else:
            return "-" + list(self.value.USE)[0]


class VariableToken(Token):
    """Token for a variable which exists only in the context of the formula"""


def token_conflicts(token1: Token, token2: Token) -> bool:
    """
    Returns true if and only if two tokens, which use minus-format (e.g. -foo)
    to indicate a disabled token, conflict. E.g. foo and -foo
    """
    return token1.value == token2.value and token1.polarity != token2.polarity


def expand_use_conditionals(tokens: List[str]) -> List[Union[str, List]]:
    """Expands any conditional use dependencies in the token tree"""
    result = []
    for token in tokens:
        if isinstance(token, list):
            result.append(expand_use_conditionals(token))
        elif isinstance(token, Atom) and token.USE:
            for flag in token.USE:
                stripped = token.strip_use()
                sflag = flag.rstrip("?=").lstrip("!")
                if flag.endswith("?") and not flag.startswith("!"):
                    result += parse_usestr(
                        f"{sflag}? ( {stripped}[{sflag}] ) !{sflag}? ( {stripped} )",
                        Atom,
                    )
                elif flag.endswith("?") and flag.startswith("!"):
                    result += parse_usestr(
                        f"{sflag}? ( {stripped} ) !{sflag}? ( {stripped}[-{sflag}] )",
                        Atom,
                    )
                elif flag.endswith("=") and not flag.startswith("!"):
                    result += parse_usestr(
                        f"{sflag}? ( {stripped}[{sflag}] ) !{sflag}? ( {stripped}[-{sflag}] )",
                        Atom,
                    )
                elif flag.endswith("=") and flag.startswith("!"):
                    result += parse_usestr(
                        f"{sflag}? ( {stripped}[-{sflag}] ) !{sflag}? ( {stripped}[{sflag}] )",
                        Atom,
                    )
                else:
                    result.append(Atom(stripped + f"[{flag}]"))
        else:
            result.append(token)
    return result
