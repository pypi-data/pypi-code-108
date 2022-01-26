from __future__ import annotations

from typing import TYPE_CHECKING, List

from aasm.generating.code import Code
from aasm.generating.python_code import PythonCode
from aasm.generating.python_graph import PythonGraph
from aasm.intermediate.action import SendMessageAction
from aasm.intermediate.argument import (AgentParam, Connection, ConnectionList,
                                        EnumValue, MessageList,
                                        ReceivedMessageParam, SendMessageParam)
from aasm.intermediate.behaviour import MessageReceivedBehaviour
from aasm.intermediate.block import Block
from aasm.intermediate.declaration import Declaration
from aasm.intermediate.instruction import (Add, AddElement, Clear, Divide,
                                           ExpDist, IfEqual, IfGreaterThan,
                                           IfGreaterThanOrEqual, IfInList,
                                           IfLessThan, IfLessThanOrEqual,
                                           IfNotEqual, IfNotInList, Length,
                                           Multiply, NormalDist, RemoveElement,
                                           RemoveNElements, Round, Send, Set,
                                           Subset, Subtract, UniformDist,
                                           WhileEqual, WhileGreaterThan,
                                           WhileGreaterThanOrEqual,
                                           WhileLessThan, WhileLessThanOrEqual,
                                           WhileNotEqual)
from aasm.parsing.parse import parse_lines

if TYPE_CHECKING:
    from aasm.intermediate.action import Action
    from aasm.intermediate.agent import Agent
    from aasm.intermediate.argument import Argument
    from aasm.intermediate.behaviour import Behaviour
    from aasm.intermediate.message import Message as IntermediateMessage


def get_spade_code(aasm_lines: List[str], indent_size: int = 4, debug: bool = False) -> Code:
    """Generates SPADE code in Python from `aasm_lines`.

        Parameters
        ----------
        aasm_lines: List[str]
            Lines of code written in Agents Assembly

        indent_size: int, optional
            Python code indentation size
            
        debug: bool, optional
            Print the translator debug information to the standard output

        Returns
        -------
        SPADE code along with the algorithm for the graph generation

        Raises
        ------
        PanicException
            If an error is detected while parsing the `aasm_lines`.
    """
    parsed = parse_lines(aasm_lines, debug)
    return Code(
        PythonSpadeCode(indent_size, parsed.agents).code_lines, 
        PythonGraph(indent_size, parsed.graph).code_lines
    )


