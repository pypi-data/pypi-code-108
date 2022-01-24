'\nMast: Matcher of ASTs for Python\nCopyright (c) 2017-2018, Benjamin P. Wood, Wellesley College\n\nmast.py\n\nThis version is included in potluck instead of codder.\n\nSee NOTE below for how to run this file as a script.\n\nUses the builtin ast package for parsing of concrete syntax and\nrepresentation of abstract syntax for both source code and patterns.\n\nThe main API for pattern matching with mast:\n\n- `parse`: parse an AST from a python source string\n- `parse_file`: parse an AST from a python source file\n- `parse_pattern`: parse a pattern from a pattern source string\n- `match`: check if an AST matches a pattern\n- `find`: search for the first (improper) sub-AST matching a pattern\n- `findall`: search for all (improper) sub-ASTs matching a pattern\n- `count`: count all (improper) sub-ASTs matching a pattern\n\nAPI utility functions applicable to all ASTs in ast:\n\n- `dump`: a nicer version of ast.dump AST structure pretty-printing\n- `ast2source`: source: pretty-print an AST to python source\n\nNOTE: To run this file as a script, go up one directory and execute\n\n```sh\npython -m potluck.mast\n```\n\nFor example, if this file is ~/Sites/potluck/potluck/mast.py, then\n\n```sh\ncd ~/Sites/potluck\npython -m potluck.mast\n```\n\nBecause of relative imports, you *cannot* attempt to run this file\nas a script in ~/Sites/potluck/potluck. Here\'s what will happen:\n\n```sh\n$ cd ~/Sites/potluck/potluck\n$ python mast.py\nTraceback (most recent call last):\nFile "mast.py", line 40, in <module>\n  from .util import (...\nSystemError: Parent module \'\' not loaded, cannot perform relative import\n```\n\nThis StackOverflow post is helpful for understanding this issue:\nhttps://stackoverflow.com/questions/14132789/relative-imports-for-the-billionth-time\n\nSOME HISTORY\n[2019/01/19-23, lyn] Python 2 to 3 conversion plus debugging aids\n[2021/06/22ish, Peter Mawhorter] Linting pass; import into potluck\n\nTODO:\n\n* have flag to control debugging prints (look for $)\n\nDocumentation of the Python ast package:\n\n- Python 2: https://docs.python.org/2/library/ast.html\n- Python 3:\n    - https://docs.python.org/3/library/ast.html\n    - https://greentreesnakes.readthedocs.io/en/latest/\n'
import ast
import os
import re
import sys
from collections import OrderedDict as odict
from .mast_utils import Some, takeone, FiniteIterator, iterone, iterempty, dict_unbind
import itertools
ichain = itertools.chain.from_iterable
def dump(node):
    'Nicer display of ASTs.'
    return (ast.dump(node, ) if isinstance(node, ast.AST, ) else ((('[') + (', '.join(map(dump, node, ), ))) + (']') if (type(node, )) == (list) else ((('(') + (', '.join(map(dump, node, ), ))) + (')') if (type(node, )) == (tuple) else ((('{') + (', '.join((((dump(key, )) + (': ')) + (dump(value, )) for (key, value) in node.items()), ))) + ('}') if (type(node, )) == (dict) else (node.dump(dump, ) if ((type(node, )) == (Some)) or ((type(node, )) == (FiniteIterator)) else repr(node, ))))))

def showret(x, prefix=''):
    'Shim for use debugging AST return values.'
    print(prefix, dump(x, ), )
    return x

NODE_VAR_SPEC = (1, re.compile('\\A_(?:([a-zA-Z0-9]+)_)?\\Z', ))
'Spec for names of scalar pattern variables.'
SEQ_TYPES = set([ast.arguments, ast.Assign, ast.Call, ast.Expr, ast.Tuple, ast.List, list, type(None, ), ast.BoolOp], )
'Types against which sequence patterns match.'
SET_VAR_SPEC = (1, re.compile('\\A___(?:([a-zA-Z0-9]+)___)?\\Z', ))
'Spec for names of sequence pattern variables.'
if ((sys.version_info[0]) < (3)) or ((sys.version_info[1]) < (8)):
    LIT_TYPES = { 'int': (lambda x: (Some(x.n, ) if ((type(x, )) == (ast.Num)) and ((type(x.n, )) == (int)) else None)), 'float': (lambda x: (Some(x.n, ) if ((type(x, )) == (ast.Num)) and ((type(x.n, )) == (float)) else None)), 'str': (lambda x: (Some(x.s, ) if (type(x, )) == (ast.Str) else None)), 'bool': (lambda x: (Some(x.value, ) if ((type(x, )) == (ast.NameConstant)) and (((x.value) is (True)) or ((x.value) is (False))) else None)) }
    'Types against which typed literal pattern variables match.'
else:
    LIT_TYPES = { 'int': (lambda x: (Some(x.value, ) if ((type(x, )) == (ast.Constant)) and ((type(x.value, )) == (int)) else None)), 'float': (lambda x: (Some(x.value, ) if ((type(x, )) == (ast.Constant)) and ((type(x.value, )) == (float)) else None)), 'str': (lambda x: (Some(x.value, ) if ((type(x, )) == (ast.Constant)) and ((type(x.value, )) == (str)) else None)), 'bool': (lambda x: (Some(x.value, ) if ((type(x, )) == (ast.Constant)) and (((x.value) is (True)) or ((x.value) is (False))) else None)) }
    'Types against which typed literal pattern variables match.'
TYPED_LIT_VAR_SPEC = ((1, 2), re.compile((('\\A_([a-zA-Z0-9]+)_(') + ('|'.join(LIT_TYPES.keys(), ))) + (')_\\Z'), ))
'Spec for names/types of typed literal pattern variables.'
def var_is_anonymous(identifier):
    'Determine whether a pattern variable name (string) is anonymous.'
    assert (type(identifier, )) == (str)
    return not (re.search('[a-zA-Z0-9]', identifier, ))

def node_is_name(node):
    'Determine if a node is an AST Name node.'
    return isinstance(node, ast.Name, )

def identifier_key(identifier, spec):
    "Extract the name of a pattern variable from its identifier string,\n    returning an option: Some(key) if identifier is valid variable\n    name according to spec, otherwise None.\n\n    Examples for NODE_VAR_SPEC:\n    identifier_key('_a_') => Some('a')\n    identifier_key('_') => Some('_')\n    identifier_key('_a') => None\n\n    "
    assert (type(identifier, )) == (str)
    (groups, regex) = spec
    match = regex.match(identifier, )
    if match:
        if var_is_anonymous(identifier, ):
            return identifier
        else:
            if (type(groups, )) == (tuple):
                return tuple((match.group(i, ) for i in groups), )
            else:
                return match.group(groups, )
    else:
        return None

def node_var(pat, spec=NODE_VAR_SPEC, wrap=False):
    'Extract the key name of a scalar pattern variable,\n    returning Some(key) if pat is a scalar pattern variable,\n    otherwise None.\n\n    A named or anonymous node variable pattern, written `_a_` or `_`,\n    respectively, may appear in any expression or identifier context\n    in a pattern.  It matches any single AST in the corresponding\n    position in the target program.\n\n    '
    if wrap:
        pat = ast.Name(id=pat, ctx=None)
    else:
        if isinstance(pat, ast.Expr, ):
            pat = pat.value
        else:
            if (isinstance(pat, ast.alias, )) and ((pat.asname) is (None)):
                pat = ast.Name(id=pat.name, ctx=None)
    return (identifier_key(pat.id, spec, ) if node_is_name(pat, ) else None)

def node_var_str(pat, spec=NODE_VAR_SPEC):
    return node_var(pat, spec=spec, wrap=True)

def set_var(pat, wrap=False):
    'Extract the key name of a set or sequence pattern variable,\n    returning Some(key) if pat is a set or sequence pattern variable,\n    otherwise None.\n\n    A named or anonymous set or sequence pattern variable, written\n    `___a___` or `___`, respectively, may appear as an element of a\n    set or sequence context in a pattern.  It matches 0 or more nodes\n    in the corresponding context in the target program.\n\n    '
    return node_var(pat, spec=SET_VAR_SPEC, wrap=wrap)

def set_var_str(pat):
    return set_var(pat, wrap=True)

def typed_lit_var(pat):
    'Extract the key name of a typed literal pattern variable,\n    returning Some(key) if pat is a typed literal pattern variable,\n    otherwise None.\n\n    A typed literal variable pattern, written `_a_type_`, may appear\n    in any expression context in a pattern.  It matches any single AST\n    node for a literal of the given primitive type in the\n    corresponding position in the target program.\n\n    '
    return node_var(pat, spec=TYPED_LIT_VAR_SPEC)

def is_pat(p):
    'Determine if p could be a pattern (by type).'
    return (isinstance(p, ast.AST, )) or ((type(p, )) == (str))

def node_is_docstring(node):
    'Is this node a docstring node?'
    return (isinstance(node, ast.Expr, )) and (isinstance(node.value, ast.Str, ))

def node_is_bindable(node):
    'Can a node pattern variable bind to this node?'
    result = (isinstance(node, ast.expr, )) or (isinstance(node, ast.stmt, )) or ((isinstance(node, ast.alias, )) and ((node.asname) is (None)))
    return result

def node_is_lit(node, ty):
    'Is this node a literal primitive node?'
    return ((isinstance(node, ast.Num, )) and ((ty) == (type(node.n, )))) or ((isinstance(node, ast.Str, )) and ((ty) == (str))) or ((isinstance(node, ast.Name, )) and ((ty) == (bool)) and (((node.id) == ('True')) or ((node.id) == ('False'))))

def expr_has_type(node, ty):
    'Is this expr statically guaranteed to be of this type?\n\n    Literals and conversions have definite types.  All other types are\n    conservatively statically unknown.\n\n    '
    return (node_is_lit(node, ty, )) or (match(node, '{}(_)'.format(ty.__name__, ), ))

def node_line(node):
    'Bet the line number of the source line on which this node starts.\n    (best effort)'
    try:
        return (node.lineno if (type(node, )) != (list) else node[0].lineno)
    except Exception:
        return None

