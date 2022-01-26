from __future__ import annotations

from typing import Dict, List


class FloatParam:
    def __init__(self, name: str):
        self.name: str = name
        self.value: str = ''
        self.is_value_set: bool = False
        
    def set_value(self, value: str) -> None:
        self.is_value_set = True
        self.value = value
        
    def print(self) -> None:
        print(f'MessageFloatParam {self.name} = {self.value}')


class Message:
    RESERVED_CONNECTION_PARAMS = [ 'sender' ]
    RESERVED_TYPE_PARAMS = [ 'type', 'performative' ]
    
    def __init__(self, msg_type: str, msg_performative: str):
        self.type: str = msg_type
        self.performative: str = msg_performative
        self.float_params: Dict[str, FloatParam] = {}
        
    @property
    def param_names(self) -> List[str]:
        return [ *Message.RESERVED_CONNECTION_PARAMS,
                 *Message.RESERVED_TYPE_PARAMS,
                 *list(self.float_params) ]
    
    @property
    def are_all_params_set(self) -> bool:
        return all([float_param.is_value_set for float_param in self.float_params.values()])
    
    @property
    def unset_params(self) -> List[str]:
        unset_params: List[str] = []
        for name, float_param in self.float_params.items():
            if not float_param.is_value_set:
                unset_params.append(name)
        return unset_params
    
    def param_exists(self, name: str) -> bool:
        return name in self.param_names
    
    def add_float(self, float_param: FloatParam) -> None:
        self.float_params[float_param.name] = float_param
        
    def print(self) -> None:
        print(f'Message {self.type}/{self.performative}')
        for float_params in self.float_params.values():
            float_params.print()
