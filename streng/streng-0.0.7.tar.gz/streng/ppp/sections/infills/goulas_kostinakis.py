from dataclasses import dataclass
import numpy as np
from sympy.solvers import solve
from sympy import Symbol
import math
from streng.common.io import results_display_older


@dataclass
class InfillPanelGK:
    h: float
    l: float
    fwc: float
    t: float
    ρ: float
    N: float
    Ac: float

    kw = None
    γcr = None
    τcr = None
    τu = None
    γu = None
    area = None
    γD = None
    τ002 = None

    kw_BC = None
    kw_CD = None
    Aw = None
    α = None
    EsAs_AB = None
    EsAs_BC = None
    EsAs_CD = None
    d = None
    dA = None
    dB = None
    dC = None
    dD = None
    dE = None
    δA = None
    δB = None
    δC = None
    δD = None
    δE = None
    FA = None
    FB = None
    FC = None
    FD = None
    FE = None

    XFδ = None
    YFδ = None

    log_list = None

    def __post_init__(self):
        self.calc()

    @staticmethod
    def τ3(γ: float, τu: float, γu: float, ρ: float, σ: float):
        x1 = (γ / γu) - 1
        x2 = ρ ** (3.82 * (1 - 0.22 * σ))
        x3 = 1.0 + 0.166 * σ
        return τu * (1 - 0.24 * np.sqrt(x1 / (x2 * x3)))


    def calc(self):

        self.log_list = list()

        self.σ = self.N * 0.001 / self.Ac

        self.kw = 1.71 * self.fwc * (80 + self.h / self.t)
        self.γcr = 0.09 / (self.fwc ** 0.5 * (80 + self.h / self.t))
        self.τcr = self.kw * self.γcr

        self.τu = 0.22 * self.fwc ** 0.5
        self.γu = 4.545 * self.γcr



        self.τ002 = self.τ3(0.02, self.τu, self.γu, self.ρ, self.σ)

        # τ-γ για τους 2 πρώτους κλάδους
        x1 = [0, self.γcr, self.γu]
        y1 = [0, self.τcr, self.τu]

        # τ-γ για τον 3ο κλάδο
        x2 = np.linspace(self.γu, 0.02, 50)
        vτ3 = np.vectorize(self.τ3)
        y2 = vτ3(x2, self.τu, self.γu, self.ρ, self.σ)

        # Εμβαδό κάτω από το διάγραμμα του 3ου κλάδου
        self.area = np.trapz(y2, x2)

        γtmp = Symbol('γtmp')
        self.γD = float(solve((self.τ002 * (0.02 - γtmp) + 0.5 * (γtmp - self.γu) * (self.τ002 + self.τu) - self.area), γtmp)[0])

        self.kw_BC = (self.τu - self.τcr) / (self.γu - self.γcr)
        self.kw_CD = (self.τ002 - self.τu) / (self.γD - self.γu)

        self.Aw = self.l * self.t
        self.α = np.arctan(self.h / self.l)  # Η γωνία με την οριζόντιο

        self.EsAs_AB = 1000 * self.Aw * self.kw / (math.sin(self.α) * math.cos(self.α) * math.cos(self.α))
        self.EsAs_BC = 1000 * self.Aw * self.kw_BC / (math.sin(self.α) * math.cos(self.α) * math.cos(self.α))
        self.EsAs_CD = 1000 * self.Aw * self.kw_CD / (math.sin(self.α) * math.cos(self.α) * math.cos(self.α))

        self.d = (self.h ** 2 + self.l ** 2) ** 0.5
        self.dA = self.d
        self.dB = math.sqrt(math.pow(self.h, 2) + math.pow(self.l - self.h * self.γcr, 2))
        self.dC = math.sqrt(math.pow(self.h, 2) + math.pow(self.l - self.h * self.γu, 2))
        self.dD = math.sqrt(math.pow(self.h, 2) + math.pow(self.l - self.h * self.γD, 2))
        self.dE = math.sqrt(math.pow(self.h, 2) + math.pow(self.l - self.h * 0.02, 2))

        self.δA = 0.0
        self.δB = - (self.dB - self.dA)
        self.δC = - (self.dC - self.dA)
        self.δD = - (self.dD - self.dA)
        self.δE = - (self.dE - self.dA)

        self.FA = 0
        self.FB = self.EsAs_AB * self.δB / self.d
        self.FC = self.EsAs_BC * (self.δC - self.δB) / self.d + self.FB
        self.FD = self.EsAs_CD * (self.δD - self.δC) / self.d + self.FC
        self.FE = self.FD

        self.log_list.append({'quantity': 'σ', 'value': self.σ, 'units': ''})
        self.log_list.append({'quantity': '1oς κλάδος', 'value':None, 'units': ''})
        self.log_list.append({'quantity': 'kw', 'value': self.kw, 'units': 'MPa'})
        self.log_list.append({'quantity': 'γcr', 'value': self.γcr, 'units': ''})
        self.log_list.append({'quantity': 'τcr', 'value': self.τcr, 'units': 'MPa'})
        self.log_list.append({'quantity': '2oς κλάδος', 'value':None, 'units': ''})
        self.log_list.append({'quantity': 'γu', 'value': self.γu, 'units': ''})
        self.log_list.append({'quantity': 'τu', 'value': self.τu, 'units': 'MPa'})

        # self.log_list.append({'quantity': 'x1', 'value': x1, 'units': ''})
        # self.log_list.append({'quantity': 'y1', 'value': y1, 'units': ''})
        # self.log_list.append({'quantity': 'x2', 'value': x2, 'units': ''})
        # self.log_list.append({'quantity': 'y2', 'value': y2, 'units': ''})

        self.log_list.append({'quantity': '3oς κλάδος', 'value':None, 'units': ''})
        self.log_list.append({'quantity': 'Εμβαδό 3ου κλάδου', 'value': self.area, 'units': ''})

        self.log_list.append({'quantity': 'γD', 'value': self.γD, 'units': ''})
        self.log_list.append({'quantity': 'τD=τ002', 'value': self.τ002, 'units': 'MPa'})

        self.log_list.append({'quantity': 'kw_BC', 'value': self.kw_BC, 'units': ''})
        self.log_list.append({'quantity': 'kw_CD', 'value': self.kw_CD, 'units': ''})

        self.log_list.append({'quantity': 'EsAs_AB', 'value': self.EsAs_AB, 'units': ''})
        self.log_list.append({'quantity': 'EsAs_BC', 'value': self.EsAs_BC, 'units': ''})
        self.log_list.append({'quantity': 'EsAs_CD', 'value': self.EsAs_CD, 'units': ''})

        self.log_list.append({'quantity': 'dA', 'value': self.dA, 'units': ''})
        self.log_list.append({'quantity': 'dB', 'value': self.dB, 'units': ''})
        self.log_list.append({'quantity': 'dC', 'value': self.dC, 'units': ''})
        self.log_list.append({'quantity': 'dD', 'value': self.dD, 'units': ''})
        self.log_list.append({'quantity': 'dE', 'value': self.dE, 'units': ''})

        self.log_list.append({'quantity': 'δA', 'value': self.δA, 'units': ''})
        self.log_list.append({'quantity': 'δB', 'value': self.δB, 'units': ''})
        self.log_list.append({'quantity': 'δC', 'value': self.δC, 'units': ''})
        self.log_list.append({'quantity': 'δD', 'value': self.δD, 'units': ''})
        self.log_list.append({'quantity': 'δE', 'value': self.δE, 'units': ''})



        self.log_list.append({'quantity': 'FA', 'value': self.FA, 'units': ''})
        self.log_list.append({'quantity': 'FB', 'value': self.FB, 'units': ''})
        self.log_list.append({'quantity': 'FC', 'value': self.FC, 'units': ''})
        self.log_list.append({'quantity': 'FD', 'value': self.FD, 'units': ''})
        self.log_list.append({'quantity': 'FE', 'value': self.FE, 'units': ''})

        self.XFδ = [self.δA, self.δB, self.δC, self.δD, self.δE]
        self.YFδ = [self.FA, self.FB, self.FC, self.FD, self.FE]


    def log_panda(self):
        return results_display_older.log_dataframe(self.log_list)

    def log_markdown_table(self):
        return results_display_older.log_markdown_table(self.log_list)

    def __str__(self):
        return self.log_markdown_table()
