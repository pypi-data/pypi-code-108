from __future__ import annotations

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from aasm.intermediate.action import Action
    from aasm.intermediate.message import Message


class Behaviour:
    def __init__(self, name: str):
        self.name = name
        self.actions: Dict[str, Action] = {}
        
    @property
    def last_action(self) -> Action:
        return self.actions[list(self.actions.keys())[-1]]
    
    def add_action(self, action: Action) -> None:
        self.actions[action.name] = action
        
    def action_exists(self, name: str) -> bool:
        return name in self.actions

    def print(self) -> None:
        print(f'Behaviour {self.name}')
        for action in self.actions.values():
            action.print()


class SetupBehaviour(Behaviour):
    def __init__(self, name: str):
        super().__init__(name)
        
        
class OneTimeBehaviour(Behaviour):
    def __init__(self, name: str, delay: str):
        super().__init__(name)
        self.delay: str = delay
        
        
class CyclicBehaviour(Behaviour):
    def __init__(self, name: str, period: str):
        super().__init__(name)
        self.period: str = period
        
        
class MessageReceivedBehaviour(Behaviour):
    def __init__(self, name: str, message: Message):
        super().__init__(name)
        self.received_message: Message = message
