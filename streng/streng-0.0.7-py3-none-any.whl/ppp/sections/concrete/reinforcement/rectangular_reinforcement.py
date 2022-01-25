from dataclasses import dataclass
from . import areas
from .combos import LongReinforcementLayer, TransReinforcementLayer

from streng.common.io import results_display_older


@dataclass
class RectangularSectionReinforcement:
    long1: LongReinforcementLayer
    long2: LongReinforcementLayer
    longV: LongReinforcementLayer
    disdia: LongReinforcementLayer
    trans: TransReinforcementLayer
    cnom: float
    side_hoop_legs: int = 0  # Πρόσθετα σκέλη συνδετήρα στη 2ουσα παρειά. Πχ Αν είναι 0 είναι 2τμητοι, αν είναι 2 είναι 4τμητοι

    @property
    def d1(self):
        return self.cnom + self.trans.dia + 0.5 * self.long1.dia_max

    @property
    def d2(self):
        return self.cnom + self.trans.dia + 0.5 * self.long2.dia_max

    @property
    def Astot(self):
        return self.long1.As + self.long2.As + self.longV.As


