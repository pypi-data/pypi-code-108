#!/usr/bin/env python3
import logging
from collections.abc import Iterable

from quickspider.core.error import InvalidInputError
from quickspider.core.utils import MyIterator, ProcessExceptionEmpty


class BaseNode:
    """最基础的节点，所有的节点都应该继承自这个节点，否则会无法识别"""
    def __init__(self, _name):
        self._name = _name
        self._input = None
        self._middle = None
        self._output = None
        self._child = []
        self._parent = None
        self._controller = None
        self._status = "EMPTY"
        self.logger = logging.getLogger(self._name)
        self.logger.setLevel(logging.DEBUG)

    def __call__(self, _input):
        self._set_input(_input)
        status, _output = self.activate()
        if status:
            print("[Activate Success]")
            return _output
        print("[Activate Failed]")
        raise Exception("Failed")

    def init(self):
        """节点实例化后，预先初始化"""
        self.logger.debug("init")

    def post(self):
        """在即将关闭前，调用该方法"""
        self.logger.debug("post")

    # 实现with协议，方便单独使用
    def __enter__(self):
        self.init()
        return self

    def __exit__(self, type, value, trace):
        self.post()

    def add_child(self, node):
        """给节点添加后续节点"""
        if isinstance(node, Iterable):
            for n in node:
                self._add_child(n)
            return n
        self._add_child(node)
        return node

    def __repr__(self):
        return f"""
        name: {self._name}
        status: {self._status}
        _input: {self._input}
        middle: {self._middle}
        output: {self._output}
"""

    def __getitem__(self, key):
        return self._child[key]

    def _set_input(self, _input):
        self.logger.debug("set input to {_input}")
        self._input = _input

    def _add_child(self, node):
        self._child.append(node)
        node._parent = self

    def _clear_input(self):
        self.logger.debug("clear input")
        self._input = None

    def _clear_output(self):
        self.logger.debug("clear output")
        self._output = None

    def _clear_middle(self):
        self.logger.debug("clear middle")
        self._middle = None

    def _is_leaf(self):
        return not self._child

    def _is_header(self):
        return not self._parent

    def _not_empty(self):
        _not_empty = bool(self._middle)
        if _not_empty:
            self._status = "ACTIVATED"
        else:
            self._status = "EMPTY"
        return _not_empty

    def _empty(self):
        return not self._not_empty()

    # HACK should be implement by user
    def process_input(self, _input):
        self.logger.debug("[process | input -> middle]")
        return _input

    def _input_valid(self):
        """默认的检验输入合法的方法"""
        if self._input is not None:
            return True
        return False

    def _slot_input_to_middle(self):
        if not self._input_valid():
            raise InvalidInputError
        _input = self._input
        # 具体实现委托给 process_input
        if isinstance(_input, ProcessExceptionEmpty):
            _middle = _input
        else:
            try:
                _middle = self.process_input(_input)
            except Exception as e:
                # print(e)
                _middle = ProcessExceptionEmpty()
        self._middle = _middle
        self._clear_input()
        self._not_empty()

    def _slot_fill_middle(self):
        if self._status == "EMPTY":
            self.logger.debug("activate: [EMPTY | input -> middle]")
            try:
                self._slot_input_to_middle()
            except Exception as e:
                self.logger.debug(
                    f"activate: [EMPTY {self._name} | input -> middle] + failed with {e}"
                )
                raise e

    def _slot_middle_to_output(self):
        self.logger.debug("activate: [middle -> output]")
        one_piece = self._middle
        self._output = one_piece
        self._clear_middle()
        self._not_empty()

    def _slot_output_to_next(self):
        if self._is_leaf():
            self.logger.debug("activate: [LEAF | output -> child]")
            _output = self._slot_output_to_child_leaf()
        else:
            self.logger.debug("activate: [output -> child]")
            if isinstance(self._output, ProcessExceptionEmpty):
                return
            _output = self._slot_output_to_child()
        return _output

    def _slot_output_to_child(self):
        _output = self._output
        for child in self._child:
            child._set_input(_output)
        self._clear_output()
        self._not_empty()
        return _output

    def _slot_output_to_child_leaf(self):
        _output = self._output
        self._clear_output()
        return _output

    # HACK CORE
    def activate(self):
        self.logger.debug("activate: start")
        # 如果需要编写抽象类，如IteratorNode，则必须实现_empty()
        try:
            self._slot_fill_middle()
            self._slot_middle_to_output()
            _output = self._slot_output_to_next()
        except Exception as e:
            # print(e)
            return False, None
        return True, _output


class IterableNode(BaseNode):
    """迭代器节点"""
    def __init__(self, _name):
        super().__init__(_name)
        self._middle = MyIterator([])

    def _not_empty(self):
        _not_empty = self._middle.not_empty()
        if _not_empty:
            self._status = "ACTIVATED"
        else:
            self._status = "EMPTY"
        return _not_empty

    def _slot_input_to_middle(self):
        assert self._input is not None
        _input = self._input
        _middle = self.process_input(_input)
        self._middle = MyIterator(_middle)
        self._clear_input()
        self._not_empty()

    def _slot_middle_to_output(self):
        one_piece = self._fetch_one_piece()
        self._output = one_piece
        self._not_empty()

    def _fetch_one_piece(self):
        if not self._not_empty():
            return None
        return self._middle.fetch_one_piece()

    # HACK test
    def process_input(self, _input):
        return (_input + f"_{i}_by_[{self._name}]" for i in range(5))
