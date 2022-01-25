import io
import json
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Dict, List


class Node:
    def __hash__(self):
        return id(self)


@dataclass
class ListNode(Node):
    children: List[Node]

    @property
    def section(self):
        return self.children and all(child.section for child in self.children)

    @cached_property
    def length(self):

        child_lengths = sum(child.length for child in self.children)
        if len(self.children) == 0:
            return 2
        else:
            return child_lengths + 2 * (len(self.children) - 1) + 4


@dataclass
class Pair:
    key: str
    value: Node

    @property
    def section(self):
        return self.value.section


@dataclass
class DictNode(Node):
    children: List[Pair]
    section: bool = True

    @cached_property
    def length(self):
        child_lengths = sum(
            len(pair.key) + 3 + pair.value.length for pair in self.children
        )
        if len(self.children) == 0:
            return 2
        else:
            return child_lengths + 2 * (len(self.children) - 1) + 4


@dataclass
class LeafNode(Node):
    value: Any
    section = False

    @cached_property
    def length(self):
        return len(json.dumps(self.value))


def parse_tree(data):
    if isinstance(data, dict):
        return DictNode([Pair(k, parse_tree(v)) for k, v in data.items()])
    elif isinstance(data, list):
        return ListNode([parse_tree(v) for v in data])
    else:
        return LeafNode(data)


def write_horizontal_list(obj, output, indent, max_width):
    output.write("[ ")
    for i, child in enumerate(obj.children):
        if i != 0:
            output.write(", ")
        write_compound(0, child, output, indent, max_width)
    output.write(" ]")


def write_horizontal_dict(obj, output, indent, max_width):
    output.write("{ ")
    for i, pair in enumerate(obj.children):
        key, child = pair.key, pair.value
        if child != LeafNode(None):
            if i != 0:
                output.write(", ")
            key_str = f"{key} = "
            output.write(key_str)
            write_compound(0, child, output, indent, max_width)
    output.write(" }")


def write_vertical_list(current_indent, obj, output, indent, max_width):
    output.write("[\n")
    for i, child in enumerate(obj.children):
        child_indent = current_indent + indent
        output.write(" " * child_indent)
        write_compound(child_indent, child, output, indent, max_width)
        if i != len(obj.children):
            output.write(", ")

        output.write("\n")

    output.write(" " * current_indent)
    output.write("]")


def write_vertical_dict(current_indent, obj, output, indent, max_width):
    output.write("{\n")
    for i, pair in enumerate(obj.children):
        key, child = pair.key, pair.value
        if child != LeafNode(None):
            if i != 0:
                output.write(",\n")
            child_indent = current_indent + indent
            output.write(" " * child_indent)
            key_str = f"{key} = "
            output.write(key_str)
            write_compound(child_indent, child, output, indent, max_width)
    output.write("\n")
    output.write(" " * current_indent)
    output.write("}")


def write_compound(current_indent, obj, output, indent, max_width):

    vertical = current_indent + obj.length > max_width

    if isinstance(obj, ListNode) and vertical:
        write_vertical_list(current_indent, obj, output, indent, max_width)
    elif isinstance(obj, ListNode) and not vertical:
        write_horizontal_list(obj, output, indent, max_width)
    elif isinstance(obj, DictNode) and vertical:
        write_vertical_dict(current_indent, obj, output, indent, max_width)
    elif isinstance(obj, DictNode) and not vertical:
        write_horizontal_dict(obj, output, indent, max_width)
    else:
        write_leaf(obj, output)


def write_child(current_indent, child, output, indent, max_width):
    if isinstance(child, LeafNode):
        write_leaf(child, output)
        output.write("\n")
    else:
        write_compound(current_indent, child, output, indent, max_width)
        output.write("\n")


def write_leaf(leaf, output):
    if isinstance(leaf.value, str) and len(leaf.value) > 255:
        output.write('"""')
        output.write(leaf.value)
        output.write('"""')
    else:
        output.write(json.dumps(leaf.value))


def write_section(section, output, indent, max_width):

    for pair in section.children:
        key, child = pair.key, pair.value
        if child != LeafNode(None):
            output.write(f"{key} = ")
            write_child(0, child, output, indent, max_width)
    output.write("\n")


def dump(data, f, indent=4, max_width=100):
    output = f
    tree = parse_tree(data)

    blank_section = DictNode([])
    sections = [("", blank_section)]
    for pair in tree.children:
        key, value = pair.key, pair.value
        if value.section:
            if isinstance(value, DictNode):
                sections.append((f"[{key}]", value))
            elif isinstance(value, ListNode):
                for child in value.children:
                    sections.append((f"[[{key}]]", child))
        else:
            blank_section.children.append(Pair(key, value))

    for key, section in sections:
        if key:
            output.write(key)
            output.write("\n")
        write_section(section, output, indent, max_width)


def dumps(data, indent=4, max_width=100):
    f = io.StringIO()
    dump(data, f, indent, max_width)
    return f.getvalue()
