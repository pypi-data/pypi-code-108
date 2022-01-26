from datetime import timedelta
from sqlalchemy.orm import Query
from sqlalchemy.orm.session import Session
from threedi_api_client.openapi.models.measure_location import MeasureLocation
from threedi_api_client.openapi.models.measure_specification import (
    MeasureSpecification,
)
from threedi_api_client.openapi.models.memory_structure_control import (
    MemoryStructureControl,
)
from threedi_api_client.openapi.models.table_structure_control import (
    TableStructureControl,
)
from threedi_modelchecker.simulation_templates.exceptions import (
    SchematisationError,
)
from threedi_modelchecker.simulation_templates.models import StructureControls
from threedi_modelchecker.simulation_templates.utils import (
    strip_dict_none_values,
)
from threedi_modelchecker.threedi_model.constants import (
    ControlTableActionTypes,
)
from threedi_modelchecker.threedi_model.constants import ControlType
from threedi_modelchecker.threedi_model.constants import (
    MeasureLocationContentTypes,
)
from threedi_modelchecker.threedi_model.constants import MeasureVariables
from threedi_modelchecker.threedi_model.models import Control
from threedi_modelchecker.threedi_model.models import ControlGroup
from threedi_modelchecker.threedi_model.models import ControlMeasureGroup
from threedi_modelchecker.threedi_model.models import ControlMeasureMap
from threedi_modelchecker.threedi_model.models import ControlMemory
from threedi_modelchecker.threedi_model.models import ControlTable
from typing import Dict
from typing import List
from typing import Union


INFINITE_SIM_DURATION = int((timedelta(days=365) * 100).total_seconds())


def control_measure_map_to_measure_location(
    c_measure_map: ControlMeasureMap,
) -> MeasureLocation:
    # Connection nodes should be only option here.
    CONTENT_TYPE_MAP = {
        MeasureLocationContentTypes.v2_connection_nodes: "v2_connection_node"
    }

    return MeasureLocation(
        weight=str(round(float(c_measure_map.weight), 2)),
        content_type=CONTENT_TYPE_MAP[c_measure_map.object_type],
        content_pk=c_measure_map.object_id,
    )


def to_measure_specification(
    control: Union[ControlMemory, ControlTable],
    group: ControlGroup,
    locations: List[MeasureLocation],
) -> MeasureSpecification:
    VARIABLE_MAPPING = {
        MeasureVariables.waterlevel: "s1",
        MeasureVariables.volume: "vol1",
        MeasureVariables.discharge: "q",
        MeasureVariables.velocity: "u1",
    }

    # Use > as default for memory control
    operator = ">"
    if hasattr(control, "measure_operator"):
        operator = control.measure_operator.value

    return MeasureSpecification(
        name=group.name[:50] if group.name else "",
        variable=VARIABLE_MAPPING[control.measure_variable],
        locations=locations,
        operator=operator,
    )


TYPE_MAPPING = {ControlTableActionTypes.set_capacity: "set_pump_capacity"}
CAPACITY_FACTOR: float = 0.001


def parse_action_value(value) -> List[float]:
    # First clean the input:
    # - remove whitespace at the start & end (strip)
    # - replace 'internal' whitespace with ;
    # - replace commas with ;
    value = (";".join(value.strip().split())).replace(",", ";")
    # This could have yielded double semicolons (in case of <whitespace>;)
    while ";;" in value:
        value.replace(";;", ";")
    return [float(y) for y in value.split(";")]


def parse_action_table(table) -> List[List[float]]:
    """Parse an action table (for table controls)

    For table controls, the action table consists of multiple records, with
    2 or 3 values each, like:

    - "1.2;2.3#1.3;2.1#1.5;5.6"
    - "1.2;2.3;3.4#1.3;2.1;5.6#1.5;5.6;6.7"

    Sometimes, the values are separated by a space and not a semicolon (;). This
    function also accepts those inputs.
    """
    return [parse_action_value(x) for x in table.split("#")]


