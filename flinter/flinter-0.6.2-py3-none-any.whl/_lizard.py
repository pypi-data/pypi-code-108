
import re

from lizard import BARE_NESTING
from lizard import Namespace
from lizard import FunctionInfo

from flinter.error_processing import fmt_analysis
from flinter.error_processing import get_statements_errors
from flinter.error_processing import get_vars_errors
from flinter.error_processing import get_nesting_errors
from flinter.error_processing import get_args_errors


DEFAULT_SYNTAX = {
    "namespace_blocks": ["program", "module"],
    "context_blocks": ["function", "subroutine"]
}

DEFAULT_STRUCT_RULES = {
    "var-declaration": r"\w+\s*(?:\(.*\))?\s*(?:::| )\s*(\w+(?:\s*,\s*\w+)*)",
    "max-statements-in-context": 50,
    "max-declared-locals": 12,
    "min-varlen": 3,
    "max-varlen": 20,
    "max-arguments": 4,
    "min-arglen": 3,
    "max-arglen": 20,
    "max-nesting-levels": 3
}

DEFAULT_REGEXP_RULES = {
}


class NodePrinter:
    def __init__(self, title_getter, children_getter, arg_getter):
        self.title_getter = title_getter
        self.arg_getter = arg_getter
        self.children_getter = children_getter

    def _format(self, node, tab=''):
        dec = ' '
        result = ''
        args = list(self.arg_getter(node))
        children = [(self.title_getter(child), child) for child in self.children_getter(node)]
        lines = args + children
        for i, (title, arg) in enumerate(lines):
            result += '\n' + tab
            if i == len(lines) - 1:
                result += '└'
                pad = ' '
            else:
                result += '├'
                pad = '│'
            result += dec + title
            if i >= len(args):
                result += self._format(arg, tab + pad + dec)
            else:
                result += ': ' + str(arg)
        return result

    def __call__(self, node):
        print(self.title_getter(node) + self._format(node))


class StackListener(list):

    def __init__(self, context):
        super().__init__()
        self.context = context

    def append(self, nest):
        self.context.add_nesting(nest)
        return super().append(nest)

    def pop(self, *args):
        nest = super().pop(*args)
        self.context.pop_nesting(nest)
        return nest


