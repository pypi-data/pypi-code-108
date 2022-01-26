from .checks import geo_query
from .checks.base import BaseCheck
from .checks.base import CheckLevel
from .checks.base import FileExistsCheck
from .checks.base import ForeignKeyCheck
from .checks.base import NotNullCheck
from .checks.base import QueryCheck
from .checks.base import RangeCheck
from .checks.cross_section_definitions import CrossSectionEqualElementsCheck
from .checks.cross_section_definitions import (
    CrossSectionFirstElementNonZeroCheck,
)
from .checks.cross_section_definitions import CrossSectionFloatCheck
from .checks.cross_section_definitions import CrossSectionFloatListCheck
from .checks.cross_section_definitions import CrossSectionIncreasingCheck
from .checks.cross_section_definitions import CrossSectionNonZeroCheck
from .checks.cross_section_definitions import CrossSectionNullCheck
from .checks.factories import generate_enum_checks
from .checks.factories import generate_foreign_key_checks
from .checks.factories import generate_geometry_checks
from .checks.factories import generate_geometry_type_checks
from .checks.factories import generate_not_null_checks
from .checks.factories import generate_type_checks
from .checks.factories import generate_unique_checks
from .checks.other import BoundaryCondition1DObjectNumberCheck
from .checks.other import ConnectionNodesDistance
from .checks.other import ConnectionNodesLength
from .checks.other import CrossSectionLocationCheck
from .checks.other import LinestringLocationCheck
from .checks.other import OpenChannelsWithNestedNewton
from .checks.other import Use0DFlowCheck
from .checks.timeseries import TimeseriesIncreasingCheck
from .checks.timeseries import TimeseriesRowCheck
from .checks.timeseries import TimeseriesTimestepCheck
from .checks.timeseries import TimeseriesValueCheck
from .threedi_model import models
from .threedi_model.models import constants
from sqlalchemy import func
from sqlalchemy.orm import Query
from typing import List


def is_none_or_empty(col):
    return (col == None) | (col == "")


CONDITIONS = {
    "has_dem": Query(models.GlobalSetting).filter(
        ~is_none_or_empty(models.GlobalSetting.dem_file)
    ),
    "has_no_dem": Query(models.GlobalSetting).filter(
        is_none_or_empty(models.GlobalSetting.dem_file)
    ),
    "0d_surf": Query(models.GlobalSetting).filter(
        models.GlobalSetting.use_0d_inflow == constants.InflowType.SURFACE
    ),
    "0d_imp": Query(models.GlobalSetting).filter(
        models.GlobalSetting.use_0d_inflow == constants.InflowType.IMPERVIOUS_SURFACE
    ),
}

CHECKS: List[BaseCheck] = []

## 002x: FRICTION
CHECKS += [
    RangeCheck(
        error_code=21,
        column=table.friction_value,
        min_value=0,
    )
    for table in [
        models.CrossSectionLocation,
        models.Culvert,
        models.Pipe,
    ]
]
CHECKS += [
    RangeCheck(
        error_code=21,
        column=table.friction_value,
        filters=(table.crest_type == constants.CrestType.BROAD_CRESTED.value),
        min_value=0,
    )
    for table in [
        models.Orifice,
        models.Weir,
    ]
]
CHECKS += [
    RangeCheck(
        error_code=22,
        level=CheckLevel.WARNING,
        column=table.friction_value,
        filters=table.friction_type == constants.FrictionType.MANNING.value,
        max_value=1,
        right_inclusive=False,  # 1 is not allowed
        message=f"{table.__tablename__}.friction_value is not less than 1 while MANNING friction is selected. CHEZY friction will be used instead. In the future this will lead to an error.",
    )
    for table in [
        models.CrossSectionLocation,
        models.Culvert,
        models.Pipe,
    ]
]
CHECKS += [
    RangeCheck(
        error_code=23,
        level=CheckLevel.WARNING,
        column=table.friction_value,
        filters=(table.friction_type == constants.FrictionType.MANNING.value)
        & (table.crest_type == constants.CrestType.BROAD_CRESTED.value),
        max_value=1,
        right_inclusive=False,  # 1 is not allowed
        message=f"{table.__tablename__}.friction_value is not less than 1 while MANNING friction is selected. CHEZY friction will be used instead. In the future this will lead to an error.",
    )
    for table in [
        models.Orifice,
        models.Weir,
    ]
]
CHECKS += [
    NotNullCheck(
        error_code=24,
        column=table.friction_value,
        filters=table.crest_type == constants.CrestType.BROAD_CRESTED.value,
    )
    for table in [models.Orifice, models.Weir]
]
CHECKS += [
    NotNullCheck(
        error_code=25,
        column=table.friction_type,
        filters=table.crest_type == constants.CrestType.BROAD_CRESTED.value,
    )
    for table in [models.Orifice, models.Weir]
]


## 003x: CALCULATION TYPE

CHECKS += [
    QueryCheck(
        error_code=31,
        column=models.Channel.calculation_type,
        filters=CONDITIONS["has_no_dem"].exists(),
        invalid=Query(models.Channel).filter(
            models.Channel.calculation_type.in_(
                [
                    constants.CalculationType.EMBEDDED,
                    constants.CalculationType.CONNECTED,
                    constants.CalculationType.DOUBLE_CONNECTED,
                ]
            ),
        ),
        message=f"v2_channel.calculation_type cannot be "
        f"{constants.CalculationType.EMBEDDED}, "
        f"{constants.CalculationType.CONNECTED} or "
        f"{constants.CalculationType.DOUBLE_CONNECTED} when "
        f"v2_global_settings.dem_file is null",
    )
]

## 004x: VARIOUS OBJECT SETTINGS
CHECKS += [
    RangeCheck(
        error_code=41,
        column=table.discharge_coefficient_negative,
        min_value=0,
    )
    for table in [models.Culvert, models.Weir, models.Orifice]
]
CHECKS += [
    RangeCheck(
        error_code=42,
        column=table.discharge_coefficient_positive,
        min_value=0,
    )
    for table in [models.Culvert, models.Weir, models.Orifice]
]
CHECKS += [
    RangeCheck(
        error_code=43,
        level=CheckLevel.WARNING,
        column=table.dist_calc_points,
        min_value=0,
        left_inclusive=False,  # 0 itself is not allowed
        message=f"{table.__tablename__}.dist_calc_points is not greater than 0, in the future this will lead to an error",
    )
    for table in [models.Channel, models.Pipe, models.Culvert]
]
CHECKS += [
    QueryCheck(
        error_code=44,
        column=models.ConnectionNode.storage_area,
        invalid=Query(models.ConnectionNode)
        .join(models.Manhole)
        .filter(models.ConnectionNode.storage_area < 0),
        message="v2_connection_nodes.storage_area is not greater than or equal to 0",
    ),
]