class PatternSyntaxError(BaseException):
    'Exception for errors in pattern syntax.'
    def __init__(self, node, message):
        BaseException.__init__(self, 'At pattern line {}: {}'.format(node_line(node, ), message, ), )


class PatternValidator(ast.NodeVisitor):
    'AST visitor: check pattern structure.'
    def __init__(self):
        self.parent = None
        pass

    def generic_visit(self, pat):
        oldparent = self.parent
        self.parent = pat
        try:
            return ast.NodeVisitor.generic_visit(self, pat, )
        finally:
            self.parent = oldparent
            pass
        pass

    def visit_Name(self, pat):
        sn = set_var(pat, )
        if sn:
            if (type(self.parent, )) not in (SEQ_TYPES):
                raise PatternSyntaxError(pat, 'Set/sequence variable ({}) not allowed in {} node'.format(sn, type(self.parent, ), ), )
            pass
        pass

    def visit_arg(self, pat):
        '[2019/01/22, lyn] Python 3 now has arg object for param (not Name object).\n           So copied visit_Name here.'
        sn = set_var(pat, )
        if sn:
            if (type(self.parent, )) not in (SEQ_TYPES):
                raise PatternSyntaxError(pat, 'Set/sequence variable ({}) not allowed in {} node'.format(sn.value, type(self.parent, ), ), )
            pass
        pass

    def visit_Call(self, c):
        if (1) < (sum((1 for kw in c.keywords if set_var_str(kw.arg, )), )):
            raise PatternSyntaxError(c.keywords, 'Calls may use at most one keyword argument set variable.', )
        return self.generic_visit(c, )

    def visit_keyword(self, k):
        if (identifier_key(k.arg, SET_VAR_SPEC, )) and (not ((node_is_name(k.value, )) and (var_is_anonymous(k.value.id, )))):
            raise PatternSyntaxError(k.value, 'Value patterns for keyword argument set variables must be _.', )
        return self.generic_visit(k, )

    pass

class RemoveDocstrings(ast.NodeTransformer):
    'AST Transformer: remove all docstring nodes.'
    def filterDocstrings(self, seq):
        filt = [self.visit(n, ) for n in seq if not (node_is_docstring(n, ))]
        return filt

    def visit_Expr(self, node):
        if isinstance(node.value, ast.Str, ):
            assert False
        else:
            return self.generic_visit(node, )

    def visit_FunctionDef(self, node):
        return ast.copy_location(ast.FunctionDef(name=node.name, args=self.generic_visit(node.args, ), body=self.filterDocstrings(node.body, )), node, )

    def visit_Module(self, node):
        return ast.copy_location(ast.Module(body=self.filterDocstrings(node.body, )), node, )

    def visit_For(self, node):
        return ast.copy_location(ast.For(body=self.filterDocstrings(node.body, ), target=node.target, iter=node.iter, orelse=self.filterDocstrings(node.orelse, )), node, )

    def visit_While(self, node):
        return ast.copy_location(ast.While(body=self.filterDocstrings(node.body, ), test=node.test, orelse=self.filterDocstrings(node.orelse, )), node, )

    def visit_If(self, node):
        return ast.copy_location(ast.If(body=self.filterDocstrings(node.body, ), test=node.test, orelse=self.filterDocstrings(node.orelse, )), node, )

    def visit_With(self, node):
        return ast.copy_location(ast.With(body=self.filterDocstrings(node.body, ), items=node.items), node, )

    def visit_Try(self, node):
        return ast.copy_location(ast.Try(body=self.filterDocstrings(node.body, ), handlers=self.filterDocstrings(node.handlers, ), orelse=self.filterDocstrings(node.orelse, ), finalbody=self.filterDocstrings(node.finalbody, )), node, )

    def visit_ClassDef(self, node):
        return ast.copy_location(ast.ClassDef(body=self.filterDocstrings(node.body, ), name=node.name, bases=node.bases, decorator_list=node.decorator_list), node, )


class FlattenBoolOps(ast.NodeTransformer):
    'AST transformer: flatten nested boolean expressions.'
    def visit_BoolOp(self, node):
        values = []
        for v in node.values:
            if (isinstance(v, ast.BoolOp, )) and ((v.op) == (node.op)):
                values += v.values
            else:
                values.append(v, )
                pass
            pass
        return ast.copy_location(ast.BoolOp(op=node.op, values=values), node, )

    pass

class ContainsCall(Exception):
    'Exception raised when prohibiting call expressions.'
    pass

class ProhibitCall(ast.NodeVisitor):
    'AST visitor: check call-freedom.'
    def visit_Call(self, c):
        raise ContainsCall

    pass

class SetLoadContexts(ast.NodeTransformer):
    '\n    Transforms any AugStore contexts into Load contexts, for use with\n    DesugarAugAssign.\n    '
    def visit_AugStore(self, ctx):
        return ast.copy_location(ast.Load(), ctx, )


class DesugarAugAssign(ast.NodeTransformer):
    'AST transformer: desugar augmented assignments (e.g., `+=`)\n    when simple desugaring does not duplicate effectful expressions.\n\n    FIXME: this desugaring and others cause surprising match\n    counts. See: https://github.com/wellesleycs111/codder/issues/31\n\n    FIXME: This desugaring should probably not happen in cases where\n    .__iadd__ and .__add__ yield different results, for example with\n    lists where .__iadd__ is really extend while .__add__ creates a new\n    list, such that\n\n        [1, 2] + "34"\n\n    is an error, but\n\n        x = [1, 2]\n        x += "34"\n\n    is not!\n\n    A better approach might be to avoid desugaring entirely and instead\n    provide common collections of match rules for common patterns.\n\n    '
    def visit_AugAssign(self, assign):
        try:
            ProhibitCall().visit(assign.target, )
            return ast.copy_location(ast.Assign(targets=[self.visit(assign.target, )], value=ast.copy_location(ast.BinOp(left=SetLoadContexts().visit(assign.target, ), op=self.visit(assign.op, ), right=self.visit(assign.value, )), assign, )), assign, )
        except ContainsCall:
            return self.generic_visit(assign, )

    def visit_AugStore(self, ctx):
        return ast.copy_location(ast.Store(), ctx, )

    def visit_AugLoad(self, ctx):
        return ast.copy_location(ast.Load(), ctx, )


class ExpandExplicitElsePattern(ast.NodeTransformer):
    'AST transformer: transform patterns that in include `else: ___`\n    to use `else: _; ___` instead, forcing the else to have at least\n    one statement.'
    def visit_If(self, ifelse):
        if ((1) == (len(ifelse.orelse, ))) and (set_var(ifelse.orelse[0], )):
            return ast.copy_location(ast.If(test=ifelse.test, body=ifelse.body, orelse=[ast.copy_location(ast.Expr(value=ast.Name(id='_', ctx=None)), ifelse.orelse[0], ), ifelse.orelse[0]]), ifelse, )
        else:
            return self.generic_visit(ifelse, )


def pipe_visit(node, visitors):
    'Send an AST through a pipeline of AST visitors/transformers.'
    if (0) == (len(visitors, )):
        return node
    else:
        v = visitors[0]
        if isinstance(v, ast.NodeTransformer, ):
            return pipe_visit(v.visit(node, ), visitors[1:], )
        else:
            v.visit(node, )
            return pipe_visit(node, visitors[1:], )

def parse_file(path, docstrings=True):
    'Load and parse a program AST from the given path.'
    with open(path, )as f:
        return parse(f.read(), filename=path, docstrings=docstrings)
    pass

STANDARD_PASSES = [RemoveDocstrings, FlattenBoolOps]
'Thunks for AST visitors/transformers that are applied during parsing.'
DOCSTRING_PASSES = [FlattenBoolOps]
'Extra thunks for docstring mode?'
class MastParseError(Exception):
    def __init__(self, pattern, error):
        super(MastParseError, self, ).__init__('Error parsing pattern source string <<<\n{}\n>>>\n{}'.format(pattern, str(error, ), ), )
        self.trigger = error
        pass

    pass

def parse(string, docstrings=True, filename='<unknown>', passes=STANDARD_PASSES):
    'Parse an AST from a string.'
    if (type(string, )) == (str):
        string = str(string, )
    assert (type(string, )) == (str)
    if (docstrings) and ((RemoveDocstrings) in (passes)):
        passes.remove(RemoveDocstrings, )
    pipe = [thunk() for thunk in passes]
    try:
        parsed_ast = ast.parse(string, filename=filename)
    except Exception as error:
        raise MastParseError(string, error, )
    return pipe_visit(parsed_ast, pipe, )

PATTERN_PARSE_CACHE = {  }
'a pattern parsing cache'
PATTERN_PASSES = (STANDARD_PASSES) + ([])
def parse_pattern(pat, toplevel=False, docstrings=True):
    'Parse and validate a pattern.'
    if isinstance(pat, ast.AST, ):
        PatternValidator().visit(pat, )
        return pat
    else:
        if (type(pat, )) == (list):
            iter((lambda x: PatternValidator().visit(x, )), pat, )
            return pat
        else:
            if (type(pat, )) == (str):
                cache_key = (toplevel, docstrings, pat)
                pat_ast = PATTERN_PARSE_CACHE.get(cache_key, )
                if not (pat_ast):
                    pat_ast = parse(pat, filename='<pattern>', passes=PATTERN_PASSES)
                    PatternValidator().visit(pat_ast, )
                    if not (toplevel):
                        if (len(pat_ast.body, )) == (1):
                            b = pat_ast.body[0]
                            pat_ast = (b.value if isinstance(b, ast.Expr, ) else b)
                            pass
                        else:
                            pat_ast = pat_ast.body
                            pass
                        pass
                    PATTERN_PARSE_CACHE[cache_key] = pat_ast
                    pass
                return pat_ast
            else:
                assert False, 'Cannot parse pattern of type {}: {}'.format(type(pat, ), dump(pat, ), )

def pat(pat, toplevel=False, docstrings=True):
    'Alias for parse_pattern.'
    return parse_pattern(pat, toplevel, docstrings, )

