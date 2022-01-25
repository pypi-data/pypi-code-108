"""
Mast: Matcher of ASTs for Python
Copyright (c) 2017-2018, Benjamin P. Wood, Wellesley College

mast.py

This version is included in potluck instead of codder.

See NOTE below for how to run this file as a script.

Uses the builtin ast package for parsing of concrete syntax and
representation of abstract syntax for both source code and patterns.

The main API for pattern matching with mast:

- `parse`: parse an AST from a python source string
- `parse_file`: parse an AST from a python source file
- `parse_pattern`: parse a pattern from a pattern source string
- `match`: check if an AST matches a pattern
- `find`: search for the first (improper) sub-AST matching a pattern
- `findall`: search for all (improper) sub-ASTs matching a pattern
- `count`: count all (improper) sub-ASTs matching a pattern

API utility functions applicable to all ASTs in ast:

- `dump`: a nicer version of ast.dump AST structure pretty-printing
- `ast2source`: source: pretty-print an AST to python source

NOTE: To run this file as a script, go up one directory and execute

```sh
python -m potluck.mast
```

For example, if this file is ~/Sites/potluck/potluck/mast.py, then

```sh
cd ~/Sites/potluck
python -m potluck.mast
```

Because of relative imports, you *cannot* attempt to run this file
as a script in ~/Sites/potluck/potluck. Here's what will happen:

```sh
$ cd ~/Sites/potluck/potluck
$ python mast.py
Traceback (most recent call last):
File "mast.py", line 40, in <module>
  from .util import (...
SystemError: Parent module '' not loaded, cannot perform relative import
```

This StackOverflow post is helpful for understanding this issue:
https://stackoverflow.com/questions/14132789/relative-imports-for-the-billionth-time

SOME HISTORY
[2019/01/19-23, lyn] Python 2 to 3 conversion plus debugging aids
[2021/06/22ish, Peter Mawhorter] Linting pass; import into potluck

TODO:

* have flag to control debugging prints (look for $)

Documentation of the Python ast package:

- Python 2: https://docs.python.org/2/library/ast.html
- Python 3:
    - https://docs.python.org/3/library/ast.html
    - https://greentreesnakes.readthedocs.io/en/latest/
"""

import ast
import os
import re
import sys

from collections import OrderedDict as odict

from .mast_utils import (
    Some,
    takeone,
    FiniteIterator,
    iterone,
    iterempty,
    dict_unbind
)

import itertools
ichain = itertools.chain.from_iterable


#------------------------------------#
# AST data structure pretty printing #
#------------------------------------#

def dump(node):
    """Nicer display of ASTs."""
    return (
        ast.dump(node) if isinstance(node, ast.AST)
        else '[' + ', '.join(map(dump, node)) + ']' if type(node) == list
        else '(' + ', '.join(map(dump, node)) + ')' if type(node) == tuple
        else '{' + ', '.join(dump(key) + ': ' + dump(value)
                             for key, value in node.items()) + '}'
            if type(node) == dict
        # Sneaky way to have dump descend into Some and FiniteIterator objects
        # for debugging
        else node.dump(dump)
          if (type(node) == Some or type(node) == FiniteIterator)
          else repr(node)
    )


def showret(x, prefix=''):
    """Shim for use debugging AST return values."""
    print(prefix, dump(x))
    return x


#-------------------#
# Pattern Variables #
#-------------------#

NODE_VAR_SPEC = (1, re.compile(r'\A_(?:([a-zA-Z0-9]+)_)?\Z'))
"""Spec for names of scalar pattern variables."""

SEQ_TYPES = set([
    ast.arguments,
    ast.Assign,
    ast.Call,
    ast.Expr,
    # ast.For,
    # ast.Print, # removed from ast module in Python 3
    ast.Tuple,
    ast.List,
    list,
    type(None),
    ast.BoolOp,
])
"""Types against which sequence patterns match."""

SET_VAR_SPEC = (1, re.compile(r'\A___(?:([a-zA-Z0-9]+)___)?\Z'))
"""Spec for names of sequence pattern variables."""

if sys.version_info[0] < 3 or sys.version_info[1] < 8:
    # This was the setup before 3.8
    LIT_TYPES = {
        'int': lambda x: (Some(x.n)
                          if type(x) == ast.Num and type(x.n) == int
                          else None),
        'float': lambda x: (Some(x.n)
                            if type(x) == ast.Num and type(x.n) == float
                            else None),
        'str': lambda x: (Some(x.s)
                          if type(x) == ast.Str
                          else None),
        # 'bool': lambda x: (Some(bool(x.id))
        # Lyn notes this was a bug! Should have been Some(bool(x.id == 'True'))!
        #                    if type(x) == ast.Name and (x.id == 'True'
        #                                                or x.id == 'False')
        #                    else None),
        # -----
        # Above is Python 2 code for bools; below is Python 3 (where bools
        # are named constants)
        'bool': lambda x: (
            Some(x.value)
            if (
                type(x) == ast.NameConstant
            and (x.value is True or x.value is False)
            ) else None
        ),
    }
    """Types against which typed literal pattern variables match."""
else:
    # From 3.8, Constant is used in place of lots of previous stuff
    LIT_TYPES = {
        'int': lambda x: (Some(x.value)
                          if type(x) == ast.Constant and type(x.value) == int
                          else None),
        'float': lambda x: (Some(x.value)
                            if type(x) == ast.Constant
                                and type(x.value) == float
                            else None),
        'str': lambda x: (Some(x.value)
                          if type(x) == ast.Constant and type(x.value) == str
                          else None),
        'bool': lambda x: (
            Some(x.value)
            if (
                type(x) == ast.Constant
            and (x.value is True or x.value is False)
            ) else None
        ),
    }
    """Types against which typed literal pattern variables match."""

TYPED_LIT_VAR_SPEC = (
    (1, 2),
    re.compile(r'\A_([a-zA-Z0-9]+)_(' + '|'.join(LIT_TYPES.keys()) + r')_\Z')
)
"""Spec for names/types of typed literal pattern variables."""


def var_is_anonymous(identifier):
    """Determine whether a pattern variable name (string) is anonymous."""
    assert type(identifier) == str # All Python 3 strings are unicode
    return not re.search(r'[a-zA-Z0-9]', identifier)


def node_is_name(node):
    """Determine if a node is an AST Name node."""
    return isinstance(node, ast.Name)


def identifier_key(identifier, spec):
    """Extract the name of a pattern variable from its identifier string,
    returning an option: Some(key) if identifier is valid variable
    name according to spec, otherwise None.

    Examples for NODE_VAR_SPEC:
    identifier_key('_a_') => Some('a')
    identifier_key('_') => Some('_')
    identifier_key('_a') => None

    """
    assert type(identifier) == str # All Python 3 strings are unicode
    groups, regex = spec
    match = regex.match(identifier)
    if match:
        if var_is_anonymous(identifier):
            return identifier
        elif type(groups) == tuple:
            return tuple(match.group(i) for i in groups)
        else:
            return match.group(groups)
    else:
        return None


def node_var(pat, spec=NODE_VAR_SPEC, wrap=False):
    """Extract the key name of a scalar pattern variable,
    returning Some(key) if pat is a scalar pattern variable,
    otherwise None.

    A named or anonymous node variable pattern, written `_a_` or `_`,
    respectively, may appear in any expression or identifier context
    in a pattern.  It matches any single AST in the corresponding
    position in the target program.

    """
    if wrap:
        pat = ast.Name(id=pat, ctx=None)
    elif isinstance(pat, ast.Expr):
        pat = pat.value
    elif isinstance(pat, ast.alias) and pat.asname is None:
        # [Peter Mawhorter 2021-8-29] Want to treat aliases without an
        # 'as' part kind of like normal Name nodes.
        pat = ast.Name(id=pat.name, ctx=None)
    return (
        identifier_key(pat.id, spec)
        if node_is_name(pat)
        else None
    )


def node_var_str(pat, spec=NODE_VAR_SPEC):

    return node_var(pat, spec=spec, wrap=True)


def set_var(pat, wrap=False):
    """Extract the key name of a set or sequence pattern variable,
    returning Some(key) if pat is a set or sequence pattern variable,
    otherwise None.

    A named or anonymous set or sequence pattern variable, written
    `___a___` or `___`, respectively, may appear as an element of a
    set or sequence context in a pattern.  It matches 0 or more nodes
    in the corresponding context in the target program.

    """
    return node_var(pat,
                    spec=SET_VAR_SPEC,
                    wrap=wrap)


def set_var_str(pat):
    return set_var(pat, wrap=True)


def typed_lit_var(pat):
    """Extract the key name of a typed literal pattern variable,
    returning Some(key) if pat is a typed literal pattern variable,
    otherwise None.

    A typed literal variable pattern, written `_a_type_`, may appear
    in any expression context in a pattern.  It matches any single AST
    node for a literal of the given primitive type in the
    corresponding position in the target program.

    """
    return node_var(pat, spec=TYPED_LIT_VAR_SPEC)

# def stmt_var(pat):
#     """Extract the key name of a sequence pattern variable, returning
#     Some(key) if pat is a sequence pattern variable appearing in a
#     statement context, otherwise None.
#     """
#     return seq_var(pat.value) if isinstance(pat, ast.Expr) else None


#---------------------#
# AST Node Properties #
#---------------------#

def is_pat(p):
    """Determine if p could be a pattern (by type)."""
    # All Python 3 strings are unicode
    return isinstance(p, ast.AST) or type(p) == str


def node_is_docstring(node):
    """Is this node a docstring node?"""
    return isinstance(node, ast.Expr) and isinstance(node.value, ast.Str)


def node_is_bindable(node):
    """Can a node pattern variable bind to this node?"""
    # return isinstance(node, ast.expr) or isinstance(node, ast.stmt)
    # Modified to allow debugging prints
    result = (
        isinstance(node, ast.expr)
     or isinstance(node, ast.stmt)
     or (isinstance(node, ast.alias) and node.asname is None)
    )
    # print('\n$ node_is_bindable({}) => {}'.format(dump(node),result))
    return result


def node_is_lit(node, ty):
    """Is this node a literal primitive node?"""
    return (
        (isinstance(node, ast.Num) and ty == type(node.n)) # noqa E721
        # All Python 3 strings are unicode
     or (isinstance(node, ast.Str) and ty == str)
     or (
            isinstance(node, ast.Name)
        and ty == bool
        and (node.id == 'True' or node.id == 'False')
        )
    )


def expr_has_type(node, ty):
    """Is this expr statically guaranteed to be of this type?

    Literals and conversions have definite types.  All other types are
    conservatively statically unknown.

    """
    return node_is_lit(node, ty) or match(node, '{}(_)'.format(ty.__name__))


def node_line(node):
    """Bet the line number of the source line on which this node starts.
    (best effort)"""
    try:
        return node.lineno if type(node) != list else node[0].lineno
    except Exception:
        return None


#---------------------------#
# Checkers and Transformers #
#---------------------------#

class PatternSyntaxError(BaseException):
    """Exception for errors in pattern syntax."""
    def __init__(self, node, message):
        BaseException.__init__(
            self,
            "At pattern line {}: {}".format(node_line(node), message)
        )


class PatternValidator(ast.NodeVisitor):
    """AST visitor: check pattern structure."""
    def __init__(self):
        self.parent = None
        pass

    def generic_visit(self, pat):
        oldparent = self.parent
        self.parent = pat
        try:
            return ast.NodeVisitor.generic_visit(self, pat)
        finally:
            self.parent = oldparent
            pass
        pass

    def visit_Name(self, pat):
        sn = set_var(pat)
        if sn:
            if type(self.parent) not in SEQ_TYPES:
                raise PatternSyntaxError(
                    pat,
                    "Set/sequence variable ({}) not allowed in {} node".format(
                        sn, type(self.parent)
                    )
                )
            pass
        pass

    def visit_arg(self, pat):
        '''[2019/01/22, lyn] Python 3 now has arg object for param (not Name object).
           So copied visit_Name here.'''
        sn = set_var(pat)
        if sn:
            if type(self.parent) not in SEQ_TYPES:
                raise PatternSyntaxError(
                    pat,
                    "Set/sequence variable ({}) not allowed in {} node".format(
                        sn.value, type(self.parent)
                    )
                )
            pass
        pass

    def visit_Call(self, c):
        if 1 < sum(1 for kw in c.keywords if set_var_str(kw.arg)):
            raise PatternSyntaxError(
                c.keywords,
                "Calls may use at most one keyword argument set variable."
            )
        return self.generic_visit(c)

    def visit_keyword(self, k):
        if (identifier_key(k.arg, SET_VAR_SPEC)
            and not (node_is_name(k.value)
                     and var_is_anonymous(k.value.id))):
            raise PatternSyntaxError(
                k.value,
                "Value patterns for keyword argument set variables must be _."
            )
        return self.generic_visit(k)
    pass


