from ctypes import Union
import dataclasses
from typing import Optional, Union

from .message import Message


@dataclasses.dataclass
class AgentResultMessage(Message):
    '''
    Result of the Agent
    '''
    result: Union[str, dict] # can be an url [string] to the agents database or a dict with the results. 
    error_message: str
    error_code: int