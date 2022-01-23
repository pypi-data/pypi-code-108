from dataclasses import dataclass
from enum import Enum, auto

# Enumerations for various grammatical features:

# https://docs.python.org/3/library/enum.html#using-automatic-values
class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class Mutation(AutoName):
    Nil = auto()
    Len1 = auto()
    Len2 = auto()
    Len3 = auto()
    Ecl1 = auto()
    Ecl1x = auto()
    Ecl2 = auto()
    Ecl3 = auto()
    PrefT = auto()
    PrefH = auto()
    Len1D = auto()
    Len2D = auto()
    Len3D = auto()


class Strength(AutoName):
    Strong = auto()
    Weak = auto()


class Number(AutoName):
    Sg = auto()
    Pl = auto()


class Gender(AutoName):
    Masc = auto()
    Fem = auto()


# Encapsulates a word form, a phrase form or a clause form:
@dataclass
class Form:
    value: str


# Class for noun and noun phrase forms in the singular:
@dataclass
class FormSg(Form):
    gender: Gender


# Class for noun forms in the plural genitive:
@dataclass
class FormPlGen(Form):
    strength: Strength
    # in the plural genitive, a noun form has strength.