# TODO [Peter 2021-6-24]: This pass breaks things subtly by removing
# e.g., decorators lists, resulting in an AST tree that cannot be
# compiled and run as code! In the past there was mention that without
# this pass things would break... but for now it's disabled by default.
class RemoveDocstrings(ast.NodeTransformer):
    """AST Transformer: remove all docstring nodes."""
    def filterDocstrings(self, seq):
        # print('PREFILTERED', seq)
        filt = [self.visit(n) for n in seq
                if not node_is_docstring(n)]
        # print('FILTERED', dump(filt))
        return filt

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Str):
            assert False
            # return ast.copy_location(ast.Expr(value=None), node)
        else:
            return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # print('Removing docstring: %s' % dump(node.body[0].value))
        return ast.copy_location(ast.FunctionDef(
            name=node.name,
            args=self.generic_visit(node.args),
            body=self.filterDocstrings(node.body),
        ), node)

    def visit_Module(self, node):
        return ast.copy_location(ast.Module(
            body=self.filterDocstrings(node.body)
        ), node)

    def visit_For(self, node):
        return ast.copy_location(ast.For(
            body=self.filterDocstrings(node.body),
            target=node.target,
            iter=node.iter,
           orelse=self.filterDocstrings(node.orelse)
        ), node)

    def visit_While(self, node):
        return ast.copy_location(ast.While(
            body=self.filterDocstrings(node.body),
            test=node.test,
            orelse=self.filterDocstrings(node.orelse)
        ), node)

    def visit_If(self, node):
        return ast.copy_location(ast.If(
            body=self.filterDocstrings(node.body),
            test=node.test,
            orelse=self.filterDocstrings(node.orelse)
        ), node)

    def visit_With(self, node):
        return ast.copy_location(ast.With(
            body=self.filterDocstrings(node.body),
            # Python 3 just has withitems:
            items=node.items
            # Old Python 2 stuff:
            #context_expr=node.context_expr,
            #optional_vars=node.optional_vars
        ), node)

#     def visit_TryExcept(self, node):
#         return ast.copy_location(ast.TryExcept(
#             body=self.filterDocstrings(node.body),
#             handlers=self.filterDocstrings(node.handlers),
#             orelse=self.filterDocstrings(node.orelse)
#         ), node)

#     def visit_TryFinally(self, node):
#         return ast.copy_location(ast.TryFinally(
#             body=self.filterDocstrings(node.body),
#             finalbody=self.filterDocstrings(node.finalbody)
#         ), node)
#

# In Python 3, a single Try node covers both TryExcept and TryFinally
    def visit_Try(self, node):
        return ast.copy_location(ast.Try(
            body=self.filterDocstrings(node.body),
            handlers=self.filterDocstrings(node.handlers),
            orelse=self.filterDocstrings(node.orelse),
            finalbody=self.filterDocstrings(node.finalbody)
         ), node)

    def visit_ClassDef(self, node):
        return ast.copy_location(ast.ClassDef(
            body=self.filterDocstrings(node.body),
            name=node.name,
            bases=node.bases,
            decorator_list=node.decorator_list
        ), node)


class FlattenBoolOps(ast.NodeTransformer):
    """AST transformer: flatten nested boolean expressions."""
    def visit_BoolOp(self, node):
        values = []
        for v in node.values:
            if isinstance(v, ast.BoolOp) and v.op == node.op:
                values += v.values
            else:
                values.append(v)
                pass
            pass
        return ast.copy_location(ast.BoolOp(op=node.op, values=values), node)
    pass


class ContainsCall(Exception):
    """Exception raised when prohibiting call expressions."""
    pass


class ProhibitCall(ast.NodeVisitor):
    """AST visitor: check call-freedom."""
    def visit_Call(self, c):
        raise ContainsCall
    pass


class SetLoadContexts(ast.NodeTransformer):
    """
    Transforms any AugStore contexts into Load contexts, for use with
    DesugarAugAssign.
    """
    def visit_AugStore(self, ctx):
        return ast.copy_location(ast.Load(), ctx)


class DesugarAugAssign(ast.NodeTransformer):
    """AST transformer: desugar augmented assignments (e.g., `+=`)
    when simple desugaring does not duplicate effectful expressions.

    FIXME: this desugaring and others cause surprising match
    counts. See: https://github.com/wellesleycs111/codder/issues/31

    FIXME: This desugaring should probably not happen in cases where
    .__iadd__ and .__add__ yield different results, for example with
    lists where .__iadd__ is really extend while .__add__ creates a new
    list, such that

        [1, 2] + "34"

    is an error, but

        x = [1, 2]
        x += "34"

    is not!

    A better approach might be to avoid desugaring entirely and instead
    provide common collections of match rules for common patterns.

    """
    def visit_AugAssign(self, assign):
        try:
            # Desugaring *all* AugAssigns is not sound.
            # Example: xs[f()] += 1  -->  xs[f()] = xs[f()] + 1
            # Check for presence of call in target.
            ProhibitCall().visit(assign.target)
            return ast.copy_location(
                ast.Assign(
                    targets=[self.visit(assign.target)],
                    value=ast.copy_location(
                        ast.BinOp(
                            left=SetLoadContexts().visit(assign.target),
                            op=self.visit(assign.op),
                            right=self.visit(assign.value)
                        ),
                        assign
                    )
                ),
                assign
            )
        except ContainsCall:
            return self.generic_visit(assign)

    def visit_AugStore(self, ctx):
        return ast.copy_location(ast.Store(), ctx)

    def visit_AugLoad(self, ctx):
        return ast.copy_location(ast.Load(), ctx)


class ExpandExplicitElsePattern(ast.NodeTransformer):
    """AST transformer: transform patterns that in include `else: ___`
    to use `else: _; ___` instead, forcing the else to have at least
    one statement."""
    def visit_If(self, ifelse):
        if 1 == len(ifelse.orelse) and set_var(ifelse.orelse[0]):
            return ast.copy_location(
                ast.If(
                    test=ifelse.test,
                    body=ifelse.body,
                    orelse=[
                        ast.copy_location(
                            ast.Expr(value=ast.Name(id='_', ctx=None)),
                            ifelse.orelse[0]
                        ),
                        ifelse.orelse[0]
                    ]
                ),
                ifelse
            )
        else:
            return self.generic_visit(ifelse)


def pipe_visit(node, visitors):
    """Send an AST through a pipeline of AST visitors/transformers."""
    if 0 == len(visitors):
        return node
    else:
        v = visitors[0]
        if isinstance(v, ast.NodeTransformer):
            # visit for the transformed result
            return pipe_visit(v.visit(node), visitors[1:])
        else:
            # visit for the effect
            v.visit(node)
            return pipe_visit(node, visitors[1:])


#---------#
# Parsing #
#---------#

def parse_file(path, docstrings=True):
    """Load and parse a program AST from the given path."""
    with open(path) as f:
        return parse(f.read(), filename=path, docstrings=docstrings)
    pass


# Note: 2021-7-29 Peter Mawhorter: A bug in DesugarAugAssign was found
# and fixed (incorrectly left Store context on RHS, which was apparently
# ignored in many Python versions...). However, upon consideration I've
# decided to remove it from standard + docstring passes, since the
# problem with += and lists is pretty relevant (I've seen students
# accidentally do list += string several times in office hours)!
STANDARD_PASSES = [
    RemoveDocstrings,
    #DesugarAugAssign,
    FlattenBoolOps
]
"""Thunks for AST visitors/transformers that are applied during parsing."""


DOCSTRING_PASSES = [
    #DesugarAugAssign,
    FlattenBoolOps
]
"""Extra thunks for docstring mode?"""


class MastParseError(Exception):
    def __init__(self, pattern, error):
        super(MastParseError, self).__init__(
            'Error parsing pattern source string <<<\n{}\n>>>\n{}'.format(
                pattern, str(error)
            )
        )
        self.trigger = error # hang on to the original error
        pass
    pass


def parse(
    string,
    docstrings=True,
    filename='<unknown>',
    passes=STANDARD_PASSES
):
    """Parse an AST from a string."""
    if type(string) == str: # All Python 3 strings are unicode
        string = str(string)
    assert type(string) == str # All Python 3 strings are unicode
    if docstrings and RemoveDocstrings in passes:
        passes.remove(RemoveDocstrings)
    pipe = [thunk() for thunk in passes]

    try:
        parsed_ast = ast.parse(string, filename=filename)
    except Exception as error:
        raise MastParseError(string, error)
    return pipe_visit(parsed_ast, pipe)


PATTERN_PARSE_CACHE = {}
"""a pattern parsing cache"""


PATTERN_PASSES = STANDARD_PASSES + [
    # ExpandExplicitElsePattern,
    # Not currently used because a number of existing rules and specs
    # actually use the ability of `if _: ___; else: ___` to match
    # either an if-else or an elseless if.
]


def parse_pattern(pat, toplevel=False, docstrings=True):
    """Parse and validate a pattern."""
    if isinstance(pat, ast.AST):
        PatternValidator().visit(pat)
        return pat
    elif type(pat) == list:
        iter(lambda x: PatternValidator().visit(x), pat)
        return pat
    elif type(pat) == str: # All Python 3 strings are unicode
        cache_key = (toplevel, docstrings, pat)
        pat_ast = PATTERN_PARSE_CACHE.get(cache_key)
        if not pat_ast:
            # 2021-6-16 Peter commented this out (should it be used
            # instead of passes on the line below?)
            # pipe = [thunk() for thunk in PATTERN_PASSES]
            pat_ast = parse(pat, filename='<pattern>', passes=PATTERN_PASSES)
            PatternValidator().visit(pat_ast)
            if not toplevel:
                # Unwrap as needed.
                if len(pat_ast.body) == 1:
                    # If the pattern is a single definition, statement, or
                    # expression, unwrap the Module node.
                    b = pat_ast.body[0]
                    pat_ast = b.value if isinstance(b, ast.Expr) else b
                    pass
                else:
                    # If the pattern is a sequence of definitions or
                    # statements, validate from the top, but return only
                    # the Module body.
                    pat_ast = pat_ast.body
                    pass
                pass
            PATTERN_PARSE_CACHE[cache_key] = pat_ast
            pass
        return pat_ast
    else:
        assert False, 'Cannot parse pattern of type {}: {}'.format(
            type(pat),
            dump(pat)
        )


def pat(pat, toplevel=False, docstrings=True):
    """Alias for parse_pattern."""
    return parse_pattern(pat, toplevel, docstrings)


#--------------#
# Permutations #
#--------------#

# [2019/02/09, lyn] Careful below! generally need list(map(...)) in Python 3
ASSOCIATIVE_OPS = list(map(type, [
    ast.Add(), ast.Mult(), ast.BitOr(), ast.BitXor(), ast.BitAnd(),
    ast.Eq(), ast.NotEq(), ast.Is(), ast.IsNot()
]))
"""Types of AST operation nodes that are associative."""


def op_is_assoc(op):
    """Determine if the given operation node is associative."""
    return type(op) in ASSOCIATIVE_OPS


MIRRORING = [
    (ast.Lt(), ast.Gt()),
    (ast.LtE(), ast.GtE()),
    (ast.Eq(), ast.Eq()),
    (ast.NotEq(), ast.NotEq()),
    (ast.Is(), ast.Is()),
    (ast.IsNot(), ast.IsNot()),
]
"""Pairs of operations that are mirrors of each other."""


def mirror(op):
    """Return the mirror operation of the given operation if any."""
    for (x, y) in MIRRORING:
        if type(x) == type(op):
            return y
        elif type(y) == type(op):
            return x
        pass
    return None


def op_has_mirror(op):
    """Determine if the given operation has a mirror."""
    return bool(mirror)