## 005x: CROSS SECTIONS

CHECKS += [
    CrossSectionLocationCheck(
        level=CheckLevel.WARNING, max_distance=1.0, error_code=52
    ),
    OpenChannelsWithNestedNewton(error_code=53),
    QueryCheck(
        error_code=54,
        level=CheckLevel.WARNING,
        column=models.CrossSectionLocation.reference_level,
        invalid=Query(models.CrossSectionLocation).filter(
            models.CrossSectionLocation.reference_level
            > models.CrossSectionLocation.bank_level,
        ),
        message="v2_cross_section_location.bank_level will be ignored if it is below the reference_level",
    ),
    QueryCheck(
        error_code=55,
        column=models.Channel.id,
        invalid=Query(models.Channel).filter(
            ~models.Channel.cross_section_locations.any()
        ),
        message="v2_channel has no cross section locations",
    ),
]

## 006x: PUMPSTATIONS

CHECKS += [
    QueryCheck(
        error_code=61,
        column=models.Pumpstation.upper_stop_level,
        invalid=Query(models.Pumpstation).filter(
            models.Pumpstation.upper_stop_level <= models.Pumpstation.start_level,
        ),
        message="v2_pumpstation.upper_stop_level should be greater than v2_pumpstation.start_level",
    ),
    QueryCheck(
        error_code=62,
        column=models.Pumpstation.lower_stop_level,
        invalid=Query(models.Pumpstation).filter(
            models.Pumpstation.lower_stop_level >= models.Pumpstation.start_level,
        ),
        message="v2_pumpstation.lower_stop_level should be less than v2_pumpstation.start_level",
    ),
    RangeCheck(
        error_code=64,
        column=models.Pumpstation.capacity,
        min_value=0,
    ),
    QueryCheck(
        error_code=65,
        level=CheckLevel.WARNING,
        column=models.Pumpstation.capacity,
        invalid=Query(models.Pumpstation).filter(models.Pumpstation.capacity == 0.0),
        message="v2_pumpstation.capacity should be be greater than 0",
    ),
]

## 007x: BOUNDARY CONDITIONS

CHECKS += [
    QueryCheck(
        error_code=71,
        column=models.BoundaryCondition1D.connection_node_id,
        invalid=Query(models.BoundaryCondition1D).filter(
            (
                models.BoundaryCondition1D.connection_node_id
                == models.Pumpstation.connection_node_start_id
            )
            | (
                models.BoundaryCondition1D.connection_node_id
                == models.Pumpstation.connection_node_end_id
            ),
        ),
        message="v2_1d_boundary_conditions cannot be connected to a pumpstation",
    ),
    # 1d boundary conditions should be connected to exactly 1 object
    BoundaryCondition1DObjectNumberCheck(error_code=72),
]

## 008x: CROSS SECTION DEFINITIONS

CHECKS += [
    CrossSectionNullCheck(
        error_code=81,
        column=models.CrossSectionDefinition.width,
        shapes=None,  # all shapes
    ),
    CrossSectionNullCheck(
        error_code=82,
        column=models.CrossSectionDefinition.height,
        shapes=(
            constants.CrossSectionShape.CLOSED_RECTANGLE,
            constants.CrossSectionShape.TABULATED_RECTANGLE,
            constants.CrossSectionShape.TABULATED_TRAPEZIUM,
        ),
    ),
    CrossSectionFloatCheck(
        error_code=83,
        column=models.CrossSectionDefinition.width,
        shapes=(
            constants.CrossSectionShape.RECTANGLE,
            constants.CrossSectionShape.CIRCLE,
            constants.CrossSectionShape.CLOSED_RECTANGLE,
            constants.CrossSectionShape.EGG,
        ),
    ),
    CrossSectionFloatCheck(
        error_code=84,
        column=models.CrossSectionDefinition.height,
        shapes=(constants.CrossSectionShape.CLOSED_RECTANGLE,),
    ),
    CrossSectionNonZeroCheck(
        error_code=85,
        level=CheckLevel.WARNING,
        column=models.CrossSectionDefinition.width,
        shapes=(
            constants.CrossSectionShape.RECTANGLE,
            constants.CrossSectionShape.CIRCLE,
            constants.CrossSectionShape.CLOSED_RECTANGLE,
            constants.CrossSectionShape.EGG,
        ),
    ),
    CrossSectionNonZeroCheck(
        error_code=86,
        level=CheckLevel.WARNING,
        column=models.CrossSectionDefinition.height,
        shapes=(constants.CrossSectionShape.CLOSED_RECTANGLE,),
    ),
    CrossSectionFloatListCheck(
        error_code=87,
        column=models.CrossSectionDefinition.width,
        shapes=(
            constants.CrossSectionShape.TABULATED_RECTANGLE,
            constants.CrossSectionShape.TABULATED_TRAPEZIUM,
        ),
    ),
    CrossSectionFloatListCheck(
        error_code=88,
        column=models.CrossSectionDefinition.height,
        shapes=(
            constants.CrossSectionShape.TABULATED_RECTANGLE,
            constants.CrossSectionShape.TABULATED_TRAPEZIUM,
        ),
    ),
    CrossSectionEqualElementsCheck(
        error_code=89,
        shapes=(
            constants.CrossSectionShape.TABULATED_RECTANGLE,
            constants.CrossSectionShape.TABULATED_TRAPEZIUM,
        ),
    ),
    CrossSectionIncreasingCheck(
        error_code=90,
        column=models.CrossSectionDefinition.height,
        shapes=(
            constants.CrossSectionShape.TABULATED_RECTANGLE,
            constants.CrossSectionShape.TABULATED_TRAPEZIUM,
        ),
    ),
    CrossSectionFirstElementNonZeroCheck(
        error_code=91,
        level=CheckLevel.WARNING,
        column=models.CrossSectionDefinition.width,
        shapes=(constants.CrossSectionShape.TABULATED_RECTANGLE,),
    ),
]


## 01xx: LEVEL CHECKS

