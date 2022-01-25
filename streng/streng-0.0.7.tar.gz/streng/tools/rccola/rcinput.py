import numpy as np
from dataclasses import dataclass, astuple, field


@dataclass
class FirstRow:
    TYPEC: int
    TYPES: int
    ISPALL: int
    ICSTR: int
    ICSTRS: int
    NPTS: int
    NPTSS: int
    ITCONF: int
    ISSTL: int
    IECU: int
    ISSTR: int
    IGRAPH: int


@dataclass
class SecondRow:
    NLOAD: int
    NLAYER: int
    NDATA1: int
    NDATA2: int
    NSTRNI: int
    NSTRNC: int
    NITT: int


@dataclass
class ConcSectInfo:
    T: float
    B: float
    TC: float
    BC: float


@dataclass
class ReinfPlaceInfoTYPES12:
    GT: float
    NB1: int
    AS1: float
    NB2: int
    AS2: float
    NBAR: int
    AF: float


@dataclass
class ReinfPlaceInfoTYPES3:
    NL: int
    NBAR: int
    YS: list
    AS: list
    NBS: list
    IBUC: list
    YSS: list
    ASS: list
    NBSS: list


@dataclass
class LongReinfProps:
    FYS: float
    YMS: float
    ESH: float
    YSH: float
    ESU: float
    FSU: float
    ESDYN: float  # For ISSTR=1


@dataclass
class TransReinfInfo:
    FYSTRP: float
    ASSTRP: float
    S: float
    XL: float
    XSTRP: float
    ESUSTRP: float


@dataclass
class ConcPropsICSTR2348:
    FCJ: float
    S: float
    PPP: float


@dataclass
class ConcUnconfinedPropsICSTRS2:
    FCJS: float
    SS: float
    PPX: float
    NSP: int


@dataclass
class GeometryConcCrossSectionInfo:
    AA: list
    N1: list
    A1: list
    AAc: list
    N1c: list


@dataclass
class RccolaInput:
    first_row: FirstRow
    second_row: SecondRow
    conc_sect_info: ConcSectInfo
    reinf_place_info_TYPES12: ReinfPlaceInfoTYPES12
    reinf_place_info_TYPES3: ReinfPlaceInfoTYPES3
    long_reinf_props: LongReinfProps
    trans_reinf_info: TransReinfInfo
    conc_props_ICSTR2348: ConcPropsICSTR2348
    conc_unconfined_props_ICSTRS2: ConcUnconfinedPropsICSTRS2
    geometry_conc_crossec_info: GeometryConcCrossSectionInfo
    axials: np.array
    strains: np.array = None
    strains_defaults: int = None

    def run(self):
        if self.strains_defaults == 1:
            self.strains = np.array([0.0, 0.001, 0.002, 0.003, 0.0035, 0.004, 0.005, 0.006, 0.007, 0.008,
                                     0.009, 0.01, 0.011, 0.012, 0.013, 0.014, 0.015, 0.016, 0.018, 0.02,
                                     0.022, 0.024, 0.026, 0.028, 0.03])
            self.second_row.NSTRNI = 4
            self.second_row.NSTRNC = 24