# MIRROR_OPS = set(reduce(lambda acc,(x,y): acc + [x,y], MIRRORING, []))
# ASSOCIATIVE_IF_PURE_OPS = set([
#     ast.And(), ast.Or()
# ])


# Patterns for potentially effectful operations
FUNCALL = parse_pattern('_(___)')
METHODCALL = parse_pattern('_._(___)')
ASSIGN = parse_pattern('_ = _')
DEL = parse_pattern('del _')
PRINT = parse_pattern('print(___)')
IMPURE2 = [METHODCALL, ASSIGN, DEL, PRINT]


# Patterns for definitely pure operations
PUREFUNS = set(['len', 'round', 'int', 'str', 'float', 'list', 'tuple',
                'map', 'filter', 'reduce', 'iter', 'all', 'any'])


class PermuteBoolOps(ast.NodeTransformer):
    """AST transformer: permute topmost boolean operation
    according to the given index order."""
    def __init__(self, indices):
        self.indices = indices

    def visit_BoolOp(self, node):
        if self.indices:
            values = [
                self.generic_visit(node.values[i])
                for i in self.indices
            ]
            self.indices = None
            return ast.copy_location(
                ast.BoolOp(op=node.op, values=values),
                node
            )
        else:
            return self.generic_visit(node)

# class PermuteAST(ast.NodeVisitor):
#     def visit_BinOp(self, node):
#         yield self.generic_visit(node)
#         if op_is_assoc(node) and ispure(node):


def node_is_pure(node, purefuns=[]):
    """Determine if the given node is (conservatively pure (effect-free)."""
    return (
        count(node, FUNCALL,
              matchpred=lambda x, env:
              x.func not in PUREFUNS and x.func not in purefuns) == 0
        and all(count(node, pat) == 0 for pat in IMPURE2)
    )


def permutations(node):
    """
    Generate all permutations of the binary and boolean operations, as
    well as of import orderings, in and below node, via associativity and
    mirroring, respecting purity. Because this is heavily exponential,
    limiting the number of imported names and the complexity of binary
    operation trees in your patterns is a good thing.
    """
    # TODO: These permutations allow matching like this:
    # Node: import math, sys, io
    # Pat: import _x_, ___
    # can bind x to math or io, but NOT sys (see TODO near
    # parse_pattern("___"))
    if isinstance(node, ast.Import):
        for perm in list_permutations(node.names):
            yield ast.Import(names=perm)
    elif isinstance(node, ast.ImportFrom):
        for perm in list_permutations(node.names):
            yield ast.ImportFrom(
                module=node.module,
                names=perm,
                level=node.level
            )
    if (
        isinstance(node, ast.BinOp)
    and op_is_assoc(node)
    and node_is_pure(node)
    ):
        for left in permutations(node.left):
            for right in permutations(node.right):
                yield ast.copy_location(ast.BinOp(
                    left=left,
                    op=node.op,
                    right=right,
                    ctx=node.ctx
                ))
                yield ast.copy_location(ast.BinOp(
                    left=right,
                    op=node.op,
                    right=left,
                    ctx=node.ctx
                ))
    elif (isinstance(node, ast.Compare)
          and len(node.ops) == 1
          and op_has_mirror(node.ops[0])
          and node_is_pure(node)):
        assert len(node.comparators) == 1
        for left in permutations(node.left):
            for right in permutations(node.comparators[0]):
                # print('PERMUTE', dump(left), dump(node.ops), dump(right))
                yield ast.copy_location(ast.Compare(
                    left=left,
                    ops=node.ops,
                    comparators=[right]
                ), node)
                yield ast.copy_location(ast.Compare(
                    left=right,
                    ops=[mirror(node.ops[0])],
                    comparators=[left]
                ), node)
    elif isinstance(node, ast.BoolOp) and node_is_pure(node):
        #print(dump(node))
        stuff = [[x for x in permutations(v)] for v in node.values]
        prod = [x for x in itertools.product(*stuff)]
        # print(prod)
        for values in prod:
            # print('VALUES', map(dump,values))
            for indices in itertools.permutations(range(len(node.values))):
                # print('BOOL', map(dump, values))
                yield PermuteBoolOps(indices).visit(
                    ast.copy_location(
                        ast.BoolOp(op=node.op, values=values),
                        node
                    )
                )
                pass
            pass
        pass
    else:
        # print('NO', dump(node))
        yield node
    pass


def list_permutations(items):
    """
    A generator which yields all possible orderings of the given list.
    """
    if len(items) <= 1:
        yield items[:]
    else:
        first = items[0]
        for subperm in list_permutations(items[1:]):
            for i in range(len(subperm) + 1):
                yield subperm[:i] + [first] + subperm[i:]


#----------#
# Matching #
#----------#

def match(node, pat, **kwargs):
    """A convenience wrapper for matchpat that accepts a patterns either
    as an pre-parsed AST or as a pattern source string to be parsed.

    """
    return matchpat(node, parse_pattern(pat), **kwargs)


def predtrue(node, matchenv):
    """The True predicate"""
    return True


def matchpat(
    node,
    pat,
    matchpred=predtrue,
    env={},
    gen=False,
    normalize=False
):
    """Match an AST against a (pre-parsed) pattern.

    The optional keyword argument matchpred gives a predicate of type
    (AST node * match environment) -> bool that filters structural
    matches by arbitrary additional criteria.  The default is the true
    predicate, accepting all structural matches.

    The optional keyword argument gen determines whether this function:
      - (gen=True)  yields an environment for each way pat matches node.
      - (gen=False) returns Some(the first of these environments), or
                    None if there are no matches (default).

    EXPERIMENTAL
    The optional keyword argument normalize determines whether to
    rewrite the target AST node and the pattern to inline simple
    straightline variable assignments into large expressions (to the
    extent possible) for matching.  The default is no normalization
    (False).  Normalization is experimental.  It is rather ad hoc and
    conservative and may causes unintuitive matching behavior.  Use
    with caution.

    INTERNAL
    The optional keyword env gives an initial match environment which
    may be used to constrain otherwise free pattern variables.  This
    argument is mainly intended for internal use.

    """
    assert node is not None
    assert pat is not None
    if normalize:
        if isinstance(node, ast.AST) or type(node) == list:
            node = canonical_pure(node)
            pass
        if isinstance(node, ast.AST) or type(node) == list:
            pat = canonical_pure(pat)
            pass
        pass

    # Permute the PATTERN, not the AST, so that nodes returned
    # always match real code.
    matches = (matchenv
               # outer iteration
               for permpat in permutations(pat)
               # inner iteration
               for matchenv in imatches(node, permpat,
                                        Some(env), True)
               if matchpred(node, matchenv))

    return matches if gen else takeone(matches)


def bind(env1, name, value):
    """
    Unify the environment in option env1 with a new binding of name to
    value.  Return Some(extended environment) if env1 is Some(existing
    environment) in which name is not bound or is bound to value.
    Otherwise, env1 is None or the existing binding of name
    incompatible with value, return None.
    """
    # Lyn modified to allow debugging prints
    assert type(name) == str
    if env1 is None:
        # return None
        result = None
    env = env1.value
    if var_is_anonymous(name):
        # return env1
        result = env1
    elif name in env:
        if takeone(imatches(env[name], value, Some({}), True)):
            # return env1
            result = env1
        else:
            # return None
            result = None
    else:
        env = env.copy()
        env[name] = value
        # print 'bind', name, dump(value), dump(env)
        # return Some(env)
        result = Some(env)
    # print(
    #    '\n$ bind({}, {}, {}) => {}'.format(
    #         dump(env1),
    #         name,
    #         dump(value),
    #         dump(result)
    #     )
    # )
    return result
    pass


IGNORE_FIELDS = set(['ctx', 'lineno', 'col_offset'])
"""AST node fields to be ignored when matching children."""


def argObjToName(argObj):
    '''Convert Python 3 arg object into a Name node,
       ignoring any annotation, lineno, and col_offset.'''
    if argObj is None:
        return None
    else:
        return ast.Name(id=argObj.arg, ctx=None)


def astStr(astObj):
    """
    Converts an AST object to a string, imperfectly.
    """
    if isinstance(astObj, ast.Name):
        return astObj.id
    elif isinstance(astObj, ast.Str):
        return repr(astObj.s)
    elif isinstance(astObj, ast.Num):
        return str(astObj.n)
    elif isinstance(astObj, (list, tuple)):
        return str([astStr(x) for x in astObj])
    elif hasattr(astObj, "_fields") and len(astObj._fields) > 0:
        return "{}({})".format(
            type(astObj).__name__,
            ', '.join(astStr(getattr(astObj, f)) for f in astObj._fields)
        )
    elif hasattr(astObj, "_fields"):
        return type(astObj).__name__
    else:
        return '<{}>'.format(type(astObj).__name__)


def defaultToName(defObj):
    """
    Converts a default expression to a name for matching purposes.
    TODO: Actually do recursive matching on these expressions!
    """
    if isinstance(defObj, ast.Name):
        return defObj.id
    else:
        return astStr(defObj)


def field_values(node):
    """Return a list of the values of all matching-relevant fields of the
    given AST node, with fields in consistent list positions."""

    # Specializations:
    if isinstance(node, ast.FunctionDef):
        return [ast.Name(id=v, ctx=None) if k == 'name'
                # Lyn sez: commented out following, because fields are
                # only name, arguments, body
                # else sorted(v, key=lambda x: x.arg) if k == 'keywords'
                else v
                for (k, v) in ast.iter_fields(node)
                if k not in IGNORE_FIELDS]

    if isinstance(node, ast.ClassDef):
        return [ast.Name(id=v, ctx=None) if k == 'name'
                else v
                for (k, v) in ast.iter_fields(node)
                if k not in IGNORE_FIELDS]

    if isinstance(node, ast.Call):
        # Old: sorted(v, key=lambda kw: kw.arg)
        # New: keyword args use nominal (not positional) matching.
        #return [sorted(v, key=lambda kw: kw.arg) if k == 'keywords' else v
        return [
            (
                odict((kw.arg, kw.value) for kw in v)
                if k == 'keywords'
                else v
            )
            for (k, v) in ast.iter_fields(node)
            if k not in IGNORE_FIELDS
        ]

    # Lyn sez: ast.arguments handling is new for Python 3
    if isinstance(node, ast.arguments):
        argList = [
            # Need to create Name nodes to match patterns.
            argObjToName(argObj)
            for argObj in node.args
        ] # Ignores argObj annotation, lineno, col_offset
        if (
            node.vararg is None
        and node.kwarg is None
        and node.kwonlyargs == []
        and node.kw_defaults == []
        and node.defaults == []
        ):
            # Optimize (for debugging purposes) this very common case by
            # returning a singleton list of lists
            return [argList]
        else:
            # In unoptimized case, return list with sublists and
            # argObjects/Nones:
            # TODO: treat triple underscores separately/specially!!!
            return [
                argList,
                argObjToName(node.vararg),
                argObjToName(node.kwarg),
                [argObjToName(argObj) for argObj in node.kwonlyargs],
                # Peter 2019-9-30 the defaults cannot be reliably converted
                # into names, because they are expressions!
                node.kw_defaults,
                node.defaults
            ]

    if isinstance(node, ast.keyword):
        return [ast.Name(id=v, ctx=None) if k == 'arg' else v
                for (k, v) in ast.iter_fields(node)
                if k not in IGNORE_FIELDS]

    if isinstance(node, ast.Global):
        return [ast.Name(id=n, ctx=None) for n in sorted(node.names)]

    if isinstance(node, ast.Import):
        return [ node.names ]

    if isinstance(node, ast.ImportFrom):
        return [ast.Name(id=node.module, ctx=None), node.level, node.names]

    if isinstance(node, ast.alias):
        result = [ ast.Name(id=node.name, ctx=None) ]
        if node.asname is not None:
            result.append(ast.Name(id=node.asname, ctx=None))
        return result

    # General cases:
    if isinstance(node, ast.AST):
        return [v for (k, v) in ast.iter_fields(node)
                if k not in IGNORE_FIELDS]

    if type(node) == list:
        return node

    # Added by Peter Mawhorter 2019-4-2 to fix problem where subpatterns fail
    # to match within keyword arguments of functions because field_values
    # returns an odict as one value for functions with kwargs, and asking for
    # the field_values of that odict was hitting the base case below.
    if isinstance(node, (dict, odict)):
        return [
          ast.Name(id=n, ctx=None) for n in node.keys()
        ] + list(node.values())

    return []


