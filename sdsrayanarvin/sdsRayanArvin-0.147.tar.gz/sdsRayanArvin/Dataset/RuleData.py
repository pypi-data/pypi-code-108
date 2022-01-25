from enum import Enum
from typing import Optional, List
from datetime import datetime


class Condition(Enum):
    AND = "and"
    OR = "or"


class Operation(Enum):
    BIGGER = "bigger"
    EQUAL = "equal"
    SMALLER = "smaller"


class RuleStation:
    ID_rule_station: int
    ID_rule_task: int
    ID_outputs: int

    def __init__(self, ID_rule_station: int, ID_rule_task: int, ID_outputs: int) -> None:
        self.ID_rule_station = ID_rule_station
        self.ID_rule_task = ID_rule_task
        self.ID_outputs = ID_outputs


class RuleTime:
    ID_rule_time: int
    ID_rule_task: int
    type: str

    def __init__(self, ID_rule_time: int, ID_rule_task: int, type: str) -> None:
        self.ID_rule_time = ID_rule_time
        self.ID_rule_task = ID_rule_task
        self.type = type


class RuleWeatherType(Enum):
    TEMPERATURE = "temperature"
    WIND_SPEED = "windSpeed"


class RuleWeather:
    ID_rule_weather: int
    ID_rule_task: int
    ID_farm: int
    type: RuleWeatherType

    def __init__(self, ID_rule_weather: int, ID_rule_task: int, ID_farm: int, type: RuleWeatherType) -> None:
        self.ID_rule_weather = ID_rule_weather
        self.ID_rule_task = ID_rule_task
        self.ID_farm = ID_farm
        self.type = type


class RuleTaskType(Enum):
    STATION = "station"
    TIME = "time"
    WEATHER = "weather"


class RuleTask:
    ID_rule_task: int
    ID_rule_group: int
    type: RuleTaskType
    condition: Optional[Condition]
    operation: Operation
    value: str
    rule_station: Optional[RuleStation]
    rule_weather: Optional[RuleWeather]
    rule_time: Optional[RuleTime]

    def __init__(self, ID_rule_task: int, ID_rule_group: int, type: RuleTaskType, condition: Optional[Condition], operation: Operation, value: str, rule_station: Optional[RuleStation], rule_weather: Optional[RuleWeather], rule_time: Optional[RuleTime]) -> None:
        self.ID_rule_task = ID_rule_task
        self.ID_rule_group = ID_rule_group
        self.type = type
        self.condition = condition
        self.operation = operation
        self.value = value
        if rule_station:
            self.rule_station = RuleStation(**dict(rule_station))
        if rule_weather:
            self.rule_weather = RuleWeather(**dict(rule_weather))
        if rule_time:
            self.rule_time = RuleTime(**dict(rule_time))


class RuleWorkflow:
    ID_rule_workflows: int
    ID_rule_group: int
    ID_workflows: int

    def __init__(self, ID_rule_workflows: int, ID_rule_group: int, ID_workflows: int) -> None:
        self.ID_rule_workflows = ID_rule_workflows
        self.ID_rule_group = ID_rule_group
        self.ID_workflows = ID_workflows


class RuleType(Enum):
    PROCESS = "process"
    RULE = "rule"


class Rule:
    ID_rule_group: int
    ID_org: int
    title: str
    active: int
    parent: Optional[int]
    type: RuleType
    created_at: datetime
    updated_at: datetime
    deleted_at: None
    rule_task: List[RuleTask] = []
    rule_workflows: List[RuleWorkflow] = []
    parents = []

    def __init__(self, ID_rule_group: int, ID_org: int, title: str, active: int, parent: int, type: RuleType, created_at: datetime, updated_at: datetime, deleted_at: None, rule_task: List[RuleTask], rule_workflows: List[RuleWorkflow], parents=[]) -> None:
        self.ID_rule_group = ID_rule_group
        self.ID_org = ID_org
        self.title = title
        self.active = active
        self.parent = parent
        self.type = type
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
        self.rule_task = []
        self.rule_workflows = []
        self.parents = []
        for param in rule_task:
            self.rule_task.append(RuleTask(**dict(param)))
        for param in rule_workflows:
            self.rule_workflows.append(RuleWorkflow(**dict(param)))

        self.parents: List[Rule] = RuleData(parents).data


class RuleData:
    data: List[Rule] = []

    def __init__(self, data) -> None:
        self.data = []
        for param in data:
            self.data.append(Rule(**dict(param)))
