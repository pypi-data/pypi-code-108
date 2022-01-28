"""Kat model compiler.

This takes parsed productions, figures out the dependencies and builds the model in the
correct order.

Sean Leavey <sean.leavey@ligo.org>
"""

import logging
from collections import defaultdict, ChainMap
from io import StringIO
import re
from functools import singledispatchmethod
from networkx import (
    selfloop_edges,
    lexicographical_topological_sort,
    simple_cycles,
    descendants,
    NetworkXUnfeasible,
)
import numpy as np
from ..warnings import KeywordUsedWarning
from .. import Model
from ..env import warn
from ..symbols import Resolving
from ..utilities import option_list, ngettext
from ..exceptions import (
    FinesseException,
    ModelAttributeError,
    ModelParameterDefaultValueError,
    ModelParameterSelfReferenceError,
    ContextualTypeError,
    ContextualValueError,
)
from .graph import ROOT_NODE_NAME, KatGraph, KatNodeType, KatEdgeType
from .containers import (
    KatToken,
    KatReferenceToken,
    KatScript,
    KatElement,
    KatFunction,
    KatKwarg,
    KatGroupedExpression,
    KatExpression,
    KatArray,
    KatNumericalArray,
)
from .parser import KatParser
from .exceptions import KatScriptError, KatSyntaxError, KatMissingAfterDirective
from .util import duplicates, merge_attributes

LOGGER = logging.getLogger(__name__)


def _production(node, graph):
    from .generator import KatUnfiller

    unfiller = KatUnfiller()
    return unfiller.production(node, graph)


def _user_arg_productions_by_name(name, statement_node, adapter, graph):
    """Get arguments with name `name` specified by the user corresponding to the `graph`
    node `statement_node`.

    This searches the arguments specified by the user, so it can therefore be used to
    find invalid or duplicate arguments. Any positional arguments specified by the user
    are still matched by looking up the setter signature via `adapter`.

    Yields
    ------
    :class:`.TokenContainer`
        Production matching `name`.
    """
    for node in graph.sorted_dependent_argument_nodes(statement_node):
        try:
            argument = graph.argument(node, adapter)
        except TypeError:
            # This is an additional, unsupported positional argument.
            continue

        if argument.name == name:
            yield _production(node, graph)