class PythonSpadeCode(PythonCode):
    def __init__(self, indent_size: int, agents: List[Agent]):
        super().__init__(indent_size)
        if agents:
            self.add_required_imports()
            for agent in agents:
                self.add_newlines(2)
                self.generate_agent(agent)
    
    def add_required_imports(self) -> List[str]:
        self.add_line('import copy')
        self.add_line('import datetime')
        self.add_line('import random')
        self.add_line('import httpx')
        self.add_line('import numpy')
        self.add_line('import orjson')
        self.add_line('import spade')
    
    def generate_agent(self, agent: Agent) -> None:
        self.add_line(f'class {agent.name}(spade.agent.Agent):')
        self.indent_right()

        self.add_agent_constructor(agent)
        self.add_newline()

        self.add_message_utils()
        self.add_newline()

        self.add_agent_setup(agent)
        self.add_newline()

        self.add_backup_behaviour(agent)
        self.add_newline()

        for setup_behaviour in agent.setup_behaviours.values():
            self.add_agent_behaviour(setup_behaviour, 'spade.behaviour.OneShotBehaviour')
            self.add_newline()
        
        for one_time_behaviour in agent.one_time_behaviours.values():
            self.add_agent_behaviour(one_time_behaviour, 'spade.behaviour.TimeoutBehaviour')
            self.add_newline()
        
        for cyclic_behaviour in agent.cyclic_behaviours.values():
            self.add_agent_behaviour(cyclic_behaviour, 'spade.behaviour.PeriodicBehaviour')
            self.add_newline()
        
        for message_received_behaviour in agent.message_received_behaviours.values():
            self.add_agent_behaviour(message_received_behaviour, 'spade.behaviour.CyclicBehaviour')
            self.add_newline()
        
        self.indent_left()
        
    def add_agent_constructor(self, agent: Agent) -> None:
        self.add_line('def __init__(self, jid, password, backup_url = None, backup_period = 60, backup_delay = 0, logger = None, **kwargs):')
        self.indent_right()

        self.add_line('super().__init__(jid, password, verify_security=False)')
        self.add_line('if logger: logger.debug(f\'[{jid}] Received parameters: jid: {jid}, password: {password}, backup_url: {backup_url}, backup_period: {backup_period}, backup_delay: {backup_delay}, kwargs: {kwargs}\')')
        self.add_line('self.logger = logger')
        self.add_line('self.backup_url = backup_url')
        self.add_line('self.backup_period = backup_period')
        self.add_line('self.backup_delay = backup_delay')
        self.add_line('self.connections = kwargs.get("connections", [])')
        self.add_line('self.msgRCount = kwargs.get("msgRCount", 0)')
        self.add_line('self.msgSCount = kwargs.get("msgSCount", 0)')

        for init_float_param in agent.init_floats.values():
            self.add_line(f'self.{init_float_param.name} = kwargs.get("{init_float_param.name}", {init_float_param.value})')
        
        for dist_normal_float_param in agent.dist_normal_floats.values():
            self.add_line(f'self.{dist_normal_float_param.name} = kwargs.get("{dist_normal_float_param.name}", numpy.random.normal({dist_normal_float_param.mean}, {dist_normal_float_param.std_dev}))')
        
        for dist_exp_float_param in agent.dist_exp_floats.values():
            self.add_line(f'self.{dist_exp_float_param.name} = kwargs.get("{dist_exp_float_param.name}", numpy.random.exponential(1/{dist_exp_float_param.lambda_}))')
        
        for enum_param in agent.enums.values():
            values = []
            percentages = []
            for enum_value in enum_param.enum_values:
                values.append(f'\"{enum_value.value}\"')
                percentages.append(enum_value.percentage)
            values = f'[{", ".join(values)}]'
            percentages = f'[{", ".join(percentages)}]'
            self.add_line(f'self.{enum_param.name} = kwargs.get("{enum_param.name}", random.choices({values}, {percentages})[0])')
        
        for connection_list_param in agent.connection_lists.values():
            self.add_line(f'self.{connection_list_param.name} = kwargs.get("{connection_list_param.name}", [])')
        
        for message_list_param in agent.message_lists.values():
            self.add_line(f'self.{message_list_param.name} = kwargs.get("{message_list_param.name}", [])')
            
        self.add_line('if self.logger: self.logger.debug(f\'[{self.jid}] Class dict after initialization: {self.__dict__}\')')
        
        self.indent_left()
        self.add_newline()

        self.add_line('@property')
        self.add_line('def connCount(self):')
        self.indent_right()
        self.add_line('return len(self.connections)')

        self.indent_left()

    def add_message_utils(self) -> None:
        self.add_line('def get_json_from_spade_message(self, msg):')
        self.indent_right()
        self.add_line('return orjson.loads(msg.body)')
        self.indent_left()
        self.add_newline()

        self.add_line('def get_spade_message(self, receiver_jid, body):')
        self.indent_right()
        self.add_line('msg = spade.message.Message(to=receiver_jid)')
        self.add_line('body[\"sender\"] = str(self.jid)')
        self.add_line('msg.metadata[\"type\"] = body[\"type\"]')
        self.add_line('msg.metadata[\"performative\"] = body[\"performative\"]')
        self.add_line('msg.body = str(orjson.dumps(body), encoding="utf-8")')
        self.add_line('return msg')

        self.indent_left()
        
    def add_agent_setup(self, agent: Agent) -> None:
        self.add_line('def setup(self):')
        self.indent_right()

        self.add_line('if self.backup_url:')
        self.indent_right()
        self.add_no_match_template('BackupBehaviour')
        self.add_line('self.add_behaviour(self.BackupBehaviour(start_at=datetime.datetime.now() + datetime.timedelta(seconds=self.backup_delay), period=self.backup_period), BackupBehaviour_template)')
        self.indent_left()
        
        for setup_behaviour in agent.setup_behaviours.values():
            self.add_no_match_template(f'{setup_behaviour.name}')
            self.add_line(f'self.add_behaviour(self.{setup_behaviour.name}(), {setup_behaviour.name}_template)')
        
        for one_time_behaviour in agent.one_time_behaviours.values():
            self.add_no_match_template(f'{one_time_behaviour.name}')
            self.add_line(f'self.add_behaviour(self.{one_time_behaviour.name}(start_at=datetime.datetime.now() + datetime.timedelta(seconds={one_time_behaviour.delay})), {one_time_behaviour.name}_template)')
        
        for cyclic_behaviour in agent.cyclic_behaviours.values():
            self.add_no_match_template(f'{cyclic_behaviour.name}')
            self.add_line(f'self.add_behaviour(self.{cyclic_behaviour.name}(period={cyclic_behaviour.period}), {cyclic_behaviour.name}_template)')
        
        for message_received_behaviour in agent.message_received_behaviours.values():
            self.add_line(f'{message_received_behaviour.name}_template = spade.template.Template()')
            self.add_line(f'{message_received_behaviour.name}_template.set_metadata(\"type\", \"{message_received_behaviour.received_message.type}\")')
            self.add_line(f'{message_received_behaviour.name}_template.set_metadata(\"performative\", \"{message_received_behaviour.received_message.performative}\")')
            self.add_line(f'self.add_behaviour(self.{message_received_behaviour.name}(), {message_received_behaviour.name}_template)')
        
        self.add_line('if self.logger: self.logger.debug(f\'[{self.jid}] Class dict after setup: {self.__dict__}\')')
        
        self.indent_left()
        
    def add_no_match_template(self, behaviour_name: str) -> None:
        self.add_line(f'{behaviour_name}_template = spade.template.Template()')
        self.add_line(f'{behaviour_name}_template.set_metadata("reserved", "no_message_match")')

    def add_backup_behaviour(self, agent: Agent) -> None:
        self.add_line('class BackupBehaviour(spade.behaviour.PeriodicBehaviour):')
        self.indent_right()
        self.add_line('def __init__(self, start_at, period):')
        self.indent_right()
        self.add_line('super().__init__(start_at=start_at, period=period)')
        self.add_line('self.http_client = httpx.AsyncClient(timeout=period)')
        self.indent_left()
        self.add_newline()
        
        self.add_line('async def run(self):')
        self.indent_right()
        self.add_line('data = {')
        self.indent_right()
        self.add_line('"jid": str(self.agent.jid),')
        self.add_line(f'"type": "{agent.name}",')
        
        self.add_line('"floats": {')
        self.indent_right()
        self.add_line('"msgRCount": self.agent.msgRCount,')
        self.add_line('"msgSCount": self.agent.msgSCount,')
        self.add_line('"connCount": self.agent.connCount,')
        for float_param_name in agent.float_param_names:
            self.add_line(f'"{float_param_name}": self.agent.{float_param_name},')
        self.indent_left()
        self.add_line('},')
        
        self.add_line('"enums": {')
        self.indent_right()
        for enum_param_name in agent.enums:
            self.add_line(f'"{enum_param_name}": self.agent.{enum_param_name},')
        self.indent_left()
        self.add_line('},')
        
        self.add_line('"connections": {')
        self.indent_right()
        self.add_line('"connections": self.agent.connections,')
        for connection_list_param_name in agent.connection_lists:
            self.add_line(f'"{connection_list_param_name}": self.agent.{connection_list_param_name},')
        self.indent_left()
        self.add_line('},')
        
        self.add_line('"messages": {')
        self.indent_right()
        for message_list_param_name in agent.message_lists:
            self.add_line(f'"{message_list_param_name}": self.agent.{message_list_param_name},')
        self.indent_left()
        self.add_line('}')
        
        self.indent_left()
        self.add_line('}')
        self.add_line('if self.agent.logger: self.agent.logger.debug(f\'[{self.agent.jid}] Sending backup data: {data}\')')
        self.add_line('try:')
        self.indent_right()
        self.add_line('await self.http_client.post(self.agent.backup_url, headers={"Content-Type": "application/json"}, data=orjson.dumps(data))')
        self.indent_left()
        self.add_line('except Exception as e:')
        self.indent_right()
        self.add_line('if self.agent.logger: self.agent.logger.error(f\'[{self.agent.jid}] Backup error type: {e.__class__}, additional info: {e}\')')
        self.indent_left()
        self.indent_left()
        self.indent_left()
        
    def add_agent_behaviour(self, behaviour: Behaviour, behaviour_type: str) -> None:
        self.add_line(f'class {behaviour.name}({behaviour_type}):')
        self.indent_right()

        for action in behaviour.actions.values():                
            self.add_action(behaviour, action)
        
        self.add_line('async def run(self):')
        self.indent_right()
        if isinstance(behaviour, MessageReceivedBehaviour):
            self.add_rcv_message()
        elif not behaviour.actions.values():
            self.add_line('...')
            self.indent_left()
            self.indent_left()
            return

        if isinstance(behaviour, MessageReceivedBehaviour):
            self.indent_right()

        for action in behaviour.actions.values():
            self.add_action_call(behaviour, action)
              
        if isinstance(behaviour, MessageReceivedBehaviour):
            self.indent_left()
                    
        self.indent_left()
        self.indent_left()

    def add_rcv_message(self) -> None:
        self.add_line('rcv = await self.receive(timeout=100000)')
        self.add_line('if rcv:')
        self.indent_right()
        self.add_line('rcv = self.agent.get_json_from_spade_message(rcv)')
        self.add_line('self.agent.msgRCount += 1')
        self.add_line('if self.agent.logger: self.agent.logger.debug(f\'[{self.agent.jid}] Received message: {rcv}\')')
        self.indent_left()

    def add_action_call(self, behaviour: Behaviour, action: Action) -> None:
        action_call = ''
        if isinstance(action, SendMessageAction):
            action_call += 'await '
        action_call += f'self.{action.name}'
        if isinstance(behaviour, MessageReceivedBehaviour):
            action_call += '(rcv)'
        else:
            action_call += '()'
        self.add_line(action_call)

    def add_action(self, behaviour: Behaviour, action: Action) -> None:
        self.add_action_def(behaviour, action)
        self.indent_right()
        
        self.add_line(f'if self.agent.logger: self.agent.logger.debug(f\'[{{self.agent.jid}}] Run action {action.name}\')')

        if isinstance(action, SendMessageAction):
            self.add_send_message(action.send_message)
        
        self.add_block(action.main_block)
        self.indent_left()

        self.add_newline()

    def add_action_def(self, behaviour: Behaviour, action: Action) -> None:
        action_def = ''
        if isinstance(action, SendMessageAction):
            action_def += 'async '
        action_def += f'def {action.name}'
        if isinstance(behaviour, MessageReceivedBehaviour):
            action_def += '(self, rcv):'
        else:
            action_def += '(self):'
        self.add_line(action_def)

    def add_send_message(self, message: IntermediateMessage) -> None:            
        send_msg = f'send = {{ \"type\": \"{message.type}\", \"performative\": \"{message.performative}\", '
        for float_param_name in message.float_params:
            send_msg += f'\"{float_param_name}\": 0.0, '
        send_msg += '}'
        self.add_line(send_msg)
    
    def parse_arg(self, arg: Argument) -> str:
        match arg.type_in_op:
            case AgentParam():
                return f'self.agent.{arg.expr}'
            
            case EnumValue():
                return f'\"{arg.expr}\"'
            
            case ReceivedMessageParam():
                prop = arg.expr.split('.')[1]
                return f'rcv[\"{prop}\"]'
            
            case SendMessageParam():
                prop = arg.expr.split('.')[1]
                return f'send[\"{prop}\"]'
            
            case _:
                return arg.expr
        
    def add_block(self, block: Block) -> None:
        if not block.statements:
            self.add_line('...')
            return
        
        for statement in block.statements:
            match statement:
                case Block():
                    self.indent_right()
                    self.add_block(statement)
                    self.indent_left()
            
                case Declaration():
                    value = self.parse_arg(statement.value)
                    self.add_line(f'{statement.name} = {value}')
                    
                case Subset():
                    to_list = self.parse_arg(statement.arg1)
                    from_list = self.parse_arg(statement.arg2)
                    num = self.parse_arg(statement.arg3)
                    self.add_line(f'if round({num}) > 0:')
                    self.indent_right()
                    self.add_line(f'{to_list} = [copy.deepcopy(elem) for elem in random.sample({from_list}, min(round({num}), len({from_list})))]')
                    self.indent_left()
                    self.add_line('else:')
                    self.indent_right()
                    self.add_line(f'{to_list} = []')
                    self.indent_left()
                    
                case Clear():
                    list_ = self.parse_arg(statement.arg1)
                    self.add_line(f'{list_}.clear()')
                    
                case Send() if isinstance(statement.arg1.type_in_op, Connection):
                    receiver = self.parse_arg(statement.arg1)
                    self.add_line(f'if self.agent.logger: self.agent.logger.debug(f\'[{{self.agent.jid}}] Send message {{send}} to \u007b{receiver}\u007d\')')
                    self.add_line(f'await self.send(self.agent.get_spade_message({receiver}, send))')
                    self.add_line('self.agent.msgSCount += 1')
                    
                case Send() if isinstance(statement.arg1.type_in_op, ConnectionList):
                    receivers = self.parse_arg(statement.arg1)
                    self.add_line(f'if self.agent.logger: self.agent.logger.debug(f\'[{{self.agent.jid}}] Send message {{send}} to \u007b{receivers}\u007d\')')
                    self.add_line(f'for receiver in {receivers}:')
                    self.indent_right()
                    self.add_line('await self.send(self.agent.get_spade_message(receiver, send))')
                    self.add_line('self.agent.msgSCount += 1')
                    self.indent_left()
                    
                case Set() if isinstance(statement.arg2.type_in_op, MessageList):
                    msg = self.parse_arg(statement.arg1)
                    msg_list = self.parse_arg(statement.arg2)
                    self.add_line(f'if len(list(filter(lambda msg: msg.body["type"] == {msg}.body["type"] and msg.body["performative"] == {msg}.body["performative"], {msg_list}))):')
                    self.indent_right()
                    self.add_line(f'{msg} = copy.deepcopy(random.choice(list(filter(lambda msg: msg.body["type"] == {msg}.body["type"] and msg.body["performative"] == {msg}.body["performative"], {msg_list}))))')
                    self.indent_left()
                    self.add_line('else:')
                    self.indent_right()
                    self.add_line('return')
                    self.indent_left()
                    
                case Set():
                    arg1 = self.parse_arg(statement.arg1)
                    arg2 = self.parse_arg(statement.arg2)
                    self.add_line(f'{arg1} = {arg2}')
                    
                case Round():
                    num = self.parse_arg(statement.arg1)
                    self.add_line(f'{num} = round({num})')
                    
                case UniformDist():
                    result = self.parse_arg(statement.arg1)
                    a = self.parse_arg(statement.arg2)
                    b = self.parse_arg(statement.arg3)
                    self.add_line(f'{result} = random.uniform({a}, {b})')
                    
                case NormalDist():
                    result = self.parse_arg(statement.arg1)
                    mean = self.parse_arg(statement.arg2)
                    std_dev = self.parse_arg(statement.arg3)
                    self.add_line(f'{result} = numpy.random.normal({mean}, {std_dev})')
                    
                case ExpDist():
                    result = self.parse_arg(statement.arg1)
                    lambda_ = self.parse_arg(statement.arg2)
                    self.add_line(f'{result} = numpy.random.exponential(1/{lambda_}) if {lambda_} > 0 else 0')
                
                case _:
                    arg1 = self.parse_arg(statement.arg1)
                    arg2 = self.parse_arg(statement.arg2)
                    match statement:
                        case IfGreaterThan():
                            self.add_line(f'if {arg1} > {arg2}:')
                            
                        case IfGreaterThanOrEqual():
                            self.add_line(f'if {arg1} >= {arg2}:')
                
                        case IfLessThan():
                            self.add_line(f'if {arg1} < {arg2}:')
                            
                        case IfLessThanOrEqual():
                            self.add_line(f'if {arg1} <= {arg2}:')
                    
                        case IfEqual():
                            self.add_line(f'if {arg1} == {arg2}:')

                        case IfNotEqual():
                            self.add_line(f'if {arg1} != {arg2}:')
                            
                        case WhileGreaterThan():
                            self.add_line(f'while {arg1} > {arg2}:')

                        case WhileGreaterThanOrEqual():
                            self.add_line(f'while {arg1} >= {arg2}:')

                        case WhileLessThan():
                            self.add_line(f'while {arg1} < {arg2}:')
                    
                        case WhileLessThanOrEqual():
                            self.add_line(f'while {arg1} <= {arg2}:')
                    
                        case WhileEqual():
                            self.add_line(f'while {arg1} == {arg2}:')
                    
                        case WhileNotEqual():
                            self.add_line(f'while {arg1} != {arg2}:')
                    
                        case Add():
                            self.add_line(f'{arg1} += {arg2}')

                        case Subtract():
                            self.add_line(f'{arg1} -= {arg2}')

                        case Multiply():
                            self.add_line(f'{arg1} *= {arg2}')

                        case Divide():
                            self.add_line(f'if {arg2} == 0: return')
                            self.add_line(f'{arg1} /= {arg2}')
                            
                        case AddElement():
                            self.add_line(f'if {arg2} not in {arg1}: {arg1}.append({arg2})')
                    
                        case RemoveElement():
                            self.add_line(f'if {arg2} in {arg1}: {arg1}.remove({arg2})')
                            
                        case IfInList():
                            self.add_line(f'if {arg2} in {arg1}:')
                            
                        case IfNotInList():
                            self.add_line(f'if {arg2} not in {arg1}:')
                            
                        case Length():
                            self.add_line(f'{arg1} = len({arg2})')
                            
                        case RemoveNElements():
                            self.add_line(f'if round({arg2}) > 0:')
                            self.indent_right()
                            self.add_line(f'if round({arg2}) < len({arg1}):')
                            self.indent_right()
                            self.add_line(f'random.shuffle({arg1})')
                            self.add_line(f'{arg1} = {arg1}[:len({arg1}) - round({arg2})]')
                            self.indent_left()
                            self.add_line('else:')
                            self.indent_right()
                            self.add_line(f'{arg1} = []')
                            self.indent_left()
                            self.indent_left()
