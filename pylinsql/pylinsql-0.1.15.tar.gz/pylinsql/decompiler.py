"""
Reconstruct the original Python code from a Python generator expression.

This module is used internally.
"""

import dis
import itertools
import os
from dataclasses import dataclass
from types import CodeType
from typing import Iterable, List, Tuple

from .ast import *
from .evaluator import Evaluator, JumpResolver
from .node import (
    AbstractNode,
    ConditionExpressionChecker,
    LoopConditionChecker,
    NodeConjunction,
    NodeDisjunction,
    NodeIfThenElse,
    NodeInstructions,
    NodeSequence,
    NodeVisitor,
)


_DEBUG: bool = int(os.getenv("DEBUG", "0")) != 0
if _DEBUG:
    from .plot import plot_directed_graph


def all_equal(iterable: Iterable[T]) -> bool:
    iterator = iter(iterable)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == x for x in iterator)


def pairwise(iterable: Iterable[T]) -> Iterable[Tuple[T, T]]:
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


@dataclass
class _BasicBlockSpan:
    "An interval that contains instructions and ends with a (conditional) jump instruction."

    start_offset: int = None
    start_index: int = None
    end_index: int = None


def _get_basic_blocks(instructions: List[dis.Instruction]) -> List[_BasicBlockSpan]:
    jmp = JumpResolver()

    blocks = []
    block = _BasicBlockSpan(start_index=0, start_offset=0)
    for prev_index, (prev_instr, next_instr) in enumerate(pairwise(instructions)):
        next_index = prev_index + 1
        if next_instr.is_jump_target or jmp.test(prev_instr):
            # terminate block before jump target and after jump instruction
            block.end_index = next_index
            blocks.append(block)

            # start new block
            block = _BasicBlockSpan(
                start_offset=next_instr.offset, start_index=next_index
            )
    block.end_index = len(instructions)
    blocks.append(block)
    return blocks


@dataclass
class CodeExpression:
    local_vars: List[str]
    conditional_expr: Expression
    yield_expr: Expression


