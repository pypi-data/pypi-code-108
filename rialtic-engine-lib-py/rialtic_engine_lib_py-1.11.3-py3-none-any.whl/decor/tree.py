from copy import deepcopy, copy
from typing import Dict, Optional, Tuple, Type, Any, Callable, List

from schema.insight_engine_response import InsightType

from enginelib.decor.errors import DecisionTreeError, CustomParameterError
from enginelib.decor.node import AbstractNode, DecisionNode, LeafNode, Label
from enginelib.decor.predicate import Predicate
from enginelib.decor.registry import Registry
from enginelib.decor.result import AbstractResult
from enginelib.simple_insight import SimpleInsight


class Tree:
    """Used by the developer that will build the engine to organize
    the predicate functions that implements the various nodes of a
    decision tree. The main functionality provided by this class is
    the @node decorator.
    """
    def __init__(self, ResultClass: Type[AbstractResult], name: str = 'untitled'):
        #: the class that holds the data (type and text) of the
        #     insight nodes in the decision tree of the engine.
        self.ResultClass = ResultClass
        ResultClass.validate()

        #: the root node of the decision tree.
        self.root: Optional[AbstractNode] = None
        self._root_label: Optional[str] = None

        #: FUTURE: stores information about functions that implement
        #: custom parameters.
        self.parameter_decorated: Dict[str, List[Tuple[str, Callable[..., Any]]]] = dict()

        # TEMPORARY DATA STRUCTURES:
        # (no longer needed after Tree.assemble() is called)

        # self._node_decorated[label] stores triple (yes_label, no_label, predicate_func)
        self._node_decorated: Dict[str, Tuple[str, str, Callable[..., bool]]] = dict()

        # The node with label x is temporarily stored in self._node[x]
        self._node: Dict[str, AbstractNode] = dict()

        #: the name of this decision tree (useful when there are many trees).
        self.name = name

        self.execute_before: Dict[str, List[Predicate]] = dict()
        self.execute_after: Dict[str, List[Predicate]] = dict()

    def __copy__(self):
        new_tree = Tree(self.ResultClass, self.name)
        new_tree.execute_before = {**self.execute_before}
        new_tree.execute_after = {**self.execute_after}
        new_tree.parameter_decorated = {label: copy(obj) for label, obj in self.parameter_decorated.items()}
        if self.root is not None:
            # the tree is assembled
            new_tree.root = deepcopy(self.root)
        else:
            # the tree is not assembled
            new_tree._root_label = self._root_label
            new_tree._node_decorated = copy(self._node_decorated)
        return new_tree

    def before(self, label: Label):
        """Use this decorator to do computations like computing a parameter or filtering OC/OCL
        right before a node predicate is executed. If many functions are decorated with the
        @before(label) for the same label, then they will be executed in the order they are
        decorated.

        Functions decorated with @before(label) should not return any value. If some do, its
        return value will be ignored."""
        label = str(label)

        def inner(func):
            # No validation on func is performed at this moment.
            # Validations are delayed until Tree.assemble() is called.
            self.execute_before.setdefault(label, list()).append(Predicate(func, require_return_bool=False))
            return func

        return inner

    def after(self, label: Label):
        """Use this decorator to do computations like computing a parameter or filtering OC/OCL
        right after a node predicate is executed. If many functions are decorated with the
        @after(label) for the same label, then they will be executed in the order they are
        decorated.

        Functions decorated with @after(label) should not return any value. If some do, its
        return value will be ignored."""
        label = str(label)

        def inner(func):
            # No validation on func is performed at this moment.
            # Validations are delayed until Tree.assemble() is called.
            self.execute_after.setdefault(label, list()).append(Predicate(func, require_return_bool=False))
            return func

        return inner

    def node(self, label: Label, yes_label: Label, no_label: Label = ''):
        """Decorates a predicate function that is supposed to implement node
        [label] in the decision tree with the YES branch going to node [yes_label]
        and NO branch going to node [no_label].

        Labels can be int or str, but they are all converted to str internally,
        so 100 and '100' refer to the same node."""
        label, yes_label, no_label = str(label), str(yes_label), str(no_label)

        if not label:
            raise DecisionTreeError(message='The label of a node cannot be the empty string.')

        if self.root:
            raise DecisionTreeError(message='Trying to use decorator @node(...), but the tree is already assembled.')

        def decorator(func):
            # No validation on func is performed at this moment.
            # Validations are delayed until Tree.assemble() is called.
            self._node_decorated[label] = yes_label, no_label, func
            if self._root_label is None:
                # The first function decorated with @node(...) sets the root label.
                self._root_label = label
            return func

        return decorator

    def _do_not_use_this_decorator(self, label: Label, name: Optional[str] = None):
        """
        Former @parameter decorator. Removed support to this decorator because most parameters
        are defined AFTER a node is executed and not before as it was implemented here.
        OLD DOC STRING:
        The parameter that is being defined with this decorator will be computed
        immediately before the traversal of the tree reaches the node with the given label."""
        label = str(label)

        if not label:
            raise DecisionTreeError(message='The label of a custom parameter cannot be the empty string.')

        if self.root:
            raise DecisionTreeError(
                message='Trying to use decorator @parameter(...), but the tree is already assembled.')

        def decorator(func):
            # If no name is provided, the parameter name will be the name of the function:
            param_name = name or func.__name__

            self._validate_parameter_decorated_func(param_name, func)
            self.parameter_decorated.setdefault(label, list()).append((param_name, func))
            return func

        return decorator

    def _assemble_recursive(self, label: str, allowed_custom_parameters: Dict[str, Type], dev_mode: bool = False) \
            -> AbstractNode:
        if label in self._node:
            print(f'Warning! The structure is not a tree: node {label} has more than one parent.')
            return self._node[label]

        if self.ResultClass.is_valid(label):
            if label in self.execute_after and not dev_mode:
                raise DecisionTreeError(
                    f'Not allowed to decorate a function with @after({label}) as label "{label}" is an end-node.'
                )
            return LeafNode(label=label, simple_insight=self.ResultClass.simple_insight(label))

        if label not in self._node_decorated:
            if dev_mode:
                return LeafNode(label=label, simple_insight=SimpleInsight(
                    insight_type=InsightType.Error,
                    text='MISSING NODE'
                ))
            else:
                raise DecisionTreeError(message=f'Node {label} not found when assembling the tree.')

        new_custom_parameters = {
            param_name: func.__annotations__['return']
            for param_name, func in self.parameter_decorated.get(label, list())
        }
        allowed_custom_parameters = {**allowed_custom_parameters, **new_custom_parameters}

        yes_label, no_label, func = self._node_decorated.pop(label)
        predicate = Predicate(func, allowed_custom_parameters)
        yes_node = self._assemble_recursive(yes_label, allowed_custom_parameters, dev_mode=dev_mode)
        no_node = self._assemble_recursive(no_label, allowed_custom_parameters, dev_mode=dev_mode)
        node = DecisionNode(label, predicate, yes_node, no_node)
        self._node[label] = node
        return node

    def assemble(self, new_root_label: Optional[Label] = None, dev_mode: bool = False):
        """After all predicate functions have been decorated with @node,
        and before the tree can be traversed by the Policy class, it must
        be assembled. This method calls a recursive function that creates
        each node and links them together according to the given structure.

        The developer do not need to call this method.
        """
        if self.root:
            # Tree already assembled: there is nothing to be done.
            return

        if new_root_label is not None:
            self._root_label = str(new_root_label)

        if self._root_label is None:
            raise DecisionTreeError(message='No root node was defined for this tree.')

        self.root = self._assemble_recursive(self._root_label, allowed_custom_parameters=dict(), dev_mode=dev_mode)

        # Verify each @node decorated function appears in the tree.
        if self._node_decorated:
            print(end='WARNING! There are nodes that are not connected to the root of the tree:')
            print(self._node_decorated.keys())

        # Verify each @parameter decorated function is associated to a node of the tree.
        _remaining_parameters = set(self.parameter_decorated.keys()).difference(self._node.keys())
        for label in _remaining_parameters:
            print('WARNING! The list of custom parameters',
                  [param_name for param_name, _ in self.parameter_decorated[label]],
                  f'was defined at node {label}, but this node is either not defined or',
                  'not connected to the root of the tree.')

        del self._node
        del self._node_decorated

    def print(self):
        """Prints the tree in the standard output for verification."""
        t = copy(self)
        if t.root is None:
            t.assemble(dev_mode=True)
        t.root.print()

    @staticmethod
    def _validate_parameter_decorated_func(param_name: str, func):
        assert 'return' in func.__annotations__, \
            '@parameter decorated functions must have its return type annotated.'

        assert param_name != 'data', \
            'Error: parameter "data" is reserved. Please, use a different name for your custom parameter.'

        if func.__code__.co_argcount != 1 or len(func.__annotations__) != 2:
            raise CustomParameterError(f'@parameter decorated functions must have exactly '
                                       f'one argument with annotated type {Registry.__name__}.')
        for func_param_name, param_type in func.__annotations__:
            if func_param_name != 'return':
                if param_type is not Registry:
                    raise CustomParameterError(f'The single argument of a @parameter decorated '
                                               f'function must have type {Registry.__name__}.')

    @property
    def root_label(self):
        return self._root_label
