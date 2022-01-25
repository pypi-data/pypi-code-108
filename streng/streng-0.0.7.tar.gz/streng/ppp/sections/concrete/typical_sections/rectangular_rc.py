from dataclasses import dataclass
from streng.ppp.sections.geometry.rectangular import RectangularSectionGeometry
from streng.ppp.sections.concrete.reinforcement import rectangular_reinforcement
from streng.ppp.sections.concrete.reinforcement import ratios as reinf_ratios
from .common import SectionMaterials, ReinforcementRatios


@dataclass
class RectangularConcreteSection(RectangularSectionGeometry):
    reinforcement: rectangular_reinforcement.RectangularSectionReinforcement
    materials: SectionMaterials

    def __post_init__(self):
        # super(RectangularConcreteSection, self).__post_init__()
        self.calc()


    def calc(self):
        # super(RectangularConcreteSection, self).calc()
        self.d = self.h - self.reinforcement.d1
        self.ratios = ReinforcementRatios(
              ρ1=reinf_ratios.ρ(self.reinforcement.long1.As, self.b, self.d),
              ρ2=reinf_ratios.ρ(self.reinforcement.long2.As, self.b, self.d),
              ρv=reinf_ratios.ρ(self.reinforcement.longV.As, self.b, self.d),
              ρd=reinf_ratios.ρ(self.reinforcement.disdia.As, self.b, self.d),
              ρtot=reinf_ratios.ρ(self.reinforcement.Astot, self.b, self.d),
              ρw=reinf_ratios.ρw(self.reinforcement.trans.n, self.reinforcement.trans.dia, self.b, self.reinforcement.trans.s),
              ω1=reinf_ratios.ω(self.reinforcement.long1.As, self.b, self.d, self.materials.fy, self.materials.fc),
              ω2=reinf_ratios.ω(self.reinforcement.long2.As, self.b, self.d, self.materials.fy, self.materials.fc),
              ωv=reinf_ratios.ω(self.reinforcement.longV.As, self.b, self.d, self.materials.fy, self.materials.fc),
              ωd=reinf_ratios.ω(self.reinforcement.disdia.As, self.b, self.d, self.materials.fy, self.materials.fc),
              ωtot=reinf_ratios.ω(self.reinforcement.Astot, self.b, self.d, self.materials.fy, self.materials.fc))
