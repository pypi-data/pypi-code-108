from __future__ import annotations

from typing import TYPE_CHECKING, List

from aasm.intermediate.block import Block

if TYPE_CHECKING:
    from aasm.intermediate.declaration import Declaration
    from aasm.intermediate.instruction import Instruction
    from aasm.intermediate.message import Message


class Action:
    def __init__(self, name: str):
        self.name: str = name
        self._block_stack: List[Block] = [Block([])]
        self._nested_blocks_count: int = 0
        
    @property
    def main_block(self) -> Block:
        return self._block_stack[0]
    
    @property
    def current_block(self) -> Block:
        return self._block_stack[-1]
    
    def is_declaration_in_scope(self, name: str) -> bool:
        return name in self.current_block.declarations_in_scope
    
    def add_declaration(self, declaration: Declaration) -> None:
        self.current_block.add_declaration(declaration)
    
    def add_instruction(self, instruction: Instruction) -> None:
        self.current_block.add_statement(instruction)
        
    def start_block(self) -> None:
        new_block = Block(self.current_block._declared_names)
        self.current_block.add_statement(new_block)
        self._block_stack.append(new_block)
        self._nested_blocks_count += 1
    
    def end_block(self) -> None:
        self._block_stack.pop()
        self._nested_blocks_count -= 1
        
    def print(self) -> None:
        print(f'Action {self.name}')
        self.main_block.print()


class ModifySelfAction(Action):
    def __init__(self, name: str):
        super().__init__(name)
        
    def print(self) -> None:
        print('ModifySelfAction')
        super().print()


class SendMessageAction(Action):
    def __init__(self, name: str, message: Message):
        super().__init__(name)
        self.send_message: Message = message
        
    def print(self) -> None:
        print('SendMessageAction')
        super().print()
        self.send_message.print()