class KatCompiler:
    """Kat model compiler."""

    def __init__(self, spec=None):
        if spec is None:
            from .spec import KatSpec

            spec = KatSpec()

        self.spec = spec
        self.graph = None
        self.build_graph = None
        self._parser = None
        self._parameter_dependencies = None
        self._build_order = None
        self._element_script_order = None

    @property
    def script(self):
        return self._parser.script

    def compile(self, string, **kwargs):
        """Compile the contents of `string`.

        Parameters
        ----------
        string : :class:`str`
            The string to compile kat script from.

        Other Parameters
        ----------------
        kwargs
            Keyword arguments supported by :meth:`.compile_file`.

        Returns
        -------
        :class:`.Model`
            The model compiled from reading `string`.
        """
        return self.compile_file(StringIO(string), **kwargs)

    def compile_file(self, fobj, model=None, resolve=True, build=True):
        """Compile the contents of the specified file.

        Parameters
        ----------
        fobj : :class:`io.FileIO`
            The file object to compile kat script from. This should be opened in text
            mode.

        model : :class:`.Model`, optional
            An existing model to compile the contents of `fobj` into. If not specified,
            a new, empty model is created.

        resolve : :class:`bool`, optional
            Resolve the parsed script. If False, the parsed contents is added to graph
            but no sanity checks are performed and nothing is returned. Defaults to
            True.

        build : :class:`bool`, optional
            Build the parsed script. If False, no Finesse objects will be added to the
            model and nothing will be returned. Defaults to True.

        Returns
        -------
        :class:`.Model` or None
            If `resolve` and `build` are True, the model compiled from reading `fobj`;
            None otherwise.

        Raises
        ------
        :class:`.KatSyntaxError`
            If a syntax error is present in the contents of `fobj`.
        """
        # Reset state.
        self._parser = KatParser()
        self.graph = KatGraph()
        self.build_graph = None
        self._parameter_dependencies = []
        self._element_script_order = {}

        try:
            script = self._parser.parse_file(fobj)
        except KatSyntaxError as e:
            # There was a syntax error. Try to improve the error message using the spec.
            self._reraise_parser_error_in_spec_context(e)

        # Build the parse graph.
        self._fill(script, ROOT_NODE_NAME)

        # At this stage there shouldn't be any dependencies between branches.
        assert self.graph.is_tree()

        if resolve:
            self._resolve()

            if build:
                model = self._build(ROOT_NODE_NAME, model)

                # Merge the compiled syntax graph into the model.
                if model.syntax_graph is None:
                    model.syntax_graph = self.graph
                else:
                    LOGGER.debug("merging compiled syntax into existing syntax graph")
                    model.syntax_graph.merge(self.graph)

                # Sort the model elements back into script order.
                def script_order_sort(item):
                    _, obj = item

                    # Ensure the script's elements appear after any existing elements in
                    # the model, but sort script elements in line order. We rely on
                    # :meth:`.Model.sort_elements` being stable to retain the order of
                    # existing elements.
                    try:
                        return 1, self._element_script_order[obj]
                    except KeyError:
                        # This object wasn't compiled as part of this call; leave it
                        # in its current position.
                        return (0,)

                model.sort_elements(key=script_order_sort)

                return model

    @property
    def _directive_functions(self):
        return ChainMap(self.spec.commands, self.spec.analyses)

    @property
    def _expression_functions(self):
        return ChainMap(self.spec.expression_functions, self.spec.unary_operators)

    @property
    def _available_functions(self):
        return ChainMap(self._directive_functions, self._expression_functions)

    def _fill(self, value, path, **attributes):
        attributes = merge_attributes(
            attributes, self._item_node_attributes(value, path)
        )
        self.graph.add_node(path, **attributes)

        if hasattr(value, "arguments"):
            # Assemble arguments.
            for order, argument in enumerate(value.arguments):
                argument_path = self.graph.item_node_name(order, path)
                self._fill(argument, argument_path)
                self.graph.add_edge(
                    argument_path, path, type=KatEdgeType.ARGUMENT, order=order
                )

        return attributes

    @singledispatchmethod
    def _item_node_attributes(self, item, path):
        """Get the attributes for `item` to be added to the corresponding node."""
        raise NotImplementedError(
            f"don't know how to handle an item with type '{item.__class__.__name__}'"
        )

    @_item_node_attributes.register(KatScript)
    def _(self, script, path):
        return {"type": KatNodeType.ROOT, "extra_tokens": script.extra}

    @_item_node_attributes.register(KatToken)
    def _(self, token, path):
        attributes = {"token": token}
        if token.type == "NAME":
            # This could be a keyword, constant or parameter reference.
            name = token.value

            if name in self.spec.keywords:
                token_type = KatNodeType.KEYWORD
            elif name in self.spec.constants:
                token_type = KatNodeType.CONSTANT
            else:
                # Assume this is a parameter like `l1.P`.
                self._parameter_dependencies.append(path)
                token_type = KatNodeType.PARAMETER
        else:
            # This is some other token like a number or string.
            token_type = KatNodeType.VALUE

        attributes["type"] = token_type

        return attributes

    @_item_node_attributes.register(KatReferenceToken)
    def _(self, token, path):
        attributes = {"token": token, "type": KatNodeType.PARAMETER_REFERENCE}
        self._parameter_dependencies.append(path)
        return attributes

    @_item_node_attributes.register(KatKwarg)
    def _(self, kwarg, path):
        return self._fill(
            kwarg.value, path, key_token=kwarg.key, extra_tokens=kwarg.extra
        )

    @_item_node_attributes.register(KatElement)
    def _(self, element, path):
        directive_token = element.directive
        element_type = directive_token.value
        if element_type not in self.spec.elements:
            if element_type in self.spec.commands or element_type in self.spec.analyses:
                # Syntax error was on an command or analysis definition.
                raise KatIncorrectFormError(directive_token, self.script, self.spec)
            else:
                raise KatSyntaxError(
                    f"unknown element '{directive_token.raw_value}'",
                    self.script,
                    directive_token,
                )
        return {
            "token": element.directive,
            "name_token": element.name,
            "type": KatNodeType.ELEMENT,
            "extra_tokens": element.extra,
        }

    @_item_node_attributes.register(KatFunction)
    def _(self, function, path):
        directive_token = function.directive
        if directive_token.value not in self._available_functions:
            raise KatSyntaxError(
                f"unknown function '{directive_token.raw_value}'",
                self.script,
                directive_token,
            )
        return {
            "token": directive_token,
            "type": KatNodeType.FUNCTION,
            "extra_tokens": function.extra,
        }

    @_item_node_attributes.register(KatGroupedExpression)
    def _(self, group, path):
        return {
            "type": KatNodeType.GROUPED_EXPRESSION,
            "extra_tokens": group.extra,
        }

    @_item_node_attributes.register(KatExpression)
    def _(self, expression, path):
        operator_token = expression.operator
        if operator_token.value not in self.spec.binary_operators:
            raise KatSyntaxError(
                f"unknown expression operator '{operator_token.raw_value}'",
                self.script,
                expression.operator,
            )
        return {"type": KatNodeType.EXPRESSION, "token": operator_token}

    @_item_node_attributes.register(KatArray)
    def _(self, array, path):
        return {"type": KatNodeType.ARRAY, "extra_tokens": array.extra}

    @_item_node_attributes.register(KatNumericalArray)
    def _(self, array, path):
        return {"type": KatNodeType.NUMERICAL_ARRAY, "extra_tokens": array.extra}

    def _resolve(self):
        """Resolve references and perform sanity checks on the graph.

        Dependencies due to parameters (e.g. `m1.p1.o`) and parameter references (e.g.
        `&l1.P`) are created by drawing edges to the relevant nodes, transforming the
        parse tree into a graph.

        This additionally checks that:

        - element names are valid and unique,
        - keyword arguments aren't defined in duplicate, and
        - no cycles exist due to dependencies (i.e. if a reference depends on the
          referencing component or its ancestors in any way).

        The `order` attributes of the root edges are overwritten using a topological
        sort to ensure the resulting graph is built in a way that most types of
        dependency can be resolved.
        """
        # Various types of node that we need to validate.
        elements = defaultdict(list)
        singular_directives = defaultdict(list)
        analyses = []

        root_directive_nodes = self.graph.dependent_argument_nodes(
            ROOT_NODE_NAME, data=True
        )

        for directive_node, data in root_directive_nodes:
            node_type = data["type"]
            token = data["token"]
            directive = token.value

            if node_type in KatNodeType.DIRECTIVE_NODES:
                if node_type in KatNodeType.ELEMENT:
                    name_token = data["name_token"]
                    name = name_token.value

                    if name in self.spec.constants:
                        # Disallow.
                        raise KatScriptError(
                            f"constant '{name}' cannot be used as an element name",
                            self.script,
                            [[name_token]],
                        )
                    elif name in self.spec.keywords:
                        warn(
                            f"element name {repr(name)} (line {name_token.lineno}) is "
                            f"also the name of a keyword, which may lead to confusion",
                            KeywordUsedWarning,
                        )

                    adapter = self._element_adapter(directive)
                    elements[name].append(directive_node)
                elif node_type in KatNodeType.FUNCTION:
                    adapter = self._function_adapter(directive)
                    if directive in self.spec.analyses:
                        analyses.append(token)

                if adapter.singular:
                    singular_directives[directive].append(directive_node)

                # Check for duplicate keyword arguments.
                dupekvs = duplicates(
                    [
                        self.graph.nodes[node]["key_token"]
                        for node in self.graph.dependent_argument_nodes(directive_node)
                        if "key_token" in self.graph.nodes[node]
                    ],
                    key=lambda token: token.raw_value,
                )
                if dupekvs:
                    keys, dupetokens = zip(*dupekvs)
                    keylist = option_list([f"'{key}'" for key in keys], final_sep="and")
                    msg = ngettext(
                        len(keys),
                        f"duplicate arguments with key {keylist}",
                        f"duplicate arguments with keys {keylist}",
                        sub=False,
                    )
                    error_tokens = [
                        [token] for tokens in dupetokens for token in tokens
                    ]
                    raise KatDirectiveError(
                        msg,
                        directive,
                        self.script,
                        error_tokens,
                        self.spec,
                        add_syntax_hint=True,
                    )

        for directive, nodes in singular_directives.items():
            if len(nodes) > 1:
                raise KatScriptError(
                    f"there can only be one '{directive}' directive",
                    self.script,
                    [[self.graph.nodes[node]["token"]] for node in nodes],
                )

        for name, nodes in elements.items():
            if len(nodes) > 1:
                raise KatScriptError(
                    f"multiple elements with name '{name}'",
                    self.script,
                    [[self.graph.nodes[node]["name_token"]] for node in nodes],
                )

        # Check that there isn't more than one root analysis.
        if len(analyses) > 1:
            raise KatScriptError(
                "duplicate analysis trees (combine with 'series' or 'parallel')",
                self.script,
                [[token] for token in analyses],
            )

        # Create dependencies for parameters and parameter references.
        for source_param_path in self._parameter_dependencies:
            source_token = self.graph.nodes[source_param_path]["token"]

            # Targets may not exist in the current script; they may already be in the
            # model prior to parsing.
            try:
                target_directive_path = self.graph.param_target_element_path(
                    source_token.value, ROOT_NODE_NAME
                )
            except ValueError:
                LOGGER.debug(
                    f"parameter '{source_token.raw_value}' targetted by "
                    f"'{source_param_path}' does not exist in the script - ignoring"
                )
                continue

            # Add the dependency.
            self.graph.add_edge(
                target_directive_path,
                source_param_path,
                type=KatEdgeType.DEPENDENCY,
            )

        # Create graph with just the root directives (use a copy because it may be
        # modified during compilation).
        self.build_graph = self.graph.directive_graph(ROOT_NODE_NAME)

        def node_build_order(source_graph):
            """Compute node topological order, or throw a cycle error."""
            # Remove self-references, since these will be dealt with by the compiler.
            graph = source_graph.copy()
            for edge in selfloop_edges(source_graph):
                graph.remove_edge(*edge)

            try:
                # Compute topological order, resolving ambiguities in favour of lower
                # line numbers.
                # Convert to list so we know immediately if there are cycles.
                return list(
                    lexicographical_topological_sort(
                        graph, key=lambda node: graph.nodes[node]["token"].lineno
                    )
                )
            except NetworkXUnfeasible:
                # The graph contains at least one cyclic dependency. Work out the
                # cause(s) by finding cycles using the full graph.
                cyclic_param_nodes = set()
                for cycle_nodes in simple_cycles(self.graph):
                    for cycle_node in cycle_nodes:
                        data = self.graph.nodes[cycle_node]
                        if data["type"] not in KatNodeType.DEPENDENT_NODES:
                            # Ignore anything in the cycle that isn't a reference node
                            # (e.g. directives).
                            continue

                        cyclic_param_nodes.add(cycle_node)

                # Grab and sort the cyclic tokens in line order.
                cyclic_parameter_tokens = sorted(
                    [self.graph.nodes[node]["token"] for node in cyclic_param_nodes],
                    key=lambda tok: tok.lineno,
                )

                raise KatCycleError(self.script, cyclic_parameter_tokens)

        # Split the nodes into groups depending on whether they descend from a node with
        # the "last" flag.
        first_build_nodes = set(self.build_graph.nodes)
        second_build_nodes = set()
        for node in self.build_graph.nodes():
            adapter = self._directive_adapter(self.graph.nodes[node]["token"].value)

            try:
                last = adapter.factory.last
            except AttributeError:
                last = False

            if not last or node in second_build_nodes:
                # Keep the directive in the first set.
                continue

            # All nodes that descend from (depend on) specified node.
            children = descendants(self.build_graph, node)

            # Move node and descendants from first to second build step.
            first_build_nodes.remove(node)
            first_build_nodes.difference_update(children)
            second_build_nodes.add(node)
            second_build_nodes.update(children)

        first_build_order = node_build_order(
            self.build_graph.subgraph(first_build_nodes)
        )
        second_build_order = node_build_order(
            self.build_graph.subgraph(second_build_nodes)
        )
        self._build_order = first_build_order + second_build_order
        LOGGER.debug(f"Build order: {self._build_order}")

    def _build(self, node, model, kwarg_as_dict=True):
        """Build the branch at `node` into a model item.

        `kwarg_as_dict` sets whether keyword arguments should be returned as
        :class:`.dict` instead of just values.
        """
        data = self.graph.nodes[node]
        nodetype = data["type"]

        if nodetype in KatNodeType.COMPILER_TERMINAL_NODES:
            # Just use the value.
            value = data["token"].value
        elif nodetype == KatNodeType.CONSTANT:
            # Look up the symbol corresponding to the constant.
            value = self.spec.constants[data["token"].value]
        elif nodetype == KatNodeType.PARAMETER:
            # Copy existing model parameter by value.
            target = data["token"].value
            value = model.get(target)
            LOGGER.debug(f"parameter {node} targets {target} by value")
        elif nodetype == KatNodeType.PARAMETER_REFERENCE:
            source_directive_path = self.graph.branch_base(node, ROOT_NODE_NAME)

            if self.graph.has_edge(source_directive_path, node):
                # This is a reference to another parameter in the same element. Throw an
                # exception that can get caught by the argument compiler. Doing it this
                # way ensures expressions with nested self-references (like `1-&m1.T` in
                # `m m1 1-&m1.T 0`) get set as resolving.
                LOGGER.debug(f"{node} is a self-reference")
                raise KatParameterSelfReferenceException()

            # Copy existing model parameter by reference.
            target = data["token"].value
            try:
                value = model.get(target).ref
            except FinesseException as e:
                # There was an error getting a reference to the target.
                raise KatParameterBuildError(e, self.script, node, self.graph) from e
            LOGGER.debug(f"parameter {node} targets {target} by reference")
        elif nodetype == KatNodeType.EXPRESSION:
            operator = self.spec.binary_operators[data["token"].value]
            arguments = self._built_arguments(node, model)
            # Arguments are already in order.
            assert len(arguments) == 2
            lhs, rhs = arguments
            value = operator(lhs, rhs)

            # Eagerly evaluate the expression if its arguments don't depend on anything
            # else.
            if self.graph.is_independent(node):
                value = value.eval()
                LOGGER.debug(
                    f"eagerly evaluated dependencyless expression '{node}' to a "
                    f"{type(value)}"
                )
        elif nodetype == KatNodeType.GROUPED_EXPRESSION:
            arguments = self._built_arguments(node, model)
            assert len(arguments) == 1
            value = arguments[0]
        elif nodetype == KatNodeType.ARRAY:
            value = self._built_arguments(node, model)
        elif nodetype == KatNodeType.NUMERICAL_ARRAY:
            value = np.array(self._built_arguments(node, model))
        elif nodetype == KatNodeType.ELEMENT:
            args, kwargs = self._built_directive_params(node, model)
            adapter = self._element_adapter(data["token"].value)

            # Add name to arguments.
            name = data["name_token"].value
            args = [name, *args]

            try:
                value = adapter.factory(*args, **kwargs)
            except Exception as e:
                raise KatDirectiveBuildError(
                    e,
                    data["token"].value,
                    self.script,
                    node,
                    adapter,
                    self.graph,
                    self.spec,
                ) from e
        elif nodetype == KatNodeType.FUNCTION:
            function_name = data["token"].value

            if function_name in self._expression_functions:
                operator = self._expression_functions[function_name]
                args, kwargs = self._built_directive_params(node, model)

                try:
                    value = operator(*args, **kwargs)
                except TypeError as e:
                    # Replace 'lambda' in the function init error with the function
                    # name.
                    args = list(e.args)
                    args[0] = re.sub(
                        r"(\<lambda\>(\d+)?|\w+)\(\)",
                        f"'{function_name}'",
                        args[0],
                    )
                    raise TypeError(*args)

                # Eagerly evaluate the function if its arguments don't depend on
                # anything else.
                if self.graph.is_independent(node):
                    value = value.eval()
                    LOGGER.debug(
                        f"eagerly evaluated dependencyless function '{node}' to a "
                        f"{type(value)}"
                    )
            else:
                # A directive function.
                adapter = self._function_adapter(data["token"].value)
                args, kwargs = self._built_directive_params(node, model)

                if adapter.factory is not None:
                    try:
                        value = adapter.factory(*args, **kwargs)
                    except Exception as e:
                        raise KatDirectiveBuildError(
                            e,
                            data["token"].value,
                            self.script,
                            node,
                            adapter,
                            self.graph,
                            self.spec,
                        ) from e
                else:
                    LOGGER.debug(f"function {node} has arguments {args}, {kwargs}")
                    value = args, kwargs
        elif nodetype == KatNodeType.ROOT:
            if model is None:
                LOGGER.debug("creating new model")
                model = Model()
            else:
                LOGGER.debug(f"compiling into existing model {repr(model)}")

            # Use the computed build order, not the argument order.
            for argument_node in self._build_order:
                item = self._build(argument_node, model)
                directive_token = self.graph.nodes[argument_node]["token"]
                directive = directive_token.value
                adapter = self._directive_adapter(directive)

                if self.graph.nodes[argument_node]["type"] is KatNodeType.ELEMENT:
                    # Remember the item's original order for when we sort the elements.
                    self._element_script_order[item] = directive_token.lineno

                LOGGER.debug(f"applying {repr(item)} ({argument_node}) to model")
                try:
                    adapter.setter(model, item)
                except Exception as e:
                    raise KatDirectiveBuildError(
                        e,
                        directive,
                        self.script,
                        argument_node,
                        adapter,
                        self.graph,
                        self.spec,
                    ) from e

                # Get all nodes connected to this argument node by a DEPENDENCY edge,
                # where the node is a subbranch of the argument node.
                # Convert to a list because we'll iterate multiple times.
                self_references = list(
                    self.graph.filter_dependent_nodes(
                        argument_node,
                        key=lambda refnode, _: self.graph.branch_base(
                            refnode, ROOT_NODE_NAME
                        )
                        == argument_node,
                    )
                )

                if self_references:
                    # Delete graph dependencies so that references resolve when we build
                    # again.
                    for target in self_references:
                        LOGGER.debug(f"breaking dependency {argument_node} -> {target}")
                        self.graph.remove_edge(argument_node, target)

                    for self_ref_path in self_references:
                        self_ref_param_path = self.graph.branch_base(
                            self_ref_path, argument_node
                        )

                        # Figure out the signature argument and use it to grab the
                        # corresponding element's parameter.
                        reference_argument = self.graph.argument(
                            self_ref_param_path, adapter
                        )

                        LOGGER.debug(
                            f"resolving self-referencing {reference_argument.name}"
                        )
                        value = self._build(
                            self_ref_param_path, model, kwarg_as_dict=False
                        )

                        LOGGER.debug(
                            f"setting {reference_argument.name} to {repr(value)} (type "
                            f"{type(value)})"
                        )
                        try:
                            adapter.setter.update_parameter(
                                item, reference_argument, value
                            )
                        except Exception as e:
                            raise KatParameterBuildError(
                                e, self.script, self_ref_param_path, self.graph
                            ) from e

                    LOGGER.debug(f"finished resolving self-refs for {repr(item)}")

            # Remove dependency edges from the graph. They are no longer needed now that
            # we've built everything, and if left they can interfere merging of syntax
            # graphs in the model.
            self.graph.remove_edges_from(
                [
                    (u, v)
                    for u, v, edgetype in self.graph.edges(data="type")
                    if edgetype == KatEdgeType.DEPENDENCY
                ]
            )

            value = model
        else:
            raise RuntimeError(f"don't know how to compile parameter {repr(nodetype)}")

        # Create a dictionary for keyword arguments, if requested.
        if kwarg_as_dict and "key_token" in data:
            value = {data["key_token"].value: value}

        LOGGER.debug(f"compiled {nodetype} {node} to {type(value)}")
        return value

    def _built_arguments(self, node, model):
        """Get built dependent arguments of the current node."""
        return [
            self._build(argument_node, model)
            for argument_node in self.graph.sorted_dependent_argument_nodes(node)
        ]

    def _built_directive_params(self, node, model):
        """Get built dependent arguments of the current node in Python signature form.

        Self-referencing parameters are caught here too, and set to :class:`.Resolving`;
        these are fully resolved at the end of compilation.
        """
        args = []
        kwargs = {}
        for argument_node in self.graph.sorted_dependent_argument_nodes(node):
            try:
                item = self._build(argument_node, model)
            except KatParameterSelfReferenceException:
                item = Resolving()

                # Detect kwargs.
                if key_token := self.graph.nodes[argument_node].get("key_token"):
                    item = {key_token.value: item}

            if isinstance(item, dict):
                kwargs.update(item)
            else:
                args.append(item)
        return args, kwargs

    def _element_adapter(self, element):
        return self.spec.elements[element]

    def _function_adapter(self, function):
        if command := self.spec.commands.get(function):
            return command
        if analysis := self.spec.analyses.get(function):
            return analysis

        raise KeyError(f"could not find function corresponding to '{function}'")

    def _directive_adapter(self, directive):
        try:
            return self._element_adapter(directive)
        except KeyError:
            try:
                return self._function_adapter(directive)
            except KeyError:
                raise KeyError(
                    f"could not find directive corresponding to '{directive}'"
                )

    def _reraise_parser_error_in_spec_context(self, error):
        """Try to improve parser errors using the :class:`.KatSpec`.

        The parser is unaware of the available elements and functions etc. in the kat
        language spec, because this is only used during compilation. In some cases the
        error messages can be improved with knowledge of the spec, so this method
        identifies such cases.
        """
        if isinstance(error, KatMissingAfterDirective):
            # Use the spec to figure out whether the user might have missed a
            # parenthesis or a name.
            if error.directive.value in self.spec.directives:
                raise KatIncorrectFormError(error.directive, self.script, self.spec)
            else:
                # Unrecognised directive type. Since that's the earlier error, throw
                # that.
                raise KatScriptError(
                    f"unknown element or function '{error.directive.raw_value}'",
                    self.script,
                    [[error.directive]],
                )

        # Nothing matched, so just reraise.
        raise error