CHECKS += [
    QueryCheck(
        level=CheckLevel.WARNING,
        error_code=102,
        column=table.invert_level_start_point,
        invalid=Query(table)
        .join(
            models.ConnectionNode,
            table.connection_node_start_id == models.ConnectionNode.id,
        )
        .join(models.Manhole)
        .filter(
            table.invert_level_start_point < models.Manhole.bottom_level,
        ),
        message=f"{table.__tablename__}.invert_level_start_point should be higher than or equal to v2_manhole.bottom_level. In the future, this will lead to an error.",
    )
    for table in [models.Pipe, models.Culvert]
]
CHECKS += [
    QueryCheck(
        level=CheckLevel.WARNING,
        error_code=103,
        column=table.invert_level_end_point,
        invalid=Query(table)
        .join(
            models.ConnectionNode,
            table.connection_node_end_id == models.ConnectionNode.id,
        )
        .join(models.Manhole)
        .filter(
            table.invert_level_end_point < models.Manhole.bottom_level,
        ),
        message=f"{table.__tablename__}.invert_level_end_point should be higher than or equal to v2_manhole.bottom_level. In the future, this will lead to an error.",
    )
    for table in [models.Pipe, models.Culvert]
]
CHECKS += [
    QueryCheck(
        level=CheckLevel.WARNING,
        error_code=104,
        column=models.Pumpstation.lower_stop_level,
        invalid=Query(models.Pumpstation)
        .join(
            models.ConnectionNode,
            models.Pumpstation.connection_node_start_id == models.ConnectionNode.id,
        )
        .join(models.Manhole)
        .filter(
            models.Pumpstation.type_ == constants.PumpType.SUCTION_SIDE,
            models.Pumpstation.lower_stop_level <= models.Manhole.bottom_level,
        ),
        message="v2_pumpstation.lower_stop_level should be higher than "
        "v2_manhole.bottom_level. In the future, this will lead to an error.",
    ),
    QueryCheck(
        level=CheckLevel.WARNING,
        error_code=105,
        column=models.Pumpstation.lower_stop_level,
        invalid=Query(models.Pumpstation)
        .join(
            models.ConnectionNode,
            models.Pumpstation.connection_node_end_id == models.ConnectionNode.id,
        )
        .join(models.Manhole)
        .filter(
            models.Pumpstation.type_ == constants.PumpType.DELIVERY_SIDE,
            models.Pumpstation.lower_stop_level <= models.Manhole.bottom_level,
        ),
        message="v2_pumpstation.lower_stop_level should be higher than "
        "v2_manhole.bottom_level. In the future, this will lead to an error.",
    ),
    QueryCheck(
        level=CheckLevel.WARNING,
        error_code=106,
        column=models.Manhole.bottom_level,
        invalid=Query(models.Manhole).filter(
            models.Manhole.drain_level < models.Manhole.bottom_level,
            models.Manhole.calculation_type.in_(
                [constants.CalculationTypeNode.CONNECTED]
            ),
        ),
        message="v2_manhole.drain_level >= v2_manhole.bottom_level when "
        "v2_manhole.calculation_type is CONNECTED. In the future, this will lead to an error.",
    ),
    QueryCheck(
        level=CheckLevel.WARNING,
        error_code=107,
        column=models.Manhole.drain_level,
        filters=CONDITIONS["has_no_dem"]
        .filter(models.GlobalSetting.manhole_storage_area > 0)
        .exists(),
        invalid=Query(models.Manhole).filter(
            models.Manhole.calculation_type.in_(
                [constants.CalculationTypeNode.CONNECTED]
            ),
            models.Manhole.drain_level == None,
        ),
        message="v2_manhole.drain_level cannot be null when using sub-basins (v2_global_settings.manhole_storage_area > 0) and no DEM is supplied.",
    ),
]

## 020x: Spatial checks

CHECKS += [ConnectionNodesDistance(error_code=201, minimum_distance=0.001)]
CHECKS += [
    QueryCheck(
        error_code=202,
        level=CheckLevel.WARNING,
        column=table.id,
        invalid=Query(table).filter(geo_query.length(table.the_geom) < 0.05),
        message=f"Length of a {table} is very short (< 0.05 m). A length of at least 1.0 m is recommended.",
    )
    for table in [models.Channel, models.Culvert]
]
CHECKS += [
    ConnectionNodesLength(
        error_code=203,
        level=CheckLevel.WARNING,
        column=models.Pipe.id,
        start_node=models.Pipe.connection_node_start,
        end_node=models.Pipe.connection_node_end,
        min_distance=0.05,
    )
]
CHECKS += [
    ConnectionNodesLength(
        error_code=204,
        level=CheckLevel.WARNING,
        column=table.id,
        filters=table.crest_type == constants.CrestType.BROAD_CRESTED,
        start_node=table.connection_node_start,
        end_node=table.connection_node_end,
        min_distance=0.05,
    )
    for table in [models.Orifice, models.Weir]
]
CHECKS += [
    LinestringLocationCheck(error_code=205, column=table.the_geom, max_distance=1)
    for table in [models.Channel, models.Culvert]
]


## 025x: Connectivity

CHECKS += [
    QueryCheck(
        error_code=251,
        level=CheckLevel.WARNING,
        column=models.ConnectionNode.id,
        invalid=Query(models.ConnectionNode)
        .join(models.Manhole)
        .filter(
            models.Manhole.calculation_type == constants.CalculationTypeNode.ISOLATED,
            models.ConnectionNode.id.notin_(
                Query(models.Pipe.connection_node_start_id).union_all(
                    Query(models.Pipe.connection_node_end_id),
                    Query(models.Channel.connection_node_start_id),
                    Query(models.Channel.connection_node_end_id),
                    Query(models.Culvert.connection_node_start_id),
                    Query(models.Culvert.connection_node_end_id),
                    Query(models.Weir.connection_node_start_id),
                    Query(models.Weir.connection_node_end_id),
                    Query(models.Pumpstation.connection_node_start_id),
                    Query(models.Pumpstation.connection_node_end_id),
                    Query(models.Orifice.connection_node_start_id),
                    Query(models.Orifice.connection_node_end_id),
                )
            ),
        ),
        message="This is an isolated connection node without connections. Connect it to either a pipe, "
        "channel, culvert, weir, orifice or pumpstation.",
    ),
    QueryCheck(
        level=CheckLevel.WARNING,
        error_code=252,
        column=models.Pipe.id,
        invalid=Query(models.Pipe)
        .join(
            models.ConnectionNode,
            models.Pipe.connection_node_start_id == models.ConnectionNode.id,
        )
        .filter(
            models.Pipe.calculation_type == constants.PipeCalculationType.ISOLATED,
            models.ConnectionNode.storage_area.is_(None),
        )
        .union(
            Query(models.Pipe)
            .join(
                models.ConnectionNode,
                models.Pipe.connection_node_end_id == models.ConnectionNode.id,
            )
            .filter(
                models.Pipe.calculation_type == constants.PipeCalculationType.ISOLATED,
                models.ConnectionNode.storage_area.is_(None),
            )
        ),
        message="When connecting two isolated pipes, it is recommended to add storage to the connection node.",
    ),
]
CHECKS += [
    QueryCheck(
        error_code=253,
        column=table.connection_node_end_id,
        invalid=Query(table).filter(
            table.connection_node_start_id == table.connection_node_end_id
        ),
        message=f"a {table.__tablename__} cannot be connected to itself (connection_node_start_id must not equal connection_node_end_id)",
    )
    for table in (
        models.Channel,
        models.Culvert,
        models.Orifice,
        models.Pipe,
        models.Pumpstation,
        models.Weir,
    )
]