imatchCount = 0 # For showing stack depth in debugging prints for imathces


def imatches(node, pat, env1, seq):
    """Exponential backtracking match generating 0 or more matching
    environments.  Supports multiple sequence patterns in one context,
    simple permutations of semantically equivalent but syntactically
    mirrored patterns.
    """
    # Lyn change early-return pattern to named result returned at end to
    # allow debugging prints
    # global imatchCount #$
    # print('\n$ {}Entering imatches({}, {}, {}, {})'.format(
    #         '| '*imatchCount, dump(node), dump(pat), dump(env1), seq))
    # imatchCount += 1 #$
    result = iterempty() # default result if not overridden
    if env1 is None:
        result = iterempty()
        # imatchCount -= 1 #$
        # print(
        #     '\n$ {} Exiting imatches({}, {}, {}, {}) => {})'.format(
        #         '| ' * imatchCount,
        #         dump(node),
        #         dump(pat),
        #         dump(env1),
        #         seq,
        #         dump(result)
        #     )
        # )
        return result
    env = env1.value
    assert env is not None
    if (
        (
            type(pat) == bool
         or type(pat) == str # All Python 3 strings are unicode
         or pat is None
        )
    and node == pat
    ):
        result = iterone(env)
    elif type(pat) == int or type(pat) == float:
        # Literal int or float pattern
        if type(node) == type(pat):
            if (
                (type(pat) == int and node == pat)
             or (type(pat) == float and abs(node - pat) < 0.001)
            ):
                result = iterone(env)
            pass
    elif node_var(pat):
        # Var pattern.
        # Match and bind name to node.
        if node_is_bindable(node):
            # [Peter Mawhorter 2021-8-29] Attempting to allow import
            # aliases to unify with variable references later on. If the
            # alias has an 'as' part we unify as if it's a name with that
            # ID, otherwise we use the name part as the ID.
            if isinstance(node, ast.alias):
                if node.asname:
                    bind_as = ast.Name(id=node.asname, ctx=None)
                else:
                    bind_as = ast.Name(id=node.name, ctx=None)
            else:
                bind_as = node
            env2 = bind(env1, node_var(pat), bind_as)
            if env2:
                result = iterone(env2.value)
            pass
    elif typed_lit_var(pat):
        # Var pattern to bind only a literal of given type.
        id, ty = typed_lit_var(pat)
        lit = LIT_TYPES[ty](node)
        # Match and bind name to literal.
        if lit:
            env2 = bind(env1, id, lit.value)
            if env2:
                result = iterone(env2.value)
            pass
    elif type(node) == type(pat):
        # Node and pattern have same type.
        if type(pat) == list:
            # Node and pattern are both lists.  Do positional matching.
            if len(pat) == 0:
                # Empty list pattern.  Node must also be empty.
                if len(node) == 0:
                    result = iterone(env)
                pass
            elif len(node) == 0:
                # Non-empty list pattern with empty node.
                # Try to match sequence subpatterns.
                if seq:
                    psn = set_var(pat[0])
                    if psn:
                        result = imatches(node, pat[1:],
                                          bind(env1, psn, []), seq)
                    pass
                pass
            else:
                # Both are non-empty.
                psn = set_var(pat[0])
                if seq and psn:
                    # First subpattern is a sequence pattern.
                    # Try all consumption sizes, greediest first.
                    # Unsophisticated exponential backtracking search.
                    result = ichain(
                        imatches(
                            node[i:],
                            pat[1:],
                            bind(env1, psn, node[:i]),
                            seq
                        )
                        for i in range(len(node), -1, -1)
                    )
                # Lyn sez: common special case helpful for more concrete
                # debugging results (e.g., may return FiniteIterator
                # rather than itertools.chain object.)
                elif len(node) == 1 and len(pat) == 1:
                    result = imatches(node[0], pat[0], env1, True)
                else:
                    # For all matches of scalar first element sub pattern.
                    # Generate all corresponding matches of remainder.
                    # Unsophisticated exponential backtracking search.
                    result = ichain(
                        imatches(node[1:], pat[1:], Some(bs), seq)
                       for bs in imatches(node[0], pat[0], env1, True)
                    )
                pass
        elif type(node) == dict or type(node) == odict:
            result = match_dict(node, pat, env1)
        else:
            # Node and pat have same type, but are not lists.
            # Match scalar structures by matching lists of their fields.
            if isinstance(node, ast.AST):
                # TODO: DEBUG
                #if isinstance(node, ast.Import):
                #    print(
                #        "FV2i",
                #        dump(field_values(node)),
                #        dump(field_values(pat))
                #    )
                #if isinstance(node, ast.alias):
                #    print(
                #        "FV2a",
                #        dump(field_values(node)),
                #        dump(field_values(pat))
                #    )
                result = imatches(
                    field_values(node),
                    field_values(pat),
                    env1,
                    False
                )
            pass
        pass
    # return iterempty()
    # imatchCount -= 1 #$
    # print(
    #     '\n$ {} Exiting imatches({}, {}, {}, {}) => {})'.format(
    #         '| ' * imatchCount,
    #         dump(node),
    #         dump(pat),
    #         dump(env1),
    #         seq,
    #         dump(result)
    #     )
    # )
    return result


def match_dict(node, pat, env1):
    # Node and pattern are both dictionaries. Do nominal matching.
    # Match all named key patterns, then all single-key pattern variables,
    # and finally the multi-key pattern variables.
    assert all(type(k) == str # All Python 3 strings are unicode
               for k in pat)
    assert all(type(k) == str # All Python 3 strings are unicode
               for k in node)

    def match_keys(node, pat, envopt):
        """Match literal keys."""
        keyopt = takeone(k for k in pat
                         if not node_var_str(k)
                         and not set_var_str(k))
        if keyopt:
            # There is at least one named key in the pattern.
            # If this key is also in the program node, then for each
            # match of the corresponding node value and pattern value,
            # generate all matches for the remaining keys.
            key = keyopt.value
            if key in node:
                return ichain(match_keys(dict_unbind(node, key),
                                         dict_unbind(pat, key),
                                         Some(kenv))
                              for kenv in imatches(node[key], pat[key],
                                                   envopt, False))
            else:
                return iterempty()
            pass
        else:
            # The pattern contains no literal keys.
            # Generate all matches for the node and set key variables.
            return match_var_keys(node, pat, envopt)
        pass

    def match_var_keys(node, pat, envopt):
        """Match node variable keys."""
        keyvaropt = takeone(k for k in pat if node_var_str(k))
        if keyvaropt:
            # There is at least one single-key variable in the pattern.
            # For each key-value pair in the node whose value matches
            # this single-key variable's associated value pattern,
            # generate all matches for the remaining keys.
            keyvar = keyvaropt.value
            return ichain(match_var_keys(dict_unbind(node, nkey),
                                         dict_unbind(pat, keyvar),
                                         bind(Some(kenv),
                                              node_var_str(keyvar),
                                              ast.Name(id=nkey, ctx=None)))
                          # outer iteration:
                          for nkey, nval in node.items()
                          # inner iteration:
                          for kenv in imatches(nval, pat[keyvar],
                                               envopt, False))
        else:
            # The pattern contains no single-key variables.
            # Generate all matches for the set key variables.
            return match_set_var_keys(node, pat, envopt)
        pass

    def match_set_var_keys(node, pat, envopt):
        """Match set variable keys."""
        # NOTE: see discussion of match environments for this case:
        # https://github.com/wellesleycs111/codder/issues/25
        assert envopt
        keysetvaropt = takeone(k for k in pat if set_var_str(k))
        if keysetvaropt:
            # There is a multi-key variable in the pattern.
            # Capture all remaining key-value pairs in the node.
            e = bind(envopt, set_var_str(keysetvaropt.value),
                     [(ast.Name(id=kw, ctx=None), karg)
                      for kw, karg in node.items()])
            return iterone(e.value) if e else iterempty()
        elif 0 == len(node):
            # There is no multi-key variable in the pattern.
            # There is a match only if there are no remaining
            # keys in the node.
            # There should also be no remaining keys in the pattern.
            assert 0 == len(pat)
            return iterone(envopt.value)
        else:
            return iterempty()

    return match_keys(node, pat, env1)


def find(node, pat, **kwargs):
    """Pre-order search for first sub-AST matching pattern, returning
    (matched node, bindings)."""
    kwargs['gen'] = True
    return takeone(findall(node, parse_pattern(pat), **kwargs))


def findall(node, pat, outside=[], **kwargs):
    """
    Search for all sub-ASTs matching pattern, returning list of (matched
    node, bindings).
    """
    assert node is not None
    assert pat is not None
    gen = kwargs.get('gen', False)
    kwargs['gen'] = True
    pat = parse_pattern(pat)
    # Top-level sequence patterns are not "anchored" to the ends of
    # the containing block when *finding* a submatch within a node (as
    # opposed to matching a node exactly).  They may match any
    # contiguous subsequence.
    # - To allow sequence patterns to match starting later than the
    #   beginning of a program sequence, matching is attempted
    #   recursively with smaller and smaller suffixes of the program
    #   sequence.
    # - To allow sequence patterns to match ending earlier
    #   than the end of a program block, we implicitly ensure that a
    #   sequence wildcard pattern terminates every top-level sequence
    #   pattern.
    # TODO: Because permutations are applied later, this doesn't allow
    # all the matching we'd like in the following scenario
    # Node: [ alias(name="x"), alias(name="y"), alias(name="z") ]
    # Pat: [ alias(name="_a_"), alias(name="___") ]
    # here because order of aliases doesn't matter, we *should* be able
    # to bind _a_ to x, y, OR z, but it can only bind to x or z, NOT y
    if type(pat) == list and not set_var(pat[-1]):
        pat = pat + [parse_pattern('___')]
        pass

    def findall_scalar_pat_iter(node):
        """Generate all matches of a scalar (non-list) pattern at this node
        or any non-excluded descendant of this node."""
        assert type(pat) != list
        assert node is not None
        # Yield any environment(s) for match(es) of pattern at node.
        envs = [e for e in matchpat(node, pat, **kwargs)]
        if 0 < len(envs):
            yield (node, envs)
        # Continue the search for matches in sub-ASTs of node, only if
        # node is not excluded by a "match outside" pattern.
        if not any(match(node, op) for op in outside):
            for n in field_values(node):
                if n: # Search only within non-None children.
                    for result in findall_scalar_pat_iter(n):
                        yield result
                        pass
                    pass
                pass
            pass
        pass

    def findall_list_pat_iter(node):
        """Generate all matches of a list pattern at this node or any
        non-excluded descendant of this node."""
        assert type(pat) == list
        assert 0 < len(pat)
        if type(node) == list:
            # If searching against a list:
            # - match against the list itself
            # - search against the first child of the list
            # - search against the tail of the list

            # Match against the list itself.
            # Yield any environment(s) for match(es) of pattern at node.
            envs = [e for e in matchpat(node, pat, **kwargs)]
            if 0 < len(envs):
                yield (node, envs)
            # Continue the search for matches in sub-ASTs of node,
            # only if node is not excluded by a "match outside"
            # pattern.
            if (
                not any(match(node, op) for op in outside)
            and 0 < len(node) # only in nonempty nodes...
            ):
                # Search for matches in the first sub-AST.
                for m in findall_list_pat_iter(node[0]):
                    yield m
                    pass
                if not set_var(pat[0]):
                    # If this sequence pattern does not start with
                    # a sequence wildcard, then:
                    # Search for matches in the tail of the list.
                    # (Includes matches against the entire tail.)
                    for m in findall_list_pat_iter(node[1:]):
                        yield m
                        pass
                    pass
                pass
            pass
        elif not any(match(node, op) for op in outside): # and node is not list
            # A list pattern cannot match against a scalar node.
            # Search for matches in children of this scalar (non-list)
            # node, only if node is not excluded by a "match outside"
            # pattern.

            # Optimize to search only where list patterns could match.

            # Body blocks
            for ty in [ast.ClassDef, ast.FunctionDef, ast.With, ast.Module,
                       ast.If, ast.For, ast.While,
                       # ast.TryExcept, ast.TryFinally,
                       # In Python 3, a single Try node covers both
                       # TryExcept and TryFinally
                       ast.Try,
                       ast.ExceptHandler]:
                if isinstance(node, ty):
                    for m in findall_list_pat_iter(node.body):
                        yield m
                        pass
                    break
                pass
            # Block else blocks
            for ty in [ast.If, ast.For, ast.While,
                       # ast.TryExcept
                       # In Python 3, a single Try node covers both
                       # TryExcept and TryFinally
                       ast.Try
                       ]:
                if isinstance(node, ty) and node.orelse:
                    for m in findall_list_pat_iter(node.orelse):
                        yield m
                        pass
                    break
                pass

