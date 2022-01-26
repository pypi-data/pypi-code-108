from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple


@dataclass(frozen=True)
class FieldInfo:
    name: str
    type: Any


@dataclass(frozen=True)
class FieldInfoIni(FieldInfo):
    ini_section: str


@dataclass(frozen=True)
class FieldInfoSqlite(FieldInfo):
    table_name: str


@dataclass(frozen=True)
class AggregationFieldInfoOld(FieldInfo):
    pass


@dataclass(frozen=True)
class FieldInfoAPI(FieldInfo):
    default: Optional[Any]


class SettingsTables(str, Enum):
    global_settings = "v2_global_settings"
    numerical_settings = "v2_numerical_settings"
    aggregation_settings = "v2_aggregation_settings"


physical_settings_map = {
    "use_advection_1d": [
        FieldInfoIni("advection_1d", int, "physics"),
        FieldInfoAPI("use_advection_1d", int, 1),
        FieldInfoSqlite("advection_1d", int, SettingsTables.global_settings.value),
    ],
    "use_advection_2d": [
        FieldInfoIni("advection_2d", int, "physics"),
        FieldInfoAPI("use_advection_2d", int, 1),
        FieldInfoSqlite("advection_2d", int, SettingsTables.global_settings.value),
    ],
}

time_step_settings_map = {
    "time_step": [
        FieldInfoIni("timestep", float, "simulation"),
        FieldInfoAPI("time_step", float, 1.0),
        FieldInfoSqlite("sim_time_step", float, SettingsTables.global_settings.value),
    ],
    "min_time_step": [
        FieldInfoIni("minimum_timestep", float, "simulation"),
        FieldInfoAPI("min_time_step", float, 0.01),
        FieldInfoSqlite(
            "minimum_sim_time_step", float, SettingsTables.global_settings.value
        ),
    ],
    "max_time_step": [
        FieldInfoIni("maximum_timestep", float, "simulation"),
        FieldInfoAPI("max_time_step", float, 1.0),
        FieldInfoSqlite(
            "maximum_sim_time_step", float, SettingsTables.global_settings.value
        ),
    ],
    "use_time_step_stretch": [
        FieldInfoIni("timestep_plus", bool, "numerics"),
        FieldInfoAPI("use_time_step_stretch", bool, False),
        FieldInfoSqlite("timestep_plus", bool, SettingsTables.global_settings.value),
    ],
    "output_time_step": [
        FieldInfoIni("output_timestep", float, "output"),
        FieldInfoAPI("output_time_step", float, 1.0),
        FieldInfoSqlite(
            "output_time_step", float, SettingsTables.global_settings.value
        ),
    ],
}