ASSOCIATIVE_OPS = list(map(type, [ast.Add(), ast.Mult(), ast.BitOr(), ast.BitXor(), ast.BitAnd(), ast.Eq(), ast.NotEq(), ast.Is(), ast.IsNot()], ), )
'Types of AST operation nodes that are associative.'
def op_is_assoc(op):
    'Determine if the given operation node is associative.'
    return (type(op, )) in (ASSOCIATIVE_OPS)

MIRRORING = [(ast.Lt(), ast.Gt()), (ast.LtE(), ast.GtE()), (ast.Eq(), ast.Eq()), (ast.NotEq(), ast.NotEq()), (ast.Is(), ast.Is()), (ast.IsNot(), ast.IsNot())]
'Pairs of operations that are mirrors of each other.'
def mirror(op):
    'Return the mirror operation of the given operation if any.'
    for (x, y) in MIRRORING:
        if (type(x, )) == (type(op, )):
            return y
        else:
            if (type(y, )) == (type(op, )):
                return x
        pass
    return None

def op_has_mirror(op):
    'Determine if the given operation has a mirror.'
    return bool(mirror, )

FUNCALL = parse_pattern('_(___)', )
METHODCALL = parse_pattern('_._(___)', )
ASSIGN = parse_pattern('_ = _', )
DEL = parse_pattern('del _', )
PRINT = parse_pattern('print(___)', )
IMPURE2 = [METHODCALL, ASSIGN, DEL, PRINT]
PUREFUNS = set(['len', 'round', 'int', 'str', 'float', 'list', 'tuple', 'map', 'filter', 'reduce', 'iter', 'all', 'any'], )
class PermuteBoolOps(ast.NodeTransformer):
    'AST transformer: permute topmost boolean operation\n    according to the given index order.'
    def __init__(self, indices):
        self.indices = indices

    def visit_BoolOp(self, node):
        if self.indices:
            values = [self.generic_visit(node.values[i], ) for i in self.indices]
            self.indices = None
            return ast.copy_location(ast.BoolOp(op=node.op, values=values), node, )
        else:
            return self.generic_visit(node, )


def node_is_pure(node, purefuns=[]):
    'Determine if the given node is (conservatively pure (effect-free).'
    return ((count(node, FUNCALL, matchpred=(lambda x, env: ((x.func) not in (PUREFUNS)) and ((x.func) not in (purefuns))))) == (0)) and (all(((count(node, pat, )) == (0) for pat in IMPURE2), ))

def permutations(node):
    '\n    Generate all permutations of the binary and boolean operations, as\n    well as of import orderings, in and below node, via associativity and\n    mirroring, respecting purity. Because this is heavily exponential,\n    limiting the number of imported names and the complexity of binary\n    operation trees in your patterns is a good thing.\n    '
    if isinstance(node, ast.Import, ):
        for perm in list_permutations(node.names, ):
            yield ast.Import(names=perm)
    else:
        if isinstance(node, ast.ImportFrom, ):
            for perm in list_permutations(node.names, ):
                yield ast.ImportFrom(module=node.module, names=perm, level=node.level)
    if (isinstance(node, ast.BinOp, )) and (op_is_assoc(node, )) and (node_is_pure(node, )):
        for left in permutations(node.left, ):
            for right in permutations(node.right, ):
                yield ast.copy_location(ast.BinOp(left=left, op=node.op, right=right, ctx=node.ctx), )
                yield ast.copy_location(ast.BinOp(left=right, op=node.op, right=left, ctx=node.ctx), )
    else:
        if (isinstance(node, ast.Compare, )) and ((len(node.ops, )) == (1)) and (op_has_mirror(node.ops[0], )) and (node_is_pure(node, )):
            assert (len(node.comparators, )) == (1)
            for left in permutations(node.left, ):
                for right in permutations(node.comparators[0], ):
                    yield ast.copy_location(ast.Compare(left=left, ops=node.ops, comparators=[right]), node, )
                    yield ast.copy_location(ast.Compare(left=right, ops=[mirror(node.ops[0], )], comparators=[left]), node, )
        else:
            if (isinstance(node, ast.BoolOp, )) and (node_is_pure(node, )):
                stuff = [[x for x in permutations(v, )] for v in node.values]
                prod = [x for x in itertools.product(*stuff, )]
                for values in prod:
                    for indices in itertools.permutations(range(len(node.values, ), ), ):
                        yield PermuteBoolOps(indices, ).visit(ast.copy_location(ast.BoolOp(op=node.op, values=values), node, ), )
                        pass
                    pass
                pass
            else:
                yield node
    pass

def list_permutations(items):
    '\n    A generator which yields all possible orderings of the given list.\n    '
    if (len(items, )) <= (1):
        yield items[:]
    else:
        first = items[0]
        for subperm in list_permutations(items[1:], ):
            for i in range((len(subperm, )) + (1), ):
                yield ((subperm[:i]) + ([first])) + (subperm[i:])

def match(node, pat, **<ast.arg object at 0x109742ca0>):
    'A convenience wrapper for matchpat that accepts a patterns either\n    as an pre-parsed AST or as a pattern source string to be parsed.\n\n    '
    return matchpat(node, parse_pattern(pat, ), None=kwargs)

def predtrue(node, matchenv):
    'The True predicate'
    return True

def matchpat(node, pat, matchpred=predtrue, env={  }, gen=False, normalize=False):
    'Match an AST against a (pre-parsed) pattern.\n\n    The optional keyword argument matchpred gives a predicate of type\n    (AST node * match environment) -> bool that filters structural\n    matches by arbitrary additional criteria.  The default is the true\n    predicate, accepting all structural matches.\n\n    The optional keyword argument gen determines whether this function:\n      - (gen=True)  yields an environment for each way pat matches node.\n      - (gen=False) returns Some(the first of these environments), or\n                    None if there are no matches (default).\n\n    EXPERIMENTAL\n    The optional keyword argument normalize determines whether to\n    rewrite the target AST node and the pattern to inline simple\n    straightline variable assignments into large expressions (to the\n    extent possible) for matching.  The default is no normalization\n    (False).  Normalization is experimental.  It is rather ad hoc and\n    conservative and may causes unintuitive matching behavior.  Use\n    with caution.\n\n    INTERNAL\n    The optional keyword env gives an initial match environment which\n    may be used to constrain otherwise free pattern variables.  This\n    argument is mainly intended for internal use.\n\n    '
    assert (node) is not (None)
    assert (pat) is not (None)
    if normalize:
        if (isinstance(node, ast.AST, )) or ((type(node, )) == (list)):
            node = canonical_pure(node, )
            pass
        if (isinstance(node, ast.AST, )) or ((type(node, )) == (list)):
            pat = canonical_pure(pat, )
            pass
        pass
    matches = (matchenv for permpat in permutations(pat, ) for matchenv in imatches(node, permpat, Some(env, ), True, ) if matchpred(node, matchenv, ))
    return (matches if gen else takeone(matches, ))

def bind(env1, name, value):
    '\n    Unify the environment in option env1 with a new binding of name to\n    value.  Return Some(extended environment) if env1 is Some(existing\n    environment) in which name is not bound or is bound to value.\n    Otherwise, env1 is None or the existing binding of name\n    incompatible with value, return None.\n    '
    assert (type(name, )) == (str)
    if (env1) is (None):
        result = None
    env = env1.value
    if var_is_anonymous(name, ):
        result = env1
    else:
        if (name) in (env):
            if takeone(imatches(env[name], value, Some({  }, ), True, ), ):
                result = env1
            else:
                result = None
        else:
            env = env.copy()
            env[name] = value
            result = Some(env, )
    return result
    pass

IGNORE_FIELDS = set(['ctx', 'lineno', 'col_offset'], )
'AST node fields to be ignored when matching children.'
def argObjToName(argObj):
    'Convert Python 3 arg object into a Name node,\n       ignoring any annotation, lineno, and col_offset.'
    if (argObj) is (None):
        return None
    else:
        return ast.Name(id=argObj.arg, ctx=None)

def astStr(astObj):
    '\n    Converts an AST object to a string, imperfectly.\n    '
    if isinstance(astObj, ast.Name, ):
        return astObj.id
    else:
        if isinstance(astObj, ast.Str, ):
            return repr(astObj.s, )
        else:
            if isinstance(astObj, ast.Num, ):
                return str(astObj.n, )
            else:
                if isinstance(astObj, (list, tuple), ):
                    return str([astStr(x, ) for x in astObj], )
                else:
                    if (hasattr(astObj, '_fields', )) and ((len(astObj._fields, )) > (0)):
                        return '{}({})'.format(type(astObj, ).__name__, ', '.join((astStr(getattr(astObj, f, ), ) for f in astObj._fields), ), )
                    else:
                        if hasattr(astObj, '_fields', ):
                            return type(astObj, ).__name__
                        else:
                            return '<{}>'.format(type(astObj, ).__name__, )

def defaultToName(defObj):
    '\n    Converts a default expression to a name for matching purposes.\n    TODO: Actually do recursive matching on these expressions!\n    '
    if isinstance(defObj, ast.Name, ):
        return defObj.id
    else:
        return astStr(defObj, )