class CodeExpressionAnalyzer:
    code_object: CodeType
    instructions: List[dis.Instruction]

    def __init__(self, code_object: CodeType):
        self.code_object = code_object
        self.instructions = list(dis.Bytecode(self.code_object))

    def _get_abstract_nodes(self, blocks: List[_BasicBlockSpan]) -> List[AbstractNode]:
        jmp = JumpResolver()
        nodes: List[AbstractNode] = []
        node_by_offset: Dict[int, Tuple[AbstractNode, int, int]] = {}
        for block in blocks:
            node = AbstractNode(
                NodeInstructions(self.instructions[block.start_index : block.end_index])
            )
            nodes.append(node)
            on_true, on_false = jmp.process(
                self.instructions[block.start_index : block.end_index][-1],
            )
            node_by_offset[block.start_offset] = (
                node,
                on_true,
                on_false,
            )

        for node, on_true, on_false in node_by_offset.values():
            node.set_target(
                node_by_offset[on_true][0] if on_true is not None else None,
                node_by_offset[on_false][0] if on_false is not None else None,
            )

        if _DEBUG:
            plot_directed_graph("Control Flow Graph", nodes)

        return nodes

    def _disassemble(self, nodes: List[AbstractNode]) -> CodeExpression:
        # dis.dis(self.code_object)
        entry_node = nodes[0]

        # merge subgraphs that correspond to conditional expressions into a single node
        for index, node in enumerate(nodes):
            checker = ConditionExpressionChecker()

            expr_nodes = None
            if len(node.origins) > 1:
                # possible terminal node of a conditional block
                for k in range(2, index):
                    candidate_nodes = nodes[index - k : index]
                    if checker.matches(candidate_nodes):
                        expr_nodes = candidate_nodes
                        break

            if expr_nodes is not None:
                expr_head_node = expr_nodes[0]
                expr_cond_node = self._get_expr_condition(expr_nodes, node)

                # re-wire edges to include new node and exclude old nodes
                expr_cond_node.seize_origins(expr_head_node)
                expr_cond_node.set_target(checker.target_node, checker.target_node)

        # remove prolog and epilog from generator
        # prolog pushes the single iterable argument (a.k.a. ".0") to the stack that a generator expression receives:
        #       0 LOAD_FAST                0 (.0)
        # epilog pops the stack and returns None to indicate end of iteration
        # >>   48 LOAD_CONST               4 (None)
        #      50 RETURN_VALUE
        nodes = entry_node.traverse_top_down()
        prolog = nodes[0]
        body = nodes[1:-1]
        epilog = nodes[-1]

        checker = LoopConditionChecker()
        if len(body) > 2 and checker.matches(body):
            # extract conditional expression
            loop_nodes = [
                node
                for node in body
                if node is not checker.iterator_node and node is not checker.body_node
            ]
            loop_cond_node = self._get_loop_condition(
                loop_nodes, checker.iterator_node, checker.body_node
            )

            # re-wire edges to include new node and exclude old nodes
            loop_expr = NodeSequence.from_nodes(
                [checker.iterator_node, loop_cond_node, checker.body_node]
            )
        else:
            loop_expr = NodeSequence.from_nodes(body)

        seq_expr = NodeSequence([prolog.expr, loop_expr, epilog.expr])
        seq_node = AbstractNode(seq_expr)

        # evaluate nodes in appropriate order to produce an expression
        evaluator = Evaluator(self.code_object)
        visitor = NodeVisitor(evaluator)
        visitor.visit(seq_node)
        cond_expr = visitor.visit(seq_node)

        return CodeExpression(evaluator.variables, cond_expr, visitor.yield_expr)

    def _get_expr_condition(
        self, nodes: List[AbstractNode], target: AbstractNode
    ) -> AbstractNode:
        "Extracts a conditional expression from the 'yield' part of a generator expression."

        # create special nodes `True` and `False`
        empty_node = AbstractNode(NodeInstructions([]))
        sink_nodes: List[AbstractNode] = []

        # redirect nodes that directly jump to next statement node
        for node in nodes:
            if node.on_true is node.on_false:
                if node.on_true is target:
                    sink_nodes.append(node)
                continue
            if node.on_true is target:
                node.set_on_true(empty_node)
            if node.on_false is target:
                node.set_on_false(empty_node)

        for sink_node in sink_nodes:
            sink_node.set_target(None, None)
        if len(sink_nodes) < 2:
            sink_nodes.append(empty_node)

        # align edges to be consistent
        self._align_edges(nodes)

        root = nodes[0]
        sorted_nodes = root.topological_sort()
        for sink_node in sink_nodes:
            sorted_nodes.remove(sink_node)

        cond_node = self._merge_conditional_nodes(sorted_nodes)
        cond_node.expr = NodeIfThenElse(
            cond_node.expr, cond_node.on_true.expr, cond_node.on_false.expr
        )
        return cond_node

    def _get_loop_condition(
        self,
        nodes: List[AbstractNode],
        iterator_node: AbstractNode,
        yield_node: AbstractNode,
    ) -> AbstractNode:
        "Extracts the loop condition from the 'if' part of a generator expression."

        # identify loop structural elements
        # loop head (a single block):
        # >>    2 FOR_ITER                18 (to 22)
        # loop body (a single block that yields values):
        #      ...
        #      14 BUILD_TUPLE              2
        #      16 YIELD_VALUE
        #      18 POP_TOP
        #      20 JUMP_ABSOLUTE            2
        # conditional nodes (several interconnected blocks that jump on conditions)

        # create special nodes `True` and `False`
        true_node = AbstractNode(Constant(True))
        false_node = AbstractNode(Constant(False))

        true_nodes = yield_node.get_unconditional_ancestors()
        false_nodes = iterator_node.get_unconditional_ancestors()

        # redirect result statement nodes to Boolean result nodes
        for node in nodes:
            if node.on_true in true_nodes:
                node.set_on_true(true_node)
            elif node.on_true in false_nodes:
                node.set_on_true(false_node)
            if node.on_false in false_nodes:
                node.set_on_false(false_node)
            elif node.on_false in true_nodes:
                node.set_on_false(true_node)

        # eliminate edges not part of the conditional expression
        root = iterator_node.on_true
        cond_nodes = root.traverse_top_down()
        for node in nodes:
            if node not in cond_nodes:
                node.set_target(None, None)

        cond_nodes = root.traverse_top_down()

        # align edges to be consistent
        self._align_edges(cond_nodes)

        # ensure that True/False result nodes are consistent with their inputs
        if not all(origin.on_true is true_node for origin in true_node.origins):
            # fix inconsistency by flipping all nodes
            for node in cond_nodes:
                node.twist()
        assert all(node.is_origin_consistent() for node in cond_nodes)

        sorted_nodes = root.topological_sort()
        assert len(cond_nodes) == len(sorted_nodes)
        sorted_nodes.remove(true_node)
        sorted_nodes.remove(false_node)

        return self._merge_conditional_nodes(sorted_nodes)

    def _align_edges(self, cond_nodes: List[AbstractNode]) -> None:
        "Align DAG edge colors such that all incoming edges are either green (true) edges or red (false) edges."

        marked = set()
        for node in cond_nodes:
            edge_type = False
            for origin in node.origins:
                if origin in marked:
                    edge_type = origin.on_true is node
                    break
            for origin in node.origins:
                if edge_type != (origin.on_true is node):
                    origin.twist()
                    marked.add(origin)
        assert all(node.is_origin_consistent() for node in cond_nodes)

    def _merge_conditional_nodes(
        self, sorted_nodes: List[AbstractNode]
    ) -> AbstractNode:

        if _DEBUG:
            plot_directed_graph("Boolean condition graph", sorted_nodes)

        idle = False
        while len(sorted_nodes) > 1:
            replacements = False

            for start in range(len(sorted_nodes) - 1):
                # locate a span of abstract nodes that could form a single conjunction
                conj_start = sorted_nodes[start]
                conj_sinks = conj_start.on_false.get_unconditional_descendants()

                end = start + 1
                while (
                    end < len(sorted_nodes) and sorted_nodes[end].on_false in conj_sinks
                ):
                    end += 1

                if end - start > 1:
                    conj_expr = NodeConjunction(
                        [n.expr for n in sorted_nodes[start:end]]
                    )
                    conj_node = AbstractNode(conj_expr)
                    conj_node.set_target(sorted_nodes[end - 1].on_true, conj_sinks[-1])
                    conj_node.seize_origins(conj_start)
                    for n in sorted_nodes[start:end]:
                        n.set_target(None, None)
                    sorted_nodes[start:end] = [conj_node]
                    replacements = True
                    break

                # locate a span of abstract nodes that could form a single disjunction
                disj_start = sorted_nodes[start]
                disj_sinks = disj_start.on_true.get_unconditional_descendants()

                end = start + 1
                while (
                    end < len(sorted_nodes) and sorted_nodes[end].on_true in disj_sinks
                ):
                    end += 1

                if end - start > 1:
                    disj_expr = NodeDisjunction(
                        [n.expr for n in sorted_nodes[start:end]]
                    )
                    disj_node = AbstractNode(disj_expr)
                    disj_node.set_target(disj_sinks[-1], sorted_nodes[end - 1].on_false)
                    disj_node.seize_origins(disj_start)
                    for n in sorted_nodes[start:end]:
                        n.set_target(None, None)
                    sorted_nodes[start:end] = [disj_node]
                    replacements = True
                    break

            if replacements:
                idle = False
            else:
                if idle:
                    break

                idle = True
                sorted_nodes[0].twist()

        if idle:
            raise NotImplementedError("unable to simplify conditional expression")

        return sorted_nodes[0]

    def get_expression(self) -> CodeExpression:
        # convert instructions into abstract nodes with symbolic expressions
        blocks = _get_basic_blocks(self.instructions)
        nodes = self._get_abstract_nodes(blocks)
        return self._disassemble(nodes)
