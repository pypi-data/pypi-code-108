import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sympy.solvers import solve
from sympy import Symbol
from dataclasses import dataclass, field
from typing import List
from streng.ppp.sections.concrete.typical_sections.rectangular_rc import RectangularConcreteSection
from streng.codes.greek.kanepe.raw.ch7.rotation import θycalc, θum, αcalc
from streng.codes.greek.kanepe.raw.ch7a.yield_point import ξycalc, Mycalc, ABξφ_conc, ABξφ_steel
from streng.codes.greek.kanepe.raw.ch7c.shear import VRcalc, Vwcalc, VRccalc

from streng.common.io.output import OutputTable, OutputExtended

@dataclass
class RectangularKanepe:
    rcs: RectangularConcreteSection
    Ls: float
    N: float
    bi: List[float] = field(default_factory=list)

    calc_on_init: bool = field(repr=False, default=True)

    results: OutputExtended = field(init=False, repr=False, default_factory=OutputExtended)

    θy: float = field(init=False, repr=False)
    θu_ini: float = field(init=False, repr=False)
    θu: float = field(init=False, repr=False)
    My: float = field(init=False, repr=False)


    results_Mtheta: pd.DataFrame = field(init=False, repr=False)
    figures: List[object] = field(init=False, repr=False, default_factory=list)



    def __post_init__(self):
        if self.calc_on_init == True:
            self.calculate()

    def calculate(self):
        N = self.N

        Ec = self.rcs.materials.Ec
        Es = self.rcs.materials.Es
        fc = self.rcs.materials.fc
        fy = self.rcs.materials.fy
        fyw = self.rcs.materials.fyw
        self.results.outputTables['materials'] = self.rcs.materials.to_OutputTable

        b = self.rcs.b
        h = self.rcs.h

        Ls = self.Ls
        αs = Ls / h

        _out_section_data = []
        _out_section_data.append({'quantity': 'b', 'value': b, 'note': 'm'})
        _out_section_data.append({'quantity': 'h', 'value': h, 'note': 'm'})
        _out_section_data.append({'quantity': 'Ls', 'value': Ls, 'note': 'm (Μήκος διάτμησης)'})
        _out_section_data.append({'quantity': 'αs', 'value': αs, 'note': '(Λόγος διάτμησης)'})


        d1 = self.rcs.reinforcement.d1
        d2 = self.rcs.reinforcement.d2
        d = h - d1
        δ2 = d2 / d
        z = d - d2
        cnom = self.rcs.reinforcement.cnom
        Φw = self.rcs.reinforcement.trans.dia

        ΦL = self.rcs.reinforcement.long1.dia_max

        s = self.rcs.reinforcement.trans.s

        n_b = self.rcs.reinforcement.trans.n               # αριθμός σκελών συνδετήρα κύριας (b) παρειάς
        n_h = self.rcs.reinforcement.side_hoop_legs + 2    # αριθμός σκελών συνδετήρα 2ουσας (h) παρειάς

        _out_section_data.append({'quantity': 'd1', 'value': d1, 'note': 'm'})
        _out_section_data.append({'quantity': 'd2', 'value': d2, 'note': 'm (ή d`)'})
        _out_section_data.append({'quantity': 'd', 'value': d, 'note': 'm'})
        _out_section_data.append({'quantity': 'δ`', 'value': δ2, 'note': '(ή δ2)'})
        _out_section_data.append({'quantity': 'z', 'value': z, 'note': 'm'})
        _out_section_data.append({'quantity': 'cnom', 'value': cnom, 'note': 'm'})
        _out_section_data.append({'quantity': 'Φw', 'value': Φw, 'note': 'm'})
        _out_section_data.append({'quantity': 'ΦL', 'value': ΦL, 'note': 'm'})
        _out_section_data.append({'quantity': 's', 'value': s, 'note': 'm'})


        As = self.rcs.reinforcement.long1.As
        As2 = self.rcs.reinforcement.long2.As
        Asv = self.rcs.reinforcement.longV.As
        Asd = self.rcs.reinforcement.disdia.As
        Asw = self.rcs.reinforcement.trans.As
        Astot = self.rcs.reinforcement.Astot

        _out_section_data.append({'quantity': 'As', 'value': As, 'note': 'm2 Εμβαδό του εφελκυόμενου οπλισμού'})
        _out_section_data.append({'quantity': 'As2', 'value': As2, 'note': 'm2 Εμβαδό του θλιβόμενου οπλισμού'})
        _out_section_data.append({'quantity': 'Asv', 'value': Asv, 'note': 'm2 Εμβαδό του ενδιάμεσου οπλισμού'})
        _out_section_data.append({'quantity': 'Asd', 'value': Asd, 'note': 'm2 Εμβαδό του δισδιαγώνιου οπλισμού'})
        _out_section_data.append({'quantity': 'Asw', 'value': Asw, 'note': 'm2 Εμβαδό του εγκάρσιου οπλισμού'})
        _out_section_data.append({'quantity': 'Astot', 'value': Astot, 'note': 'm2 Συνολικό εμβαδό του διαμήκους οπλισμού, Astot'})


        self.results.outputTables['section'] = OutputTable(data=_out_section_data)

        ρ = self.rcs.ratios.ρ1
        ω = self.rcs.ratios.ω1
        ρ2 = self.rcs.ratios.ρ2
        ω2 = self.rcs.ratios.ω2
        ρv = self.rcs.ratios.ρv
        ωv = self.rcs.ratios.ωv
        ρtot = self.rcs.ratios.ρtot
        ωtot = self.rcs.ratios.ωtot
        ρd = self.rcs.ratios.ρd
        ωd = self.rcs.ratios.ωd
        ρs = self.rcs.ratios.ρw


        self.results.outputTables['ratios'] = self.rcs.ratios.to_OutputTable

        _out_yield_data = []

        α = Es / Ec
        _out_yield_data.append({'quantity': 'α', 'value': α})

        A_steel, B_steel, ξy_steel, φy_steel = ABξφ_steel(ρ, ρ2, ρv, N, b, d, δ2, fy, α, Es)
        _out_yield_data.append({'quantity': 'A_steel', 'value': A_steel})
        _out_yield_data.append({'quantity': 'B_steel', 'value': B_steel})
        _out_yield_data.append({'quantity': 'ξy_steel', 'value': ξy_steel})
        _out_yield_data.append({'quantity': 'φy_steel', 'value': φy_steel, 'note': 'm-1'})

        A_conc, B_conc, ξy_conc, φy_conc = ABξφ_conc(ρ, ρ2, ρv, N, b, d, δ2, α, Ec, fc)
        _out_yield_data.append({'quantity': 'A_conc', 'value': A_conc})
        _out_yield_data.append({'quantity': 'B_conc', 'value': B_conc})
        _out_yield_data.append({'quantity': 'ξy_conc', 'value': ξy_conc})
        _out_yield_data.append({'quantity': 'φy_conc', 'value': φy_conc, 'note': 'm-1'})

        if φy_steel < φy_conc:
            ξy = ξy_steel
            φy = φy_steel
            verdict = 'χάλυβα'
        else:
            ξy = ξy_conc
            φy = φy_conc
            verdict = 'μη-γραμμικότητας των παραμορφώσεων του θλιβόµενου σκυροδέματος'

        My = Mycalc(b, d, φy, Ec, ξy, δ2, ρ, ρ2, ρv, Es)

        xy = ξy * d

        _out_yield_data.append({'quantity': f'Διαρροή λόγω', 'value': None, 'note': verdict})
        _out_yield_data.append({'quantity': 'ξy', 'value': ξy})
        _out_yield_data.append({'quantity': 'xy', 'value': xy, 'note': 'm (Το ύψος της θλιβόμενης ζώνης στη διαρροή)'})
        _out_yield_data.append({'quantity': 'φy', 'value': φy, 'note': 'm-1'})
        _out_yield_data.append({'quantity': 'My', 'value': My, 'note': 'kNm'})


        VRc = VRccalc(ρtot, b, d, fc / 1000, N, b * h)

        VMu = My / Ls
        if VRc < VMu:
            αv = 1.
        else:
            αv = 0.

        θy = θycalc(φy, Ls, αv, z, h, ΦL, fy/1000., fc/1000.)

        _out_yield_data.append({'quantity': 'VRc', 'value': VRc, 'note': 'kN'})
        _out_yield_data.append({'quantity': 'αv', 'value': αv})
        _out_yield_data.append({'quantity': 'VMu', 'value': VMu, 'note': 'kN'})
        _out_yield_data.append({'quantity': 'θy', 'value': θy})

        self.results.outputTables['yield'] = OutputTable(data=_out_yield_data)


        _out_ultimate_point_data = []

        ν = N / (b*h*fc)
        _out_ultimate_point_data.append({'quantity': 'ν', 'value': ν})

        bo = b - 2 * (cnom + 0.5*Φw)
        ho = h - 2 * (cnom + 0.5*Φw)
        _out_ultimate_point_data.append({'quantity': 'bo', 'value': bo})
        _out_ultimate_point_data.append({'quantity': 'ho', 'value': ho})

        if ho/bo > 2.0:
            _out_ultimate_point_data.append({'quantity': 'hο/bο', 'value': ho / bo,
                                             'note': 'hο/bο>2.0 Χρησιμοποιείται, ως ho, το ύψος της θλιβόµενης ζώνης εντός του περισφιγμένου πυρήνα'})
            ho = xy - (cnom + 0.5*Φw)
            _out_ultimate_point_data.append({'quantity': 'ho', 'value': ho, 'note': 'Τελική τιμή'})


        if len(self.bi) == 0.0:
            # self.bi = np.array([bo, ho, bo, ho])  # Για 2τμητους συνδετήρες

            spaces_b = int(round(n_b - 1, 0))
            spaces_h = int(round(n_h - 1, 0))
            space_length_b = bo / spaces_b
            space_length_h = ho / spaces_h
            bi = []
            for i in range(2 * spaces_h): bi.append(space_length_h)
            for i in range(2 * spaces_b): bi.append(space_length_b)
            self.bi = np.array(bi)


        Σbi2 = sum(self.bi**2)
        απερ = αcalc(s, bo, ho, Σbi2)
        θu_ini = θum(ν, ωtot, ω2, αs, απερ, ρs, ρd, fc / 1000, fyw / 1000)
        μθ_ini = θu_ini / θy

        Vw = Vwcalc(ρs, b, z, fyw)


        _out_ultimate_point_data.append({'quantity': 'Σbi2', 'value': Σbi2, 'note': 'm2'})
        _out_ultimate_point_data.append({'quantity': 'απερ', 'value': απερ, 'note': 'Συντελεστής αποδοτικότητας περίσφιξης'})
        _out_ultimate_point_data.append({'quantity': 'θu_ini', 'value': θu_ini, 'note': 'Αρχική τιμή στροφής αστοχίας (χωρίς τον έλεγχο για τις τέμνουσες)'})
        _out_ultimate_point_data.append({'quantity': 'μθ_ini', 'value': μθ_ini, 'note': 'Αρχική τιμή πλαστιμότητας στροφών (χωρίς τον έλεγχο για τις τέμνουσες)'})
        _out_ultimate_point_data.append({'quantity': 'Vw', 'value': Vw, 'note': 'kN'})


        υ = Symbol('υ')
        μθplsol = float(solve((((h - xy) / (2 * Ls)) * min(N / 1000, 0.55 * b * d * fc / 1000) + (1 - 0.05 * υ) * (
                    0.16 * max(0.5, 100 * ρtot) * (1 - 0.16 * min(5, αs)) * (
                        (fc / 1000) ** 0.5) * b * d + Vw / 1000) * 1000 - My / Ls), υ)[0])
        θsol = θy * (μθplsol + 1)

        _out_ultimate_point_data.append({'quantity': 'μθplsol', 'value': μθplsol, 'note': ''})
        _out_ultimate_point_data.append({'quantity': 'θsol', 'value': θsol, 'note': ''})


        VR0 = VRcalc(h, xy, Ls, N / 1000, b * d, fc / 1000, 0., ρtot, αs, Vw / 1000) * 1000 # yVRs[0]
        My_ini = My
        θy_ini = θy
        if VR0 < My / Ls:
            θu = 1.4 * θy
            θy = θy * VR0 * Ls / My
            My = VR0 * Ls
            _out_ultimate_point_data.append({'quantity': 'Πρόωρη αστοχία', 'note': 'από τέμνουσα πριν τη διαρροή'})

        elif θsol < θu_ini:
            θu = θsol
            _out_ultimate_point_data.append({'quantity': 'Πρόωρη αστοχία','note': 'από τέμνουσα πριν την εξάντληση της θu'})

        else:
            θu = θu_ini

        μθ = θu/θy
        θpl = θu - θy
        _out_ultimate_point_data.append({'quantity': 'θu', 'value': θu, 'note': 'Τελική τιμή'})
        _out_ultimate_point_data.append({'quantity': 'μθ', 'value': μθ, 'note': 'Τελική τιμή'})
        _out_ultimate_point_data.append({'quantity': 'θpl', 'value': θpl, 'note': 'Λαμβάνεται ως θpl = θu - θy'})


        self.results.outputTables['ultimate'] = OutputTable(data=_out_ultimate_point_data)


        self.θy = θy
        self.My_ini = My_ini
        self.θy_ini = θy_ini
        self.θu_ini = θu_ini
        self.My = My
        self.θu = θu
        self.θpl = θpl
        self.Mu = My  # θεωρώ για την ώρα μηδενική κράτυνση



        # da = {'M': [0, My, My, 0.2 * My, 0.2 * My], 'θ': [0, 0, θpl, θpl, 5 * θpl]}
        # self.results_Mtheta = pd.DataFrame(data=da, index=['A', 'B', 'C', 'D', 'E'])
        # print(df.round({'M': 2, 'θ': 4}))


    def get_etabs9_7_2_M3(self, negative = False):
        θy_ini = self.θy_ini
        θu_ini = self.θu_ini
        My = self.My_ini
        Mu = self.My_ini


        if negative == True:
            return(f'TYPE "M3"  -E "-{5.*self.θpl:.4f} -{0.2*self.My:.2f}"  -D "-{1.5*self.θpl:.4f} -{0.2*self.My:.2f}"  -C "-{self.θpl:.4f} -{self.My:.2f}"  -B "0 -{self.My:.2f}"')
        else:
            return (f'TYPE "M3"  B "0 {self.My:.2f}"  C "{self.θpl:.4f} {self.My:.2f}"  D "{1.5*self.θpl:.4f} {0.2*self.My:.2f}"  E "{5.*self.θpl:.4f} {0.2*self.My:.2f}"')

    def print_output_tables(self):
        for key, value in self.results.outputTables.items():
            print(key)
            print(value)
            print('')


    @property
    def figure_initial(self):
        θy_ini = self.θy_ini
        θu_ini = self.θu_ini
        My = self.My_ini
        Mu = self.My_ini

        xMθs = [0., θy_ini, θu_ini]
        yMθs = [0., My, Mu]

        f, ax = plt.subplots(figsize=(8, 5))
        ax.plot(xMθs, yMθs, lw=2)
        ax.axis([0, 1.2 * θu_ini, 0, 1.2 * Mu])
        ax.set_title('Αρχικό διάγραμμα Μ-θ (χωρίς τον έλεγχο για τις τέμνουσες)')
        ax.set_ylabel('M (kN)')
        ax.set_xlabel('θ')
        fig = (f, ax)

        return fig


    @property
    def figure_final(self):
        θy = self.θy
        θu = self.θu
        My = self.My
        Mu = self.My

        xMθs = [0., θy, θu]
        yMθs = [0., My, Mu]

        f, ax = plt.subplots(figsize=(8, 5))
        ax.plot(xMθs, yMθs, lw=2)
        ax.axis([0, 1.2 * θu, 0, 1.2 * Mu])
        ax.set_title('Τελικό διάγραμμα Μ-θ')
        ax.set_ylabel('M (kN)')
        ax.set_xlabel('θ')
        fig = (f, ax)

        return fig

    @property
    def figure_shear_strength(self):
        xs = np.linspace(0., 1.5 * self.θu_ini, 100)
        yVRs = list()
        yMs = list()

        xy = self.results.outputTables['yield'].retrieve(search_field='quantity',
                                                         search_value='xy',
                                                         find_field='value')

        αs = self.results.outputTables['section'].retrieve(search_field='quantity',
                                                           search_value='αs',
                                                           find_field='value')

        Vw = self.results.outputTables['ultimate'].retrieve(search_field='quantity',
                                                            search_value='Vw',
                                                            find_field='value')

        for x in xs:
            μθpl = max(0, (x / self.θy) - 1)
            VRi = VRcalc(self.rcs.h, xy, self.Ls, self.N / 1000, self.rcs.b * self.rcs.d, self.rcs.materials.fc / 1000, μθpl, self.rcs.ratios.ρtot, αs, Vw / 1000) * 1000
            MVRi = VRi * self.Ls

            yVRs.append(VRi)
            yMs.append(MVRi)

        xsy = [self.θy, self.θy]
        ysy = [0, 1.2 * max(yVRs)]

        xsu = [self.θu_ini, self.θu_ini]
        ysu = [0, 1.2 * max(yVRs)]

        f, ax = plt.subplots(figsize=(8, 5))
        ax.plot(xs, yVRs, label="Τέμνουσα αντοχής VR", lw=2)
        ax.plot(xsy, ysy, label="Διαρροή", linestyle='--')
        ax.plot(xsu, ysu, label="Καμπτική αστοχία", linestyle='--')
        ax.axis([0, 1.5 * self.θu_ini, 0, 1.2 * max(yVRs)])
        ax.set_title('Μείωση της τέμνουσας αντοχής με την ανελαστική παραμόρφωση')
        ax.set_ylabel('VR (kN)')
        ax.set_xlabel('θ')
        ax.legend()
        fig = (f, ax)

        return fig

    @property
    def figure_shear_check(self):
        xs = np.linspace(0., 1.5 * self.θu_ini, 100)
        yVRs = list()
        yMs = list()

        xy = self.results.outputTables['yield'].retrieve(search_field='quantity',
                                                         search_value='xy',
                                                         find_field='value')

        αs = self.results.outputTables['section'].retrieve(search_field='quantity',
                                                           search_value='αs',
                                                           find_field='value')

        Vw = self.results.outputTables['ultimate'].retrieve(search_field='quantity',
                                                            search_value='Vw',
                                                            find_field='value')

        for x in xs:
            μθpl = max(0, (x / self.θy) - 1)
            VRi = VRcalc(self.rcs.h, xy, self.Ls, self.N / 1000, self.rcs.b * self.rcs.d, self.rcs.materials.fc / 1000, μθpl, self.rcs.ratios.ρtot, αs, Vw / 1000) * 1000
            MVRi = VRi * self.Ls

            yVRs.append(VRi)
            yMs.append(MVRi)

        ymax = max(max(yMs), self.My_ini)

        xsy = [self.θy_ini, self.θy_ini]
        ysy = [0, 1.2 * ymax]

        xsu = [self.θu_ini, self.θu_ini]
        ysu = [0, 1.2 * ymax]

        xMθs = [0, self.θy_ini, self.θu_ini]
        yMθs = [0, self.My_ini, self.My_ini]


        f, ax = plt.subplots(figsize=(8, 5))
        ax.plot(xs, yMs, label="Ροπή τέμνουσας αντοχής (VR*Ls)", lw=2)
        ax.plot(xsy, ysy, label="Διαρροή", linestyle='--')
        ax.plot(xsu, ysu, label="Αστοχία", linestyle='--')
        ax.axis([0, 1.5 * self.θu_ini, 0, 1.2 * ymax])
        ax.set_title('Έλεγχος πρόωρης αστοχίας από διάτμηση')
        ax.set_ylabel('M (kN)')
        ax.set_xlabel('θ')
        ax.plot(xMθs, yMθs, label="Αρχικό διάγραμμα Μ-θ")
        ax.legend()
        fig = (f, ax)

        return fig