## 030x: SETTINGS

CHECKS += [
    QueryCheck(
        error_code=302,
        column=models.GlobalSetting.dem_obstacle_detection,
        invalid=Query(models.GlobalSetting).filter(
            models.GlobalSetting.dem_obstacle_detection == True,
        ),
        message="v2_global_settings.dem_obstacle_detection is True, while this feature is not supported",
    ),
    QueryCheck(
        error_code=303,
        level=CheckLevel.WARNING,
        column=models.GlobalSetting.use_1d_flow,
        invalid=Query(models.GlobalSetting).filter(
            models.GlobalSetting.use_1d_flow == False,
            Query(func.count(models.ConnectionNode.id) > 0).label("1d_count"),
        ),
        message="v2_global_settings.use_1d_flow is turned off while there are 1D "
        "elements in the model",
    ),
    QueryCheck(
        error_code=304,
        column=models.GlobalSetting.groundwater_settings_id,
        invalid=Query(models.GlobalSetting).filter(
            models.GlobalSetting.groundwater_settings_id != None,
            models.GlobalSetting.simple_infiltration_settings != None,
        ),
        message="simple_infiltration in combination with groundwater flow is not allowed.",
    ),
    RangeCheck(
        error_code=305,
        column=models.GlobalSetting.kmax,
        min_value=0,
        left_inclusive=False,  # 0 is not allowed
    ),
    RangeCheck(
        error_code=306,
        level=CheckLevel.WARNING,
        column=models.GlobalSetting.dist_calc_points,
        min_value=0,
        left_inclusive=False,  # 0 itself is not allowed
        message="v2_global_settings.dist_calc_points is not greater than 0, in the future this will lead to an error",
    ),
    RangeCheck(
        error_code=307,
        column=models.GlobalSetting.grid_space,
        min_value=0,
        left_inclusive=False,  # 0 itself is not allowed
    ),
    RangeCheck(
        error_code=308,
        column=models.GlobalSetting.embedded_cutoff_threshold,
        min_value=0,
    ),
    RangeCheck(
        error_code=309,
        column=models.GlobalSetting.max_angle_1d_advection,
        min_value=0,
        max_value=0.5 * 3.14159,
    ),
    RangeCheck(
        error_code=310,
        column=models.GlobalSetting.table_step_size,
        min_value=0,
        left_inclusive=False,
    ),
    RangeCheck(
        error_code=311,
        column=models.GlobalSetting.table_step_size_1d,
        min_value=0,
        left_inclusive=False,
    ),
    RangeCheck(
        error_code=312,
        column=models.GlobalSetting.table_step_size_volume_2d,
        min_value=0,
        left_inclusive=False,
    ),
    RangeCheck(
        error_code=313,
        column=models.GlobalSetting.frict_coef,
        filters=models.GlobalSetting.frict_type == constants.FrictionType.MANNING,
        min_value=0,
        max_value=1,
    ),
    RangeCheck(
        error_code=314,
        column=models.GlobalSetting.frict_coef,
        filters=models.GlobalSetting.frict_type == constants.FrictionType.CHEZY,
        min_value=0,
    ),
    RangeCheck(
        error_code=315,
        column=models.GlobalSetting.interception_global,
        min_value=0,
    ),
    RangeCheck(
        error_code=316,
        column=models.GlobalSetting.manhole_storage_area,
        min_value=0,
    ),
    QueryCheck(
        error_code=317,
        column=models.GlobalSetting.epsg_code,
        invalid=CONDITIONS["has_no_dem"].filter(models.GlobalSetting.epsg_code == None),
        message="v2_global_settings.epsg_code may not be NULL if no dem file is provided",
    ),
    QueryCheck(
        error_code=318,
        level=CheckLevel.WARNING,
        column=models.GlobalSetting.epsg_code,
        invalid=CONDITIONS["has_dem"].filter(models.GlobalSetting.epsg_code == None),
        message="if v2_global_settings.epsg_code is NULL, it will be extracted from the DEM later, however, the modelchecker will use ESPG:28992 for its spatial checks",
    ),
    QueryCheck(
        error_code=319,
        column=models.GlobalSetting.use_2d_flow,
        invalid=CONDITIONS["has_no_dem"].filter(
            models.GlobalSetting.use_2d_flow == True
        ),
        message="v2_global_settings.use_2d_flow may not be TRUE if no dem file is provided",
    ),
    QueryCheck(
        error_code=320,
        column=models.GlobalSetting.use_2d_flow,
        invalid=Query(models.GlobalSetting).filter(
            models.GlobalSetting.use_1d_flow == False,
            models.GlobalSetting.use_2d_flow == False,
        ),
        message="v2_global_settings.use_1d_flow and v2_global_settings.use_2d_flow cannot both be FALSE",
    ),
    QueryCheck(
        level=CheckLevel.WARNING,
        error_code=321,
        column=models.GlobalSetting.manhole_storage_area,
        invalid=Query(models.GlobalSetting).filter(
            models.GlobalSetting.manhole_storage_area > 0,
            (
                (models.GlobalSetting.use_2d_flow == True)
                | (~is_none_or_empty(models.GlobalSetting.dem_file))
            ),
        ),
        message="sub-basins (v2_global_settings.manhole_storage_area > 0) should only be used when there is no DEM supplied and there is no 2D flow",
    ),
    QueryCheck(
        error_code=322,
        column=models.GlobalSetting.water_level_ini_type,
        invalid=Query(models.GlobalSetting).filter(
            ~is_none_or_empty(models.GlobalSetting.initial_waterlevel_file),
            models.GlobalSetting.water_level_ini_type == None,
        ),
        message="an initial waterlevel type (v2_global_settings.water_level_ini_type) should be defined when using an initial waterlevel file.",
    ),
]