def field_values(node):
    'Return a list of the values of all matching-relevant fields of the\n    given AST node, with fields in consistent list positions.'
    if isinstance(node, ast.FunctionDef, ):
        return [(ast.Name(id=v, ctx=None) if (k) == ('name') else v) for (k, v) in ast.iter_fields(node, ) if (k) not in (IGNORE_FIELDS)]
    if isinstance(node, ast.ClassDef, ):
        return [(ast.Name(id=v, ctx=None) if (k) == ('name') else v) for (k, v) in ast.iter_fields(node, ) if (k) not in (IGNORE_FIELDS)]
    if isinstance(node, ast.Call, ):
        return [(odict(((kw.arg, kw.value) for kw in v), ) if (k) == ('keywords') else v) for (k, v) in ast.iter_fields(node, ) if (k) not in (IGNORE_FIELDS)]
    if isinstance(node, ast.arguments, ):
        argList = [argObjToName(argObj, ) for argObj in node.args]
        if ((node.vararg) is (None)) and ((node.kwarg) is (None)) and ((node.kwonlyargs) == ([])) and ((node.kw_defaults) == ([])) and ((node.defaults) == ([])):
            return [argList]
        else:
            return [argList, argObjToName(node.vararg, ), argObjToName(node.kwarg, ), [argObjToName(argObj, ) for argObj in node.kwonlyargs], node.kw_defaults, node.defaults]
    if isinstance(node, ast.keyword, ):
        return [(ast.Name(id=v, ctx=None) if (k) == ('arg') else v) for (k, v) in ast.iter_fields(node, ) if (k) not in (IGNORE_FIELDS)]
    if isinstance(node, ast.Global, ):
        return [ast.Name(id=n, ctx=None) for n in sorted(node.names, )]
    if isinstance(node, ast.Import, ):
        return [node.names]
    if isinstance(node, ast.ImportFrom, ):
        return [ast.Name(id=node.module, ctx=None), node.level, node.names]
    if isinstance(node, ast.alias, ):
        result = [ast.Name(id=node.name, ctx=None)]
        if (node.asname) is not (None):
            result.append(ast.Name(id=node.asname, ctx=None), )
        return result
    if isinstance(node, ast.AST, ):
        return [v for (k, v) in ast.iter_fields(node, ) if (k) not in (IGNORE_FIELDS)]
    if (type(node, )) == (list):
        return node
    if isinstance(node, (dict, odict), ):
        return ([ast.Name(id=n, ctx=None) for n in node.keys()]) + (list(node.values(), ))
    return []

imatchCount = 0
def imatches(node, pat, env1, seq):
    'Exponential backtracking match generating 0 or more matching\n    environments.  Supports multiple sequence patterns in one context,\n    simple permutations of semantically equivalent but syntactically\n    mirrored patterns.\n    '
    result = iterempty()
    if (env1) is (None):
        result = iterempty()
        return result
    env = env1.value
    assert (env) is not (None)
    if (((type(pat, )) == (bool)) or ((type(pat, )) == (str)) or ((pat) is (None))) and ((node) == (pat)):
        result = iterone(env, )
    else:
        if ((type(pat, )) == (int)) or ((type(pat, )) == (float)):
            if (type(node, )) == (type(pat, )):
                if (((type(pat, )) == (int)) and ((node) == (pat))) or (((type(pat, )) == (float)) and ((abs((node) - (pat), )) < (0.001))):
                    result = iterone(env, )
                pass
        else:
            if node_var(pat, ):
                if node_is_bindable(node, ):
                    if isinstance(node, ast.alias, ):
                        if node.asname:
                            bind_as = ast.Name(id=node.asname, ctx=None)
                        else:
                            bind_as = ast.Name(id=node.name, ctx=None)
                    else:
                        bind_as = node
                    env2 = bind(env1, node_var(pat, ), bind_as, )
                    if env2:
                        result = iterone(env2.value, )
                    pass
            else:
                if typed_lit_var(pat, ):
                    (id, ty) = typed_lit_var(pat, )
                    lit = LIT_TYPES[ty](node, )
                    if lit:
                        env2 = bind(env1, id, lit.value, )
                        if env2:
                            result = iterone(env2.value, )
                        pass
                else:
                    if (type(node, )) == (type(pat, )):
                        if (type(pat, )) == (list):
                            if (len(pat, )) == (0):
                                if (len(node, )) == (0):
                                    result = iterone(env, )
                                pass
                            else:
                                if (len(node, )) == (0):
                                    if seq:
                                        psn = set_var(pat[0], )
                                        if psn:
                                            result = imatches(node, pat[1:], bind(env1, psn, [], ), seq, )
                                        pass
                                    pass
                                else:
                                    psn = set_var(pat[0], )
                                    if (seq) and (psn):
                                        result = ichain((imatches(node[i:], pat[1:], bind(env1, psn, node[:i], ), seq, ) for i in range(len(node, ), - (1), - (1), )), )
                                    else:
                                        if ((len(node, )) == (1)) and ((len(pat, )) == (1)):
                                            result = imatches(node[0], pat[0], env1, True, )
                                        else:
                                            result = ichain((imatches(node[1:], pat[1:], Some(bs, ), seq, ) for bs in imatches(node[0], pat[0], env1, True, )), )
                                    pass
                        else:
                            if ((type(node, )) == (dict)) or ((type(node, )) == (odict)):
                                result = match_dict(node, pat, env1, )
                            else:
                                if isinstance(node, ast.AST, ):
                                    result = imatches(field_values(node, ), field_values(pat, ), env1, False, )
                                pass
                        pass
    return result

def match_dict(node, pat, env1):
    assert all(((type(k, )) == (str) for k in pat), )
    assert all(((type(k, )) == (str) for k in node), )
    def match_keys(node, pat, envopt):
        'Match literal keys.'
        keyopt = takeone((k for k in pat if (not (node_var_str(k, ))) and (not (set_var_str(k, )))), )
        if keyopt:
            key = keyopt.value
            if (key) in (node):
                return ichain((match_keys(dict_unbind(node, key, ), dict_unbind(pat, key, ), Some(kenv, ), ) for kenv in imatches(node[key], pat[key], envopt, False, )), )
            else:
                return iterempty()
            pass
        else:
            return match_var_keys(node, pat, envopt, )
        pass

    def match_var_keys(node, pat, envopt):
        'Match node variable keys.'
        keyvaropt = takeone((k for k in pat if node_var_str(k, )), )
        if keyvaropt:
            keyvar = keyvaropt.value
            return ichain((match_var_keys(dict_unbind(node, nkey, ), dict_unbind(pat, keyvar, ), bind(Some(kenv, ), node_var_str(keyvar, ), ast.Name(id=nkey, ctx=None), ), ) for (nkey, nval) in node.items() for kenv in imatches(nval, pat[keyvar], envopt, False, )), )
        else:
            return match_set_var_keys(node, pat, envopt, )
        pass

    def match_set_var_keys(node, pat, envopt):
        'Match set variable keys.'
        assert envopt
        keysetvaropt = takeone((k for k in pat if set_var_str(k, )), )
        if keysetvaropt:
            e = bind(envopt, set_var_str(keysetvaropt.value, ), [(ast.Name(id=kw, ctx=None), karg) for (kw, karg) in node.items()], )
            return (iterone(e.value, ) if e else iterempty())
        else:
            if (0) == (len(node, )):
                assert (0) == (len(pat, ))
                return iterone(envopt.value, )
            else:
                return iterempty()

    return match_keys(node, pat, env1, )

def find(node, pat, **<ast.arg object at 0x1097db910>):
    'Pre-order search for first sub-AST matching pattern, returning\n    (matched node, bindings).'
    kwargs['gen'] = True
    return takeone(findall(node, parse_pattern(pat, ), None=kwargs), )

def findall(node, pat, outside=[], **<ast.arg object at 0x1097dbdf0>):
    '\n    Search for all sub-ASTs matching pattern, returning list of (matched\n    node, bindings).\n    '
    assert (node) is not (None)
    assert (pat) is not (None)
    gen = kwargs.get('gen', False, )
    kwargs['gen'] = True
    pat = parse_pattern(pat, )
    if ((type(pat, )) == (list)) and (not (set_var(pat[- (1)], ))):
        pat = (pat) + ([parse_pattern('___', )])
        pass
    def findall_scalar_pat_iter(node):
        'Generate all matches of a scalar (non-list) pattern at this node\n        or any non-excluded descendant of this node.'
        assert (type(pat, )) != (list)
        assert (node) is not (None)
        envs = [e for e in matchpat(node, pat, None=kwargs)]
        if (0) < (len(envs, )):
            yield (node, envs)
        if not (any((match(node, op, ) for op in outside), )):
            for n in field_values(node, ):
                if n:
                    for result in findall_scalar_pat_iter(n, ):
                        yield result
                        pass
                    pass
                pass
            pass
        pass

    def findall_list_pat_iter(node):
        'Generate all matches of a list pattern at this node or any\n        non-excluded descendant of this node.'
        assert (type(pat, )) == (list)
        assert (0) < (len(pat, ))
        if (type(node, )) == (list):
            envs = [e for e in matchpat(node, pat, None=kwargs)]
            if (0) < (len(envs, )):
                yield (node, envs)
            if (not (any((match(node, op, ) for op in outside), ))) and ((0) < (len(node, ))):
                for m in findall_list_pat_iter(node[0], ):
                    yield m
                    pass
                if not (set_var(pat[0], )):
                    for m in findall_list_pat_iter(node[1:], ):
                        yield m
                        pass
                    pass
                pass
            pass
        else:
            if not (any((match(node, op, ) for op in outside), )):
                for ty in [ast.ClassDef, ast.FunctionDef, ast.With, ast.Module, ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler]:
                    if isinstance(node, ty, ):
                        for m in findall_list_pat_iter(node.body, ):
                            yield m
                            pass
                        break
                    pass
                for ty in [ast.If, ast.For, ast.While, ast.Try]:
                    if (isinstance(node, ty, )) and (node.orelse):
                        for m in findall_list_pat_iter(node.orelse, ):
                            yield m
                            pass
                        break
                    pass
                if isinstance(node, ast.Try, ):
                    for h in node.handlers:
                        for m in findall_list_pat_iter(h.body, ):
                            yield m
                            pass
                        pass
                    pass
                pass
        pass

    matches = (findall_list_pat_iter if (type(pat, )) == (list) else findall_scalar_pat_iter)(node, )
    return (matches if gen else list(matches, ))

def count(node, pat, **<ast.arg object at 0x1097f6940>):
    '\n    Count all sub-ASTs matching pattern. Does NOT count individual\n    environments that match (i.e., ways that bindings could attach at a\n    given node), but rather counts nodes at which one or more bindings\n    are possible.\n    '
    assert ('gen') not in (kwargs)
    return sum((1 for x in findall(node, pat, gen=True, None=kwargs)), )

class Unimplemented(Exception):
    pass

