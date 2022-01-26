from __future__ import annotations

import contextlib
import contextvars
import enum
import json
import logging
import operator
import re
from typing import Any, Dict, Iterable, List, Optional, Union

import exrex
import xmlschema
from faker import Faker
from typing_extensions import TypeAlias
from xmlschema.validators import (
    XsdAnyElement,
    XsdAtomic,
    XsdElement,
    XsdEnumerationFacets,
    XsdGroup,
    XsdList,
    XsdType,
    XsdUnion,
)
from xmlschema.validators.complex_types import XsdComplexType

from . import utils

JsonMLData: TypeAlias = "list[str | dict[str, Any] | list[JsonMLData]]"

log = logging.getLogger(__name__)


class Validation(enum.Enum):
    strict = "strict"
    lax = "lax"
    skip = "skip"


visited = contextvars.ContextVar("visited")
recursive = contextvars.ContextVar("recursive", default=False)
depth = contextvars.ContextVar("depth", default=0)
inside_union = contextvars.ContextVar("inside_union", default=False)

faker = Faker()

skip_optional = contextvars.ContextVar("skip_optional", default=False)
max_depth = contextvars.ContextVar("max_depth", default=0)


def check_bounds(node):
    if isinstance(node, SkipNode):
        return node

    if skip_optional.get() and node.is_composed() and node.is_optional():
        return SkipNode(node.node)

    md = max_depth.get()
    if md and md < depth.get():
        return TooDeepNode(node.node)

    if node.visited() and node.is_composed():
        return RecursionNode(node.node)


@contextlib.contextmanager
def set_context(data: dict[contextvars.ContextVar[Any], Any]):
    tokens: dict[contextvars.ContextVar, contextvars.Token] = {}
    for cv, value in data.items():
        tokens[cv] = cv.set(value)
    yield
    for cv, token in tokens.items():
        cv.reset(token)


class Builder:
    root: xmlschema.XsdElement

    def __init__(self, schema: xmlschema.XMLSchema, root: str):
        el = utils.lookup(root, schema)

        assert el is not None, "Builder root at {str} must be available"

        self.root = el

    def build(self, data):
        ns = {f"xmlns:{k}": v for k, v in utils.ns.items()}
        if len(data) < 2 or not isinstance(data[1], dict):
            data[1:1] = [{}]
        # breakpoint()
        data[1].update(ns)

        el = self.root.encode(data, converter=xmlschema.JsonMLConverter)
        return el

    def example(
        self,
        fmt: str,
        seed: Optional[str] = None,
        skip_optional: bool = True,
        max_depth: int = 0,
    ):
        if not seed:
            seed = Faker().pystr()
        log.info("Using seed: %s", seed)
        Faker.seed(seed)

        tree = BfsTree(self.root, skip_optional, False, max_depth)
        example = tree.dictize()
        if fmt == "xml":
            el = self.build(example)
            return xmlschema.etree_tostring(
                el, namespaces=utils.ns, xml_declaration=True
            )
        else:
            return json.dumps(example, indent=2)

    def print_tree(
        self,
        fmt,
        skip_optional,
        qualified: bool = True,
        max_depth: int = 0,
        annotated: bool = False,
    ):
        tree = DfsTree(
            self.root, skip_optional, qualified, max_depth, annotated
        )
        if fmt == "overview":
            print(tree)
        elif fmt == "dataclass":
            tree.max_depth = 2
            print_dataclass(tree)

    def implementations(self) -> list[BaseNode]:
        node = make_node(self.root)
        if not node.is_abstract():
            return [node]

        return list(node.children)


def print_dataclass(tree):
    definition = ""
    for node in tree:
        d = depth.get()
        if d == 0:
            definition += "@dataclass\n"
            definition += f"class {node.node.local_name}:\n"

        elif d == 1:
            definition += f"    {node.node.local_name}"
            type_ = "{type}"
            value = None
            if node.is_multiple():
                type_ = f"list[{type_}]"
                value = "field(default_factory=list)"
            if node.is_optional():
                type_ = f"Optional[{type_}]"
                if not value:
                    value = "None"

            definition += f": {type_}"
            if value:
                definition += f" = {value}"
            definition += "\n"

        elif d == 2:
            name = node.name(False) or "Any"
            type_ = name.replace(":", ".")
            if "codeListValue" in getattr(node.node, "attributes", {}):
                type_ = f"Codelist[{type_}]"
            definition = definition.format(type=type_)

    print(definition)


class Tree:
    def __init__(
        self,
        node,
        skip_optional: bool,
        qualified: bool,
        max_depth: int = 0,
        annotated: bool = False,
    ):
        self.skip_optional = skip_optional
        self.qualified = qualified
        self.max_depth = max_depth
        self.annotated = annotated
        self.node = make_node(node)

    def _yield_from_node(self, node: BaseNode):
        bound = check_bounds(node)
        if bound:
            yield bound
            return

        yield from node

    def __iter__(self):
        ctx = contextvars.copy_context()
        with set_context(
            {
                visited: set(),
                max_depth: self.max_depth,
                skip_optional: self.skip_optional,
            }
        ):
            yield from ctx.run(self._yield_from_node, self.node)