class KatIncorrectFormError(KatSyntaxError):
    """Error representing an element, command or analysis that uses the wrong syntax
    form.

    For example, this is thrown when a command is written in "element" KatScript form,
    and vice versa.

    This is technically a syntax error, but it is not caught there because it doesn't
    know which directives use which type of syntax.
    """

    def __init__(self, user_directive_token, script, spec):
        user_directive = user_directive_token.raw_value
        adapter = spec.directives[user_directive]
        form = adapter.documenter.syntax_correction(user_directive, spec=spec)

        super().__init__(
            f"{repr(user_directive)} should be written in the form {repr(form)}",
            script,
            user_directive_token,
        )


class KatCycleError(KatScriptError):
    """Cyclic parameters."""

    def __init__(self, script, cyclic_nodes):
        # Convert list of error tokens to error item lists.
        items = [[item] for item in cyclic_nodes]
        super().__init__("cyclic parameters", script, items)


class KatDirectiveError(KatScriptError):
    """Error compiling a directive (either resolving or building)."""

    def __init__(
        self, error, directive, script, error_items, spec, add_syntax_hint=False
    ):
        syntax = None
        if add_syntax_hint:
            adapter = spec.directives[directive]
            syntax = adapter.documenter.syntax(spec, adapter)

        super().__init__(error, script, error_items, syntax=syntax)