SIMPLE_INLINE_TYPES = [ast.Expr, ast.Return, ast.Name, ast.Store, ast.Load, ast.Param]
class InlineAvailableExpressions(ast.NodeTransformer):
    def __init__(self, other=None):
        self.available = (dict(other.available, ) if other else {  })

    def visit_Name(self, name):
        if (isinstance(name.ctx, ast.Load, )) and ((name.id) in (self.available)):
            return self.available[name.id]
        else:
            return self.generic_visit(name, )

    def visit_Assign(self, assign):
        raise Unimplemented
        new = ast.copy_location(ast.Assign(targets=assign.targets, value=self.visit(assign.value, )), assign, )
        self.available[assign.targets[0].id] = new.value
        return new

    def visit_If(self, ifelse):
        test = self.visit(ifelse.test, )
        body_inliner = InlineAvailableExpressions(self, )
        orelse_inliner = InlineAvailableExpressions(self, )
        body = body_inliner.inline_block(ifelse.body, )
        orelse = orelse_inliner.inline_block(ifelse.orelse, )
        self.available = {name: body_inliner.available[name] for name in (set(body_inliner.available, )) & (set(orelse_inliner.available, )) if (body_inliner.available[name]) == (orelse_inliner.available[name])}
        return ast.copy_location(ast.If(test=test, body=body, orelse=orelse), ifelse, )

    def generic_visit(self, node):
        if not (any((isinstance(node, t, ) for t in SIMPLE_INLINE_TYPES), )):
            raise Unimplemented()
        return ast.NodeTransformer.generic_visit(self, node, )

    def inline_block(self, block):
        return [self.visit(stmt, ) for stmt in block]


class DeadCodeElim(ast.NodeTransformer):
    def __init__(self, other=None):
        self.used = (set(other.users, ) if other else set())
        pass

    def visit_Name(self, name):
        if isinstance(name.ctx, ast.Store, ):
            self.used = (self.used) - ({ name.id })
            return name
        else:
            if isinstance(name.ctx, ast.Load, ):
                self.used = (self.used) | ({ name.id })
                return name
            else:
                return name
        pass

    def visit_Assign(self, assign):
        assert all(((node_is_name(t, )) or ((isinstance(t, ast.Tuple, )) and (all((node_is_name(t, ) for t in t.elts), ))) for t in assign.targets), )
        if (any(((t.id) in (self.used) for t in assign.targets if node_is_name(t, )), )) or (any(((t.id) in (self.used) for tup in assign.targets for t in tup if ((type(tup, )) == (tuple)) and (node_is_name(t, ))), )):
            return ast.copy_location(ast.Assign(targets=[self.visit(t, ) for t in assign.targets], value=self.visit(assign.value, )), assign, )
        else:
            return None

    def visit_If(self, ifelse):
        body_elim = DeadCodeElim(self, )
        orelse_elim = DeadCodeElim(self, )
        body = body_elim.elim_block(ifelse.body, )
        orelse = orelse_elim.elim_block(ifelse.body, )
        self.used = (body_elim.used) | (orelse_elim.used)
        test = self.visit(ifelse.test, )
        return ast.copy_location(ast.If(test=test, body=body, orelse=orelse), ifelse, )

    def generic_visit(self, node):
        if not (any((isinstance(node, t, ) for t in SIMPLE_INLINE_TYPES), )):
            raise Unimplemented()
        return ast.NodeTransformer.generic_visit(self, node, )

    def elim_block(self, block):
        return [s for s in (self.visit(stmt, ) for stmt in block[::- (1)]) if s][::- (1)]


class NormalizePure(ast.NodeTransformer):
    'AST transformer: normalize/inline straightline assignments into\n    single expressions as possible.'
    def normalize_block(self, block):
        try:
            return DeadCodeElim().elim_block(InlineAvailableExpressions().inline_block(block, ), )
        except Unimplemented:
            return block

    def visit_FunctionDef(self, fun):
        normbody = self.normalize_block(fun.body, )
        if (normbody) != (fun.body):
            return ast.copy_location(ast.FunctionDef(name=fun.name, args=self.generic_visit(fun.args, ), body=normbody), fun, )
        else:
            return fun


def canonical_pure(node):
    'Return the normalized/inlined version of an AST node.'
    if (type(node, )) == (list):
        return NormalizePure().normalize_block(node, )
    else:
        assert isinstance(node, ast.AST, )
        return NormalizePure().visit(node, )

CANON_CACHE = {  }
def parse_canonical_pure(string, toplevel=False):
    'Parse a normalized/inlined version of a program.'
    if (type(string, )) == (list):
        return [parse_canonical_pure(x, ) for x in string]
    else:
        if (string) not in (CANON_CACHE):
            CANON_CACHE[string] = canonical_pure(parse_pattern(string, toplevel=toplevel), )
            pass
    return CANON_CACHE[string]

INDENT = '    '
def indent(pat, indent=INDENT):
    'Apply indents to a source string.'
    return (indent) + (pat.replace('\n', ('\n') + (indent), ))