class FlintExtension:
    ordering_index = 0

    def __init__(self,
                 path="",
                 syntax=DEFAULT_SYNTAX,
                 struct_rules=DEFAULT_STRUCT_RULES,
                 regexp_rules=DEFAULT_REGEXP_RULES):
        self.syntax = syntax
        self.struct_rules = struct_rules
        self.regexp_rules = regexp_rules
        self.last_key_word = None
        self.current_position = None
        self.context = None
        self.current_token = ""
        self.was_comment = False
        self.struct = []
        self.ns = StackListener(self)
        self.add_nesting(path)
        self.struct[0]["type"] = "file"

    def down_stream(self, tokens, reader):
        for token in tokens:
            self.was_comment = reader.get_comment_from_token(token) is not None
            yield token
    down_stream.ordering_index = 2

    def __call__(self, tokens, reader):
        self.context = reader.context
        self.ns = StackListener(self)
        self.context._nesting_stack.nesting_stack = self.ns
        for token in tokens:
            if self.current_token == "\n":
                self.struct[-1]["clean_content"].append("")
                self.struct[-1]["content"].append("")
            else:
                self.struct[-1]["content"][-1] += self.current_token
                if self.was_comment:
                    self.struct[-1]["clean_content"][-1] = self.struct[-1]["clean_content"][-1].rstrip()
                else:
                    self.struct[-1]["clean_content"][-1] += self.current_token

            self.current_position = token
            lower_token = self.current_token.lower()
            if lower_token in self.syntax["namespace_blocks"] or lower_token in self.syntax["context_blocks"]:
                self.last_key_word = lower_token
            self.current_token = token.group(0)
            yield self.current_token

        while len(self.struct) > 1:
            self.pop_nesting()

        self.evaluate(self.struct[0])

    def add_nesting(self, nest):
        start = 0
        start_line = 0
        if self.struct:
            md = self.struct[-1]["max_depth"]
            self.struct[-1]["max_depth"] = max(len(self.ns), md)
            start = self.current_position.start()
            start_line = self.context.current_line

        if nest != BARE_NESTING:
            bpath = ""
            bname = nest
            btype = self.last_key_word
            first_line = ""
            first_clean_line = ""
            if self.struct:
                first_clean_line = self.struct[-1]["clean_content"][-1]
                first_line = self.struct[-1]["content"][-1]
                self.struct[-1]["clean_content"][-1] = ""
                self.struct[-1]["content"][-1] = ""
                bpath = self.struct[-1]["path"] + "/"
            if isinstance(nest, Namespace):
                bname = nest.name
                if btype not in self.syntax["namespace_blocks"]:
                    btype = self.syntax["namespace_blocks"][0]
            elif isinstance(nest, FunctionInfo):
                bname = nest.unqualified_name
                if btype not in self.syntax["context_blocks"]:
                    btype = self.syntax["context_blocks"][0]
            self.struct.append({
                "handle": nest,
                "type": btype,
                "name": bname,
                "path": bpath + bname,
                "size": 0,
                "children": [],
                "struct_rules": {},
                "regexp_rules": {},
                "clean_content": [first_clean_line],  # lines without comments
                "content": [first_line],
                "top_depth": len(self.ns),
                "max_depth": len(self.ns),
                "start": start,
                "end": start,
                "start_line": start_line,
                "end_line": start_line,
            })

    def pop_nesting(self, nest=None):
        if len(self.struct) > 1 and nest != BARE_NESTING:
            child = self.struct.pop()
            if self.evaluate(child):
                self.struct[-1]["children"].append(child)

    def evaluate(self, block):
        block["end"] = 0 if self.current_position is None else self.current_position.end()
        block["end_line"] = self.context.current_line
        block["size"] = block["end_line"] - block["start_line"]

        if block["type"] in self.syntax["ignore_blocks"]:
            return False
        elif block["type"] in self.syntax["context_blocks"]:
            out = evaluate_func(block, self.syntax, self.struct_rules)
        elif block["type"] in self.syntax["namespace_blocks"]:
            out = evaluate_mod(block, self.syntax, self.struct_rules)
        else:
            out = {"errors": {}}
        block["struct_rules"] = out["errors"]

        block["regexp_rules"] = fmt_analysis(block["clean_content"], block["content"], block["start_line"], self.regexp_rules)

        return True


def evaluate_mod(block, syntax, struct_rules):
    return {"errors": {}}


def evaluate_func(block, syntax, struct_rules):
    """ analysis of a block """
    # TODO: allow struct rules to be optional?

    statements = block["clean_content"]
    out = {
        "args": block["handle"].parameters,
        "locals": list(),
        "errors": dict(),
    }

    for name in get_variables(statements, struct_rules["var-declaration"]):
        if name not in out["args"]:
            out["locals"].append(name)

    errors = out['errors']

    get_statements_errors(
        block['size'],
        max_lines=struct_rules["max-statements-in-context"],
        errors=errors)

    get_vars_errors(
        out["locals"],
        max_declared_locals=struct_rules["max-declared-locals"],
        min_var_len=struct_rules["min-varlen"],
        max_var_len=struct_rules["max-varlen"],
        errors=errors)

    get_args_errors(
        out["args"],
        max_arguments=struct_rules["max-arguments"],
        min_arg_len=struct_rules["min-arglen"],
        max_arg_len=struct_rules["max-arglen"],
        errors=errors)

    get_nesting_errors(
        block["max_depth"] - block["top_depth"],
        max_depth=struct_rules["max-nesting-levels"],
        errors=errors)

    return out


def get_variables(statements, var_decl_re):
    """ identifie a declaration line and give the list of varaibles"""
    var_groups = re.findall(var_decl_re, "\n".join(statements))
    return [var.strip() for var_group in var_groups for var in var_group.split(",")]
