from streng.codes.eurocodes.ec8.raw.ch5.detailing import beams as detbeams
from streng.common.io import results_display_older
from .....sections.common import norm_forces
from .....sections.concrete.reinforcement import areas
from . import flexure_tables


def d_for_M(M, bw, μ, fcd):
    return (M / (bw * μ * fcd)) ** 0.5


class RectangularBeam:

    def __init__(self, bw, h, d1, ductility_class='M'):
        self.bw = bw
        self.h = h
        self.d1 = d1
        self.ductility_class = ductility_class

    def set_loads(self, Md, Nd):
        self.Md = Md
        self.Nd = Nd

    def set_materials(self, fck, fyk, acc=0.85, γc=1.5, γs=1.15):
        self.fck = fck
        self.fyk = fyk
        self.acc = acc
        self.γc = γc
        self.γs = γs

    def calc(self):
        if self.ductility_class == 'M':
            μφ = 6.8
        else:
            μφ = 10.7

        self.fcd = self.acc * self.fck / self.γc
        self.fyd = self.fyk / self.γs
        ε = self.fyd / 200000000.

        self.ys1 = self.h / 2 - self.d1
        self.d = self.h - self.d1
        self.Msd = abs(self.Md) - self.Nd * self.ys1
        self.μsd = norm_forces.μ(self.Msd, self.bw, self.d, self.fcd)
        self.ω = flexure_tables.ω_for_μsd(self.μsd)
        self.As = areas.As_for_ω(self.ω, self.bw, self.d, self.fcd, self.fyd, self.Nd)
        self.ρmin = detbeams.ρmin(self.fck/1000., self.fyk/1000.)
        self.ρmax = detbeams.ρmax05(μφ, ε, self.fck * 1.0 / 1.5, self.fyk / 1.15)
        self.Asmin = self.ρmin * self.bw * self.d
        self.Asmaxcr = self.ρmax * self.bw * self.d
        self.Asmaxgen = 0.04 * self.bw * self.d

        if self.μsd >= 0.30:
            self.d2d = self.d1 / self.d
            self.ω1, self.ω2 = flexure_tables.ω1ω2_for_μsd(self.μsd)
            self.ρ1, self.ρ2 = flexure_tables.ρ1ρ2_for_d2d(self.d2d, self.ω1)
            self.As1 = areas.As1_for_ω1ρ1(self.ω1, self.ρ1, self.bw, self.d, self.fcd, self.fyd, self.Nd)
            self.As2 = areas.As2_for_ω2ρ2(self.ω2, self.ρ2, self.bw, self.d, self.fcd, self.fyd)

    def log_tbl(self):
        _tbl = list()
        _tbl.append(['fcd', self.fcd, 'MPa'])
        _tbl.append(['fyd', self.fyd, 'MPa'])
        _tbl.append(['ys1', self.ys1, 'm'])
        _tbl.append(['d', self.d, 'm'])
        _tbl.append(['Msd', self.Msd, 'kNm'])
        _tbl.append(['μsd', self.μsd, ''])
        _tbl.append(['ω', self.ω, ''])
        _tbl.append(['As', self.As, 'm2'])
        _tbl.append(['Asmin', self.Asmin, 'm2'])
        _tbl.append(['Asmax,κρισ', self.Asmaxcr, 'm2'])
        _tbl.append(['Asmax,γεν', self.Asmaxgen, 'm2'])

        if self.μsd >= 0.30:
            _tbl.append(['Λύση με τοποθέτηση και θλιβόμενου οπλισμού', 0., ''])
            _tbl.append(['d2/d (θεωρώντας d1=d2)', self.d2d, ''])
            _tbl.append(['ω1', self.ω1, ''])
            _tbl.append(['ω2', self.ω2, ''])
            _tbl.append(['ρ1', self.ρ1, ''])
            _tbl.append(['ρ2', self.ρ2, ''])
            _tbl.append(['As1', self.As1, 'm2'])
            _tbl.append(['As2', self.As2, 'm2'])

        return _tbl

    def log_list(self):
        _log = list()
        _log.append({'quantity': 'fcd',
                     'value': self.fcd,
                     'units': 'MPa'})
        _log.append({'quantity': 'fyd',
                     'value': self.fyd,
                     'units': 'MPa'})
        _log.append({'quantity': 'ys1',
                     'value': self.ys1,
                     'units': 'm'})
        _log.append({'quantity': 'd',
                     'value': self.d,
                     'units': 'm'})
        _log.append({'quantity': 'Msd',
                     'value': self.Msd,
                     'units': 'kNm'})
        _log.append({'quantity': 'μsd',
                     'value': self.μsd,
                     'units': ''})
        _log.append({'quantity': 'ω',
                     'value': self.ω,
                     'units': ''})
        _log.append({'quantity': 'As',
                     'value': self.As,
                     'units': 'm2'})
        _log.append({'quantity': 'Asmin',
                     'value': self.Asmin,
                     'units': 'm2'})
        _log.append({'quantity': 'Asmax,κρισ',
                     'value': self.Asmaxcr,
                     'units': 'm2'})
        _log.append({'quantity': 'Asmax,γεν',
                     'value': self.Asmaxgen,
                     'units': 'm2'})

        if self.μsd >= 0.30:
            _log.append({'quantity': 'Λύση με τοποθέτηση και θλιβόμενου οπλισμού',
                         'value': None,
                         'units': ''})
            _log.append({'quantity': 'd2/d (θεωρώντας d1=d2)',
                         'value': self.d2d,
                         'units': ''})
            _log.append({'quantity': 'ω1',
                         'value': self.ω1,
                         'units': ''})
            _log.append({'quantity': 'ω2',
                         'value': self.ω2,
                         'units': ''})
            _log.append({'quantity': 'ρ1',
                         'value': self.ρ1,
                         'units': ''})
            _log.append({'quantity': 'ρ2',
                         'value': self.ρ2,
                         'units': ''})
            _log.append({'quantity': 'As1',
                         'value': self.As1,
                         'units': 'm2'})
            _log.append({'quantity': 'As2',
                         'value': self.As2,
                         'units': 'm2'})


        return _log

    def log_panda(self):
        return results_display_older.log_dataframe(self.log_list())

    def log_markdown_table(self):
        return results_display_older.log_markdown_table(self.log_list())

    def __str__(self):
        return self.log_markdown_table()