# @dataclass
# class Rectangular:
#     b: float # το πλάτος της θλιβόμενης ζώνης[m]
#     h: float # το ύψος της διατομής[m]
#
#     reinforcement: Dict[str, object] = field(default_factory=dict)
#     materials: Dict[str, float] = field(default_factory=dict)
#
#     # Οπλισμός
#     N: float            # Αξονικό φορτίο [kN]
#     # Μήκος διάτμησης
#     Ls: float        # [m]
#     # Αποστάσεις bi περίσφιξης [m]
#     bi = np.array([0.0, 0.0])
#
#
#     cnom: float  # [m]
#     ## Διαμήκης
#     ### Εφελκυόμενος
#     nL: float  # Ο αριθτμός των εφελκυόμενων ράβδων
#     ΦL: float  # Η διάμετρος των εφελκυόμενων ράβδων [m]
#     ### Θλιβόμενος
#     nL2: float  # Ο αριθτμός των θλιβόμενων ράβδων
#     ΦL2: float  # Η διάμετρος των θλιβόμενων ράβδων [m]
#     ### Ενδιάμεσος
#     nLv: float # Ο αριθτμός των ενδιάμεσων ράβδων
#     ΦLv: float  # Η διάμετρος των ενδιάμεσων ράβδων [m]
#     ## Δισδιαγώνιος
#     nd: float # Ο αριθτμός των δισδιαγώνιων ράβδων
#     Φd: float  # Η διάμετρος των δισδιαγώνιων ράβδων [m]
#     ## Εγκάρσιος
#     nw: float  # Ο αριθμός των "τμήσεων" των συνδετήρων (πχ. 2 για 2τμητους)
#     Φw: float  # Η διάμετρος των συνδετήρων [m]
#     s: float  # Η απόσταση μεταξύ των συνδετήρων [m]
#
#
#     fc: float  # η θλιπτική αντοχή του σκυροδέματος[kPa]
#     Ec: float  # το μέτρο ελαστικότητας του σκυροδέματος [kPa]
#     fy: float  # το όριο διαρροής του χάλυβα [kPa]
#     Es: float  # το μέτρο ελαστικότητας του χάλυβα [kPa]
#     fyw: float # το όριο διαρροής του χάλυβα των συνδετήρων [kPa]