# old -> new
numerical_settings_map = {
    "cfl_strictness_factor_1d": [
        FieldInfoIni("cfl_strictness_factor_1d", float, "numerics"),
        FieldInfoAPI("cfl_strictness_factor_1d", float, 1.0),
        FieldInfoSqlite(
            "cfl_strictness_factor_1d", float, SettingsTables.numerical_settings.value
        ),
    ],
    "cfl_strictness_factor_2d": [
        FieldInfoIni("cfl_strictness_factor_2d", float, "numerics"),
        FieldInfoAPI("cfl_strictness_factor_2d", float, 1.0),
        FieldInfoSqlite(
            "cfl_strictness_factor_2d", float, SettingsTables.numerical_settings.value
        ),
    ],
    "flow_direction_threshold": [
        FieldInfoIni("flow_direction_threshold", float, "numerics"),
        FieldInfoAPI("flow_direction_threshold", float, 1e-05),
        FieldInfoSqlite(
            "flow_direction_threshold", float, SettingsTables.numerical_settings.value
        ),
    ],
    "convergence_cg": [
        FieldInfoIni("convergence_cg", float, "numerics"),
        FieldInfoAPI("convergence_cg", float, 1.0e-9),
        FieldInfoSqlite(
            "convergence_cg", float, SettingsTables.numerical_settings.value
        ),
    ],
    "convergence_eps": [
        FieldInfoIni("convergence_eps", float, "numerics"),
        FieldInfoAPI("convergence_eps", float, 1.0e-5),
        FieldInfoSqlite(
            "convergence_eps", float, SettingsTables.numerical_settings.value
        ),
    ],
    "friction_shallow_water_depth_correction": [
        FieldInfoIni("friction_shallow_water_correction", int, "physical_attributes"),
        FieldInfoAPI(
            "friction_shallow_water_depth_correction",
            int,
            0,
        ),
        FieldInfoSqlite(
            "frict_shallow_water_correction",
            int,
            SettingsTables.numerical_settings.value,
        ),
    ],
    "general_numerical_threshold": [
        FieldInfoIni("general_numerical_threshold", float, "numerics"),
        FieldInfoAPI("general_numerical_threshold", float, 1.0e-8),
        FieldInfoSqlite(
            "general_numerical_threshold",
            float,
            SettingsTables.numerical_settings.value,
        ),
    ],
    "time_integration_method": [
        FieldInfoIni("integration_method", int, "numerics"),
        FieldInfoAPI("time_integration_method", int, 0),
        FieldInfoSqlite(
            "integration_method", int, SettingsTables.numerical_settings.value
        ),
    ],
    "limiter_waterlevel_gradient_1d": [
        FieldInfoIni("limiter_grad_1d", int, "numerics"),
        FieldInfoAPI("limiter_waterlevel_gradient_1d", int, 1),
        FieldInfoSqlite(
            "limiter_grad_1d", int, SettingsTables.numerical_settings.value
        ),
    ],
    "limiter_waterlevel_gradient_2d": [
        FieldInfoIni("limiter_grad_2d", int, "numerics"),
        FieldInfoAPI("limiter_waterlevel_gradient_2d", int, 1),
        FieldInfoSqlite(
            "limiter_grad_2d", int, SettingsTables.numerical_settings.value
        ),
    ],
    "limiter_slope_crossectional_area_2d": [
        FieldInfoIni("limiter_slope_crossectional_area_2d", int, "numerics"),
        FieldInfoAPI("limiter_slope_crossectional_area_2d", int, 0),
        FieldInfoSqlite(
            "limiter_slope_crossectional_area_2d",
            int,
            SettingsTables.numerical_settings.value,
        ),
    ],
    "limiter_slope_friction_2d": [
        FieldInfoIni("limiter_slope_friction_2d", int, "numerics"),
        FieldInfoAPI("limiter_slope_friction_2d", int, 0),
        FieldInfoSqlite(
            "limiter_slope_friction_2d", int, SettingsTables.numerical_settings.value
        ),
    ],
    "max_non_linear_newton_iterations": [
        FieldInfoIni("max_nonlinear_iteration", int, "numerics"),
        FieldInfoAPI("max_non_linear_newton_iterations", int, 20),
        FieldInfoSqlite(
            "max_nonlin_iterations", int, SettingsTables.numerical_settings.value
        ),
    ],
    "max_degree_gauss_seidel": [
        FieldInfoIni("maximum_degree", int, "numerics"),
        FieldInfoAPI("max_degree_gauss_seidel", int, 20),
        FieldInfoSqlite("max_degree", int, SettingsTables.numerical_settings.value),
    ],
    "min_friction_velocity": [
        FieldInfoIni("minimum_friction_velocity", float, "numerics"),
        FieldInfoAPI("min_friction_velocity", float, 0.01),
        FieldInfoSqlite(
            "minimum_friction_velocity", float, SettingsTables.numerical_settings.value
        ),
    ],
    "min_surface_area": [
        FieldInfoIni("minimum_surface_area", float, "numerics"),
        FieldInfoAPI("min_surface_area", float, 1.0e-8),
        FieldInfoSqlite(
            "minimum_surface_area", float, SettingsTables.numerical_settings.value
        ),
    ],
    "use_preconditioner_cg": [
        FieldInfoIni("precon_cg", int, "numerics"),
        FieldInfoAPI("use_preconditioner_cg", int, 1),
        FieldInfoSqlite("precon_cg", int, SettingsTables.numerical_settings.value),
    ],
    "preissmann_slot": [
        FieldInfoIni("preissmann_slot", float, "numerics"),
        FieldInfoAPI("preissmann_slot", float, 0.0),
        FieldInfoSqlite(
            "preissmann_slot", float, SettingsTables.numerical_settings.value
        ),
    ],
    "pump_implicit_ratio": [
        FieldInfoIni("pump_implicit_ratio", float, "numerics"),
        FieldInfoAPI("pump_implicit_ratio", float, 1.0),
        FieldInfoSqlite(
            "pump_implicit_ratio", float, SettingsTables.numerical_settings.value
        ),
    ],
    "limiter_slope_thin_water_layer": [
        FieldInfoIni("thin_water_layer_definition", float, "numerics"),
        FieldInfoAPI("limiter_slope_thin_water_layer", float, 0.01),
        FieldInfoSqlite(
            "thin_water_layer_definition",
            float,
            SettingsTables.numerical_settings.value,
        ),
    ],
    "use_of_cg": [
        FieldInfoIni("use_of_cg", int, "numerics"),
        FieldInfoAPI("use_of_cg", int, 20),
        FieldInfoSqlite("use_of_cg", int, SettingsTables.numerical_settings.value),
    ],
    "use_nested_newton": [
        FieldInfoIni("nested_newton", int, "numerics"),
        FieldInfoAPI("use_nested_newton", bool, True),
        FieldInfoSqlite(
            "use_of_nested_newton", int, SettingsTables.numerical_settings.value
        ),
    ],
    "flooding_threshold": [
        FieldInfoIni("flooding_threshold", float, "numerics"),
        FieldInfoAPI("flooding_threshold", float, 0.000001),
        FieldInfoSqlite(
            "flooding_threshold", float, SettingsTables.global_settings.value
        ),
    ],
}