#             # Except handler blocks
#             if isinstance(node, ast.TryExcept):
#                 for h in node.handlers:
#                     for m in findall_list_pat_iter(h.body):
#                         yield m
#                         pass
#                     pass
#                 pass
#             # finally blocks
#             if isinstance(node, ast.TryFinally):
#                 for m in findall_list_pat_iter(node.finalbody):
#                         yield m
#                         pass
#                 pass

            # In Python 3, a single Try node covers both TryExcept and
            # TryFinally
            if isinstance(node, ast.Try):
                for h in node.handlers:
                    for m in findall_list_pat_iter(h.body):
                        yield m
                        pass
                    pass
                pass

            # General non-optimized version.
            # Must be mutually exclusive with the above if used.
            # for n in field_values(node):
            #                 if n:
            #                     for result in findall_list_pat_iter(n):
            #                         yield result
            #                         pass
            #                     pass
            #                 pass
            pass
        pass
    # Apply the right search based on pattern type.
    matches = (findall_list_pat_iter if type(pat) == list
               else findall_scalar_pat_iter)(node)
    # Return the generator or a list of all generated matches,
    # depending on gen.
    return matches if gen else list(matches)


def count(node, pat, **kwargs):
    """
    Count all sub-ASTs matching pattern. Does NOT count individual
    environments that match (i.e., ways that bindings could attach at a
    given node), but rather counts nodes at which one or more bindings
    are possible.
    """
    assert 'gen' not in kwargs
    return sum(1 for x in findall(node, pat,
                                  gen=True, **kwargs))


#---------------------------------------------------------#
# EXPERIMENTAL: Normalize/Inline Simple Straightline Code #
#---------------------------------------------------------#

class Unimplemented(Exception):
    pass


SIMPLE_INLINE_TYPES = [
    ast.Expr, ast.Return,
    # ast.Print, # Removed from ast module in Python 3
    ast.Name, ast.Store, ast.Load, ast.Param,
    # Simple augs should be desugared already.
    # Those remaining are too tricky for a simple implementation.
]


class InlineAvailableExpressions(ast.NodeTransformer):
    def __init__(self, other=None):
        self.available = dict(other.available) if other else {}

    def visit_Name(self, name):
        if isinstance(name.ctx, ast.Load) and name.id in self.available:
            return self.available[name.id]
        else:
            return self.generic_visit(name)

    def visit_Assign(self, assign):
        raise Unimplemented
        new = ast.copy_location(ast.Assign(
            targets=assign.targets,
            value=self.visit(assign.value)
        ), assign)
        self.available[assign.targets[0].id] = new.value
        return new

    def visit_If(self, ifelse):
        # Inline into the test.
        test = self.visit(ifelse.test)
        # Inline and accumulate in the then and else independently.
        body_inliner = InlineAvailableExpressions(self)
        orelse_inliner = InlineAvailableExpressions(self)
        body = body_inliner.inline_block(ifelse.body)
        orelse = orelse_inliner.inline_block(ifelse.orelse)
        # Any var->expression that is available after both branches
        # is available after.
        self.available = {
            name: body_inliner.available[name]
            for name in (set(body_inliner.available)
                         & set(orelse_inliner.available))
            if (body_inliner.available[name] == orelse_inliner.available[name])
        }
        return ast.copy_location(
            ast.If(test=test, body=body, orelse=orelse),
            ifelse
        )

    def generic_visit(self, node):
        if not any(isinstance(node, t) for t in SIMPLE_INLINE_TYPES):
            raise Unimplemented()
        return ast.NodeTransformer.generic_visit(self, node)

    def inline_block(self, block):
        # Introduce duplicate common subexpressions...
        return [self.visit(stmt) for stmt in block]


class DeadCodeElim(ast.NodeTransformer):
    def __init__(self, other=None):
        self.used = set(other.users) if other else set()
        pass

    def visit_Name(self, name):
        if isinstance(name.ctx, ast.Store):
            # Var store defines, removing from the set.
            self.used = self.used - {name.id}
            return name
        elif isinstance(name.ctx, ast.Load):
            # Var use uses, adding to the set.
            self.used = self.used | {name.id}
            return name
        else:
            return name
        pass

    def visit_Assign(self, assign):
        # This restriction prevents worries about things like:
        # x, x[0] = [[1], 2]
        # By using this restriction it is safe to keep the single set,
        # thus order of removals and additions will not be a problem
        # since defs are discovered first (always to left of =), then
        # uses are discovered next (to right of =).
        assert all(
            (
                node_is_name(t)
             or (
                    isinstance(t, ast.Tuple)
                and all(node_is_name(t) for t in t.elts)
                )
            )
            for t in assign.targets
        )
        # Now handled by visit_Name
        # self.used = self.used - set(n.id for n in assign.targets)
        if (any(t.id in self.used for t in assign.targets if node_is_name(t))
            or any(t.id in self.used
                   for tup in assign.targets for t in tup
                   if type(tup) == tuple and node_is_name(t))):
            return ast.copy_location(ast.Assign(
                targets=[self.visit(t) for t in assign.targets],
                value=self.visit(assign.value)
            ), assign)
        else:
            return None

    def visit_If(self, ifelse):
        body_elim = DeadCodeElim(self)
        orelse_elim = DeadCodeElim(self)
        # DCE the body
        body = body_elim.elim_block(ifelse.body)
        # DCE the else
        orelse = orelse_elim.elim_block(ifelse.body)
        # Use the test -- TODO: could eliminate entire if sometimes.
        # Keep it for now for clarity.
        self.used = body_elim.used | orelse_elim.used
        test = self.visit(ifelse.test)
        return ast.copy_location(ast.If(test=test, body=body, orelse=orelse),
                                 ifelse)

    def generic_visit(self, node):
        if not any(isinstance(node, t) for t in SIMPLE_INLINE_TYPES):
            raise Unimplemented()
        return ast.NodeTransformer.generic_visit(self, node)

    def elim_block(self, block):
        # Introduce duplicate common subexpressions...
        return [s for s in
                (self.visit(stmt) for stmt in block[::-1])
                if s][::-1]


class NormalizePure(ast.NodeTransformer):
    """AST transformer: normalize/inline straightline assignments into
    single expressions as possible."""
    def normalize_block(self, block):
        try:
            return DeadCodeElim().elim_block(
                InlineAvailableExpressions().inline_block(block)
            )
        except Unimplemented:
            return block

    def visit_FunctionDef(self, fun):
        # Lyn warning: previously commented code below is from Python 2
        # and won't work in Python 3 (args have changed).
        # assert 0 < len(
        #    result.value[0].intersection(set(a.id for a in fun.args.args))
        # )
        normbody = self.normalize_block(fun.body)
        if normbody != fun.body:
            return ast.copy_location(ast.FunctionDef(
                name=fun.name,
                args=self.generic_visit(fun.args),
                body=normbody,
            ), fun)
        else:
            return fun


# Note 2021-7-29 Peter Mawhorter: Disabled use of DesugarAugAssign here
# because of concerns about students using list += string. If you want
# to match += you'll have to do so explicitly (and if that's a common use
# case, we can add something to specifications and/or patterns for that).
def canonical_pure(node):
    """Return the normalized/inlined version of an AST node."""
    # print(type(fun))
    # assert isinstance(fun, ast.FunctionDef)
    # print()
    # print('FUN', dump(fun))
    if type(node) == list:
        return NormalizePure().normalize_block(node)
        #    [DesugarAugAssign().visit(stmt) for stmt in node]
        #)
    else:
        assert isinstance(node, ast.AST)
        #return NormalizePure().visit(DesugarAugAssign().visit(node))
        return NormalizePure().visit(node)


CANON_CACHE = {}


def parse_canonical_pure(string, toplevel=False):
    """Parse a normalized/inlined version of a program."""
    if type(string) == list:
        return [parse_canonical_pure(x) for x in string]
    elif string not in CANON_CACHE:
        CANON_CACHE[string] = canonical_pure(
            parse_pattern(string, toplevel=toplevel)
        )
        pass
    return CANON_CACHE[string]

#------------------------------------#
# Pretty Print ASTs to Python Source #
#------------------------------------#


INDENT = '    '


def indent(pat, indent=INDENT):
    """Apply indents to a source string."""
    return indent + pat.replace('\n', '\n' + indent)


class SourceFormatter(ast.NodeVisitor):
    """AST visitor: pretty print AST to python source string"""
    def __init__(self):
        ast.NodeVisitor.__init__(self)
        self._indent = ''
        pass

    def indent(self):
        self._indent += INDENT
        pass

    def unindent(self):
        self._indent = self._indent[:-4]
        pass

    def line(self, ln):
        return self._indent + ln + '\n'

    def lines(self, lst):
        return ''.join(lst)

    def generic_visit(self, node):
        assert False, 'visiting {}'.format(ast.dump(node))
        pass

    def visit_Module(self, m):
        return self.lines(self.visit(n) for n in m.body)

    def visit_Interactive(self, i):
        return self.lines(self.visit(n) for n in i.body)

    def visit_Expression(self, e):
        return self.line(self.visit(e.body))

    def visit_FunctionDef(self, f):
        assert not f.decorator_list
        header = self.line('def {name}({args}):'.format(
            name=f.name,
            args=self.visit(f.args))
        )
        self.indent()
        body = self.lines(self.visit(s) for s in f.body)
        self.unindent()
        return header + body + '\n'

    def visit_ClassDef(self, c):
        assert not c.decorator_list
        header = self.line('class {name}({bases}):'.format(
            name=c.name,
            bases=', '.join(self.visit(b) for b in c.bases)
        ))
        self.indent()
        body = self.lines(self.visit(s) for s in c.body)
        self.unindent()
        return header + body + '\n'

    def visit_Return(self, r):
        return self.line('return' if r.value is None
                         else 'return {}'.format(self.visit(r.value)))

    def visit_Delete(self, d):
        return self.line('del ' + ''.join(self.visit(e) for e in d.targets))

    def visit_Assign(self, a):
        return self.line(', '.join(self.visit(e)
                                   for e in a.targets)
                         + ' = ' + self.visit(a.value))

    def visit_AugAssign(self, a):
        return self.line('{target} {op}= {expr}'.format(
            target=self.visit(a.target),
            op=self.visit(a.op),
            expr=self.visit(a.value))
        )

# Print removed as ast node on Python 3
#     def visit_Print(self, p):
#         assert p.dest == None
#         return self.line('print {}{}'.format(
#             ', '.join(self.visit(e) for e in p.values),
#             ',' if p.values and not p.nl else ''
#         ))

    def visit_For(self, f):
        header = self.line('for {} in {}:'.format(
            self.visit(f.target),
            self.visit(f.iter))
        )
        self.indent()
        body = self.lines(self.visit(s) for s in f.body)
        orelse = self.lines(self.visit(s) for s in f.orelse)
        self.unindent()
        return header + body + (
            self.line('else:') + orelse
            if f.orelse else ''
        )

    def visit_While(self, w):
        # Peter 2021-6-16: Removed this assert; orelse isn't defined here
        # assert not orelse
        header = self.line('while {}:'.format(self.visit(w.test)))
        self.indent()
        body = self.lines(self.visit(s) for s in w.body)
        orelse = self.lines(self.visit(s) for s in w.orelse)
        self.unindent()
        return header + body + (
            self.line('else:') + orelse
            if w.orelse else ''
        )
        return header + body

    def visit_If(self, i):
        header = self.line('if {}:'.format(self.visit(i.test)))
        self.indent()
        body = self.lines(self.visit(s) for s in i.body)
        orelse = self.lines(self.visit(s) for s in i.orelse)
        self.unindent()
        return header + body + (
            self.line('else:') + orelse
            if i.orelse else ''
        )

    def visit_With(self, w):
        # Converted to Python3 withitems:
        header = self.line(
            'with {items}:'.format(
                items=', '.join(
                    '{expr}{asnames}'.format(
                        expr=self.visit(item.context_expr),
                        asnames=('as ' + self.visit(item.optional_vars)
                                 if item.optional_vars else '')
                    )
                        for item in w.items
                )
            )
        )
        self.indent()
        body = self.lines(self.visit(s) for s in w.body)
        self.unindent()
        return header + body

    # Python 3: raise has new abstract syntax
    def visit_Raise(self, r):
        return self.line('raise{}{}'.format(
            (' ' + self.visit(r.exc)) if r.exc else '',
            (' from ' + self.visit(r.cause)) if r.cause else ''
        ))