## 04xx: Groundwater, Interflow & Infiltration
CHECKS += [
    RangeCheck(
        error_code=401,
        column=models.Interflow.porosity,
        filters=models.Interflow.global_settings != None,
        min_value=0,
        max_value=1,
    ),
    RangeCheck(
        error_code=402,
        column=models.Interflow.impervious_layer_elevation,
        filters=models.Interflow.global_settings != None,
        min_value=0,
    ),
    RangeCheck(
        error_code=403,
        column=models.SimpleInfiltration.infiltration_rate,
        filters=models.SimpleInfiltration.global_settings != None,
        min_value=0,
    ),
    QueryCheck(
        error_code=404,
        column=models.SimpleInfiltration.infiltration_rate,
        invalid=Query(models.SimpleInfiltration).filter(
            models.SimpleInfiltration.global_settings != None,
            models.SimpleInfiltration.infiltration_rate == None,
            is_none_or_empty(models.SimpleInfiltration.infiltration_rate_file),
        ),
        message="a global simple infiltration rate (v2_simple_infiltration.infiltration_rate) should be defined when not using a simple infiltration rate file.",
    ),
    QueryCheck(
        error_code=405,
        column=models.GroundWater.equilibrium_infiltration_rate,
        invalid=Query(models.GroundWater).filter(
            models.GroundWater.global_settings != None,
            (models.GroundWater.equilibrium_infiltration_rate == None)
            | (models.GroundWater.equilibrium_infiltration_rate < 0),
            is_none_or_empty(
                models.GroundWater.equilibrium_infiltration_rate_file,
            ),
        ),
        message="a global equilibrium infiltration rate (v2_groundwater.equilibrium_infiltration_rate) should be defined and >=0 when not using an equilibrium infiltration rate file.",
    ),
    QueryCheck(
        error_code=406,
        column=models.GroundWater.equilibrium_infiltration_rate_type,
        invalid=Query(models.GroundWater).filter(
            models.GroundWater.global_settings != None,
            models.GroundWater.equilibrium_infiltration_rate_type == None,
            ~is_none_or_empty(models.GroundWater.equilibrium_infiltration_rate_file),
        ),
        message="an equilibrium infiltration rate type (v2_groundwater.equilibrium_infiltration_rate_type) should be defined when using an equilibrium infiltration rate file.",
    ),
    QueryCheck(
        error_code=407,
        column=models.GroundWater.infiltration_decay_period,
        invalid=Query(models.GroundWater).filter(
            models.GroundWater.global_settings != None,
            (models.GroundWater.infiltration_decay_period == None)
            | (models.GroundWater.infiltration_decay_period <= 0),
            is_none_or_empty(models.GroundWater.infiltration_decay_period_file),
        ),
        message="a global infiltration decay period (v2_groundwater.infiltration_decay_period) should be defined and >0 when not using an infiltration decay period file.",
    ),
    QueryCheck(
        error_code=408,
        column=models.GroundWater.infiltration_decay_period_type,
        invalid=Query(models.GroundWater).filter(
            models.GroundWater.global_settings != None,
            models.GroundWater.infiltration_decay_period_type == None,
            ~is_none_or_empty(models.GroundWater.infiltration_decay_period_file),
        ),
        message="an infiltration decay period type (v2_groundwater.infiltration_decay_period_type) should be defined when using an infiltration decay period file.",
    ),
    QueryCheck(
        error_code=409,
        column=models.GroundWater.groundwater_hydro_connectivity_type,
        invalid=Query(models.GroundWater).filter(
            models.GroundWater.global_settings != None,
            models.GroundWater.groundwater_hydro_connectivity_type == None,
            ~is_none_or_empty(models.GroundWater.groundwater_hydro_connectivity_file),
        ),
        message="a groundwater hydro connectivity type (v2_groundwater.groundwater_hydro_connectivity_type) should be defined when using a groundwater hydro connectivity file.",
    ),
    QueryCheck(
        error_code=410,
        column=models.GroundWater.groundwater_impervious_layer_level,
        invalid=Query(models.GroundWater).filter(
            models.GroundWater.global_settings != None,
            models.GroundWater.groundwater_impervious_layer_level == None,
            is_none_or_empty(
                models.GroundWater.groundwater_impervious_layer_level_file
            ),
        ),
        message="a global impervious layer level (v2_groundwater.groundwater_impervious_layer_level) should be defined when not using an impervious layer level file",
    ),
    QueryCheck(
        error_code=411,
        column=models.GroundWater.groundwater_impervious_layer_level_type,
        invalid=Query(models.GroundWater).filter(
            models.GroundWater.global_settings != None,
            models.GroundWater.groundwater_impervious_layer_level_type == None,
            ~is_none_or_empty(
                models.GroundWater.groundwater_impervious_layer_level_file
            ),
        ),
        message="a impervious layer level type (v2_groundwater.groundwater_impervious_layer_level_type) should be defined when using an impervious layer level file",
    ),
    QueryCheck(
        error_code=412,
        column=models.GroundWater.initial_infiltration_rate,
        invalid=Query(models.GroundWater).filter(
            models.GroundWater.global_settings != None,
            (models.GroundWater.initial_infiltration_rate == None)
            | (models.GroundWater.initial_infiltration_rate < 0),
            is_none_or_empty(models.GroundWater.initial_infiltration_rate_file),
        ),
        message="a global initial infiltration rate (v2_groundwater.initial_infiltration_rate) should be defined and >=0 when not using an initial infiltration rate file.",
    ),
    QueryCheck(
        error_code=413,
        column=models.GroundWater.initial_infiltration_rate_type,
        invalid=Query(models.GroundWater).filter(
            models.GroundWater.global_settings != None,
            models.GroundWater.initial_infiltration_rate_type == None,
            ~is_none_or_empty(models.GroundWater.initial_infiltration_rate_file),
        ),
        message="a initial infiltration rate type (v2_groundwater.initial_infiltration_rate_type) should be defined when using an initial infiltration rate file.",
    ),
    QueryCheck(
        error_code=414,
        column=models.GroundWater.phreatic_storage_capacity,
        invalid=Query(models.GroundWater).filter(
            models.GroundWater.global_settings != None,
            models.GroundWater.phreatic_storage_capacity == None,
            is_none_or_empty(models.GroundWater.phreatic_storage_capacity_file),
        ),
        message="a global phreatic storage capacity (v2_groundwater.phreatic_storage_capacity) should be defined when using a phreatic storage capacity file.",
    ),
    QueryCheck(
        error_code=415,
        column=models.GroundWater.phreatic_storage_capacity_type,
        invalid=Query(models.GroundWater).filter(
            models.GroundWater.global_settings != None,
            models.GroundWater.phreatic_storage_capacity_type == None,
            ~is_none_or_empty(models.GroundWater.phreatic_storage_capacity_file),
        ),
        message="a phreatic storage capacity type (v2_groundwater.phreatic_storage_capacity_type) should be defined when using a phreatic storage capacity file.",
    ),
    QueryCheck(
        error_code=416,
        column=models.Interflow.porosity,
        invalid=Query(models.Interflow).filter(
            models.Interflow.global_settings != None,
            models.Interflow.porosity == None,
            is_none_or_empty(models.Interflow.porosity_file),
            models.Interflow.interflow_type != constants.InterflowType.NO_INTERLFOW,
        ),
        message="a global porosity (v2_interflow.porosity) should be defined when not using a porosity file.",
    ),
    QueryCheck(
        error_code=417,
        column=models.Interflow.porosity_layer_thickness,
        invalid=Query(models.Interflow).filter(
            models.Interflow.global_settings != None,
            (models.Interflow.porosity_layer_thickness == None)
            | (models.Interflow.porosity_layer_thickness <= 0),
            models.Interflow.interflow_type
            in [
                constants.InterflowType.LOCAL_DEEPEST_POINT_SCALED_POROSITY,
                constants.InterflowType.GLOBAL_DEEPEST_POINT_SCALED_POROSITY,
            ],
        ),
        message=f"a porosity layer thickness (v2_interflow.porosity_layer_thickness) should be defined and >0 when "
        f"interflow_type is "
        f"{constants.InterflowType.LOCAL_DEEPEST_POINT_SCALED_POROSITY} or "
        f"{constants.InterflowType.GLOBAL_DEEPEST_POINT_SCALED_POROSITY}",
    ),
    QueryCheck(
        error_code=418,
        column=models.Interflow.impervious_layer_elevation,
        invalid=Query(models.Interflow).filter(
            models.Interflow.global_settings != None,
            models.Interflow.impervious_layer_elevation == None,
            models.Interflow.interflow_type != constants.InterflowType.NO_INTERLFOW,
        ),
        message=f"the impervious layer elevation (v2_interflow.impervious_layer_elevation) cannot be null when "
        f"v2_interflow.interflow_type is not {constants.InterflowType.NO_INTERLFOW}",
    ),
    QueryCheck(
        error_code=419,
        column=models.Interflow.hydraulic_conductivity,
        invalid=Query(models.Interflow).filter(
            models.Interflow.global_settings != None,
            (models.Interflow.hydraulic_conductivity == None)
            | (models.Interflow.hydraulic_conductivity < 0),
            is_none_or_empty(models.Interflow.hydraulic_conductivity_file),
            models.Interflow.interflow_type != constants.InterflowType.NO_INTERLFOW,
        ),
        message="v2_interflow.hydraulic_conductivity cannot be null or negative when no hydraulic conductivity file is supplied.",
    ),
    RangeCheck(
        error_code=420,
        column=models.GroundWater.phreatic_storage_capacity,
        filters=models.GroundWater.global_settings != None,
        min_value=0,
        max_value=1,
    ),
    QueryCheck(
        error_code=421,
        column=models.GroundWater.groundwater_hydro_connectivity,
        invalid=Query(models.GroundWater).filter(
            models.GroundWater.global_settings != None,
            (models.GroundWater.groundwater_hydro_connectivity < 0),
            is_none_or_empty(models.GroundWater.groundwater_hydro_connectivity_file),
        ),
        message="the global hydro connectivity (v2_groundwater.groundwater_hydro_connectivity) should be >=0 when not using an hydro connectivity file.",
    ),
]