aggregation_settings_map = {
    "flow_variable": [
        AggregationFieldInfoOld("flow_variable", str),
        FieldInfoAPI("flow_variable", str, None),
        FieldInfoSqlite(
            "flow_variable", str, SettingsTables.aggregation_settings.value
        ),
    ],
    "method": [
        AggregationFieldInfoOld("aggregation_method", str),
        FieldInfoAPI("method", str, None),
        FieldInfoSqlite(
            "aggregation_method", str, SettingsTables.aggregation_settings.value
        ),
    ],
    "interval": [
        AggregationFieldInfoOld("timestep", float),
        FieldInfoAPI("interval", float, None),
        FieldInfoSqlite("timestep", str, SettingsTables.aggregation_settings.value),
    ],
}


settings_map = {
    **physical_settings_map,
    **time_step_settings_map,
    **numerical_settings_map,
}


swagger_definitions_map = {
    "PhysicalSettings": physical_settings_map,
    "NumericalSettings": numerical_settings_map,
    "TimeStepSettings": time_step_settings_map,
    "AggregationSettings": aggregation_settings_map,
}

swagger_url_map = {
    "PhysicalSettings": "/simulations/{simulation_pk}/settings/physical/",
    "NumericalSettings": "/simulations/{simulation_pk}/settings/numerical/",
    "TimeStepSettings": "/simulations/{simulation_pk}/settings/time_step/",
    "AggregationSettings": "/simulations/{simulation_pk}/settings/aggregation/",
}


def get_sqlite_table_schemas() -> Dict[str, List[str]]:
    """
    :returns a dict of all {<settings table name>: [<field name>, ...]}
    """
    mappings = {**settings_map, **aggregation_settings_map}
    d = defaultdict(list)
    for field_info in mappings.values():
        _, _, sqlite_info = field_info
        st = SettingsTables(sqlite_info.table_name)
        d[st].append(sqlite_info.name)

    return d


def sqlalchemy_to_api_model(
    config_dict: Dict, api_model: Any, mapping: dict, extra_exclude: Tuple = None
):
    data = {}
    exclude = {"url", "id", "simulation_id"}
    if extra_exclude is not None:
        exclude = tuple(list(exclude) + list(extra_exclude))

    for name in api_model.openapi_types.keys():
        if name.lower() in exclude:
            continue
        _, api_field_info, field_info = mapping[name]
        value = config_dict[field_info.name]

        if isinstance(value, Enum):
            value = value.value

        try:
            value = field_info.type(value)
            if api_field_info.type != field_info.type:
                try:
                    value = api_field_info.type(value)
                except Exception:
                    raise
        except (ValueError, TypeError):
            value = api_field_info.default
        data[name] = value
    return api_model(**data)