#    def visit_Raise(self, r):
#        return self.line('raise{}{}{}{}{}'.format(
#             self.visit(r.type) if r.type else '',
#             ', ' if r.type and r.inst else '',
#             self.visit(r.inst) if r.inst else '',
#             ', ' if (r.type or r.inst) and r.tback else '',
#             self.visit(r.tback) if r.tback else ''
#                 ))

#     def visit_TryExcept(self, te):
#         self.indent()
#         tblock = self.lines(self.visit(s) for s in te.body)
#         orelse = self.lines(self.visit(s) for s in te.orelse)
#         self.unindent()
#         return (
#             self.line('try:')
#             + tblock
#             + ''.join(self.visit(eh) for eh in te.handlers)
#             + (self.line('else:') + orelse if orelse else '' )
#         )

#     def visit_TryFinally(self, tf):
#         self.indent()
#         tblock = self.lines(self.visit(s) for s in tf.body)
#         fblock = self.lines(self.visit(s) for s in tf.finalbody)
#         self.unindent()
#         return (
#             self.line('try:')
#             + tblock
#             + self.line('finally:')
#             + fblock
#         )

    # In Python 3, a single Try node covers both TryExcept and TryFinally
    def visit_Try(self, t):
        self.indent()
        tblock = self.lines(self.visit(s) for s in t.body)
        orelse = self.lines(self.visit(s) for s in t.orelse)
        fblock = self.lines(self.visit(s) for s in t.finalbody)
        self.unindent()
        return (
            self.line('try:')
            + tblock
            + ''.join(self.visit(eh) for eh in t.handlers)
            + (self.line('else:') + orelse if orelse else '' )
            + (self.line('finally:') + fblock if fblock else '' )
        )

    def visit_ExceptHandler(self, eh):
        header = self.line('except{}{}{}{}:'.format(
            ' ' if eh.type else '',
            self.visit(eh.type) if eh.type else '',
            ' as ' if eh.type and eh.name else ' ' if eh.name else '',
            self.visit(eh.name) if eh.name and isinstance(eh.name, ast.AST)
              else (eh.name if eh.name else '')
        ))
        self.indent()
        body = self.lines(self.visit(s) for s in eh.body)
        self.unindent()
        return header + body

    def visit_Assert(self, a):
        return self.line('assert {}{}{}'.format(
            self.visit(a.test),
            ', ' if a.msg else '',
            self.visit(a.msg) if a.msg else ''
        ))

    def visit_Import(self, i):
        return self.line(
            'import {}'.format(', '.join(self.visit(n) for n in i.names))
        )

    def visit_ImportFrom(self, f):
        return self.line('from {}{} import {}'.format(
            '.' * f.level,
            f.module if f.module else '',
            ', '.join(self.visit(n) for n in f.names)
        ))

    def visit_Exec(self, e):
        return self.line('exec {}{}{}{}{}'.format(
            self.visit(e.body),
            ' in ' if e.globals else '',
            self.visit(e.globals) if e.globals else '',
            ', ' if e.locals else '',
            self.visit(e.locals) if e.locals else ''
        ))

    def visit_Global(self, g):
        return self.line('global {}'.format(', '.join(g.names)))

    def visit_Expr(self, e):
        return self.line(self.visit(e.value))

    def visit_Pass(self, p):
        return self.line('pass')

    def visit_Break(self, b):
        return self.line('break')

    def visit_Continue(self, c):
        return self.line('continue')

    def visit_BoolOp(self, b):
        return ' {} '.format(
            self.visit(b.op)
        ).join('({})'.format(self.visit(e)) for e in b.values)

    def visit_BinOp(self, b):
        return '({}) {} ({})'.format(
            self.visit(b.left),
            self.visit(b.op),
            self.visit(b.right)
        )

    def visit_UnaryOp(self, u):
        return '{} ({})'.format(
            self.visit(u.op),
            self.visit(u.operand)
        )

    def visit_Lambda(self, ld):
        return '(lambda {}: {})'.format(
            self.visit(ld.args),
            self.visit(ld.body)
        )

    def visit_IfExp(self, i):
        return '({} if {} else {})'.format(
            self.visit(i.body),
            self.visit(i.test),
            self.visit(i.orelse)
        )

    def visit_Dict(self, d):
        return '{{ {} }}'.format(
            ', '.join('{}: {}'.format(self.visit(k), self.visit(v))
                      for k, v in zip(d.keys, d.values))
        )

    def visit_Set(self, s):
        return '{{ {} }}'.format(', '.join(self.visit(e) for e in s.elts))

    def visit_ListComp(self, lc):
        return '[{} {}]'.format(
            self.visit(lc.elt),
            ' '.join(self.visit(g) for g in lc.generators)
        )

    def visit_SetComp(self, sc):
        return '{{{} {}}}'.format(
            self.visit(sc.elt),
            ' '.join(self.visit(g) for g in sc.generators)
        )

    def visit_DictComp(self, dc):
        return '{{{} {}}}'.format(
            '{}: {}'.format(self.visit(dc.key), self.visit(dc.value)),
            ' '.join(self.visit(g) for g in dc.generators)
        )

    def visit_GeneratorExp(self, ge):
        return '({} {})'.format(
            self.visit(ge.elt),
            ' '.join(self.visit(g) for g in ge.generators)
        )

    def visit_Yield(self, y):
        return 'yield {}'.format(self.visit(y.value) if y.value else '')

    def visit_Compare(self, c):
        assert len(c.ops) == len(c.comparators)
        return '{} {}'.format(
            '({})'.format(self.visit(c.left)),
            ' '.join(
                '{} ({})'.format(self.visit(op), self.visit(expr))
                for op, expr in zip(c.ops, c.comparators)
            )
        )

    def visit_Call(self, c):
        # return '{fun}({args}{keys}{starargs}{starstarargs})'.format(
        # Unlike Python 2, Python 3 has no starargs or startstarargs
        return '{fun}({args}{keys})'.format(
            fun=self.visit(c.func),
            args=', '.join(self.visit(a) for a in c.args),
            keys=(
                (', ' if c.args else '')
              + (
                  ', '.join(self.visit(ka) for ka in c.keywords)
                    if c.keywords else ''
                )
            )
        )

    def visit_Repr(self, r):
        return 'repr({})'.format(self.visit(r.expr))

    def visit_Num(self, n):
        return repr(n.n)

    def visit_Str(self, s):
        return repr(s.s)

    def visit_Attribute(self, a):
        return '{}.{}'.format(self.visit(a.value), a.attr)

    def visit_Subscript(self, s):
        return '{}[{}]'.format(self.visit(s.value), self.visit(s.slice))

    def visit_Name(self, n):
        return n.id

    def visit_List(self, ls):
        return '[{}]'.format(', '.join(self.visit(e) for e in ls.elts))

    def visit_Tuple(self, tp):
        return '({})'.format(', '.join(self.visit(e) for e in tp.elts))

    def visit_Ellipsis(self, s):
        return '...'

    def visit_Slice(self, s):
        return '{}:{}{}{}'.format(
            self.visit(s.lower) if s.lower else '',
            self.visit(s.upper) if s.upper else '',
            ':' if s.step else '',
            self.visit(s.step) if s.step else ''
        )

    def visit_ExtSlice(self, es):
        return ', '.join(self.visit(s) for s in es.dims)

    def visit_Index(self, i):
        return self.visit(i.value)

    def visit_And(self, a):
        return 'and'

    def visit_Or(self, o):
        return 'or'

    def visit_Add(self, a):
        return '+'

    def visit_Sub(self, a):
        return '-'

    def visit_Mult(self, a):
        return '*'

    def visit_Div(self, a):
        return '/'

    def visit_Mod(self, a):
        return '%'

    def visit_Pow(self, a):
        return '**'

    def visit_LShift(self, a):
        return '<<'

    def visit_RShift(self, a):
        return '>>'

    def visit_BitOr(self, a):
        return '|'

    def visit_BixXor(self, a):
        return '^'

    def visit_BitAnd(self, a):
        return '&'

    def visit_FloorDiv(self, a):
        return '//'

    def visit_Invert(self, a):
        return '~'

    def visit_Not(self, a):
        return 'not'

    def visit_UAdd(self, a):
        return '+'

    def visit_USub(self, a):
        return '-'

    def visit_Eq(self, a):
        return '=='

    def visit_NotEq(self, a):
        return '!='

    def visit_Lt(self, a):
        return '<'

    def visit_LtE(self, a):
        return '<='

    def visit_Gt(self, a):
        return '>'

    def visit_GtE(self, a):
        return '>='

    def visit_Is(self, a):
        return 'is'

    def visit_IsNot(self, a):
        return 'is not'

    def visit_In(self, a):
        return 'in'

    def visit_NotIn(self, a):
        return 'not in'

    def visit_comprehension(self, c):
        return 'for {} in {}{}{}'.format(
            self.visit(c.target),
            self.visit(c.iter),
            ' ' if c.ifs else '',
            ' '.join('if {}'.format(self.visit(i)) for i in c.ifs)
        )

    def visit_arg(self, a):
        '''[2019/01/22, lyn] Handle new arg objects in Python 3.'''
        return a.arg # The name of the argument

    def visit_keyword(self, k):
        return '{}={}'.format(k.arg, self.visit(k.value))

    def visit_alias(self, a):
        return '{} as {}'.format(a.name, a.asname) if a.asname else a.name

    def visit_arguments(self, a):
        # [2019/01/22, lyn] Note: This does *not* handle Python 3's
        # keyword-only arguments (probably moot for 111, but not
        # beyond).
        stdargs = a.args[:-len(a.defaults)] if a.defaults else a.args
        defargs = (
            zip(a.args[-len(a.defaults):], a.defaults)
            if a.defaults else []
        )
        return '{stdargs}{sep1}{defargs}{sep2}{varargs}{sep3}{kwargs}'.format(
            stdargs=', '.join(self.visit(sa) for sa in stdargs),
            sep1=', ' if 0 < len(stdargs) and defargs else '',
            defargs=', '.join('{}={}'.format(self.visit(da), self.visit(dd))
                              for da, dd in defargs),
            sep2=', ' if 0 < len(a.args) and a.vararg else '',
            varargs='*{}'.format(a.vararg) if a.vararg else '',
            sep3=', ' if (0 < len(a.args) or a.vararg) and a.kwarg else '',
            kwargs='**{}'.format(a.kwarg) if a.kwarg else ''
        )

    def visit_NameConstant(self, nc):
        return str(nc.value)

    def visit_Starred(self, st):
        # TODO: Is this correct?
        return '*' + st.value.id


def ast2source(node):
    """Pretty print an AST as a python source string"""
    return SourceFormatter().visit(node)


def source(node):
    """Alias for ast2source"""
    return ast2source(node)


#---------#
# Testing #
#---------#