class BfsTree(Tree):
    def dictize(self, format="jml"):
        root = next(iter(self))

        return root.example(format)


class DfsTree(Tree):
    def _yield_from_node(self, node: BaseNode):
        bound = check_bounds(node)
        if bound:
            yield bound
            return

        for n in list(node):
            if n is node:
                yield n
            else:
                yield from self._yield_from_node(n)

        with node.visit() as children:
            for child in children:

                yield from self._yield_from_node(child)

    def __str__(self):
        return "\n".join(
            n.into_indent(self.qualified, self.annotated) for n in self
        )


def make_node(node: XsdType) -> BaseNode:
    if isinstance(node, XsdElement):
        return ElementNode(node)
    if isinstance(node, XsdAtomic):
        return AtomicNode(node)
    if isinstance(node, XsdUnion):
        return UnionNode(node)

    if isinstance(node, XsdList):
        return ListNode(node)

    if isinstance(node, XsdGroup):
        return GroupNode(node)
    if isinstance(node, XsdAnyElement):
        return SkipNode(node, ())

    else:
        raise TypeError(f"Unsupported node type {node}")


class BaseNode:
    children: Iterable["BaseNode"]

    def __iter__(self):
        yield self

    def __init__(self, node: XsdType, children=()):
        self.node = node
        self.children = map(make_node, children)

    @property
    def id(self):
        return self.node.qualified_name

    @contextlib.contextmanager
    def visit(self):
        with set_context(
            {
                recursive: self.visited(),
                depth: depth.get() + 1,
                inside_union: self.is_abstract() or self.is_union(),
            }
        ):
            visited.get().add(self.id)
            yield self.children

    def visited(self):
        return bool(self.id and self.id in visited.get())

    def name(self, qualified: bool):
        if qualified:
            return self.node.qualified_name
        return self.node.prefixed_name

    def is_optional(self):
        return self.node.is_emptiable()

    # def is_optional(self):
    #     return False

    def is_union(self):
        return False

    def is_abstract(self):
        return self.node.abstract

    def is_multiple(self):
        return False

    def is_composed(self):
        return True

    def _unwrap_children(self, children):
        for child in children:
            yield from child

    def _unwrap(self):
        root = self

        if root.is_abstract() or root.is_union():
            with root.visit() as options:
                options = list(self._unwrap_children(options))

                if not options:
                    return NotImplementedNode(root.node)
                root = faker.random_element(options)._unwrap()

        return root

    def example(self, format) -> Any:
        assert False, f"Example is not defined for {self.__class__.__name__}"

    def into_indent(self, qualified: bool, annotated: bool):
        spec = ""

        if self.is_optional():
            spec = "?"

        if self.is_multiple():
            spec = "*" if spec == "?" else "+"

        name = self.name(qualified)
        if name and self.is_abstract():
            name = name.join("<>")

        indent = depth.get() * "    "

        prefix = "|" if inside_union.get() else " "

        attributes = []
        if isinstance(self.node, XsdElement):
            attributes = [
                a.prefixed_name
                for a in self.node.attributes.values()
                if a.prefixed_name and not a.prefixed_name.startswith("xlink:")
            ]
        attr_text = ", ".join(attributes)
        if attr_text:
            attr_text = f" [{attr_text}]"

        details = f"{indent}{prefix}{spec}{name or '...'}{attr_text}"
        if annotated:
            details += " " + self.annotation()

        return details

    def annotation(self):
        if self.node.annotation:
            return str(self.node.annotation).strip()

        return ""

    def _resolve_substitutions(self, node):
        options = set()
        subst = node.maps.substitution_groups.get(node.name, [])
        for s in subst:
            if s.abstract:
                options.update(self._resolve_substitutions(s))
            else:
                options.add(s)
        return options


class ChoiceNode(BaseNode):
    def __init__(self, node, children):
        return super().__init__(node, children)

    def is_abstract(self):
        return True

    def name(self, *args):
        return "<Choice>"

    def is_composed(self):
        return False

    def example(self, format):
        with self.visit() as options:
            children = self._unwrap_children(options)
            choice = faker.random_element(children)
            value = choice.value(format)
            if format == "bf":
                return value if choice.is_composed() else {"$": value}
            if format == "jml":
                return value
            assert "Cannot choose {format} format"


class GroupNode(BaseNode):
    def __iter__(self):
        if self.is_choice():
            yield from ChoiceNode(self.node, list(self.node))
            return
        for item in map(make_node, self.node):
            yield from item

    def is_choice(self):
        return self.node.model == "choice"

    def is_abstract(self):
        return True

    def is_composed(self):
        return False

    @contextlib.contextmanager
    def visit(self):
        yield []


class SkipNode(BaseNode):
    def is_abstract(self):
        return False

    def example(self, format):
        if format == "bf":
            return {}
        if format == "jml":
            return None
        assert f"Format {format} is not skippable"

    def annotation(self):
        return ""

    def into_indent(self, *args, **kwargs):
        value = super().into_indent(*args, **kwargs)

        return f"{value} (skip...)"


