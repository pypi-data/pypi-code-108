import math
from dataclasses import dataclass
from streng.tools.rccola.rcinput import RccolaInput
from streng.ppp.sections.concrete.reinforcement.areas import As_layer, As


@dataclass
class Materials:
    conc_fc: float
    steel_fy: float
    steel_Es: float
    steel_εsh: float
    steel_Esh: float
    steel_εsu: float
    steel_fu: float
    steel_fyw: float
    steel_εsuw: float


@dataclass
class SquareColumn:
    b: float
    cover: float
    l: float
    dia_corner: float
    dia_side1: float
    dia_side2: float
    n_side1: int
    n_side2: int
    trans_pattern: int
    trans_dia: int
    trans_s: float
    materials: Materials
    rccola_input: RccolaInput

    def doit(self):
        b = self.b
        t = self.b
        cover = self.cover
        l = self.l
        dia_corner = self.dia_corner
        dia_side1 = self.dia_side1
        dia_side2 = self.dia_side2
        n_side1 = self.n_side1
        n_side2 = self.n_side2
        trans_pattern = self.trans_pattern
        trans_dia = self.trans_dia
        trans_s = self.trans_s

        tc = self.b - 2 * cover - trans_dia
        bc = tc
        gt = tc - 2 * trans_dia - dia_corner

        nb1 = 4 + 2 * (n_side1 + n_side2)
        as1 = (As_layer([4, 2 * n_side1, 2 * n_side2],
                        [dia_corner, dia_side1, dia_side2])) / nb1

        nb2 = nb1 - 4
        if nb2 > 0:
            as2 = (As_layer([2 * n_side1, 2 * n_side2], [dia_side1, dia_side2])) / nb2
        else:
            as2 = 0

        tempas_ac = As(trans_dia) / (tc ** 2 * trans_s)

        nbar = 0
        xstrp = 0.
        ppp = 0.

        if trans_pattern == 1:
            nbar = 0
            xstrp = 2
            ppp = (4 * tc) * tempas_ac
        elif trans_pattern == 2:
            nbar = 1
            xstrp = 2 + 2 ** 0.5
            ppp = (4 * tc + 4 * tc / 2 ** 0.5) * tempas_ac
        elif trans_pattern == 3:
            nbar = 2
            xstrp = 4
            ppp = (8 * tc + 4 * tc / 3.0) * tempas_ac
        elif trans_pattern == 4:
            nbar = 3
            xstrp = 4 + 2 ** 0.5
            ppp = (8 * tc + 4 * tc / 2.0 + 4 * tc / 2 ** 0.5) * tempas_ac
        elif trans_pattern == 5:
            nbar = 1
            xstrp = 3
            ppp = (6 * tc) * tempas_ac

        asstrp = xstrp * As(trans_dia)

        self.rccola_input.strains_defaults = 1

        self.rccola_input.first_row = RccolaInput.FirstRow(TYPEC=1,
                                                           TYPES=1,
                                                           ISPALL=0,
                                                           ICSTR=8,
                                                           ICSTRS=0,
                                                           NPTS=0,
                                                           NPTSS=0,
                                                           ITCONF=1,
                                                           ISSTL=0,
                                                           IECU=1,
                                                           ISSTR=0,
                                                           IGRAPH=3)

        self.rccola_input.second_row = RccolaInput.SecondRow(NLOAD=0,
                                                             NLAYER=0,
                                                             NDATA1=0,
                                                             NDATA2=0,
                                                             NSTRNI=4,
                                                             NSTRNC=24,
                                                             NITT=30)

        self.rccola_input.conc_sect_info = RccolaInput.ConcSectInfo(T=t,
                                                                    B=b,
                                                                    TC=tc,
                                                                    BC=bc)

        self.rccola_input.reinf_place_info_TYPES12 = RccolaInput.ReinfPlaceInfoTYPES12(GT=gt,
                                                                                       NB1=nb1,
                                                                                       AS1=as1,
                                                                                       NB2=nb2,
                                                                                       AS2=as2,
                                                                                       NBAR=nbar,
                                                                                       AF=None)

        self.rccola_input.long_reinf_props = RccolaInput.LongReinfProps(FYS=self.materials.steel_fy,
                                                                        YMS=self.materials.steel_Es,
                                                                        ESH=self.materials.steel_εsh,
                                                                        YSH=self.materials.steel_Esh,
                                                                        ESU=self.materials.steel_εsu,
                                                                        FSU=self.materials.steel_fu,
                                                                        ESDYN=None)

        self.rccola_input.trans_reinf_info = RccolaInput.TransReinfInfo(FYSTRP=self.materials.steel_fyw,
                                                                        ASSTRP=asstrp,
                                                                        S=trans_s,
                                                                        XL=l,
                                                                        XSTRP=xstrp,
                                                                        ESUSTRP=self.materials.steel_εsuw)

        self.rccola_input.conc_props_ICSTR2348 = RccolaInput.ConcPropsICSTR2348(FCJ=self.materials.conc_fc,
                                                                                S=trans_s,
                                                                                PPP=ppp)
