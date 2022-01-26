from __future__ import annotations

from copy import deepcopy
from pprint import pprint
from typing import TYPE_CHECKING, Dict, Generator, List, Tuple

from aasm.utils.exception import PanicException

if TYPE_CHECKING:
    from aasm.intermediate.action import Action
    from aasm.intermediate.agent import Agent
    from aasm.intermediate.behaviour import Behaviour
    from aasm.intermediate.graph import Graph
    from aasm.intermediate.message import Message


class ParsedData:
    def __init__(self, agents: List[Agent], messages: List[Message], graph: Graph):
        self.agents: List[Agent] = agents
        self.messages: List[Message] = messages
        self.graph: Graph = graph


class State:
    def __init__(self, lines: List[str], debug: bool):
        self.debug: bool = debug
        self.lines: List[str] = lines
        self.line_num: int = 0
        self.in_agent: bool = False
        self.in_message: bool = False
        self.in_behaviour: bool = False
        self.in_action: bool = False
        self.in_graph: bool = False
        self.agents: Dict[str, Agent] = {}
        self.messages: Dict[Tuple[str, str], Message] = {}
        self.graph: Graph = None
        
    @property
    def last_agent(self) -> Agent:
        return self.agents[list(self.agents.keys())[-1]]
    
    @property
    def last_behaviour(self) -> Behaviour:
        return self.last_agent.last_behaviour
    
    @property
    def last_action(self) -> Action:
        return self.last_agent.last_behaviour.last_action
    
    @property
    def last_message(self) -> Message:
        return self.messages[list(self.messages.keys())[-1]]
    
    def add_agent(self, agent: Agent) -> None:
        self.agents[agent.name] = agent
        
    def add_message(self, message: Message) -> None:
        self.messages[(message.type, message.performative)] = message

    def add_graph(self, graph: Graph) -> None:
        self.graph = graph
        
    def agent_exists(self, name: str) -> bool:
        return name in self.agents
    
    def message_exists(self, msg_type: str, msg_performative: str) -> bool:
        return (msg_type, msg_performative) in self.messages

    def graph_exists(self) -> bool:
        return self.graph is not None
    
    def get_message_instance(self, msg_type: str, msg_performative: str) -> Message:
        return deepcopy(self.messages[(msg_type, msg_performative)])
            
    def tokens_from_lines(self) -> Generator[list[str], None, None]:
        for line in self.lines:
            self.line_num += 1
            uncommented = line.split('#')[0]
            tokens = [token.strip() for token in uncommented.replace(',', ' ').split()]
            if tokens:
                tokens[0] = tokens[0].upper()
                yield tokens
                
    def print(self) -> None:
        if self.messages:
            print('- Messages:')
            for message in self.messages.values():
                message.print()
                print('')
        if self.agents:
            print('- Agents:')
            for agent in self.agents.values():
                agent.print()
                print('')
        if self.graph:
            print('- Graph:')
            self.graph.print()
    
    def verify_end_state(self) -> None:
        if self.in_agent:
            self.panic('Missing EAGENT')
        elif self.in_message:
            self.panic('Missing EMESSAGE')
        elif self.in_graph:
            self.panic('Missing EGRAPH')
            
    def get_parsed_data(self) -> ParsedData:
        self.verify_end_state()
        if self.debug:
            pprint(self.__dict__)
            self.print()
        return ParsedData(list(self.agents.values()), list(self.messages.values()), self.graph)

    def panic(self, reason: str, suggestion: str = '') -> None:
        if self.debug:
            pprint(self.__dict__)
            self.print()
        place = f'Error in line {self.line_num}: {self.lines[self.line_num - 1].strip()}'
        raise PanicException(place, reason, suggestion)

    def require(self, expr: bool, msg_on_error: str, suggestion_on_error: str = '') -> None:
        if not expr:
            self.panic(msg_on_error, suggestion_on_error)