class TooDeepNode(BaseNode):
    def example(self, format):
        if format == "bf":
            return {}
        if format == "jml":
            return None
        assert f"Format {format} is too deep"

    def annotation(self):
        return ""

    def into_indent(self, *args, **kwargs):
        value = super().into_indent(*args, **kwargs)
        return f"{value} (too deep...)"


class NotImplementedNode(BaseNode):
    def example(self, format):
        if format == "bf":
            return {}
        if format == "jml":
            return None
        assert f"Format {format} is not implemented"


class RecursionNode(BaseNode):
    def is_abstract(self):
        return False

    def example(self, format):
        if format == "bf":
            return {}
        if format == "jml":
            return None
        assert f"Format {format} is not recursive"

    def annotation(self):
        return ""

    def into_indent(self, *args, **kwargs):
        value = super().into_indent(*args, **kwargs)
        indent = (depth.get() + 1) * "    "

        return f"{value} (seen before)\n{indent}..."


class AtomicNode(BaseNode):
    def example(self, format):
        validators = self.node.validators
        for validator in validators:
            if isinstance(validator, XsdEnumerationFacets):
                return faker.random_element(validator.enumeration)

        node = self.node.primitive_type
        ln = node.local_name

        if node.is_datetime():
            if ln == "duration":
                return faker.pystr_format("P#YT#H")

            dt = faker.date_time()
            fmt = {
                "date": "%Y-%m-%d",
                "dateTime": "%Y-%m-%dT%H:%M:%S",
                "time": "%H:%M:%S",
                "gYearMonth": "%Y-%m",
                "gYear": "%Y",
            }
            assert ln in fmt, f"Unsupported date type {ln}"

            return dt.strftime(fmt[ln])

        if node.local_name == "string":
            if self.node.patterns:
                pat = self.node.patterns.regexps[0]
                try:
                    return exrex.getone(pat)
                except re.error as e:
                    log.error(e)
                    return faker.pystr()

            return faker.sentence()
        if node.local_name == "boolean":
            return faker.pybool()
        if node.local_name in ("decimal", "double"):
            if issubclass(self.node.python_type, int):
                return faker.pyint()

            return faker.pyfloat()

        if node.local_name == "anyURI":
            return faker.uri()

        raise TypeError(f"Unsupported atomic example {node}")

    def is_composed(self):
        return False


class ElementNode(BaseNode):
    def __init__(self, node: XsdElement):

        if node.abstract:
            children = self._resolve_substitutions(node)
        else:
            type_ = node.type
            if isinstance(type_, XsdComplexType):
                type_ = type_.content
            if isinstance(type_, (XsdGroup, XsdList, XsdAtomic, XsdUnion)):
                children = [type_]

            else:
                raise TypeError(f"Node type {node} is not supported")

        super().__init__(node, children)

    def is_multiple(self):
        return not self.node.is_single()

    def is_composed(self):
        return self.node.type.is_complex()

    def example(self, format):
        root = self._unwrap()
        if self is not root:
            return root.example(format)

        bound = check_bounds(root)
        if bound:
            if isinstance(bound, RecursionNode) and not skip_optional.get():
                with set_context(
                    {
                        skip_optional: True,
                        visited: set(),
                    }
                ):
                    return root.example(format)
            return bound.example(format)

        attrs = {}
        data: JsonMLData = [self.name(False)]

        for attr in root.node.attributes.values():
            if attr.use == "required":  # or attr.type:
                value = make_node(attr.type).example(format)
                if isinstance(value, dict):
                    value = value["$"]

                attrs[attr.name] = value

            # if attr.local_name == "nilReason":
            #     attrs[attr.name] = "missing"

        local_name = root.node.local_name
        if local_name in utils.codelist_names():
            options = utils.codelist_options(local_name)
            valid_code = faker.random_element(options)
            attrs["codeListValue"] = valid_code.name
            # XXX: debug
            if local_name == "CI_DateTypeCode":
                attrs["codeListValue"] = "creation"
            attrs["codeList"] = valid_code.location
        # if attrs:
        data.append(attrs)

        with root.visit() as children:
            for child in self._unwrap_children(children):
                child = child._unwrap()

                value = child.example(format)
                if value is None:
                    continue

                data.append(value)

        return data


class UnionNode(BaseNode):
    def __init__(self, node: XsdUnion, children=None):
        if not children:
            children = node.member_types
        super().__init__(node, children)

    def is_union(self):
        return True

    def example(self, cormat):
        with self.visit() as options:
            choice = faker.random_element(options)
            value = choice.example(format)
            if format == "bf":
                return value if choice.is_composed() else {"$": value}
            if format == "jml":
                return value
            assert f"Cannot build union for format {format}"


class ListNode(BaseNode):
    def __init__(self, node: XsdList):
        children = [node.base_type]
        super().__init__(node, children)

    def is_multiple(self):
        return True

    def example(self, format):
        component = AtomicNode(self.node.base_type)
        return [component.example(format) for _ in range(faker.random_digit())]
