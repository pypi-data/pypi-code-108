from typing import List, Optional
from enum import Enum
from datetime import datetime


class Output:
    ID_process_list_commands_output: int
    ID_process_list_commands: int
    ID_outputs: int
    output_active: bool

    def __init__(self, ID_process_list_commands_output: int, ID_process_list_commands: int, ID_outputs: int,
                 output_active: bool) -> None:
        self.ID_process_list_commands_output = ID_process_list_commands_output
        self.ID_process_list_commands = ID_process_list_commands
        self.ID_outputs = ID_outputs
        self.output_active = output_active


class Percent:
    ID_process_list_commands_percent: int
    ID_process_list_commands: int
    time: int
    active_percent: int

    def __init__(self, ID_process_list_commands_percent: int, ID_process_list_commands: int, time: int,
                 active_percent: int) -> None:
        self.ID_process_list_commands_percent = ID_process_list_commands_percent
        self.ID_process_list_commands = ID_process_list_commands
        self.time = time
        self.active_percent = active_percent


class Command:
    ID_process_list_commands: int
    ID_process_list: int
    ID_stations: int
    ID_expansions: int
    visual_outputs: bool
    output: List[Output] = []
    percent: Optional[Percent]

    def __init__(self, ID_process_list_commands: int, ID_process_list: int, ID_stations: int, ID_expansions: int,
                 visual_outputs: bool, output: List[Output], percent: Optional[Percent]) -> None:
        self.ID_process_list_commands = ID_process_list_commands
        self.ID_process_list = ID_process_list
        self.ID_stations = ID_stations
        self.ID_expansions = ID_expansions
        self.visual_outputs = visual_outputs
        self.output = []
        for param in output:
            self.output.append(Output(**dict(param)))
        if percent:
            self.percent = Percent(**dict(percent))


class Delay:
    ID_process_list_delay: int
    ID_process_list: int
    delay: int

    def __init__(self, ID_process_list_delay: int, ID_process_list: int, delay: int) -> None:
        self.ID_process_list_delay = ID_process_list_delay
        self.ID_process_list = ID_process_list
        self.delay = delay


class CommunicationType(Enum):
    SMS = "sms"
    MQTT = "mqtt"


class Communicate:
    ID_communications: int
    ID_process_list: int
    to: str
    command: str
    type: CommunicationType

    def __init__(self, ID_communications: int, ID_process_list: int, to: str, command: str,
                 type: CommunicationType) -> None:
        self.ID_communications = ID_communications
        self.ID_process_list = ID_process_list
        self.to = to
        self.command = command
        self.type = type


class ProcessListType(Enum):
    COMMAND = "command"
    DELAY = "delay"
    PERCENT = "percent"
    RULE = "rule"
    VISUAL_COMMAND = "visual_command"


class Rule:
    ID_process_list_rule: int
    ID_process_list: int
    ID_rules: int

    def __init__(self, ID_process_list_rule: int, ID_process_list: int, ID_rules: int) -> None:
        self.ID_process_list_rule = ID_process_list_rule
        self.ID_process_list = ID_process_list
        self.ID_rules = ID_rules


class ProcessList:
    ID_process_list: int
    ID_workflows: int
    process_list_type: ProcessListType
    position: int
    created_at: datetime
    updated_at: datetime
    command: Optional[Command]
    rule: Optional[Rule]
    delay: Optional[Delay]
    communicate: Optional[Communicate]

    def __init__(self, ID_process_list: int, ID_workflows: int, process_list_type: ProcessListType, position: int,
                 created_at: datetime, updated_at: datetime, command: Optional[Command], rule: Optional[Rule],
                 delay: Optional[Delay], communicate: Optional[Communicate]) -> None:
        self.ID_process_list = ID_process_list
        self.ID_workflows = ID_workflows
        self.process_list_type = process_list_type
        self.position = position
        self.created_at = created_at
        self.updated_at = updated_at
        if command:
            self.command = Command(**dict(command))
        if rule:
            self.rule = Rule(**dict(rule))
        if delay:
            self.delay = Delay(**dict(delay))
        if communicate:
            self.communicate = Communicate(**dict(communicate))


class WorkflowType(Enum):
    READ = "write"
    WRITE = "read"


class Workflow:
    ID_workflows: int
    ID_org: int
    title: str
    type: WorkflowType
    created_at: datetime
    updated_at: datetime
    deleted_at: None
    process_lists: List[ProcessList] = []

    def __init__(self, ID_workflows: int, ID_org: int, title: str, type: WorkflowType, created_at: datetime,
                 updated_at: datetime,
                 deleted_at: None, process_lists: List[ProcessList]) -> None:
        self.ID_workflows = ID_workflows
        self.ID_org = ID_org
        self.title = title
        self.type = type
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at
        self.process_lists = []
        for param in process_lists:
            self.process_lists.append(ProcessList(**dict(param)))


class WorkflowsData:
    data: Workflow

    def __init__(self, data) -> None:
        self.data = Workflow(**dict(data))


def WorkflowsOnIDLocal(WorkflowsData: List[Workflow], ID_workflows):
    for workflows in WorkflowsData:
        if int(workflows.ID_workflows) == int(ID_workflows):
            return workflows

    return None
