from dataclasses import dataclass
from enum import Enum
from typing import List, Dict


class ArgumentLabel(Enum):
    C_B = "C-B"
    C_I = "C-I"
    MC_B = "MC-B"
    MC_I = "MC-I"
    P_B = "P-B"
    P_I = "P-I"
    MP_B = "MP-B"
    MP_I = "MP-I"
    O = "O"  # noqa: E741
    B_B = "B-B"
    B_I = "B-I"
    X = "-X-"


@dataclass
class ArgumentTag:
    label: ArgumentLabel
    probability: float
    token: str


ArgumentSentence = List[ArgumentTag]

ArgumentSentences = List[ArgumentSentence]

ArgumentModelSentences = Dict[str, ArgumentSentence]