## 06xx: INFLOW
for (surface, surface_map, filters) in [
    (models.Surface, models.SurfaceMap, CONDITIONS["0d_surf"].exists()),
    (
        models.ImperviousSurface,
        models.ImperviousSurfaceMap,
        CONDITIONS["0d_imp"].exists(),
    ),
]:
    CHECKS += [
        RangeCheck(
            error_code=601,
            column=surface.area,
            min_value=0,
            filters=filters,
        ),
        RangeCheck(
            level=CheckLevel.WARNING,
            error_code=602,
            column=surface.dry_weather_flow,
            min_value=0,
            filters=filters,
        ),
        RangeCheck(
            error_code=603,
            column=surface_map.percentage,
            min_value=0,
            filters=filters,
        ),
        RangeCheck(
            error_code=604,
            level=CheckLevel.WARNING,
            column=surface_map.percentage,
            max_value=100,
            filters=filters,
        ),
        RangeCheck(
            error_code=605,
            column=surface.nr_of_inhabitants,
            min_value=0,
            filters=filters,
        ),
        QueryCheck(
            level=CheckLevel.WARNING,
            error_code=612,
            column=surface_map.connection_node_id,
            filters=filters,
            invalid=Query(surface_map).filter(
                surface_map.connection_node_id.in_(
                    Query(models.BoundaryCondition1D.connection_node_id)
                ),
            ),
            message=f"{surface_map.__tablename__} will be ignored because it is connected to a 1D boundary condition.",
        ),
    ]


CHECKS += [
    RangeCheck(
        error_code=606,
        column=models.SurfaceParameter.outflow_delay,
        min_value=0,
        filters=filters,
    ),
    RangeCheck(
        error_code=607,
        column=models.SurfaceParameter.max_infiltration_capacity,
        min_value=0,
        filters=filters,
    ),
    RangeCheck(
        error_code=608,
        column=models.SurfaceParameter.min_infiltration_capacity,
        min_value=0,
        filters=filters,
    ),
    RangeCheck(
        error_code=609,
        column=models.SurfaceParameter.infiltration_decay_constant,
        min_value=0,
        filters=filters,
    ),
    RangeCheck(
        error_code=610,
        column=models.SurfaceParameter.infiltration_recovery_constant,
        min_value=0,
        filters=filters,
    ),
    Use0DFlowCheck(error_code=611, level=CheckLevel.WARNING),
]


# 07xx: FILE EXISTENCE
CHECKS += [
    FileExistsCheck(error_code=701, column=models.GlobalSetting.dem_file),
    FileExistsCheck(error_code=702, column=models.GlobalSetting.frict_coef_file),
    FileExistsCheck(error_code=703, column=models.GlobalSetting.interception_file),
    FileExistsCheck(
        error_code=704,
        column=models.Interflow.porosity_file,
        filters=models.Interflow.global_settings != None,
    ),
    FileExistsCheck(
        error_code=705,
        column=models.Interflow.hydraulic_conductivity_file,
        filters=models.Interflow.global_settings != None,
    ),
    FileExistsCheck(
        error_code=706,
        column=models.SimpleInfiltration.infiltration_rate_file,
        filters=models.SimpleInfiltration.global_settings != None,
    ),
    FileExistsCheck(
        error_code=707,
        column=models.SimpleInfiltration.max_infiltration_capacity_file,
        filters=models.SimpleInfiltration.global_settings != None,
    ),
    FileExistsCheck(
        error_code=708,
        column=models.GroundWater.groundwater_impervious_layer_level_file,
        filters=models.GroundWater.global_settings != None,
    ),
    FileExistsCheck(
        error_code=709,
        column=models.GroundWater.phreatic_storage_capacity_file,
        filters=models.GroundWater.global_settings != None,
    ),
    FileExistsCheck(
        error_code=710,
        column=models.GroundWater.equilibrium_infiltration_rate_file,
        filters=models.GroundWater.global_settings != None,
    ),
    FileExistsCheck(
        error_code=711,
        column=models.GroundWater.initial_infiltration_rate_file,
        filters=models.GroundWater.global_settings != None,
    ),
    FileExistsCheck(
        error_code=712,
        column=models.GroundWater.infiltration_decay_period_file,
        filters=models.GroundWater.global_settings != None,
    ),
    FileExistsCheck(
        error_code=713,
        column=models.GroundWater.groundwater_hydro_connectivity_file,
        filters=models.GroundWater.global_settings != None,
    ),
    FileExistsCheck(
        error_code=714,
        column=models.GroundWater.leakage_file,
        filters=(models.GroundWater.global_settings != None),
    ),
    FileExistsCheck(
        error_code=715,
        column=models.GlobalSetting.initial_waterlevel_file,
    ),
    FileExistsCheck(
        error_code=716,
        column=models.GlobalSetting.initial_groundwater_level_file,
        filters=(models.GlobalSetting.groundwater_settings_id != None),
    ),
]


