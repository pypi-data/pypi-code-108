# -*- coding: utf-8 -*-
from __future__ import annotations
from jsp_exp import Operation as BaseOperation
from typing import Union


# 基本のOperationを拡張する
class Operation(BaseOperation):
    def __init__(self, processed_by: Union[int, str] = 'Machine', name: str = 'Operation', r: Optional[int] = None, p: Optional[int] = None, q: Optional[int] = None):
        super().__init__(processed_by, name, r, p, q)
        self.__p_plus = self.p

    @property
    def p_plus(self) -> int:
        return self.__p_plus

    @p_plus.setter
    def p_plus(self, new_val: int) -> None:
        """Validate new p_plus value is valid or not.

        Args:
            new_val (int): new p_plus value. If it is valid, it must be a positive integer.
        """
        assert new_val >= 0, f"Operation '{self.name}' is overscheduled. Please check your code."
        self.__p_plus = new_val

    def is_done(self) -> bool:
        """Return the job is already completed or not.

        Returns:
            bool: If job is already completed, then return True. Otherwise False.
        """
        return self.p_plus == 0


def create_operations(r_list: List[int], p_list: List[int], q_list: List[int]):
    unsorted_ops = [
        Operation(processed_by='M', name=f"O{i+1}", r=r, p=p, q=q)
        for i, (r, p, q) in enumerate(zip(r_list, p_list, q_list))
    ]
    return unsorted_ops
