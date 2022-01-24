# -*- coding:utf-8 -*-
# CREATED BY: jiangbohuai
# CREATED ON: 2021/10/12 5:39 PM
# LAST MODIFIED ON:
# AIM:
from typing import List, Union
import abc

from loguru import logger

from sentence_spliter.architect.sequence import SequenceABC


class JudgeTree:
    """
    方便condition
    """

    def __init__(self, args: callable):
        self.next = None
        self.args = args
        self.condition = []
        self.parent = None

    def add_children(self, args: callable, cond: 'Condition'):
        if args == self.args:
            self.condition.append(cond)
            return self
        else:
            self.parent = JudgeTree(args)
            self.parent.condition.append(cond)
            self.parent.next = self
            return self.parent

    def get_root(self):
        root = self
        # --- find root -- #
        while root.next is not None:
            root = self.next
        return root

    def judge(self, tok: SequenceABC, result: bool) -> bool:
        root = self.get_root()

        while root is not None:
            result = self.args([v(tok) for v in self.condition] + [result])
            root = root.parent
        return result


class Condition:
    def __init__(self, name: str, reverse: bool = False):
        self.reverse = reverse  # reverse result
        self.name = name
        self.judge_tree = None
        self.allow_add = True

    @abc.abstractmethod
    def run(self, tok: SequenceABC) -> bool:
        pass

    def add_or(self, cond: 'Condition'):
        assert self.allow_add is True, f"{self} has already been call, add_or is disabled"
        if self.judge_tree is None:
            self.judge_tree = JudgeTree(args=any)
        self.judge_tree = self.judge_tree.add_children(args=any, cond=cond)
        return self

    def add_and(self, cond: 'Condition'):
        assert self.allow_add is True, f"{self} has already been call, add_and is disabled"
        if self.judge_tree is None:
            self.judge_tree = JudgeTree(args=all)
        self.judge_tree = self.judge_tree.add_children(args=all, cond=cond)
        return self

    def __str__(self):
        return self.name

    def __call__(self, tok: SequenceABC, debug: bool = False):

        if not self.reverse:
            out = self.run(tok)
        else:
            out = not self.run(tok)
        # --- run judge tree -- #
        if self.judge_tree is not None:
            self.judge_tree = self.judge_tree.get_root()
            out = self.judge_tree.judge(tok, out)
        self.allow_add = False
        if debug:
            logger.debug(f'\t - ({self.name}) - {out}')
        return out


class Operation:
    def __init__(self, name: str):
        self.children = []
        self.name = name

    def __str__(self):
        return self.name

    def add_child(self, node: 'Operation', edges: Union[List[Condition], Condition] = [], args: callable = all):
        if isinstance(edges, list):
            self.children.append((edges, node, args))
        else:
            self.children.append(([edges], node, args))
        return self

    @abc.abstractmethod
    def run(self, seq: SequenceABC) -> None:
        pass

    def __call__(self, seq: SequenceABC, debug: bool = False) -> 'Operation':
        self.run(seq)
        tok = seq
        for con, opt, args in self.children:
            if debug:
                args_str = 'all' if args == all else 'any'
                logger.debug(f'\t <{opt.name}>\\{args_str}')
            # -- debug here --#

            if args([v(tok, debug) for v in con]):
                return opt

        else:
            raise Exception('DEAD loop !!!')

    def is_dead_loop(self) -> bool:
        pass

    def render(self) -> bool:
        pass


class StateMachine:
    def __init__(self, init_state: Operation):
        self.vertex = init_state

    def process(self, seq: SequenceABC, debug: bool = True):
        # -- depth first -- #
        vertex = self.vertex
        if debug:
            logger.debug(f'<{vertex}> "{seq}"-[{seq.i}]')
        while vertex.name != 'EndState':
            # -- do operation -- #
            vertex = vertex(seq, debug)
            if debug:
                logger.debug(f'<{vertex}> "{seq}"-[{seq.i}]')
        vertex.run(seq)


class Graph(Operation):
    """
    里面存在子图
    """

    def __init__(self, name: str):
        super(Graph, self).__init__(name)
        self.init_conditions()
        self.init_operations()
        self.logic_tree = self.build_logic()

    @abc.abstractmethod
    def init_conditions(self):
        pass

    @abc.abstractmethod
    def init_operations(self):
        pass

    @abc.abstractmethod
    def build_logic(self) -> 'Operation':
        pass

    def run(self, seq: SequenceABC, debug: bool = False) -> None:
        machine = StateMachine(self.logic_tree)
        machine.process(seq, debug=debug)