if __name__ == '__main__':
    tests = [
        (True, 1, '2', '2'),
        (False, 0, '2', '3'),
        (True, 1, 'x', '_a_'),
        (True, 1, '(x, y)', '(_a_, _b_)'),
        (False, 0, '(x, y)', '(_a_, _a_)'),
        (True, 1, '(x, x)', '(_a_, _a_)'),
        (True, 4, 'max(7,3)', '_x_'),
        (True, 1, 'max(7,3)', 'max(7,3)'),
        (False, 0, 'max(7,2)', 'max(7,3)'),
        (True, 1, 'max(7,3,5)', 'max(___args___)'),
        (False, 1, 'min(max(7,3),5)', 'max(___args___)'),
        (True, 2, 'min(max(7,3),5)', '_f_(___args___)'),
        (True, 1, 'min(max(7,3),5)', 'min(max(___maxargs___),___minargs___)'),
        (True, 1, 'max()', 'max(___args___)'),
        (True, 1, 'max(4)', 'max(4,___args___)'),
        (True, 1, 'max(4,5,6)', 'max(4,___args___)'),
        (True, 1, '"hello %s" % x', '_a_str_ % _b_'),
        (False, 0, 'y % x', '_a_str_ % _b_'),
        (False, 0, '7 % x', '_a_str_ % _b_'),
        (True, 1, '3', '_a_int_'),
        (True, 1, '3.4', '_a_float_'),
        (False, 0, '3', '_a_float_'),
        (False, 0, '3.4', '_a_int_'),
        (True, 1, 'True', '_a_bool_'),
        (True, 1, 'False', '_a_bool_'),
        (True, 1, 'None', 'None'),
        # node vard can bind statements or exprs based on context.
        (True, 7, 'print("hello"+str(3))', '_x_'), # 6 => 7 in Python 3
        (True, 1, 'print("hello"+str(3))', 'print(_x_)'),
        (True, 1, 'print(1)', 'print(_x_, ___args___)'),
        (False, 0, 'print(1)', 'print(_x_, _y_, ___args___)'),
        (False, 0, 'print(1, 2)', 'print(_x_)'),
        (True, 1, 'print(1, 2)', 'print(_x_, ___args___)'),
        (True, 1, 'print(1, 2)', 'print(_x_, _y_, ___args___)'),
        (True, 1, 'print(1, 2, 3)', 'print(_x_, ___args___)'),
        (True, 1, 'print(1, 2, 3)', 'print(_x_, _y_, ___args___)'),
        (True, 1,
         '''
def f(x):
    return 17
         ''',
         '''
def f(_a_):
    return _b_
         '''),
        (True, 1,
         '''
def f(x):
    return x
         ''',
         '''
def f(_a_):
    return _b_
         '''),
        (True, 1,
         '''
def f(x):
    return x
         ''',
         '''
def f(_a_):
    return _a_
         '''),
        (False, 0,
         '''
def f(x):
    return 17
         ''',
         '''
def f(_a_):
    return _a_
         '''),
        (True, 1,
         '''
def f(x):
    return 17
         ''',
         '''
def f(_x_):
    return _y_
         '''),
        (True, 1,
         '''
def f(x,y):
    print('hi')
    return x
         ''',
         '''
def f(_x_,_y_):
    print('hi')
    return _x_
         '''),
        (True, 1,
         '''
def f(x,y):
    print('hi')
    return x
         ''',
         '''
def _f_(_x_,_y_):
    print('hi')
    return _x_
         '''),
        (False, 0,
         '''
def f(x,y):
    print('hi')
    return y
         ''',
         '''
def f(_a_,_b_):
    print('hi')
    return _a_
         '''),
        (False, 0, 'x', 'y'),
        (True, 1,
         '''
def f(x,y):
    print('hi')
    return y
         ''',
         '''
def _f_(_x_,_y_):
    ___
    return _y_
         '''),
        (True, 1,
         '''
def f(x,y):
    print('hi')
    print('world')
    print('bye')
    return y
         ''',
         '''
def _f_(_x_,_y_):
    ___stmts___
    return _y_
         '''),
        (False, 0,
         '''
def f(x,y):
    print('hi')
    print('world')
    x = 4
    print('really')
    y = 7
    print('bye')
    return y
         ''',
         '''
def _f_(_x_,_y_):
    ___stmts___
    print(_z_)
    _y_ = _a_int_
    return _y_
         '''),
        (True, 1,
         '''
def f(x,y):
    print('hi')
    print('world')
    x = 4
    print('really')
    y = 7
    print('bye')
    return y
         ''',
         '''
def _f_(_x_,_y_):
    ___stmts___
    print(_z_)
    _y_ = _a_int_
    ___more___
    return _y_
         '''),
        (True, 1,
         '''
def f(x,y):
    print('hi')
    print('world')
    x = 4
    print('really')
    y = 7
    print('bye')
    return y
         ''',
         '''
def _f_(_x_,_y_):
    ___stmts___
    print(_a_)
    _b_ = _c_
    ___more___
    return _d_
         '''),
        (False, 1,
         '''
def f(x,y):
    print('hi')
    print('world')
    x = 4
    print('really')
    y = 7
    print('bye')
    return y
         ''',
         '''
___stmts___
print(_a_)
_b_ = _c_
___more___
return _d_
         '''),
        (True, 1,
         '''
def eyes():
    eye1 = Layer()
    eye2 = Layer()
    face = Layer()
    face.add(eye)
    face.add(eye2)
    return face
         ''',
         '''
def eyes():
    ___
    _face_ = Layer()
    ___
    return _face_
         '''),
        (True, 1,
         '''
def f(x,y):
    """I have a docstring.
    It is a couple lines long."""
    eye = Layer()
    if eye:
        face = Layer()
    else:
        face = Layer()
    eye2 = Layer()
    face.add(eye)
    face.add(eye2)
    return face
         ''',
         '''
def f(___args___):
    eye = Layer()
    ___
         '''),
        (True, 1, '1 == 2', '2 == 1'),
        (True, 1, '1 <= 2', '2 >= 1'),
        (False, 0, '1 <= 2', '2 <= 1'),
        (False, 0, 'f() <= 2', '2 >= f()'),
        # Hmnm, is this the semantics we want for `and`?
        (True, 1, 'a and b and c', 'b and a and c'),
        (True, 1, '(a == b) == (b == c)', '(a == b) == (c == b)'),
        (True, 1, '(a and b) and c', 'a and (b and c)'),
        (True, 1, 'a and b', 'a and b'),
        (True, 1, 'g == "a" or g == "b" or g == "c"',
         '_g_ == _a_ or _g_ == _b_ or _c_ == _g_'),
        (True, 1, '''
x = 1
y = 2
''', '''
x = 1
y = 2
'''),
        (True, 1, '''
x = 1
y = 2
''', '''
___
y = 2
'''),
        (True, 1, '''
x = 1
if (a or b or c):
    return True
else:
    return False
        ''',
         '''
___
if _:
    return _a_bool_
else:
    return _b_bool_
___
         '''),
        (True, 1, '''
if (a or b or c):
    return True
else:
    return False
        ''',
         '''
if _:
    return _a_bool_
else:
    return _b_bool_
         '''),
        (True, 1, '''
x = 1
if (a or b or c):
    return True
else:
    return False
        ''',
         '''
___
if _:
    return _a_bool_
else:
    return _b_bool_
         '''),
        (False, 1, '''
def f():
    if (a or b or c):
        return True
    else:
        return False
        ''',
         '''
___
if _:
    return _a_bool_
else:
    return _b_bool_
___
         '''),
        (False, 1, '''
def isValidGesture(gesture):
    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):
        return True
    else:
        return False
        ''', '''
if _:
    return _a_bool_
else:
    return _b_bool_
        '''),
        (False, 1, '''
def isValidGesture(gesture):
    print('blah')
    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):
        return True
    return False
        ''', '''
___
if _:
    return _a_bool_
return _b_bool_
        '''),

        (False, 1, '''
def isValidGesture(gesture):
    print('blah')
    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):
        return True
    return False
        ''', '''
if _:
    return _a_bool_
return _b_bool_
        '''),
        (False, 1, '''
def isValidGesture(gesture):
    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):
        return True
    return False
        ''', '''
if _:
    return _a_bool_
return _b_bool_
        '''),
        (False, 1, '''
def isValidGesture(gesture):
    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):
        x = True
    x = False
    return x
        ''', '''
if _:
    _x_ = _a_bool_
_x_ = _b_bool_
        '''),
        (True, 1, '''
def isValidGesture(gesture):
    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):
        return True
    return False
        ''', '''
def _(_):
    if _:
        return _a_bool_
    return _b_bool_
        '''),
        (True, 1, 'x, y = f()', '___vars___ = f()'),
        (True, 1, 'x, y = f()', '_vars_ = f()'),
        (True, 1, 'f(a=1, b=2)', 'f(b=2, a=1)'),
        (True, 1, '''
def f(x,y):
    """with a docstring"""
    if level <= 0:
        pass
    else:
        fd(3)
        lt(90)
        ''', '''
def f(_, _):
    ___
    if _:
        ___t___
    else:
        ___e___
    ___s___
'''),
        (True, 1, '''
class A(B):
    def f(self, x):
        pass
        ''', 'class _(_): ___'),
        # (True, True,
        #  'for x, y in f():\n    ___',
        #  'for ___vars___ in f():\n    ___'),
        (False, 0, 'drawLs(size/2, level - 1)', 'drawLs(_size_/2.0, _)'),
        (False, 0, '2', '2.0'),
        (False, 0, '2', '_d_float_'),
        (True, 1, '''
def keepFirstLetter(phrase):
    """Returns a new string that contains only the first occurrence of a
    letter from the original phrase.
    The first letter occurrence can be upper or lower case.
    Non-alpha characters (such as punctuations and space) are left unchanged.
    """
    #this list holds lower-cased versions of all of the letters already used
    usedCharacters = []

    finalPhrase = ""
    for n in phrase:
        if n.isalpha():
            #we need to create a temporary lower-cased version of the letter,
            #so that we can check and see if we've seen an upper or lower-cased
            #version of this letter before
            tempN = n.lower()
            if tempN not in usedCharacters:
                usedCharacters.append(tempN)
                #but we need to add the original n, so that we can preserve
                #if it was upper cased or not
                finalPhrase = finalPhrase + n

        #this adds all non-letter characters into the final phrase list
        else:
            finalPhrase = finalPhrase + n

    return finalPhrase
        ''', '''
def _(___):
    ___
    _acc_ = ""
    ___
    for _ in _:
        ___
    return _acc_
    ___
        '''),
        (False, # Pattern should not match program
         1, # Pattern should be found within program
         # Program
         '''
def keepFirstLetter(phrase):
    #this list holds lower-cased versions of all of the letters already used
    usedCharacters = []

    finalPhrase = ""
    for n in phrase:
        if n.isalpha():
            #we need to create a temporary lower-cased version of the letter,
            #so that we can check and see if we've seen an upper or lower-cased
            #version of this letter before
            tempN = n.lower()
            if tempN not in usedCharacters:
                usedCharacters.append(tempN)
                #but we need to add the original n, so that we can preserve
                #if it was upper cased or not
                finalPhrase = finalPhrase + n

        #this adds all non-letter characters into the final phrase list
        else:
            finalPhrase = finalPhrase + n

    return finalPhrase
        ''',
         # Pattern
         '''
___prefix___
_acc_ = ""
___middle___
for _ in _:
    ___
return _acc_
___suffix___
        '''),
        (True, 1, '''
a = 1
b = 2
c = 3
        ''', '''___; _x_ = _n_'''),
        (False, # Pattern should not match program
         1, # Pattern should be found within program
         # Program
         '''
def f(a):
    x = ""
    return x
        ''',
         # Pattern
         '''
_acc_ = ""
return _acc_
        '''),

        # Treatment of elses:
        (True, 1, 'if x: print(1)', 'if _: _'),
        (False, 0, 'if x: print(1)\nelse: pass', 'if _: _'),
        (True, 1, 'if x: print(1)\nelse: pass', 'if _: _\nelse: ___'),
        (False, 0, 'if x: print(1)', '''
if _: _
else:
    _
    ___
'''),
        (True, 1, 'if x: print(1)\nelse: pass', '''
if _: _
else:
    _
    ___
'''),

        # If ExpandExplicitElsePattern is used:
        # (False, 0, 'if x: print(1)', 'if _: _\nelse: ___'),

        # If ExpandExplicitElsePattern is NOT used:
        (True, 1, 'if x: print(1)', 'if _: _\nelse: ___'),

        # Keyword arguments
        (True, 1, 'f(a=1)', 'f(a=1)'),
        (True, 1, 'f(a=1)', 'f(_kw_=1)'),
        (True, 1, 'f(a=1)', 'f(_kw_=_arg_)'),
        (True, 1, 'f(a=1)', 'f(_=1)'),
        (True, 1, 'f(a=1)', 'f(_=_arg_)'),
        (True, 1, 'f(a=1, b=2)', 'f(_x_=_, _y_=_)'),
        (True, 1, 'f(a=1, b=2)', 'f(_x_=2, _y_=_)'),
        (False, 0, 'f(a=1, b=2)', 'f(_x_=_)'),
        (False, 0, 'f(a=1, b=2)', 'f(_x_=_, _y_=_, _z_=_)'),
        (False, 0, 'f(a=1, b=2)', 'f(_x_=2, _y_=2)'),
        (True, 1, 'f(a=1, b=2)', 'f(_x_=_, b=_)'),
        (True, 1, 'f(a=1, b=2)', 'f(b=_, _x_=_)'),
        (True, 1, 'f(a=1+1, b=1+1)', 'f(_c_=_x_+_x_, _d_=_y_+_y_)'),
        (True, 1, 'f(a=1+1, b=2+2)', 'f(_c_=_x_+_x_, _d_=_y_+_y_)'),
        (True, 1, 'f(a=1+2, b=2+1)', 'f(_c_=_x_+_y_, _d_=_y_+_x_)'),
        (True, 1, 'f(a=1+1, b=1+1)', 'f(_c_=_x_+_x_, _d_=_x_+_x_)'),
        (False, 0, 'f(a=1+1, b=2+2)', 'f(_c_=_x_+_x_, _d_=_x_+_x_)'),
        (True, 1, 'f(a=1, b=2)', 'f(___=_)'),
        (True, 1, 'f(a=1, b=2)', 'f(___kwargs___=_)'),
        (True, 1, 'f(a=1, b=2)', 'f(___kwargs___=_, b=_)'),
        (True, 1, 'f(a=1, b=2)', 'f(b=_, ___kwargs___=_)'),
        (True, 1, 'f(a=1, b=2)', 'f(___kwargs___=_, a=_, b=_)'),
        (True, 1, 'f(a=1, b=2)', 'f(a=_, b=_, ___kwargs___=_)'),
        (True, 1, 'f(a=1, b=2)', 'f(___kwargs___=_, b=_, a=_)'),
        (True, 1, 'f(a=1, b=2)', 'f(b=_, a=_, ___kwargs___=_)'),
        (True, 1, 'f(a=1, b=2)', 'f(a=_, ___kwargs___=_, b=_)'),
        (True, 1, 'f(a=1, b=2)', 'f(b=_, ___kwargs___=_, a=_)'),
        (True, 1, 'b = 7; f(a=1, b=2)', '_x_ = _; f(_x_=_, _y_=_)'),
        (False, 0, 'b = 7; f(a=1, b=2)', '_x_ = _; f(_x_=1, _y_=_)'),

        # and/or set wildcards
        (True, 1, 'x or y or z', '_x_ or ___rest___'),
        (True, 1, 'x or y or z', '_x_ or _y_ or ___rest___'),
        (True, 1, 'x or y or z', '_x_ or _y_ or _z_ or ___rest___'),

        # kwarg matching
        (True, 1, 'def f(x=3):\n  return x', 'def _f_(x=3):\n  return x'),
        (True, 1, 'def f(x=3):\n  return x', 'def _f_(_=3):\n  return _'),
        (True, 1, 'def f(x=3):\n  return x', 'def _f_(_=3):\n  ___'),
        (True, 1, 'def f(x=3):\n  return x', 'def _f_(_x_=3):\n  return _x_'),
        (True, 1,
         'def f(y=7):\n  return y', 'def _f_(_x_=_y_):\n  return _x_'),
        (False, 0, 'def f(x=3):\n  return x', 'def _f_(_y_=7):\n  return _x_'),

        # Succeeds!
        (True, 1, 'def f(x=12):\n  return x', 'def _f_(_=_):\n  ___'),

        # TODO: Fails because we compare all defaults as one block
        # Zero extra keyword arguments:
        (True, 1, 'def f(x=17):\n  return x', 'def _f_(_=17, ___=_):\n  ___'),

        # Should match because ___ has no default
        (True, 1, 'def f(x=17):\n  return x', 'def _f_(___, _=17):\n  ___'),

        # Multiple kwargs
        (True, 1, 'def f(x=3, y=4):\n  return x', 'def _f_(_=3, _=4):\n  ___'),
        (True, 1, 'def f(x=5, y=6):\n  return x', 'def _f_(_=_, _=_):\n  ___'),
        # ___ doesn't match kwargs
        (False, 0, 'def f(x=7, y=8):\n  return x', 'def _f_(___):\n  ___'),
        # TODO: Fails because of default matching bug
        (True, 1, 'def f(x=9, y=10):\n  return x', 'def _f_(___=_):\n  ___'),

        # Exact matching of kwarg expressions
        (True, 1, 'def f(x=y+3):\n  return x', 'def _f_(_=y+3):\n  ___'),

        # Matching of kw-only args
        (True, 1,
         'def f(*a, x=5):\n  return x',
         'def _f_(*_, _x_=5):\n  return _x_'),
        # ___ does not match *_
        (False, 0,
         'def f(*a, x=6):\n  return x',
         'def _f_(___, _x_=6):\n  return _x_'),

        # Multiple kw-only args
        (True, 1,
         'def f(*a, x=5, y=6):\n  return x, y',
         'def _f_(*_, _x_=5, _y_=6):\n  return _x_, _y_'),
        (False, 0,
         'def f(*a, x=7, y=8):\n  return x, y',
         'def _f_(___, _x_=7, _y_=8):\n  return _x_, _y_'),

        # Function with docstring (must use ast.get_docstring!)
        (False, 0, 'def f():\n  """docstring"""', 'def _f_(___):\n  _a_str_'),

        # Function with docstring (using ast.get_docstring)
        (True, 1,
         'def f(x):\n  """doc1"""\n  return x',
         'def _f_(___):\n  ___',
         lambda node, env: ast.get_docstring(node) is not None),

        # Function without docstring (using ast.get_docstring)
        (False, 0,
         'def f(x):\n  """doc2"""\n  return x',
         'def _f_(___):\n  ___',
         lambda node, env:(
             ast.get_docstring(node) is None
          or ast.get_docstring(node).strip() == ''
         )),
        (True, 1,
         'def f(x):\n  """"""\n  return x',
         'def _f_(___):\n  ___',
         lambda node, env:(
             ast.get_docstring(node) is None
          or ast.get_docstring(node).strip() == ''
         )),
        (True, 1,
         'def nodoc(x):\n  return x',
         'def _f_(___):\n  ___',
         lambda node, env:(
             ast.get_docstring(node) is None
          or ast.get_docstring(node).strip() == ''
         )),

        # TODO: Recursive matching of kwarg expressions
        (True, 1, 'def f(x=y+3):\n  return x', 'def _f_(_=_+3):\n  ___'),

        # Function with multiple normal arguments
        (True, 1, 'def f(x, y, z):\n  return x', 'def _f_(___):\n  ___'),

        # Matching redundant elif conditions
        (
          True,
          1,
          'if x == 3:\n  return x\nelif not x == 3 and x > 5:\n  return x-2',
          'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___'
        ),
        ( # order matters
          False,
          0,
          'if x == 3:\n  return x\nelif x > 5 and not x == 3:\n  return x-2',
          'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___'
        ),
        ( # not == is not the same as !=
          False,
          0,
          'if x == 3:\n  return x\nelif x > 5 and x != 3:\n  return x-2',
          'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___'
        ),
        ( # not == is not the same as !=
          True,
          1,
          'if x == 3:\n  return x\nelif x > 5 and not x == 3:\n  return x-2',
          'if _cond_:\n  ___\nelif ___ and not _cond_:\n  ___'
        ),
        ( # not == is not the same as !=
          True,
          1,
          'if x == 3:\n  return x\nelif x > 5 and x != 3:\n  return x-2',
          'if _n_ == _v_:\n  ___\nelif ___ and _n_ != _v_:\n  ___'
        ),
        ( # extra conditions do matter!
          False,
          0,
          'if x == 3:\n  return x\nelif not x == 3 and x > 5:\n  return x-2\n'
        + 'elif not x == 3 and x <= 5 and x < 0:\n  return 0',
          'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___'
        ),
        ( # match extra conditions:
          True,
          1,
          'if x == 3:\n  return x\nelif not x == 3 and x > 5:\n  return x-2\n'
        + 'elif not x == 3 and x <= 5 and x < 0:\n  return 0',
          'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___\nelif _:\n  ___'
        ),
        ( # number of conditions must match exactly:
          False,
          0,
          'if x == 3:\n  return x\nelif not x == 3 and x > 5:\n  return x-2\n'
        + 'elif not x == 3 and x <= 5 and x < 0:\n  return 0\n'
        + 'elif not x == 3 and x <= 5 and x >= 0 and x == 1:\n  return 1.5',
          'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___\nelif _:\n  ___'
        ),
        ( # matching with elif:
          True,
          2,
          'if x < 0:\n  x += 1\nelif x < 10:\n  x += 0.5\nelse:\n  x += 0.25',
          'if _:\n  ___\nelse:\n  ___'
        ),
        ( # left/right branches are both okay
          True,
          1,
          'x == 3',
          '3 == x',
        ),
        ( # order does matter for some operators
         False,
         0,
         '1 + 2 + 3',
         '3 + 2 + 1'
        ),
        ( # but not for others
         True,
         1,
         '1 and 2 and 3',
         '3 and 2 and 1'
        ),
    ]
    testNum = 1
    passes = 0
    fails = 0
    #for (expect_match, expect_count, ns, ps) in tests:
    for test_spec in tests:
        if len(test_spec) == 4:
            expect_match, expect_count, ns, ps = test_spec
            matchpred = predtrue
        elif len(test_spec) == 5:
            expect_match, expect_count, ns, ps, matchpred = test_spec
        else:
            print("Tests must have 4 or 5 parts!")
            print(test_spec)
            exit(1)

        print('$' + '-' * 60)
        print('Test #{}'.format(testNum))
        testNum += 1
        n = parse(ns)
        n = (
            n.body[0].value
            if type(n.body[0]) == ast.Expr and len(n.body) == 1
            else (
                n.body[0]
                if len(n.body) == 1
                else n.body
            )
        )
        p = parse_pattern(ps)
        print('Program: %s => %s' % (ns, dump(n)))
        if isinstance(ns, ast.FunctionDef):
            print('Docstring: %s' % (ast.get_docstring(ns)))
        print('Pattern: %s => %s' % (ps, dump(p)))
        if matchpred != predtrue:
            print('Matchpred: {}'.format(matchpred.__name__))
        for gen in [False, True]:
            result = match(n, p, gen=gen, matchpred=matchpred)
            if gen:
                result = takeone(result)
                pass
            passed = bool(result) == expect_match
            if passed:
                passes += 1
            else:
                fails += 1
                pass
            print('match(gen=%s): %s  [%s]' % (
                gen, bool(result), "PASS" if passed else "FAIL"
            ))
            # if result:
            #     for (k,v) in result.value.items():
            #         print("  %s = %s" % (k, dump(v)))
            #         pass
            #     pass
            # pass
        opt = find(n, p, matchpred=matchpred)
        findpassed = bool(opt) == (0 < expect_count)
        if findpassed:
            passes += 1
        else:
            fails += 1
            pass
        print(
            'find: {}  [{}]'.format(
                bool(opt),
                # dump(opt.value[0]) if opt else None,
                "PASS" if findpassed else "FAIL"
            )
        )
        # if opt:
        #     for (k,v) in opt.value[1].items():
        #         print("  %s = %s" % (k, dump(v)))
        #         pass
        c = count(n, p, matchpred=matchpred)
        if c == expect_count:
            passes += 1
            print('count: %s  [PASS]' % c)
        else:
            fails += 1
            print('count: %s  [FAIL], expected %d' % (c, expect_count))
            pass
        print('findall:')
        nmatches = 0
        for (node, envs) in findall(n, p, matchpred=matchpred):
            print("  %d.  %s" % (nmatches, dump(node)))
            for (i, env) in enumerate(envs):
                print("      %s.  " % chr(ord('a') + i))
                for (k, v) in env.items():
                    print("          %s = %s" % (k, dump(v)))
                    pass
                pass
            # find should return first findall result.
            # assert 0 < nmatches or (opt and opt.value == (node, bindings))
            nmatches += 1
            pass
        # count should count the same number of matches that findall finds.
        assert nmatches == c
        print()
        pass
    print("%d passed, %d failed" % (passes, fails))

    with open(__file__) as src:
        with open('self_printed_' + os.path.basename(__file__), 'w') as dest:
            dest.write(source(ast.parse(src.read())))