def to_table_control(
    control: Control,
    table_control: ControlTable,
    measure_specification: MeasureSpecification,
) -> TableStructureControl:

    action_type: str = TYPE_MAPPING.get(
        table_control.action_type, table_control.action_type.value
    )
    try:
        values = parse_action_table(table_control.action_table)
        if table_control.action_type is ControlTableActionTypes.set_capacity:
            values = [[x[0], x[1] * CAPACITY_FACTOR] for x in values]
    except (ValueError, TypeError):
        raise SchematisationError(
            f"Table control action_table incorrect format for v2_control_table.id = {table_control.id}"
        )

    try:
        control_start = int(control.start)
    except (ValueError, TypeError):
        control_start = 0

    try:
        control_end = int(control.end)
    except (ValueError, TypeError):
        control_end = INFINITE_SIM_DURATION

    return TableStructureControl(
        offset=control_start,
        duration=control_end - control_start,
        measure_specification=measure_specification,
        structure_id=table_control.target_id,
        structure_type=table_control.target_type.value,
        type=action_type,
        values=values,
    )


def to_memory_control(
    control: Control,
    memory_control: ControlMemory,
    measure_specification: MeasureSpecification,
) -> MemoryStructureControl:

    action_type: str = TYPE_MAPPING.get(
        memory_control.action_type, memory_control.action_type.value
    )

    try:
        value = parse_action_value(memory_control.action_value)
        if memory_control.action_type is ControlTableActionTypes.set_capacity:
            value = [value[0] * CAPACITY_FACTOR]
    except (ValueError, TypeError):
        raise SchematisationError(
            f"Memory control action_value incorrect format for v2_control_memory.id = {memory_control.id}"
        )

    try:
        control_start = int(control.start)
    except (ValueError, TypeError):
        control_start = 0

    try:
        control_end = int(control.end)
    except (ValueError, TypeError):
        control_end = INFINITE_SIM_DURATION

    return MemoryStructureControl(
        offset=control_start,
        duration=control_end - control_start,
        measure_specification=measure_specification,
        structure_id=memory_control.target_id,
        structure_type=memory_control.target_type.value,
        type=action_type,
        value=value,
        upper_threshold=memory_control.upper_threshold,
        lower_threshold=memory_control.lower_threshold,
        is_inverse=bool(memory_control.is_inverse),
        is_active=bool(memory_control.is_active),
    )


class StructureControlExtractor(object):
    def __init__(self, session: Session, control_group_id: int):
        self.session = session
        self._controls = None
        self._control_group_id = control_group_id

    def __initialize_controls(self):
        if self._controls is None:
            self._controls = {"table": [], "memory": []}
            table_lookup = dict(
                [
                    (x.id, x)
                    for x in Query(ControlTable).with_session(self.session).all()
                ]
            )
            memory_lookup = dict(
                [
                    (x.id, x)
                    for x in Query(ControlMemory).with_session(self.session).all()
                ]
            )
            maps_lookup = {}

            for map_item in Query([ControlMeasureMap]).with_session(self.session).all():
                if map_item.measure_group_id not in maps_lookup:
                    maps_lookup[map_item.measure_group_id] = []
                maps_lookup[map_item.measure_group_id].append(
                    control_measure_map_to_measure_location(map_item)
                )

            all_controls = (
                Query([Control, ControlGroup, ControlMeasureGroup])
                .join(ControlGroup, ControlMeasureGroup)
                .with_session(self.session)
                .filter(
                    Control.control_group_id == self._control_group_id,
                    ControlGroup.id == self._control_group_id,
                )
                .all()
            )

            for control, group, measuregroup in all_controls:
                control: Control
                maps: List[ControlMeasureGroup] = maps_lookup[measuregroup.id]

                api_control = None

                if control.control_type is ControlType.table:
                    table: ControlTable = table_lookup[control.control_id]
                    measure_spec = to_measure_specification(table, group, maps)
                    api_control = to_table_control(control, table, measure_spec)
                elif control.control_type is ControlType.memory:
                    memory: ControlMemory = memory_lookup[control.control_id]
                    measure_spec = to_measure_specification(memory, group, maps)
                    api_control = to_memory_control(control, memory, measure_spec)
                else:
                    raise SchematisationError(
                        f"Unknown control_type '{control.control_type.value}'"
                    )
                self._controls[control.control_type.value].append(api_control)

    def all_controls(self) -> StructureControls:
        self.__initialize_controls()
        return StructureControls(**self._controls)

    @property
    def memory_controls(self) -> List[MemoryStructureControl]:
        self.__initialize_controls()
        return self._controls["memory"]

    @property
    def table_controls(self) -> List[TableStructureControl]:
        self.__initialize_controls()
        return self._controls["table"]

    def as_list(self) -> List[Dict]:
        controls = []
        for control in self.all_controls():
            control_dict = control.to_dict()
            strip_dict_none_values(control_dict)
            controls.append(control_dict)
        return controls
