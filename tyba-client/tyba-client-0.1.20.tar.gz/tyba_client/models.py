from dataclasses import dataclass, field
from enum import Enum
from dataclasses_json import config, dataclass_json
import typing as t
from .utils import read_pvsyst_file

from tyba_client.utils import string_enum


def opt_field():
    return field(default=None, metadata=config(exclude=lambda x: x is None))

@dataclass_json
@dataclass
class FixedTilt(object):
    tilt: float


@dataclass_json
@dataclass
class SingleAxisTracking(object):
    rotation_limit: float = 45.0
    backtrack: bool = True

@dataclass_json
@dataclass
class SystemDesign(object):
    dc_capacity: float
    ac_capacity: float
    poi_limit: float
    gcr: float
    tracking: t.Union[FixedTilt, SingleAxisTracking]
    modules_per_string: t.Optional[int] = opt_field()
    strings_in_parallel: t.Optional[int] = opt_field()
    azimuth: t.Optional[float] = opt_field()

@dataclass_json
@dataclass
class Inverter(object):
    mppt_low: float
    mppt_high: float
    pso: float
    paco: float
    pdco: float
    vdco: float
    c0: float
    c1: float
    c2: float
    c3: float
    pnt: float
    vdcmax: float
    tdc: t.List[t.List[float]] = field(default_factory=lambda: [[1.0, 52.8, -0.021]])


@dataclass_json
@dataclass
class PVModule(object):
    bifacial: bool
    a_c: float
    n_s: float
    i_sc_ref: float
    v_oc_ref: float
    i_mp_ref: float
    v_mp_ref: float
    alpha_sc: float
    beta_oc: float
    t_noct: float
    a_ref: float
    i_l_ref: float
    i_o_ref: float
    r_s: float
    r_sh_ref: float
    adjust: float
    gamma_r: float
    bifacial_transmission_factor: float
    bifaciality: float
    bifacial_ground_clearance_height: float


@string_enum
class MermoudModuleTech(Enum):
    SiMono = "mtSiMono"
    SiPoly = "mtSiPoly"
    CdTe = "mtCdTe"
    CIS = "mtCIS"
    uCSi_aSiH = "mtuCSi_aSiH"


@dataclass_json
@dataclass
class PVModuleMermoudLejeune(object):
    bifacial: bool
    bifacial_transmission_factor: float
    bifaciality: float
    bifacial_ground_clearance_height: float
    tech: MermoudModuleTech
    i_mp_ref: float
    i_sc_ref: float
    length: float
    n_diodes: int
    n_parallel: int
    n_series: int
    r_s: float
    r_sh_0: float
    r_sh_exp: float
    r_sh_ref: float
    s_ref: float
    t_c_fa_alpha: float
    t_ref: float
    v_mp_ref: float
    v_oc_ref: float
    width: float
    alpha_sc: float
    beta_oc: float
    mu_n: float
    n_0: float
    iam_c_cs_iam_value: t.Optional[t.List[float]] = opt_field()
    iam_c_cs_inc_angle: t.Optional[t.List[float]] = opt_field()
    custom_d2_mu_tau: t.Optional[float] = opt_field()

    @classmethod
    def from_pan(cls, pan_file: str):
        pan_blob = read_pvsyst_file(pan_file)
        data = pan_blob["PVObject_"]["items"]
        commercial = data["PVObject_Commercial"]["items"]
        if "PVObject_IAM" in data:
            iam_points = [
                v.split(",")
                for k, v in data["PVObject_IAM"]["items"]["IAMProfile"]["items"].items()
                if k.startswith("Point_")
            ]
            iam_angles = [float(v[0]) for v in iam_points]
            iam_values = [float(v[1]) for v in iam_points]
        else:
            iam_angles = None
            iam_values = None

        return cls(
            bifacial="BifacialityFactor" in data,
            bifacial_transmission_factor=0.013,
            bifaciality=float(data.get("BifacialityFactor", 0.65)),
            bifacial_ground_clearance_height=1.0,
            n_parallel=int(data["NCelP"]),
            n_diodes=int(data["NDiode"]),
            n_series=int(data["NCelS"]),
            t_ref=float(data["TRef"]),
            s_ref=float(data["GRef"]),
            i_sc_ref=float(data["Isc"]),
            v_oc_ref=float(data["Voc"]),
            i_mp_ref=float(data["Imp"]),
            v_mp_ref=float(data["Vmp"]),
            alpha_sc=float(data["muISC"]) * 1e-3,  # TODO: check units
            beta_oc=float(data["muVocSpec"]) * 1e-3,
            n_0=float(data["Gamma"]),
            mu_n=float(data["muGamma"]),
            r_sh_ref=float(data["RShunt"]),
            r_s=float(data["RSerie"]),
            r_sh_0=float(data["Rp_0"]),
            r_sh_exp=float(data["Rp_Exp"]),
            tech=data["Technol"],
            length=float(commercial["Height"]),
            width=float(commercial["Width"]),
            # faiman cell temp model used by PVSyst
            t_c_fa_alpha=float(data["Absorb"]),
            # IAM
            iam_c_cs_iam_value=iam_values,
            iam_c_cs_inc_angle=iam_angles,
            custom_d2_mu_tau=data.get("D2MuTau"),
        )


