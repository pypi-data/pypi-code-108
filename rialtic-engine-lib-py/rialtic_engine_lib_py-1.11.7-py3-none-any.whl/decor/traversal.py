import os
import re
from typing import cast, Callable, Tuple, Optional, List

from schema.insight_engine_response import Trace

from enginelib.decor.predicate import Predicate
from enginelib.decor.errors import InvalidParameterError
from enginelib.decor.node import DecisionNode, LeafNode, AbstractNode
from enginelib.decor.registry import Registry
from enginelib.decor.tree import Tree


class TreeTraversal:
    """Responsible for walking down a decision tree, starting from the root,
    while also making the registry update itself (the set of qualifying
    claims and claim lines, and the custom parameters) according to
    the predicate functions in each node of the decision tree."""
    def __init__(self, decision_tree: Tree, registry: Registry):
        #: the decision tree that must be traversed.
        self.decision_tree = decision_tree
        decision_tree.assemble()

        #: the registry in its initial state.
        self.registry = registry

        #: the list of predicates and respective answers during the traversal
        self.trace: Trace = Trace()
        self.trace.tree_name = decision_tree.name

    @staticmethod
    def _log(*args, **kwargs):
        print(*args, **kwargs)

    def _eval_before(self, node: AbstractNode):
        for predicate in self.decision_tree.execute_before.get(node.label, list()):
            func, param_name = self._wrapped_predicate_func(predicate)
            self._eval_predicate(func, param_name)

    def _eval_after(self, node: AbstractNode):
        for predicate in self.decision_tree.execute_after.get(node.label, list()):
            func, param_name = self._wrapped_predicate_func(predicate)
            self._eval_predicate(func, param_name)

    def _eval_predicate(self, func: Callable, param_name: str) -> bool:
        if param_name is None:
            return func()
        elif param_name == 'oc':
            return self.registry.is_there_oc_such_that(func)
        elif param_name == 'ocl':
            return self.registry.is_there_ocl_such_that(func)
        elif param_name == 'ocl_s':
            return self.registry.is_there_ocl_s_such_that(func)
        elif param_name == 'ocl_d':
            return self.registry.is_there_ocl_d_such_that(func)
        elif param_name == 'acl':
            return self.registry.is_there_acl_such_that(func)
        else:
            raise InvalidParameterError(f'(TreeTraversal) Invalid parameter {param_name} encountered.')

    def execute(self) -> str:
        """Perform the traversal, starting from the root of the tree.
        For debugging, please set DECOR_DEBUG environment variable to a non-empty value.

        Returns:
            a SimpleInsight according to the end branch that was reached.
        """
        debug = os.environ.get('DECOR_DEBUG', '')
        self.decision_tree.assemble()

        if debug:
            msg = f'Traversal of tree "{self.decision_tree.name}" for claim {self.registry.cue.claim_num}' + \
                  f' line {self.registry.clue.sequence}:'
            self._log('-' * len(msg))
            self._log(msg)
            self._log(end=(' ' * 8))

        node = self.decision_tree.root
        while isinstance(node, DecisionNode):
            self._eval_before(node)
            func, param_name = self._wrapped_predicate_func(node.predicate)
            value = self._eval_predicate(func, param_name)
            yes_no = 'YES' if value else 'NO'
            self.trace.traversal.append((
                node.predicate.description.strip(),
                yes_no,
                str(node.label),
                self._info_qualifying_claims_and_claim_lines(param_name)
            ))
            self._eval_after(node)

            if debug:
                text, _ = re.subn(r'\s+', ' ', node.predicate.description.strip())
                self._log(f'--> #{node.label}: "{text}"')
                self._log(end=f'{yes_no.rjust(7)} ')

            node = node.yes_node if value else node.no_node

        node = cast(LeafNode, node)
        self._eval_before(node)
        if debug:
            text, _ = re.subn(r'\s+', ' ', node.simple_insight.text.strip())
            insight_text = self.registry.format_text(text)
            insight_type = node.simple_insight.insight_type
            self._log(end=f'>>> Insight #{node.label}: {insight_type}; "{insight_text}"')

        self.trace.end_label = node.label
        return node.label

    def _wrapped_predicate_func(self, predicate: Predicate) -> Tuple[Callable[..., bool], Optional[str]]:
        outer_kwargs = dict()
        if 'cue' in predicate.standard_params:
            outer_kwargs['cue'] = self.registry.cue
        if 'clue' in predicate.standard_params:
            outer_kwargs['clue'] = self.registry.clue
        if 'data' in predicate.standard_params:
            outer_kwargs['data'] = self.registry.data
        if 'registry' in predicate.standard_params:
            outer_kwargs['registry'] = self.registry
        for param_name in predicate.custom_params:
            outer_kwargs[param_name] = self.registry[param_name]

        filtering_param = set(predicate.standard_params).difference(
            {'cue', 'clue', 'data', 'registry'}
        )
        if filtering_param == set():
            if predicate.func(**outer_kwargs):
                return (lambda: True), None
            else:
                return (lambda: False), None

        def inner(**inner_kwargs) -> bool:
            inner_kwargs.update(outer_kwargs)
            return predicate.func(**inner_kwargs)

        return inner, next(iter(filtering_param))

    def _get_qualifying_ocl_s(self) -> str:
        cue_claim_num = self.registry.cue.claim_num
        return f'(CUE) Claim #{cue_claim_num}: ' + \
               ', '.join(f'{ocl_s.sequence}' for ocl_s in self.registry.iter_ocl_s())

    def _get_qualifying_ocl_d(self, oc_claim_num: str) -> str:
        return f'Claim #{oc_claim_num}: ' + \
                     ', '.join(f'{ocl_d.sequence}' for ocl_d in self.registry.dict_ocl_d[oc_claim_num])

    def _get_all_qualifying_ocl_d(self) -> List[str]:
        # limit on the number of historical claims to show:
        limit = 5
        claim_lines: List[str] = list()
        for i, oc in zip([*range(limit), 'more'], self.registry.iter_oc()):
            if i == 'more':
                claim_lines.append('(truncated)')
                break
            claim_lines.append(self._get_qualifying_ocl_d(oc.claim_num))
        return claim_lines

    def _info_qualifying_claims_and_claim_lines(self, param_name: str) -> str:
        if param_name == 'ocl_s':
            return 'Filtered OCL-S: ' + self._get_qualifying_ocl_s()
        if param_name == 'ocl_d':
            return 'Filtered OCL-D: ' + '; '.join(self._get_all_qualifying_ocl_d())
        if param_name == 'ocl':
            return 'Filtered OCL-S/D: ' + \
                   self._get_qualifying_ocl_s() + '; ' + '; '.join(self._get_all_qualifying_ocl_d())
        if param_name == 'oc':
            return 'Filtered OC (w/ OCL-D): ' + '; '.join(self._get_all_qualifying_ocl_d())
        return ''