## 110x: SIMULATION SETTINGS, timestep
CHECKS += [
    QueryCheck(
        error_code=1101,
        column=models.GlobalSetting.maximum_sim_time_step,
        invalid=Query(models.GlobalSetting).filter(
            models.GlobalSetting.maximum_sim_time_step
            < models.GlobalSetting.sim_time_step
        ),
        message="v2_global_settings.maximum_sim_time_step must be greater than or equal to v2_global_settings.sim_time_step",
    ),
    QueryCheck(
        error_code=1102,
        column=models.GlobalSetting.sim_time_step,
        invalid=Query(models.GlobalSetting).filter(
            models.GlobalSetting.minimum_sim_time_step
            > models.GlobalSetting.sim_time_step
        ),
        message="v2_global_settings.minimum_sim_time_step must be less than or equal to v2_global_settings.sim_time_step",
    ),
    QueryCheck(
        error_code=1103,
        column=models.GlobalSetting.output_time_step,
        invalid=Query(models.GlobalSetting).filter(
            models.GlobalSetting.output_time_step < models.GlobalSetting.sim_time_step
        ),
        message="v2_global_settings.output_time_step must be greater than or equal to v2_global_settings.sim_time_step",
    ),
    QueryCheck(
        error_code=1104,
        column=models.GlobalSetting.maximum_sim_time_step,
        invalid=Query(models.GlobalSetting).filter(
            models.GlobalSetting.timestep_plus == True,
            models.GlobalSetting.maximum_sim_time_step == None,
        ),
        message="v2_global_settings.maximum_sim_time_step cannot be null when "
        "v2_global_settings.timestep_plus is True",
    ),
]
CHECKS += [
    RangeCheck(
        error_code=1105,
        column=getattr(models.GlobalSetting, name),
        min_value=0,
        left_inclusive=False,
    )
    for name in (
        "sim_time_step",
        "minimum_sim_time_step",
        "maximum_sim_time_step",
        "output_time_step",
    )
]

## 111x - 114x: SIMULATION SETTINGS, numerical

CHECKS += [
    RangeCheck(
        error_code=1110,
        column=models.NumericalSettings.cfl_strictness_factor_1d,
        filters=models.NumericalSettings.global_settings != None,
        min_value=0,
        left_inclusive=False,
    ),
    RangeCheck(
        error_code=1111,
        column=models.NumericalSettings.cfl_strictness_factor_2d,
        filters=models.NumericalSettings.global_settings != None,
        min_value=0,
        left_inclusive=False,
    ),
    RangeCheck(
        error_code=1112,
        column=models.NumericalSettings.convergence_eps,
        filters=models.NumericalSettings.global_settings != None,
        min_value=1e-7,
        max_value=1e-4,
    ),
    RangeCheck(
        error_code=1113,
        column=models.NumericalSettings.convergence_cg,
        filters=models.NumericalSettings.global_settings != None,
        min_value=1e-12,
        max_value=1e-7,
    ),
    RangeCheck(
        error_code=1114,
        column=models.NumericalSettings.flow_direction_threshold,
        filters=models.NumericalSettings.global_settings != None,
        min_value=1e-13,
        max_value=1e-2,
    ),
    RangeCheck(
        error_code=1115,
        column=models.NumericalSettings.general_numerical_threshold,
        filters=models.NumericalSettings.global_settings != None,
        min_value=1e-13,
        max_value=1e-7,
    ),
    RangeCheck(
        error_code=1116,
        column=models.NumericalSettings.max_nonlin_iterations,
        filters=models.NumericalSettings.global_settings != None,
        min_value=1,
    ),
    RangeCheck(
        error_code=1117,
        column=models.NumericalSettings.max_degree,
        filters=models.NumericalSettings.global_settings != None,
        min_value=1,
    ),
    RangeCheck(
        error_code=1118,
        column=models.NumericalSettings.minimum_friction_velocity,
        filters=models.NumericalSettings.global_settings != None,
        min_value=0,
        max_value=1,
    ),
    RangeCheck(
        error_code=1119,
        column=models.NumericalSettings.minimum_surface_area,
        filters=models.NumericalSettings.global_settings != None,
        min_value=1e-13,
        max_value=1e-7,
    ),
    RangeCheck(
        error_code=1120,
        column=models.NumericalSettings.preissmann_slot,
        filters=models.NumericalSettings.global_settings != None,
        min_value=0,
    ),
    RangeCheck(
        error_code=1121,
        column=models.NumericalSettings.pump_implicit_ratio,
        filters=models.NumericalSettings.global_settings != None,
        min_value=0,
        max_value=1,
    ),
    RangeCheck(
        error_code=1122,
        column=models.NumericalSettings.thin_water_layer_definition,
        filters=models.NumericalSettings.global_settings != None,
        min_value=0,
    ),
    RangeCheck(
        error_code=1123,
        column=models.NumericalSettings.use_of_cg,
        filters=models.NumericalSettings.global_settings != None,
        min_value=1,
    ),
    RangeCheck(
        error_code=1124,
        column=models.GlobalSetting.flooding_threshold,
        min_value=0,
        max_value=0.3,
    ),
    RangeCheck(
        error_code=1124,
        level=CheckLevel.WARNING,
        column=models.GlobalSetting.flooding_threshold,
        min_value=0,
        max_value=0.05,
    ),
    QueryCheck(
        error_code=1125,
        column=models.NumericalSettings.thin_water_layer_definition,
        invalid=Query(models.NumericalSettings).filter(
            (models.NumericalSettings.global_settings != None)
            & (models.NumericalSettings.frict_shallow_water_correction == 3)
            & (models.NumericalSettings.thin_water_layer_definition <= 0)
        ),
        message="v2_numerical_settings.thin_water_layer_definition must be greater than 0 when using frict_shallow_water_correction option 3.",
    ),
    QueryCheck(
        error_code=1126,
        column=models.NumericalSettings.thin_water_layer_definition,
        invalid=Query(models.NumericalSettings).filter(
            (models.NumericalSettings.global_settings != None)
            & (models.NumericalSettings.limiter_slope_crossectional_area_2d == 3)
            & (models.NumericalSettings.thin_water_layer_definition <= 0)
        ),
        message="v2_numerical_settings.thin_water_layer_definition must be greater than 0 when using limiter_slope_crossectional_area_2d option 3.",
    ),
    QueryCheck(
        error_code=1127,
        column=models.NumericalSettings.thin_water_layer_definition,
        invalid=Query(models.NumericalSettings).filter(
            (models.NumericalSettings.global_settings != None)
            & (models.NumericalSettings.limiter_slope_friction_2d == 0)
            & (models.NumericalSettings.limiter_slope_crossectional_area_2d != 0)
        ),
        message="v2_numerical_settings.limiter_slope_friction_2d may not be 0 when using limiter_slope_crossectional_area_2d.",
    ),
]


