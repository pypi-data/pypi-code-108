from __future__ import annotations

from typing import TYPE_CHECKING
from typing import List as typingList
from typing import Type

from aasm.intermediate.action import SendMessageAction
from aasm.intermediate.behaviour import MessageReceivedBehaviour
from aasm.utils.validation import is_float, is_int

if TYPE_CHECKING:
    from parsing.state import State


class ArgumentType:
    ...


class Mutable(ArgumentType):
    ...


class Immutable(ArgumentType):
    ...


class Declared(ArgumentType):
    ...


class Float(ArgumentType):
    ...


class Integer(ArgumentType):
    ...


class Enum(ArgumentType):
    ...


class EnumValue(ArgumentType):
    ...


class List(ArgumentType):
    ...


class ConnectionList(ArgumentType):
    ...


class MessageList(ArgumentType):
    ...


class AgentParam(ArgumentType):
    ...


class Message(ArgumentType):
    ...


class MessageType(ArgumentType):
    ...


class ReceivedMessage(ArgumentType):
    ...


class ReceivedMessageParam(ArgumentType):
    ...


class SendMessage(ArgumentType):
    ...


class SendMessageParam(ArgumentType):
    ...
    

class Connection(ArgumentType):
    ...


class Argument:
    """Doesn't panic. Use in the action context."""
    
    def __init__(self, state: State, expr: str):
        self.expr: str = expr
        self.types: typingList[ArgumentType] = []
        self.type_in_op: ArgumentType | None = None
        self.set_types(state)
   
    def set_types(self, state: State) -> None:        
        self.check_agent_params(state)
        self.check_action_variables(state)
        self.check_received_message_params(state)
        self.check_send_message_params(state)
        self.check_numerical_values()
    
    def check_agent_params(self, state: State) -> None:
        if self.expr in state.last_agent.RESERVED_FLOAT_PARAMS:
            self.types.append(self.compose(Float, AgentParam, Immutable))
            
        elif self.expr in state.last_agent.RESERVED_CONNECTION_LIST_PARAMS:
            self.types.append(self.compose(List, ConnectionList, AgentParam, Mutable))
            
        elif self.expr in state.last_agent.float_param_names:
            self.types.append(self.compose(Float, AgentParam, Mutable))
            
        elif self.expr in state.last_agent.enums:
            self.types.append(self.compose(Enum, AgentParam, Mutable))
            
        elif self.expr in state.last_agent.message_lists:
            self.types.append(self.compose(List, MessageList, AgentParam, Mutable))
            
        elif self.expr in state.last_agent.connection_lists:
            self.types.append(self.compose(List, ConnectionList, AgentParam, Mutable))
            
        for enum_param in state.last_agent.enums.values():
            for enum_value in enum_param.enum_values:
                if self.expr == enum_value.value:
                    self.types.append(self.compose(EnumValue, Immutable, from_enum=enum_param.name))
        
    def check_action_variables(self, state: State) -> None:
        if state.last_action.is_declaration_in_scope(self.expr):
            self.types.append(self.compose(Float, Declared, Mutable))
    
    def check_numerical_values(self) -> None:
        if is_float(self.expr):
            self.types.append(self.compose(Float, Immutable))

        if is_int(self.expr):
            self.types.append(self.compose(Integer, Immutable))
        
    def check_received_message_params(self, state: State) -> None:
        if isinstance(state.last_behaviour, MessageReceivedBehaviour):
            if self.expr.lower().startswith('rcv.'):
                prop = self.expr.split('.')[1]
                
                if prop in state.last_behaviour.received_message.RESERVED_CONNECTION_PARAMS:
                    self.types.append(self.compose(Connection, ReceivedMessageParam, Immutable))
                    
                elif prop in state.last_behaviour.received_message.RESERVED_TYPE_PARAMS:
                    self.types.append(self.compose(MessageType, ReceivedMessageParam, Immutable))
                
                elif prop in state.last_behaviour.received_message.float_params:
                    self.types.append(self.compose(Float, ReceivedMessageParam, Immutable))
                    
            elif self.expr.lower() == 'rcv':
                self.types.append(self.compose(Message, ReceivedMessage, Immutable))
                
    def check_send_message_params(self, state: State) -> None:
        if isinstance(state.last_action, SendMessageAction):
            if self.expr.lower().startswith('send.'):
                prop = self.expr.split('.')[1]
                    
                if prop in state.last_action.send_message.RESERVED_TYPE_PARAMS:
                    self.types.append(self.compose(MessageType, SendMessageParam, Immutable))
                
                elif prop in state.last_action.send_message.float_params:
                    self.types.append(self.compose(Float, SendMessageParam, Mutable))
                    
            elif self.expr.lower() == 'send':
                self.types.append(self.compose(Message, SendMessage, Mutable))
    
    def compose(self, *classes: Type[ArgumentType], **args: str) -> ArgumentType:
        name = "_".join([klass.__name__ for klass in classes])
        if args:
            name += '|' +  "|".join([f'{key}={value}' for key, value in args.items()])
        return type(name, classes, args)()

    def has_arg(self, argument_type: ArgumentType, key: str, value: str) -> bool:
        try:
            if getattr(argument_type, key) == value:
                return True
        except AttributeError:
            ...
        return False

    def has_type(self, *classes: Type[ArgumentType], **args: str) -> bool:
        for type_ in self.types:
            if all([isinstance(type_, klass) for klass in classes]) and all([self.has_arg(type_, key, value) for key, value in args.items()]):
                return True
        return False
                    
    def set_op_type(self, *classes: Type[ArgumentType], **args: str) -> None:
        for type_ in self.types:
            if all([isinstance(type_, klass) for klass in classes]) and all([self.has_arg(type_, key, value) for key, value in args.items()]):
                self.type_in_op = type_

    def declaration_context(self, rhs: Argument) -> bool:
        if rhs.has_type(Float):
            self.type_in_op = self.compose(Float, Declared, Mutable)
            rhs.set_op_type(Float)
            return True
        
        return False
    
    def unordered_comparaison_context(self, rhs: Argument) -> bool:
        if self.has_type(Float) and rhs.has_type(Float):
            self.set_op_type(Float)
            rhs.set_op_type(Float)
            
        elif self.has_type(Enum) and rhs.has_type(EnumValue, from_enum=self.expr):
            self.set_op_type(Enum)
            rhs.set_op_type(EnumValue, from_enum=self.expr)
            
        else:
            return False
        
        return True

    def ordered_comparaison_context(self, rhs: Argument) -> bool:
        if self.has_type(Float) and rhs.has_type(Float):
            self.set_op_type(Float)
            rhs.set_op_type(Float)
            return True
        
        return False

    def math_context(self, rhs: Argument) -> bool:
        if self.has_type(Float, Mutable) and rhs.has_type(Float):
            self.set_op_type(Float, Mutable)
            rhs.set_op_type(Float)
            return True
        
        return False

    def list_modification_context(self, rhs: Argument) -> bool:
        if self.has_type(ConnectionList, Mutable) and rhs.has_type(Connection):
            self.set_op_type(ConnectionList, Mutable)
            rhs.set_op_type(Connection)
            
        elif self.has_type(MessageList, Mutable) and rhs.has_type(Message):
            self.set_op_type(MessageList, Mutable)
            rhs.set_op_type(Message)
            
        else:
            return False
        
        return True
    
    def list_n_removal_context(self, rhs: Argument) -> bool:
        if self.has_type(List, Mutable) and rhs.has_type(Float):
            self.set_op_type(List, Mutable)
            rhs.set_op_type(Float)
            return True
        
        return False
    
    def assignment_context(self, rhs: Argument) -> bool:
        if self.has_type(Enum, Mutable) and rhs.has_type(EnumValue, from_enum=self.expr):
            self.set_op_type(Enum, Mutable)
            rhs.set_op_type(EnumValue, from_enum=self.expr)
            
        elif self.has_type(Float, Mutable) and rhs.has_type(Float):
            self.set_op_type(Float, Mutable)
            rhs.set_op_type(Float)
            
        elif self.has_type(Message, Mutable) and rhs.has_type(MessageList):
            self.set_op_type(Message, Mutable)
            rhs.set_op_type(MessageList)
            
        elif self.has_type(SendMessageParam, Mutable) and rhs.has_type(Float):
            self.set_op_type(SendMessageParam, Mutable)
            rhs.set_op_type(Float)
            
        else:
            return False
        
        return True
    
    def list_subset_context(self, from_list: Argument, num: Argument) -> bool:
        if self.has_type(ConnectionList, Mutable) and from_list.has_type(ConnectionList) and num.has_type(Float):
            self.set_op_type(ConnectionList, Mutable)
            from_list.set_op_type(ConnectionList)
            num.set_op_type(Float)
            return True
        
        return False
    
    def list_inclusion_context(self, rhs: Argument) -> bool:
        if self.has_type(ConnectionList) and rhs.has_type(Connection):
            self.set_op_type(ConnectionList)
            rhs.set_op_type(Connection)
        
        elif self.has_type(MessageList) and rhs.has_type(Message):
            self.set_op_type(MessageList)
            rhs.set_op_type(Message)

        else:
            return False
        
        return True
    
    def list_clear_context(self) -> bool:
        if self.has_type(List, Mutable):
            self.set_op_type(List, Mutable)
            return True
        
        return False
    
    def list_length_context(self, rhs: Argument) -> bool:
        if self.has_type(Float, Mutable) and rhs.has_type(List):
            self.set_op_type(Float, Mutable)
            rhs.set_op_type(List)
            return True
        
        return False
    
    def send_context(self) -> bool:
        if self.has_type(ConnectionList):
            self.set_op_type(ConnectionList)
            
        elif self.has_type(Connection):
            self.set_op_type(Connection)
            
        else:
            return False
        
        return True

    def random_number_generation_context(self, *args: Argument) -> bool:
        if self.has_type(Float, Mutable) and all([arg.has_type(Float) for arg in args]):
            self.set_op_type(Float, Mutable)
            for arg in args:
                arg.set_op_type(Float)
            return True

        return False

    def round_number_context(self) -> bool:
        if self.has_type(Float, Mutable):
            self.set_op_type(Float, Mutable)
            return True

        return False

    def explain(self) -> str:
        types = f'{self.expr}: [ '
        for argument_type in self.types:
            types += type(argument_type).__name__ + ', '
        types = types.rstrip().rsplit(',', 1)[0]
        types += ' ]'
        return types

    def print(self) -> None:
        print(f'Argument {self.expr}')
        print(f'Type in op: {type(self.type_in_op).__name__}')
        for argument_type in self.types:
            type(argument_type).__name__
