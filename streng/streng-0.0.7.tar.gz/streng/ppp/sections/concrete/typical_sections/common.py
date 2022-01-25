from dataclasses import dataclass
from streng.common.io.output import OutputTable, OutputString


@dataclass
class SectionMaterials:
    fc: float
    Ec: float
    fy: float
    fyw: float
    Es: float

    @property
    def to_OutputTable(self):
        data = []
        data.append({'quantity': 'fc', 'value': self.fc})
        data.append({'quantity': 'Ec', 'value': self.Ec})
        data.append({'quantity': 'fy', 'value': self.fy})
        data.append({'quantity': 'fyw', 'value': self.fyw})
        data.append({'quantity': 'Es', 'value': self.Es})
        return OutputTable(data=data)


@dataclass
class ReinforcementRatios:
    ρ1: float
    ρ2: float
    ρv: float
    ρd: float
    ρtot: float
    ρw: float
    ω1: float
    ω2: float
    ωv: float
    ωd: float
    ωtot: float

    @property
    def to_string(self):
        data = []
        data.append(f'Ποσοστό του εφελκυόμενου οπλισμού: ρ = {self.ρ1:.5f} = {1000*self.ρ1:.2f}‰')
        data.append(f'Μηχανικό ποσοστό του εφελκυόμενου οπλισμού: ω = {self.ω1:.3f}')
        data.append(f'Ποσοστό του θλιβόμενου οπλισμού: ρ` = ρ2 = {self.ρ2:.5f} = {1000*self.ρ2:.2f}‰')
        data.append(f'Μηχανικό ποσοστό του θλιβόμενου οπλισμού: ω` = ω2 = {self.ω2:.3f}')
        data.append(f'Ποσοστό του ενδιάμεσου οπλισμού: ρv = {self.ρv:.5f} = {1000*self.ρv:.2f}‰')
        data.append(f'Μηχανικό ποσοστό του ενδιάμεσου οπλισμού: ωv = {self.ωv:.3f}')
        data.append(f'Συνολικό ποσοστό του διαμήκους οπλισμού: ρtot = {self.ρtot:.5f} = {1000*self.ρtot:.2f}‰')
        data.append(f'Συνολικό μηχανικό ποσοστό του διαμήκους οπλισμού: ωtot = {self.ωtot:.3f}')
        data.append(f'Ποσοστό του δισδιαγώνιου οπλισμού: ρd = {self.ρd:.5f} = {1000*self.ρd:.2f}‰')
        data.append(f'Μηχανικό ποσοστό του δισδιαγώνιου οπλισμού: ωd = {self.ωd:.3f}')
        data.append(f'Ποσοστό του εγκάρσιου οπλισμού (σχέση ΚΑΝ.ΕΠΕ.): ρs = {self.ρw:.5f} = {1000*self.ρw:.2f}‰')
        return OutputString(data=data)

    @property
    def to_OutputTable(self):
        data = []
        data.append({'quantity': 'ρ1', 'value': self.ρ1, 'notes': 'Ποσοστό του εφελκυόμενου οπλισμού'})
        data.append({'quantity': 'ρ2', 'value': self.ρ2, 'notes': 'Ποσοστό του θλιβόμενου οπλισμού'})
        data.append({'quantity': 'ρv', 'value': self.ρv, 'notes': 'Ποσοστό του ενδιάμεσου οπλισμού'})
        data.append({'quantity': 'ρtot', 'value': self.ρtot, 'notes': 'Συνολικό ποσοστό του διαμήκους οπλισμού'})
        data.append({'quantity': 'ρd', 'value': self.ρd, 'notes': 'Ποσοστό του δισδιαγώνιου οπλισμού'})
        data.append({'quantity': 'ω1', 'value': self.ω1, 'notes': 'Μηχανικό ποσοστό του εφελκυόμενου οπλισμού'})
        data.append({'quantity': 'ω2', 'value': self.ω2, 'notes': 'Μηχανικό ποσοστό του θλιβόμενου οπλισμού'})
        data.append({'quantity': 'ωv', 'value': self.ωv, 'notes': 'Μηχανικό ποσοστό του ενδιάμεσου οπλισμού'})
        data.append({'quantity': 'ωtot', 'value': self.ωtot, 'notes': 'Συνολικό μηχανικό ποσοστό του διαμήκους οπλισμού'})
        data.append({'quantity': 'ωd', 'value': self.ωd, 'notes': 'Μηχανικό ποσοστό του δισδιαγώνιου οπλισμού'})
        data.append({'quantity': 'ρw', 'value': self.ρw, 'notes': 'Ποσοστό του εγκάρσιου οπλισμού'})
        return OutputTable(data=data)