## 115x SIMULATION SETTINGS, aggregation

CHECKS += [
    QueryCheck(
        error_code=1150,
        column=models.AggregationSettings.aggregation_method,
        invalid=Query(models.AggregationSettings).filter(
            (models.AggregationSettings.global_settings_id != None)
            & (models.AggregationSettings.aggregation_method == "current")
            & (
                models.AggregationSettings.flow_variable.notin_(
                    ("volume", "interception")
                )
            )
        ),
        message="v2_aggregation_settings.aggregation_method can only be 'current' for 'volume' or 'interception' flow_variables.",
    )
]

## 12xx  SIMULATION, timeseries
CHECKS += [
    TimeseriesRowCheck(col, error_code=1200)
    for col in [
        models.BoundaryCondition1D.timeseries,
        models.BoundaryConditions2D.timeseries,
        models.Lateral1d.timeseries,
        models.Lateral2D.timeseries,
    ]
]
CHECKS += [
    TimeseriesTimestepCheck(col, error_code=1201)
    for col in [
        models.BoundaryCondition1D.timeseries,
        models.BoundaryConditions2D.timeseries,
        models.Lateral1d.timeseries,
        models.Lateral2D.timeseries,
    ]
]
CHECKS += [
    TimeseriesValueCheck(col, error_code=1202)
    for col in [
        models.BoundaryCondition1D.timeseries,
        models.BoundaryConditions2D.timeseries,
        models.Lateral1d.timeseries,
        models.Lateral2D.timeseries,
    ]
]
CHECKS += [
    TimeseriesIncreasingCheck(col, error_code=1203)
    for col in [
        models.BoundaryCondition1D.timeseries,
        models.BoundaryConditions2D.timeseries,
        models.Lateral1d.timeseries,
        models.Lateral2D.timeseries,
    ]
]

## 122x Structure controls

CHECKS += [
    ForeignKeyCheck(
        error_code=1220,
        column=models.ControlMeasureMap.object_id,
        reference_column=models.ConnectionNode.id,
        filters=models.ControlMeasureMap.object_type == "v2_connection_node",
    )
]
CHECKS += [
    ForeignKeyCheck(
        error_code=1221,
        column=control_table.target_id,
        reference_column=models.Channel.id,
        filters=control_table.target_type == "v2_channel",
    )
    for control_table in (models.ControlMemory, models.ControlTable)
]
CHECKS += [
    ForeignKeyCheck(
        error_code=1222,
        column=control_table.target_id,
        reference_column=models.Pipe.id,
        filters=control_table.target_type == "v2_pipe",
    )
    for control_table in (models.ControlMemory, models.ControlTable)
]
CHECKS += [
    ForeignKeyCheck(
        error_code=1223,
        column=control_table.target_id,
        reference_column=models.Orifice.id,
        filters=control_table.target_type == "v2_orifice",
    )
    for control_table in (models.ControlMemory, models.ControlTable)
]
CHECKS += [
    ForeignKeyCheck(
        error_code=1224,
        column=control_table.target_id,
        reference_column=models.Culvert.id,
        filters=control_table.target_type == "v2_culvert",
    )
    for control_table in (models.ControlMemory, models.ControlTable)
]
CHECKS += [
    ForeignKeyCheck(
        error_code=1225,
        column=control_table.target_id,
        reference_column=models.Weir.id,
        filters=control_table.target_type == "v2_weir",
    )
    for control_table in (models.ControlMemory, models.ControlTable)
]
CHECKS += [
    ForeignKeyCheck(
        error_code=1226,
        column=control_table.target_id,
        reference_column=models.Pumpstation.id,
        filters=control_table.target_type == "v2_pumpstation",
    )
    for control_table in (models.ControlMemory, models.ControlTable)
]


class Config:
    """Collection of checks

    Some checks are generated by a factory. These are usually very generic
    checks which apply to many columns, such as foreign keys."""

    def __init__(self, models):
        self.models = models
        self.checks = []
        self.generate_checks()

    def generate_checks(self):
        self.checks = []
        # Error codes 1 to 9: factories
        for model in self.models:
            self.checks += generate_foreign_key_checks(
                model.__table__,
                error_code=1,
            )
            self.checks += generate_unique_checks(model.__table__, error_code=2)
            self.checks += generate_not_null_checks(
                model.__table__,
                error_code=3,
                custom_level_map={
                    "v2_grid_refinement.refinement_level": "warning",
                    "v2_grid_refinement.the_geom": "warning",
                    "v2_grid_refinement_area.refinement_level": "warning",
                    "v2_grid_refinement_area.the_geom": "warning",
                },
            )
            self.checks += generate_type_checks(
                model.__table__,
                error_code=4,
                custom_level_map={
                    "*.sewerage": "INFO",
                    "v2_weir.external": "INFO",
                    "v2_connection_nodes.the_geom_linestring": "info",
                },
            )
            self.checks += generate_geometry_checks(
                model.__table__,
                custom_level_map={
                    "v2_connection_nodes.the_geom_linestring": "info",
                    "v2_grid_refinement.the_geom": "warning",
                    "v2_grid_refinement_area.the_geom": "warning",
                    "v2_dem_average_area.the_geom": "warning",
                    "v2_surface.the_geom": "warning",
                    "v2_impervious_surface.the_geom": "warning",
                },
                error_code=5,
            )
            self.checks += generate_geometry_type_checks(
                model.__table__,
                custom_level_map={
                    "v2_connection_nodes.the_geom_linestring": "info",
                },
                error_code=6,
            )
            self.checks += generate_enum_checks(
                model.__table__,
                error_code=7,
                custom_level_map={
                    "*.zoom_category": "INFO",
                    "v2_pipe.sewerage_type": "INFO",
                    "v2_pipe.material": "INFO",
                },
            )

        self.checks += CHECKS

    def iter_checks(self, level=CheckLevel.ERROR):
        """Iterate over checks with at least 'level'"""
        level = CheckLevel.get(level)  # normalize
        for check in self.checks:
            if check.level >= level:
                yield check