class SourceFormatter(ast.NodeVisitor):
    'AST visitor: pretty print AST to python source string'
    def __init__(self):
        ast.NodeVisitor.__init__(self, )
        self._indent = ''
        pass

    def indent(self):
        self._indent += INDENT
        pass

    def unindent(self):
        self._indent = self._indent[:- (4)]
        pass

    def line(self, ln):
        return ((self._indent) + (ln)) + ('\n')

    def lines(self, lst):
        return ''.join(lst, )

    def generic_visit(self, node):
        assert False, 'visiting {}'.format(ast.dump(node, ), )
        pass

    def visit_Module(self, m):
        return self.lines((self.visit(n, ) for n in m.body), )

    def visit_Interactive(self, i):
        return self.lines((self.visit(n, ) for n in i.body), )

    def visit_Expression(self, e):
        return self.line(self.visit(e.body, ), )

    def visit_FunctionDef(self, f):
        assert not (f.decorator_list)
        header = self.line('def {name}({args}):'.format(name=f.name, args=self.visit(f.args, )), )
        self.indent()
        body = self.lines((self.visit(s, ) for s in f.body), )
        self.unindent()
        return ((header) + (body)) + ('\n')

    def visit_ClassDef(self, c):
        assert not (c.decorator_list)
        header = self.line('class {name}({bases}):'.format(name=c.name, bases=', '.join((self.visit(b, ) for b in c.bases), )), )
        self.indent()
        body = self.lines((self.visit(s, ) for s in c.body), )
        self.unindent()
        return ((header) + (body)) + ('\n')

    def visit_Return(self, r):
        return self.line(('return' if (r.value) is (None) else 'return {}'.format(self.visit(r.value, ), )), )

    def visit_Delete(self, d):
        return self.line(('del ') + (''.join((self.visit(e, ) for e in d.targets), )), )

    def visit_Assign(self, a):
        return self.line(((', '.join((self.visit(e, ) for e in a.targets), )) + (' = ')) + (self.visit(a.value, )), )

    def visit_AugAssign(self, a):
        return self.line('{target} {op}= {expr}'.format(target=self.visit(a.target, ), op=self.visit(a.op, ), expr=self.visit(a.value, )), )

    def visit_For(self, f):
        header = self.line('for {} in {}:'.format(self.visit(f.target, ), self.visit(f.iter, ), ), )
        self.indent()
        body = self.lines((self.visit(s, ) for s in f.body), )
        orelse = self.lines((self.visit(s, ) for s in f.orelse), )
        self.unindent()
        return ((header) + (body)) + (((self.line('else:', )) + (orelse) if f.orelse else ''))

    def visit_While(self, w):
        header = self.line('while {}:'.format(self.visit(w.test, ), ), )
        self.indent()
        body = self.lines((self.visit(s, ) for s in w.body), )
        orelse = self.lines((self.visit(s, ) for s in w.orelse), )
        self.unindent()
        return ((header) + (body)) + (((self.line('else:', )) + (orelse) if w.orelse else ''))
        return (header) + (body)

    def visit_If(self, i):
        header = self.line('if {}:'.format(self.visit(i.test, ), ), )
        self.indent()
        body = self.lines((self.visit(s, ) for s in i.body), )
        orelse = self.lines((self.visit(s, ) for s in i.orelse), )
        self.unindent()
        return ((header) + (body)) + (((self.line('else:', )) + (orelse) if i.orelse else ''))

    def visit_With(self, w):
        header = self.line('with {items}:'.format(items=', '.join(('{expr}{asnames}'.format(expr=self.visit(item.context_expr, ), asnames=(('as ') + (self.visit(item.optional_vars, )) if item.optional_vars else '')) for item in w.items), )), )
        self.indent()
        body = self.lines((self.visit(s, ) for s in w.body), )
        self.unindent()
        return (header) + (body)

    def visit_Raise(self, r):
        return self.line('raise{}{}'.format(((' ') + (self.visit(r.exc, )) if r.exc else ''), ((' from ') + (self.visit(r.cause, )) if r.cause else ''), ), )

    def visit_Try(self, t):
        self.indent()
        tblock = self.lines((self.visit(s, ) for s in t.body), )
        orelse = self.lines((self.visit(s, ) for s in t.orelse), )
        fblock = self.lines((self.visit(s, ) for s in t.finalbody), )
        self.unindent()
        return ((((self.line('try:', )) + (tblock)) + (''.join((self.visit(eh, ) for eh in t.handlers), ))) + (((self.line('else:', )) + (orelse) if orelse else ''))) + (((self.line('finally:', )) + (fblock) if fblock else ''))

    def visit_ExceptHandler(self, eh):
        header = self.line('except{}{}{}{}:'.format((' ' if eh.type else ''), (self.visit(eh.type, ) if eh.type else ''), (' as ' if (eh.type) and (eh.name) else (' ' if eh.name else '')), (self.visit(eh.name, ) if (eh.name) and (isinstance(eh.name, ast.AST, )) else (eh.name if eh.name else '')), ), )
        self.indent()
        body = self.lines((self.visit(s, ) for s in eh.body), )
        self.unindent()
        return (header) + (body)

    def visit_Assert(self, a):
        return self.line('assert {}{}{}'.format(self.visit(a.test, ), (', ' if a.msg else ''), (self.visit(a.msg, ) if a.msg else ''), ), )

    def visit_Import(self, i):
        return self.line('import {}'.format(', '.join((self.visit(n, ) for n in i.names), ), ), )

    def visit_ImportFrom(self, f):
        return self.line('from {}{} import {}'.format(('.') * (f.level), (f.module if f.module else ''), ', '.join((self.visit(n, ) for n in f.names), ), ), )

    def visit_Exec(self, e):
        return self.line('exec {}{}{}{}{}'.format(self.visit(e.body, ), (' in ' if e.globals else ''), (self.visit(e.globals, ) if e.globals else ''), (', ' if e.locals else ''), (self.visit(e.locals, ) if e.locals else ''), ), )

    def visit_Global(self, g):
        return self.line('global {}'.format(', '.join(g.names, ), ), )

    def visit_Expr(self, e):
        return self.line(self.visit(e.value, ), )

    def visit_Pass(self, p):
        return self.line('pass', )

    def visit_Break(self, b):
        return self.line('break', )

    def visit_Continue(self, c):
        return self.line('continue', )

    def visit_BoolOp(self, b):
        return ' {} '.format(self.visit(b.op, ), ).join(('({})'.format(self.visit(e, ), ) for e in b.values), )

    def visit_BinOp(self, b):
        return '({}) {} ({})'.format(self.visit(b.left, ), self.visit(b.op, ), self.visit(b.right, ), )

    def visit_UnaryOp(self, u):
        return '{} ({})'.format(self.visit(u.op, ), self.visit(u.operand, ), )

    def visit_Lambda(self, ld):
        return '(lambda {}: {})'.format(self.visit(ld.args, ), self.visit(ld.body, ), )

    def visit_IfExp(self, i):
        return '({} if {} else {})'.format(self.visit(i.body, ), self.visit(i.test, ), self.visit(i.orelse, ), )

    def visit_Dict(self, d):
        return '{{ {} }}'.format(', '.join(('{}: {}'.format(self.visit(k, ), self.visit(v, ), ) for (k, v) in zip(d.keys, d.values, )), ), )

    def visit_Set(self, s):
        return '{{ {} }}'.format(', '.join((self.visit(e, ) for e in s.elts), ), )

    def visit_ListComp(self, lc):
        return '[{} {}]'.format(self.visit(lc.elt, ), ' '.join((self.visit(g, ) for g in lc.generators), ), )

    def visit_SetComp(self, sc):
        return '{{{} {}}}'.format(self.visit(sc.elt, ), ' '.join((self.visit(g, ) for g in sc.generators), ), )

    def visit_DictComp(self, dc):
        return '{{{} {}}}'.format('{}: {}'.format(self.visit(dc.key, ), self.visit(dc.value, ), ), ' '.join((self.visit(g, ) for g in dc.generators), ), )

    def visit_GeneratorExp(self, ge):
        return '({} {})'.format(self.visit(ge.elt, ), ' '.join((self.visit(g, ) for g in ge.generators), ), )

    def visit_Yield(self, y):
        return 'yield {}'.format((self.visit(y.value, ) if y.value else ''), )

    def visit_Compare(self, c):
        assert (len(c.ops, )) == (len(c.comparators, ))
        return '{} {}'.format('({})'.format(self.visit(c.left, ), ), ' '.join(('{} ({})'.format(self.visit(op, ), self.visit(expr, ), ) for (op, expr) in zip(c.ops, c.comparators, )), ), )

    def visit_Call(self, c):
        return '{fun}({args}{keys})'.format(fun=self.visit(c.func, ), args=', '.join((self.visit(a, ) for a in c.args), ), keys=((', ' if c.args else '')) + ((', '.join((self.visit(ka, ) for ka in c.keywords), ) if c.keywords else '')))

    def visit_Repr(self, r):
        return 'repr({})'.format(self.visit(r.expr, ), )

    def visit_Num(self, n):
        return repr(n.n, )

    def visit_Str(self, s):
        return repr(s.s, )

    def visit_Attribute(self, a):
        return '{}.{}'.format(self.visit(a.value, ), a.attr, )

    def visit_Subscript(self, s):
        return '{}[{}]'.format(self.visit(s.value, ), self.visit(s.slice, ), )

    def visit_Name(self, n):
        return n.id

    def visit_List(self, ls):
        return '[{}]'.format(', '.join((self.visit(e, ) for e in ls.elts), ), )

    def visit_Tuple(self, tp):
        return '({})'.format(', '.join((self.visit(e, ) for e in tp.elts), ), )

    def visit_Ellipsis(self, s):
        return '...'

    def visit_Slice(self, s):
        return '{}:{}{}{}'.format((self.visit(s.lower, ) if s.lower else ''), (self.visit(s.upper, ) if s.upper else ''), (':' if s.step else ''), (self.visit(s.step, ) if s.step else ''), )

    def visit_ExtSlice(self, es):
        return ', '.join((self.visit(s, ) for s in es.dims), )

    def visit_Index(self, i):
        return self.visit(i.value, )

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
        return 'for {} in {}{}{}'.format(self.visit(c.target, ), self.visit(c.iter, ), (' ' if c.ifs else ''), ' '.join(('if {}'.format(self.visit(i, ), ) for i in c.ifs), ), )

    def visit_arg(self, a):
        '[2019/01/22, lyn] Handle new arg objects in Python 3.'
        return a.arg

    def visit_keyword(self, k):
        return '{}={}'.format(k.arg, self.visit(k.value, ), )

    def visit_alias(self, a):
        return ('{} as {}'.format(a.name, a.asname, ) if a.asname else a.name)

    def visit_arguments(self, a):
        stdargs = (a.args[:- (len(a.defaults, ))] if a.defaults else a.args)
        defargs = (zip(a.args[- (len(a.defaults, )):], a.defaults, ) if a.defaults else [])
        return '{stdargs}{sep1}{defargs}{sep2}{varargs}{sep3}{kwargs}'.format(stdargs=', '.join((self.visit(sa, ) for sa in stdargs), ), sep1=(', ' if ((0) < (len(stdargs, ))) and (defargs) else ''), defargs=', '.join(('{}={}'.format(self.visit(da, ), self.visit(dd, ), ) for (da, dd) in defargs), ), sep2=(', ' if ((0) < (len(a.args, ))) and (a.vararg) else ''), varargs=('*{}'.format(a.vararg, ) if a.vararg else ''), sep3=(', ' if (((0) < (len(a.args, ))) or (a.vararg)) and (a.kwarg) else ''), kwargs=('**{}'.format(a.kwarg, ) if a.kwarg else ''))

    def visit_NameConstant(self, nc):
        return str(nc.value, )

    def visit_Starred(self, st):
        return ('*') + (st.value.id)


def ast2source(node):
    'Pretty print an AST as a python source string'
    return SourceFormatter().visit(node, )

def source(node):
    'Alias for ast2source'
    return ast2source(node, )