class KatDirectiveBuildError(KatDirectiveError):
    """Error during the building of a directive (i.e. the call to the Finesse Python
    object)."""

    def __init__(self, error, directive, script, statement_node, adapter, graph, spec):
        if error:
            # Rewrite the error message to provide additional context to the user about
            # what went wrong.
            error, error_items, add_syntax_hint = self._rewrite(
                error, directive, script, statement_node, adapter, graph, spec
            )
        else:
            # Mark the whole line as the cause of the error.
            error_items = [[_production(statement_node, graph)]]
            add_syntax_hint = False

        super().__init__(
            error, directive, script, error_items, spec, add_syntax_hint=add_syntax_hint
        )

    @singledispatchmethod
    def _rewrite(self, error, directive, script, statement_node, adapter, graph, spec):
        # This performs the default rewrite behaviour when no matching type is found in
        # the dispatch.

        # By default, mark the whole line as the cause of the error.
        error_items = [[_production(statement_node, graph)]]

        return str(error), error_items, False

    @_rewrite.register(TypeError)
    def _(self, error, directive, script, statement_node, adapter, graph, spec):
        # Replace the called Finesse Python API function, if present, with the directive
        # name. Replaces whatever appears before the first "()" in the error.
        msg = re.sub(r".+\(\)", f"'{directive}'", str(error))

        # Match specific error messages.
        if matches := re.search(r"unexpected keyword argument '(\w+)'", msg):

            def keyfunc(_, nodedata):
                try:
                    return nodedata["key_token"].value == matches.group(1)
                except KeyError:
                    return False

            kwarg_node = next(graph.filter_argument_nodes(statement_node, keyfunc))
            # Mark the matching kwarg key in the error.
            item = _production(kwarg_node, graph)
            error_items = [[item.key]]
        elif matches := re.search(
            r"missing (\d+) required positional arguments?:", msg
        ):
            params = list(adapter.setter.positional_args(keyword_defaults=False))
            nmissing = int(matches.group(1))
            imissingstart = len(params) - nmissing
            assert nmissing > 0
            assert imissingstart >= 0
            description = ngettext(
                nmissing,
                "{n} required positional argument",
                "{n} required positional arguments",
            )
            missing = option_list(
                [repr(arg) for arg in params[imissingstart:]], final_sep="and"
            )

            msg = f"'{directive}' missing {description}: {missing}"

            # Add a marker at the end of the arguments.
            item = _production(statement_node, graph)
            error_items = [[item.missing_argument_meta_token()]]
        elif matches := re.search(
            r"takes (\d+) positional arguments but (\d+) were given", msg
        ):
            # Fix the number of arguments.
            params = adapter.setter.positional_args()
            ncorrection = int(matches.group(1)) - len(params)
            assert ncorrection >= 0
            nnew = [int(n) - ncorrection for n in matches.groups()]
            nmax = nnew[0]
            arg = ngettext(nnew[0], "argument", "arguments", sub=False)

            msg = (
                f"'{directive}' takes {nnew[0]} positional {arg} but {nnew[1]} "
                f"were given"
            )

            # Mark the extra arguments.
            arguments = graph.sorted_dependent_argument_nodes(statement_node)
            error_items = [[_production(node, graph)] for node in arguments[nmax:]]
        elif matches := re.search(
            r"takes from (\d+) to (\d+) positional arguments but (\d+) were given",
            msg,
        ):
            # Fix the number of arguments.
            params = adapter.setter.positional_args()
            ncorrection = int(matches.group(2)) - len(params)
            assert ncorrection >= 0
            nnew = [int(n) - ncorrection for n in matches.groups()]
            nmax = nnew[1]

            msg = (
                f"'{directive}' takes from {nnew[0]} to {nnew[1]} positional "
                f"arguments but {nnew[2]} were given"
            )

            # Mark the extra arguments.
            arguments = graph.sorted_dependent_argument_nodes(statement_node)
            error_items = [[_production(node, graph)] for node in arguments[nmax:]]
        elif matches := re.search(r"got multiple values for argument '(\w+)'", msg):
            # Mark the duplicate arguments. We can't use the signature here because by
            # definition this error happens when the signature is not followed. Instead
            # we use the graph to see what was actually parsed.
            error_items = []
            items = _user_arg_productions_by_name(
                matches.group(1), statement_node, adapter, graph
            )
            for item in items:
                if hasattr(item, "key"):
                    # This is a kwarg - mark the value.
                    item = item.value
                error_items.append([item])
        else:
            # By default, mark the whole line as the cause of the error.
            error_items = [[_production(statement_node, graph)]]

        return msg, error_items, True

    @_rewrite.register(ContextualTypeError)
    def _(self, error, directive, script, statement_node, adapter, graph, spec):
        arg_item = next(
            _user_arg_productions_by_name(error.param, statement_node, adapter, graph)
        )
        error_items = [[arg_item]]

        # Substitute known types with descriptive equivalents (shield the user from
        # Finesse internals).
        allowedstr = option_list(
            [spec.type_descriptor(t, t.__name__) for t in error.allowed_types]
        )
        gotstr = spec.type_descriptor(type(error.value), type(error.value).__name__)

        msg = (
            f"invalid type for '{directive}' argument '{error.param}': expected "
            f"{allowedstr}, got {gotstr}"
        )

        return msg, error_items, True

    @_rewrite.register(ContextualValueError)
    def _(self, error, directive, script, statement_node, adapter, graph, spec):
        data = graph.nodes[statement_node]
        error_items = []

        for param, value in error.params.items():
            try:
                item = next(
                    _user_arg_productions_by_name(param, statement_node, adapter, graph)
                )
            except StopIteration:
                if value == ContextualValueError.empty:
                    # The value was empty because it wasn't specified.
                    continue

                # Names are arguments to Python but aren't to the parser.
                if param == "name" and "name_token" in data:
                    # This is an element and the issue was with the name.
                    item = data["name_token"]
                else:
                    # Something went wrong...
                    raise RuntimeError(
                        f"'{directive}' build signalled an error with argument "
                        f"'{param}' but no matching argument of graph node "
                        f"{statement_node} was found"
                    )

            if hasattr(item, "key"):
                # Mark the value when it's a kwarg.
                item = item.value

            error_items.append([item])

        if not error_items:
            if any(
                [value == ContextualValueError.empty for value in error.params.values()]
            ):
                # There are missing parameters. Add a marker at the end of the
                # arguments.
                statement = _production(statement_node, graph)
                error_items = [[statement.missing_argument_meta_token()]]
            else:
                # By default, mark the whole line as the cause of the error.
                error_items = [[_production(statement_node, graph)]]

        problem = ngettext(
            len(error.params),
            f"invalid value for '{directive}' argument",
            f"invalid values for '{directive}' arguments",
            sub=False,
        )

        extra = f": {error.extra_info}" if error.extra_info else ""
        args = option_list(error.params, final_sep="and", quotechar="'")
        msg = f"{problem} {args}{extra}"

        return msg, error_items, True


class KatParameterBuildError(KatScriptError):
    """Error during the building of a directive parameter."""

    def __init__(self, error, script, param_node, graph):
        data = graph.nodes[param_node]
        value_token = data["token"]
        show_items = [value_token]

        # Add the key if it exists.
        try:
            show_items.append(data["key_token"])
        except KeyError:
            pass

        msg = str(error).strip()

        if isinstance(error, ModelAttributeError):
            # Mark only the value.
            show_items = [value_token]
        elif isinstance(error, ModelParameterDefaultValueError):
            # A referenced component doesn't have a default model parameter.
            target = data["token"].value
            msg = f"{msg} (hint: try '&{target}.[some parameter]')"
            # Mark only the value.
            show_items = [value_token]
        elif isinstance(error, ModelParameterSelfReferenceError):
            # Grab the production.
            item = _production(param_node, graph)
            # Mark the key and the value.
            show_items = item.sorted_tokens

        super().__init__(msg, script, [show_items])


class KatParameterSelfReferenceException(Exception):
    """Indication that a parameter contains a self-reference that must be resolved
    later."""