@dataclass_json
@dataclass
class Losses(object):
    ac_wiring: t.Optional[float] = opt_field()
    dc_optimizer: t.Optional[float] = opt_field()
    enable_snow_model: t.Optional[bool] = opt_field()
    dc_wiring: t.Optional[float] = opt_field()
    diodes_connections: t.Optional[float] = opt_field()
    mismatch: t.Optional[float] = opt_field()
    nameplate: t.Optional[float] = opt_field()
    rear_irradiance: t.Optional[float] = opt_field()
    soiling: t.Optional[t.List[float]] = opt_field()
    tracking: t.Optional[float] = opt_field()
    transformer_load: t.Optional[float] = opt_field()
    transformer_no_load: t.Optional[float] = opt_field()
    transmission: t.Optional[float] = opt_field()
    lid: t.Optional[float] = opt_field()
    poi_adjustment: t.Optional[float] = opt_field()
    dc_array_adjustment: t.Optional[float] = opt_field()

@dataclass_json
@dataclass
class Layout(object):
    orientation: t.Optional[str] = opt_field()
    vertical: t.Optional[int] = opt_field()
    horizontal: t.Optional[int] = opt_field()
    aspect_ratio: t.Optional[float] = opt_field()


@dataclass_json
@dataclass
class SolarResourceTimeSeries(object):
    year: t.List[int]
    month: t.List[int]
    day: t.List[int]
    hour: t.List[int]
    minute: t.List[int]
    tdew: t.List[float]
    df: t.List[float]
    dn: t.List[float]
    gh: t.List[float]
    pres: t.List[float]
    tdry: t.List[float]
    wdir: t.List[float]
    wspd: t.List[float]
    alb: t.Optional[t.List[float]] = opt_field()

@dataclass_json
@dataclass
class SolarResource(object):
    latitude: float
    longitude: float
    time_zone_offset: float
    elevation: float
    data: SolarResourceTimeSeries
    monthly_albedo: t.Optional[t.List[float]] = opt_field()


@dataclass_json
@dataclass
class PVModel(object):
    solar_resource: t.Union[t.Tuple[float, float], SolarResource]
    inverter: t.Union[str, Inverter]
    pv_module: t.Union[str, t.Union[PVModule, PVModuleMermoudLejeune]]
    system_design: SystemDesign
    losses: t.Optional[Losses] = opt_field()
    layout: t.Optional[Layout] = opt_field()
    project_term: t.Optional[int] = None
    dc_degradation: t.Optional[float] = None

DetailedPVModel = PVModel

@dataclass_json
@dataclass
class SingleStorageInputs(object):
    power_capacity: float
    energy_capacity: float
    charge_efficiency: float
    discharge_efficiency: float
    degradation_rate: float
    cycling_cost_adder: t.Optional[float] = 0

@dataclass_json
@dataclass
class Battery(object):
    power_capacity: float
    energy_capacity: float
    charge_efficiency: float
    discharge_efficiency: float
    degradation_rate: float
    term: int

@dataclass_json
@dataclass
class StorageInputs(object):
    batteries: t.List[Battery]
    cycling_cost_adder: t.Optional[float] = 0
    annual_cycle_limit: t.Optional[float] = opt_field()
    window: t.Optional[int] = opt_field()
    step: t.Optional[int] = opt_field()
    flexible_solar: t.Optional[bool] = opt_field()


@dataclass_json
@dataclass
class AncillaryEnergyPrices(object):
    dam: t.List[float]
    rtm: t.List[float]

@dataclass_json
@dataclass
class StorageModel(object):
    storage_inputs: StorageInputs
    energy_prices: t.Union[AncillaryEnergyPrices, t.List[float]]

@dataclass_json
@dataclass
class Utilization(object):
    actual: float
    lower: float
    upper: float

@dataclass_json
@dataclass
class ReserveMarket(object):
    price: t.List[float]
    offer_cap: float
    utilization: Utilization

@dataclass_json
@dataclass
class AncillaryUpMarkets(object):
    reserves: t.Optional[ReserveMarket] = opt_field()
    reg_up: t.Optional[ReserveMarket] = opt_field()
    generic_up: t.Optional[ReserveMarket] = opt_field()

@dataclass_json
@dataclass
class AncillaryDownMarket(object):
    reg_down: t.Optional[ReserveMarket] = opt_field()
    generic_down: t.Optional[ReserveMarket] = opt_field()

@dataclass_json
@dataclass
class AncillaryMarkets(object):
    up: t.Optional[AncillaryUpMarkets] = opt_field()
    down: t.Optional[AncillaryDownMarket] = opt_field()

@dataclass_json
@dataclass
class StandaloneStorageModel(StorageModel):
    time_interval_mins: t.Optional[int] = opt_field()
    ancillary_markets: t.Optional[AncillaryMarkets] = opt_field()


@string_enum
class StorageCoupling(Enum):
    ac = 'ac'
    dc = 'dc'


@dataclass_json
@dataclass
class PVStorageModel(object):
    storage_coupling: StorageCoupling = field(metadata=StorageCoupling.__metadata__)
    pv_inputs: PVModel
    storage_inputs: StorageInputs
    energy_prices: t.Union[AncillaryEnergyPrices, t.List[float]]
    enable_grid_charge_year: t.Optional[int] = opt_field()
    ancillary_markets: t.Optional[AncillaryMarkets] = opt_field()


@string_enum
class Market:
    RT = 'realtime'
    DA = 'dayahead'

@string_enum
class AncillaryService:
    REGULATION_UP = 'Regulation Up'
    REGULATION_DOWN = 'Regulation Down'
    RESERVES = 'Reserves'
