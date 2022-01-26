from __future__ import annotations

from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from aasm.intermediate.argument import Argument


class Instruction:
    def __init__(self, **kwargs: Dict[str, Argument]):
        for key in kwargs:
            self.__dict__[key] = kwargs[key]
  
    def print(self) -> None:
        print('Instruction')
        for argument in self.__dict__.values():
            argument.print()


class IfGreaterThan(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)
 
    def print(self) -> None:
        print('IfGreaterThan')
        super().print()


class IfGreaterThanOrEqual(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)
 
    def print(self) -> None:
        print('IfGreaterThanOrEqual')
        super().print()


class IfLessThan(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('IfLessThan')
        super().print()


class IfLessThanOrEqual(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('IfLessThanOrEqual')
        super().print()


class IfEqual(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('IfEqual')
        super().print()


class IfNotEqual(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('IfNotEqual')
        super().print()


class WhileGreaterThan(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('WhileGreaterThan')
        super().print()


class WhileGreaterThanOrEqual(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('WhileGreaterThanOrEqual')
        super().print()


class WhileLessThan(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('WhileLessThan')
        super().print()


class WhileLessThanOrEqual(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('WhileLessThanOrEqual')
        super().print()


class WhileEqual(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('WhileEqual')
        super().print()


class WhileNotEqual(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('WhileNotEqual')
        super().print()


class Multiply(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('Multiply')
        super().print()


class Divide(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('Divide')
        super().print()


class Add(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('Add')
        super().print()


class Subtract(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('Subtract')
        super().print()


class AddElement(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('AddElement')
        super().print()


class RemoveElement(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('RemoveElement')
        super().print()


class Subset(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument, arg3: Argument):
        super().__init__(arg1=arg1, arg2=arg2, arg3=arg3)

    def print(self) -> None:
        print('RemoveElement')
        super().print()


class Set(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('Set')
        super().print()


class IfInList(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('IfInList')
        super().print()


class IfNotInList(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('IfNotInList')
        super().print()


class Clear(Instruction):
    def __init__(self, arg1: Argument):
        super().__init__(arg1=arg1)

    def print(self) -> None:
        print('Clear')
        super().print()


class Length(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('Length')
        super().print()


class Send(Instruction):
    def __init__(self, arg1: Argument):
        super().__init__(arg1=arg1)

    def print(self) -> None:
        print('Send')
        super().print()
        
        
class RemoveNElements(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('RemoveNElements')
        super().print()


class UniformDist(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument, arg3: Argument):
        super().__init__(arg1=arg1, arg2=arg2, arg3=arg3)

    def print(self) -> None:
        print('UniformDist')
        super().print()


class NormalDist(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument, arg3: Argument):
        super().__init__(arg1=arg1, arg2=arg2, arg3=arg3)

    def print(self) -> None:
        print('NormalDist')
        super().print()


class ExpDist(Instruction):
    def __init__(self, arg1: Argument, arg2: Argument):
        super().__init__(arg1=arg1, arg2=arg2)

    def print(self) -> None:
        print('ExpDist')
        super().print()


class Round(Instruction):
    def __init__(self, arg1: Argument):
        super().__init__(arg1=arg1)

    def print(self) -> None:
        print('Round')
        super().print()
