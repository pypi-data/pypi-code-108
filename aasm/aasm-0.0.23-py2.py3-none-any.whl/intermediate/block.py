from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from aasm.intermediate.declaration import Declaration
    from aasm.intermediate.instruction import Instruction


class Block:    
    def __init__(self, names_declared_in_parent: List[str]):
        self.statements: List[Declaration | Instruction | Block] = []
        self._declared_names: List[str] = list(names_declared_in_parent)
        
    @property
    def declarations_in_scope(self) -> List[str]:
        return self._declared_names
        
    def add_declaration(self, declaration: Declaration) -> None:
        self._declared_names.append(declaration.name)
        self.statements.append(declaration)
    
    def add_statement(self, statement: Instruction | Block) -> None:
        self.statements.append(statement)
        
    def print(self) -> None:
        print(f'Block')
        print(f'Names in scope')
        print(self._declared_names)
        for instruction in self.statements:
            instruction.print()
        print('(EndBlock)')