if (__name__) == ('__main__'):
    tests = [(True, 1, '2', '2'), (False, 0, '2', '3'), (True, 1, 'x', '_a_'), (True, 1, '(x, y)', '(_a_, _b_)'), (False, 0, '(x, y)', '(_a_, _a_)'), (True, 1, '(x, x)', '(_a_, _a_)'), (True, 4, 'max(7,3)', '_x_'), (True, 1, 'max(7,3)', 'max(7,3)'), (False, 0, 'max(7,2)', 'max(7,3)'), (True, 1, 'max(7,3,5)', 'max(___args___)'), (False, 1, 'min(max(7,3),5)', 'max(___args___)'), (True, 2, 'min(max(7,3),5)', '_f_(___args___)'), (True, 1, 'min(max(7,3),5)', 'min(max(___maxargs___),___minargs___)'), (True, 1, 'max()', 'max(___args___)'), (True, 1, 'max(4)', 'max(4,___args___)'), (True, 1, 'max(4,5,6)', 'max(4,___args___)'), (True, 1, '"hello %s" % x', '_a_str_ % _b_'), (False, 0, 'y % x', '_a_str_ % _b_'), (False, 0, '7 % x', '_a_str_ % _b_'), (True, 1, '3', '_a_int_'), (True, 1, '3.4', '_a_float_'), (False, 0, '3', '_a_float_'), (False, 0, '3.4', '_a_int_'), (True, 1, 'True', '_a_bool_'), (True, 1, 'False', '_a_bool_'), (True, 1, 'None', 'None'), (True, 7, 'print("hello"+str(3))', '_x_'), (True, 1, 'print("hello"+str(3))', 'print(_x_)'), (True, 1, 'print(1)', 'print(_x_, ___args___)'), (False, 0, 'print(1)', 'print(_x_, _y_, ___args___)'), (False, 0, 'print(1, 2)', 'print(_x_)'), (True, 1, 'print(1, 2)', 'print(_x_, ___args___)'), (True, 1, 'print(1, 2)', 'print(_x_, _y_, ___args___)'), (True, 1, 'print(1, 2, 3)', 'print(_x_, ___args___)'), (True, 1, 'print(1, 2, 3)', 'print(_x_, _y_, ___args___)'), (True, 1, '\ndef f(x):\n    return 17\n         ', '\ndef f(_a_):\n    return _b_\n         '), (True, 1, '\ndef f(x):\n    return x\n         ', '\ndef f(_a_):\n    return _b_\n         '), (True, 1, '\ndef f(x):\n    return x\n         ', '\ndef f(_a_):\n    return _a_\n         '), (False, 0, '\ndef f(x):\n    return 17\n         ', '\ndef f(_a_):\n    return _a_\n         '), (True, 1, '\ndef f(x):\n    return 17\n         ', '\ndef f(_x_):\n    return _y_\n         '), (True, 1, "\ndef f(x,y):\n    print('hi')\n    return x\n         ", "\ndef f(_x_,_y_):\n    print('hi')\n    return _x_\n         "), (True, 1, "\ndef f(x,y):\n    print('hi')\n    return x\n         ", "\ndef _f_(_x_,_y_):\n    print('hi')\n    return _x_\n         "), (False, 0, "\ndef f(x,y):\n    print('hi')\n    return y\n         ", "\ndef f(_a_,_b_):\n    print('hi')\n    return _a_\n         "), (False, 0, 'x', 'y'), (True, 1, "\ndef f(x,y):\n    print('hi')\n    return y\n         ", '\ndef _f_(_x_,_y_):\n    ___\n    return _y_\n         '), (True, 1, "\ndef f(x,y):\n    print('hi')\n    print('world')\n    print('bye')\n    return y\n         ", '\ndef _f_(_x_,_y_):\n    ___stmts___\n    return _y_\n         '), (False, 0, "\ndef f(x,y):\n    print('hi')\n    print('world')\n    x = 4\n    print('really')\n    y = 7\n    print('bye')\n    return y\n         ", '\ndef _f_(_x_,_y_):\n    ___stmts___\n    print(_z_)\n    _y_ = _a_int_\n    return _y_\n         '), (True, 1, "\ndef f(x,y):\n    print('hi')\n    print('world')\n    x = 4\n    print('really')\n    y = 7\n    print('bye')\n    return y\n         ", '\ndef _f_(_x_,_y_):\n    ___stmts___\n    print(_z_)\n    _y_ = _a_int_\n    ___more___\n    return _y_\n         '), (True, 1, "\ndef f(x,y):\n    print('hi')\n    print('world')\n    x = 4\n    print('really')\n    y = 7\n    print('bye')\n    return y\n         ", '\ndef _f_(_x_,_y_):\n    ___stmts___\n    print(_a_)\n    _b_ = _c_\n    ___more___\n    return _d_\n         '), (False, 1, "\ndef f(x,y):\n    print('hi')\n    print('world')\n    x = 4\n    print('really')\n    y = 7\n    print('bye')\n    return y\n         ", '\n___stmts___\nprint(_a_)\n_b_ = _c_\n___more___\nreturn _d_\n         '), (True, 1, '\ndef eyes():\n    eye1 = Layer()\n    eye2 = Layer()\n    face = Layer()\n    face.add(eye)\n    face.add(eye2)\n    return face\n         ', '\ndef eyes():\n    ___\n    _face_ = Layer()\n    ___\n    return _face_\n         '), (True, 1, '\ndef f(x,y):\n    """I have a docstring.\n    It is a couple lines long."""\n    eye = Layer()\n    if eye:\n        face = Layer()\n    else:\n        face = Layer()\n    eye2 = Layer()\n    face.add(eye)\n    face.add(eye2)\n    return face\n         ', '\ndef f(___args___):\n    eye = Layer()\n    ___\n         '), (True, 1, '1 == 2', '2 == 1'), (True, 1, '1 <= 2', '2 >= 1'), (False, 0, '1 <= 2', '2 <= 1'), (False, 0, 'f() <= 2', '2 >= f()'), (True, 1, 'a and b and c', 'b and a and c'), (True, 1, '(a == b) == (b == c)', '(a == b) == (c == b)'), (True, 1, '(a and b) and c', 'a and (b and c)'), (True, 1, 'a and b', 'a and b'), (True, 1, 'g == "a" or g == "b" or g == "c"', '_g_ == _a_ or _g_ == _b_ or _c_ == _g_'), (True, 1, '\nx = 1\ny = 2\n', '\nx = 1\ny = 2\n'), (True, 1, '\nx = 1\ny = 2\n', '\n___\ny = 2\n'), (True, 1, '\nx = 1\nif (a or b or c):\n    return True\nelse:\n    return False\n        ', '\n___\nif _:\n    return _a_bool_\nelse:\n    return _b_bool_\n___\n         '), (True, 1, '\nif (a or b or c):\n    return True\nelse:\n    return False\n        ', '\nif _:\n    return _a_bool_\nelse:\n    return _b_bool_\n         '), (True, 1, '\nx = 1\nif (a or b or c):\n    return True\nelse:\n    return False\n        ', '\n___\nif _:\n    return _a_bool_\nelse:\n    return _b_bool_\n         '), (False, 1, '\ndef f():\n    if (a or b or c):\n        return True\n    else:\n        return False\n        ', '\n___\nif _:\n    return _a_bool_\nelse:\n    return _b_bool_\n___\n         '), (False, 1, "\ndef isValidGesture(gesture):\n    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):\n        return True\n    else:\n        return False\n        ", '\nif _:\n    return _a_bool_\nelse:\n    return _b_bool_\n        '), (False, 1, "\ndef isValidGesture(gesture):\n    print('blah')\n    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):\n        return True\n    return False\n        ", '\n___\nif _:\n    return _a_bool_\nreturn _b_bool_\n        '), (False, 1, "\ndef isValidGesture(gesture):\n    print('blah')\n    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):\n        return True\n    return False\n        ", '\nif _:\n    return _a_bool_\nreturn _b_bool_\n        '), (False, 1, "\ndef isValidGesture(gesture):\n    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):\n        return True\n    return False\n        ", '\nif _:\n    return _a_bool_\nreturn _b_bool_\n        '), (False, 1, "\ndef isValidGesture(gesture):\n    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):\n        x = True\n    x = False\n    return x\n        ", '\nif _:\n    _x_ = _a_bool_\n_x_ = _b_bool_\n        '), (True, 1, "\ndef isValidGesture(gesture):\n    if (gesture == 'rock' or gesture == 'paper' or gesture == 'scissors'):\n        return True\n    return False\n        ", '\ndef _(_):\n    if _:\n        return _a_bool_\n    return _b_bool_\n        '), (True, 1, 'x, y = f()', '___vars___ = f()'), (True, 1, 'x, y = f()', '_vars_ = f()'), (True, 1, 'f(a=1, b=2)', 'f(b=2, a=1)'), (True, 1, '\ndef f(x,y):\n    """with a docstring"""\n    if level <= 0:\n        pass\n    else:\n        fd(3)\n        lt(90)\n        ', '\ndef f(_, _):\n    ___\n    if _:\n        ___t___\n    else:\n        ___e___\n    ___s___\n'), (True, 1, '\nclass A(B):\n    def f(self, x):\n        pass\n        ', 'class _(_): ___'), (False, 0, 'drawLs(size/2, level - 1)', 'drawLs(_size_/2.0, _)'), (False, 0, '2', '2.0'), (False, 0, '2', '_d_float_'), (True, 1, '\ndef keepFirstLetter(phrase):\n    """Returns a new string that contains only the first occurrence of a\n    letter from the original phrase.\n    The first letter occurrence can be upper or lower case.\n    Non-alpha characters (such as punctuations and space) are left unchanged.\n    """\n    #this list holds lower-cased versions of all of the letters already used\n    usedCharacters = []\n\n    finalPhrase = ""\n    for n in phrase:\n        if n.isalpha():\n            #we need to create a temporary lower-cased version of the letter,\n            #so that we can check and see if we\'ve seen an upper or lower-cased\n            #version of this letter before\n            tempN = n.lower()\n            if tempN not in usedCharacters:\n                usedCharacters.append(tempN)\n                #but we need to add the original n, so that we can preserve\n                #if it was upper cased or not\n                finalPhrase = finalPhrase + n\n\n        #this adds all non-letter characters into the final phrase list\n        else:\n            finalPhrase = finalPhrase + n\n\n    return finalPhrase\n        ', '\ndef _(___):\n    ___\n    _acc_ = ""\n    ___\n    for _ in _:\n        ___\n    return _acc_\n    ___\n        '), (False, 1, '\ndef keepFirstLetter(phrase):\n    #this list holds lower-cased versions of all of the letters already used\n    usedCharacters = []\n\n    finalPhrase = ""\n    for n in phrase:\n        if n.isalpha():\n            #we need to create a temporary lower-cased version of the letter,\n            #so that we can check and see if we\'ve seen an upper or lower-cased\n            #version of this letter before\n            tempN = n.lower()\n            if tempN not in usedCharacters:\n                usedCharacters.append(tempN)\n                #but we need to add the original n, so that we can preserve\n                #if it was upper cased or not\n                finalPhrase = finalPhrase + n\n\n        #this adds all non-letter characters into the final phrase list\n        else:\n            finalPhrase = finalPhrase + n\n\n    return finalPhrase\n        ', '\n___prefix___\n_acc_ = ""\n___middle___\nfor _ in _:\n    ___\nreturn _acc_\n___suffix___\n        '), (True, 1, '\na = 1\nb = 2\nc = 3\n        ', '___; _x_ = _n_'), (False, 1, '\ndef f(a):\n    x = ""\n    return x\n        ', '\n_acc_ = ""\nreturn _acc_\n        '), (True, 1, 'if x: print(1)', 'if _: _'), (False, 0, 'if x: print(1)\nelse: pass', 'if _: _'), (True, 1, 'if x: print(1)\nelse: pass', 'if _: _\nelse: ___'), (False, 0, 'if x: print(1)', '\nif _: _\nelse:\n    _\n    ___\n'), (True, 1, 'if x: print(1)\nelse: pass', '\nif _: _\nelse:\n    _\n    ___\n'), (True, 1, 'if x: print(1)', 'if _: _\nelse: ___'), (True, 1, 'f(a=1)', 'f(a=1)'), (True, 1, 'f(a=1)', 'f(_kw_=1)'), (True, 1, 'f(a=1)', 'f(_kw_=_arg_)'), (True, 1, 'f(a=1)', 'f(_=1)'), (True, 1, 'f(a=1)', 'f(_=_arg_)'), (True, 1, 'f(a=1, b=2)', 'f(_x_=_, _y_=_)'), (True, 1, 'f(a=1, b=2)', 'f(_x_=2, _y_=_)'), (False, 0, 'f(a=1, b=2)', 'f(_x_=_)'), (False, 0, 'f(a=1, b=2)', 'f(_x_=_, _y_=_, _z_=_)'), (False, 0, 'f(a=1, b=2)', 'f(_x_=2, _y_=2)'), (True, 1, 'f(a=1, b=2)', 'f(_x_=_, b=_)'), (True, 1, 'f(a=1, b=2)', 'f(b=_, _x_=_)'), (True, 1, 'f(a=1+1, b=1+1)', 'f(_c_=_x_+_x_, _d_=_y_+_y_)'), (True, 1, 'f(a=1+1, b=2+2)', 'f(_c_=_x_+_x_, _d_=_y_+_y_)'), (True, 1, 'f(a=1+2, b=2+1)', 'f(_c_=_x_+_y_, _d_=_y_+_x_)'), (True, 1, 'f(a=1+1, b=1+1)', 'f(_c_=_x_+_x_, _d_=_x_+_x_)'), (False, 0, 'f(a=1+1, b=2+2)', 'f(_c_=_x_+_x_, _d_=_x_+_x_)'), (True, 1, 'f(a=1, b=2)', 'f(___=_)'), (True, 1, 'f(a=1, b=2)', 'f(___kwargs___=_)'), (True, 1, 'f(a=1, b=2)', 'f(___kwargs___=_, b=_)'), (True, 1, 'f(a=1, b=2)', 'f(b=_, ___kwargs___=_)'), (True, 1, 'f(a=1, b=2)', 'f(___kwargs___=_, a=_, b=_)'), (True, 1, 'f(a=1, b=2)', 'f(a=_, b=_, ___kwargs___=_)'), (True, 1, 'f(a=1, b=2)', 'f(___kwargs___=_, b=_, a=_)'), (True, 1, 'f(a=1, b=2)', 'f(b=_, a=_, ___kwargs___=_)'), (True, 1, 'f(a=1, b=2)', 'f(a=_, ___kwargs___=_, b=_)'), (True, 1, 'f(a=1, b=2)', 'f(b=_, ___kwargs___=_, a=_)'), (True, 1, 'b = 7; f(a=1, b=2)', '_x_ = _; f(_x_=_, _y_=_)'), (False, 0, 'b = 7; f(a=1, b=2)', '_x_ = _; f(_x_=1, _y_=_)'), (True, 1, 'x or y or z', '_x_ or ___rest___'), (True, 1, 'x or y or z', '_x_ or _y_ or ___rest___'), (True, 1, 'x or y or z', '_x_ or _y_ or _z_ or ___rest___'), (True, 1, 'def f(x=3):\n  return x', 'def _f_(x=3):\n  return x'), (True, 1, 'def f(x=3):\n  return x', 'def _f_(_=3):\n  return _'), (True, 1, 'def f(x=3):\n  return x', 'def _f_(_=3):\n  ___'), (True, 1, 'def f(x=3):\n  return x', 'def _f_(_x_=3):\n  return _x_'), (True, 1, 'def f(y=7):\n  return y', 'def _f_(_x_=_y_):\n  return _x_'), (False, 0, 'def f(x=3):\n  return x', 'def _f_(_y_=7):\n  return _x_'), (True, 1, 'def f(x=12):\n  return x', 'def _f_(_=_):\n  ___'), (True, 1, 'def f(x=17):\n  return x', 'def _f_(_=17, ___=_):\n  ___'), (True, 1, 'def f(x=17):\n  return x', 'def _f_(___, _=17):\n  ___'), (True, 1, 'def f(x=3, y=4):\n  return x', 'def _f_(_=3, _=4):\n  ___'), (True, 1, 'def f(x=5, y=6):\n  return x', 'def _f_(_=_, _=_):\n  ___'), (False, 0, 'def f(x=7, y=8):\n  return x', 'def _f_(___):\n  ___'), (True, 1, 'def f(x=9, y=10):\n  return x', 'def _f_(___=_):\n  ___'), (True, 1, 'def f(x=y+3):\n  return x', 'def _f_(_=y+3):\n  ___'), (True, 1, 'def f(*a, x=5):\n  return x', 'def _f_(*_, _x_=5):\n  return _x_'), (False, 0, 'def f(*a, x=6):\n  return x', 'def _f_(___, _x_=6):\n  return _x_'), (True, 1, 'def f(*a, x=5, y=6):\n  return x, y', 'def _f_(*_, _x_=5, _y_=6):\n  return _x_, _y_'), (False, 0, 'def f(*a, x=7, y=8):\n  return x, y', 'def _f_(___, _x_=7, _y_=8):\n  return _x_, _y_'), (False, 0, 'def f():\n  """docstring"""', 'def _f_(___):\n  _a_str_'), (True, 1, 'def f(x):\n  """doc1"""\n  return x', 'def _f_(___):\n  ___', (lambda node, env: (ast.get_docstring(node, )) is not (None))), (False, 0, 'def f(x):\n  """doc2"""\n  return x', 'def _f_(___):\n  ___', (lambda node, env: ((ast.get_docstring(node, )) is (None)) or ((ast.get_docstring(node, ).strip()) == ('')))), (True, 1, 'def f(x):\n  """"""\n  return x', 'def _f_(___):\n  ___', (lambda node, env: ((ast.get_docstring(node, )) is (None)) or ((ast.get_docstring(node, ).strip()) == ('')))), (True, 1, 'def nodoc(x):\n  return x', 'def _f_(___):\n  ___', (lambda node, env: ((ast.get_docstring(node, )) is (None)) or ((ast.get_docstring(node, ).strip()) == ('')))), (True, 1, 'def f(x=y+3):\n  return x', 'def _f_(_=_+3):\n  ___'), (True, 1, 'def f(x, y, z):\n  return x', 'def _f_(___):\n  ___'), (True, 1, 'if x == 3:\n  return x\nelif not x == 3 and x > 5:\n  return x-2', 'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___'), (False, 0, 'if x == 3:\n  return x\nelif x > 5 and not x == 3:\n  return x-2', 'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___'), (False, 0, 'if x == 3:\n  return x\nelif x > 5 and x != 3:\n  return x-2', 'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___'), (True, 1, 'if x == 3:\n  return x\nelif x > 5 and not x == 3:\n  return x-2', 'if _cond_:\n  ___\nelif ___ and not _cond_:\n  ___'), (True, 1, 'if x == 3:\n  return x\nelif x > 5 and x != 3:\n  return x-2', 'if _n_ == _v_:\n  ___\nelif ___ and _n_ != _v_:\n  ___'), (False, 0, ('if x == 3:\n  return x\nelif not x == 3 and x > 5:\n  return x-2\n') + ('elif not x == 3 and x <= 5 and x < 0:\n  return 0'), 'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___'), (True, 1, ('if x == 3:\n  return x\nelif not x == 3 and x > 5:\n  return x-2\n') + ('elif not x == 3 and x <= 5 and x < 0:\n  return 0'), 'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___\nelif _:\n  ___'), (False, 0, (('if x == 3:\n  return x\nelif not x == 3 and x > 5:\n  return x-2\n') + ('elif not x == 3 and x <= 5 and x < 0:\n  return 0\n')) + ('elif not x == 3 and x <= 5 and x >= 0 and x == 1:\n  return 1.5'), 'if _cond_:\n  ___\nelif not _cond_ and ___:\n  ___\nelif _:\n  ___'), (True, 2, 'if x < 0:\n  x += 1\nelif x < 10:\n  x += 0.5\nelse:\n  x += 0.25', 'if _:\n  ___\nelse:\n  ___'), (True, 1, 'x == 3', '3 == x'), (False, 0, '1 + 2 + 3', '3 + 2 + 1'), (True, 1, '1 and 2 and 3', '3 and 2 and 1')]
    testNum = 1
    passes = 0
    fails = 0
    for test_spec in tests:
        if (len(test_spec, )) == (4):
            (expect_match, expect_count, ns, ps) = test_spec
            matchpred = predtrue
        else:
            if (len(test_spec, )) == (5):
                (expect_match, expect_count, ns, ps, matchpred) = test_spec
            else:
                print('Tests must have 4 or 5 parts!', )
                print(test_spec, )
                exit(1, )
        print(('$') + (('-') * (60)), )
        print('Test #{}'.format(testNum, ), )
        testNum += 1
        n = parse(ns, )
        n = (n.body[0].value if ((type(n.body[0], )) == (ast.Expr)) and ((len(n.body, )) == (1)) else (n.body[0] if (len(n.body, )) == (1) else n.body))
        p = parse_pattern(ps, )
        print(('Program: %s => %s') % ((ns, dump(n, ))), )
        if isinstance(ns, ast.FunctionDef, ):
            print(('Docstring: %s') % (ast.get_docstring(ns, )), )
        print(('Pattern: %s => %s') % ((ps, dump(p, ))), )
        if (matchpred) != (predtrue):
            print('Matchpred: {}'.format(matchpred.__name__, ), )
        for gen in [False, True]:
            result = match(n, p, gen=gen, matchpred=matchpred)
            if gen:
                result = takeone(result, )
                pass
            passed = (bool(result, )) == (expect_match)
            if passed:
                passes += 1
            else:
                fails += 1
                pass
            print(('match(gen=%s): %s  [%s]') % ((gen, bool(result, ), ('PASS' if passed else 'FAIL'))), )
        opt = find(n, p, matchpred=matchpred)
        findpassed = (bool(opt, )) == ((0) < (expect_count))
        if findpassed:
            passes += 1
        else:
            fails += 1
            pass
        print('find: {}  [{}]'.format(bool(opt, ), ('PASS' if findpassed else 'FAIL'), ), )
        c = count(n, p, matchpred=matchpred)
        if (c) == (expect_count):
            passes += 1
            print(('count: %s  [PASS]') % (c), )
        else:
            fails += 1
            print(('count: %s  [FAIL], expected %d') % ((c, expect_count)), )
            pass
        print('findall:', )
        nmatches = 0
        for (node, envs) in findall(n, p, matchpred=matchpred):
            print(('  %d.  %s') % ((nmatches, dump(node, ))), )
            for (i, env) in enumerate(envs, ):
                print(('      %s.  ') % (chr((ord('a', )) + (i), )), )
                for (k, v) in env.items():
                    print(('          %s = %s') % ((k, dump(v, ))), )
                    pass
                pass
            nmatches += 1
            pass
        assert (nmatches) == (c)
        print()
        pass
    print(('%d passed, %d failed') % ((passes, fails)), )
    with open(__file__, )as src:
        with open(('self_printed_') + (os.path.basename(__file__, )), 'w', )as dest:
            dest.write(source(ast.parse(src.read(), ), ), )
