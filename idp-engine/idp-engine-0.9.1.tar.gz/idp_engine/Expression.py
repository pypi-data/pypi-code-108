# Copyright 2019 Ingmar Dasseville, Pierre Carbonnelle
#
# This file is part of Interactive_Consultant.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""


(They are monkey-patched by other modules)

"""
__all__ = ["ASTNode", "Expression", "Constructor", "AIfExpr", "Quantee", "AQuantification",
           "Operator", "AImplication", "AEquivalence", "ARImplication",
           "ADisjunction", "AConjunction", "AComparison", "ASumMinus",
           "AMultDiv", "APower", "AUnary", "AAggregate", "AppliedSymbol",
           "UnappliedSymbol", "Variable",
           "Number", "Brackets", "TRUE", "FALSE", "ZERO", "ONE"]

import copy
from collections import ChainMap
from datetime import date
from fractions import Fraction
from re import findall
from sys import intern
from textx import get_location
from typing import Optional, List, Tuple, Dict, Set, Any

from .utils import unquote, OrderedSet, BOOL, INT, REAL, DATE, CONCEPT, RESERVED_SYMBOLS, \
    IDPZ3Error, DEF_SEMANTICS, Semantics


class ASTNode(object):
    """superclass of all AST nodes
    """

    def check(self, condition, msg):
        """raises an exception if `condition` is not True

        Args:
            condition (Bool): condition to be satisfied
            msg (str): error message

        Raises:
            IDPZ3Error: when `condition` is not met
        """
        if not condition:
            try:
                location = get_location(self)
            except:
                raise IDPZ3Error(f"{msg}")
            line = location['line']
            col = location['col']
            raise IDPZ3Error(f"Error on line {line}, col {col}: {msg}")

    def dedup_nodes(self, kwargs, arg_name):
        """pops `arg_name` from kwargs as a list of named items
        and returns a mapping from name to items

        Args:
            kwargs (Dict[str, ASTNode])
            arg_name (str): name of the kwargs argument, e.g. "interpretations"

        Returns:
            Dict[str, ASTNode]: mapping from `name` to AST nodes

        Raises:
            AssertionError: in case of duplicate name
        """
        ast_nodes = kwargs.pop(arg_name)
        out = {}
        for i in ast_nodes:
            # can't get location here
            assert i.name not in out, f"Duplicate '{i.name}' in {arg_name}"
            out[i.name] = i
        return out

    def annotate(self, idp):
        return  # monkey-patched

    def annotate1(self, idp):
        return  # monkey-patched

    def interpret(self, problem: Any) -> "Expression":
        return self  # monkey-patched


class Annotations(ASTNode):
    def __init__(self, **kwargs):
        annotations = kwargs.pop('annotations')

        self.annotations = {}
        for s in annotations:
            p = s.split(':', 1)
            if len(p) == 2:
                try:
                    # Do we have a Slider?
                    # The format of p[1] is as follows:
                    # (lower_sym, upper_sym): (lower_bound, upper_bound)
                    pat = r"\(((.*?), (.*?))\)"
                    arg = findall(pat, p[1])
                    l_symb = arg[0][1]
                    u_symb = arg[0][2]
                    l_bound = arg[1][1]
                    u_bound = arg[1][2]
                    slider_arg = {'lower_symbol': l_symb,
                                  'upper_symbol': u_symb,
                                  'lower_bound': l_bound,
                                  'upper_bound': u_bound}
                    k, v = (p[0], slider_arg)
                except:  # could not parse the slider data
                    k, v = (p[0], p[1])
            else:
                k, v = ('reading', p[0])
            self.check(k not in self.annotations,
                       f"Duplicate annotation: [{k}: {v}]")
            self.annotations[k] = v


class Constructor(ASTNode):
    """Constructor declaration

    Attributes:
        name (string): name of the constructor

        sorts (List[Symbol]): types of the arguments of the constructor

        type (string): name of the type that contains this constructor

        arity (Int): number of arguments of the constructor

        tester (SymbolDeclaration): function to test if the constructor
        has been applied to some arguments (e.g., is_rgb)

        symbol (Symbol): only for Symbol constructors
    """

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        self.sorts = kwargs.pop('args') if 'args' in kwargs else []

        self.name = (self.name.s.name if type(self.name) == UnappliedSymbol else
                     self.name)
        self.arity = len(self.sorts)

        self.type = None
        self.symbol = None
        self.tester = None

    def __str__(self):
        return (self.name if not self.sorts else
                f"{self.name}({','.join((str(a) for a in self.sorts))}" )


class Accessor(ASTNode):
    """represents an accessor and a type

    Attributes:
        accessor (Symbol, Optional): name of accessor function

        type (string): name of the output type of the accessor

        decl (SymbolDeclaration): declaration of the accessor function
    """
    def __init__(self, **kwargs):
        self.accessor = kwargs.pop('accessor') if 'accessor' in kwargs else None
        self.type = kwargs.pop('type').name
        self.decl = None

    def __str__(self):
        return (self.type if not self.accessor else
                f"{self.accessor}: {self.type}" )


class Expression(ASTNode):
    """The abstract class of AST nodes representing (sub-)expressions.

    Attributes:
        code (string):
            Textual representation of the expression.  Often used as a key.

            It is generated from the sub-tree.
            Some tree transformations change it (e.g., instantiate),
            others don't.

        sub_exprs (List[Expression]):
            The children of the AST node.

            The list may be reduced by simplification.

        type (string):
            The name of the type of the expression, e.g., ``bool``.

        co_constraint (Expression, optional):
            A constraint attached to the node.

            For example, the co_constraint of ``square(length(top()))`` is
            ``square(length(top())) = length(top())*length(top()).``,
            assuming ``square`` is appropriately defined.

            The co_constraint of a defined symbol applied to arguments
            is the instantiation of the definition for those arguments.
            This is useful for definitions over infinite domains,
            as well as to compute relevant questions.

        simpler (Expression, optional):
            A simpler, equivalent expression.

            Equivalence is computed in the context of the theory and structure.
            Simplifying an expression is useful for efficiency
            and to compute relevant questions.

        value (Optional[Expression]):
            A rigid term equivalent to the expression, obtained by
            transformation.

            Equivalence is computed in the context of the theory and structure.

        annotations (Dict[str, str]):
            The set of annotations given by the expert in the IDP-Z3 program.

            ``annotations['reading']`` is the annotation
            giving the intended meaning of the expression (in English).

        original (Expression):
            The original expression, before propagation and simplification.

        variables (Set(string)):
            The set of names of the variables in the expression.

        is_type_constraint_for (string):
            name of the symbol for which the expression is a type constraint

    """
    __slots__ = ('sub_exprs', 'simpler', 'value', 'code',
                 'annotations', 'original', 'str', 'variables', 'type',
                 'is_type_constraint_for', 'co_constraint',
                 'questions', 'relevant')

    def __init__(self):
        self.sub_exprs: List["Expression"]
        self.simpler: Optional["Expression"] = None
        self.value: Optional["Expression"] = None

        self.code: str = intern(str(self))
        if not hasattr(self, 'annotations') or self.annotations == None:
            self.annotations: Dict[str, str] = {'reading': self.code}
        elif type(self.annotations) == Annotations:
            self.annotations = self.annotations.annotations
        self.original: Expression = self

        self.str: str = self.code
        self.variables: Optional[Set[str]] = None
        self.type: Optional[str] = None
        self.is_type_constraint_for: Optional[str] = None
        self.co_constraint: Optional["Expression"] = None

        # attributes of the top node of a (co-)constraint
        self.questions: Optional[OrderedSet] = None
        self.relevant: Optional[bool] = None

    def copy(self):
        " create a deep copy (except for rigid terms and variables) "
        if self.value == self:
            return self
        out = copy.copy(self)
        out.sub_exprs = [e.copy() for e in out.sub_exprs]
        out.variables = copy.copy(out.variables)
        out.value = None if out.value is None else out.value.copy()
        out.simpler = None if out.simpler is None else out.simpler.copy()
        out.co_constraint = (None if out.co_constraint is None
                             else out.co_constraint.copy())
        if hasattr(self, 'questions'):
            out.questions = copy.copy(self.questions)
        return out

    def same_as(self, other):
        if self.str == other.str:
            return True
        if self.value is not None and self.value is not self:
            return self.value  .same_as(other)
        if self.simpler is not None:
            return self.simpler.same_as(other)
        if other.value is not None and other.value is not other:
            return self.same_as(other.value)
        if other.simpler is not None:
            return self.same_as(other.simpler)

        if (isinstance(self, Brackets)
           or (isinstance(self, AQuantification) and len(self.quantees) == 0)):
            return self.sub_exprs[0].same_as(other)
        if (isinstance(other, Brackets)
           or (isinstance(other, AQuantification) and len(other.quantees) == 0)):
            return self.same_as(other.sub_exprs[0])

        return self.str == other.str and type(self) == type(other)

    def __repr__(self): return str(self)

    def __str__(self):
        if self.value is not None and self.value is not self:
            return str(self.value)
        if self.simpler is not None:
            return str(self.simpler)
        return self.__str1__()

    def __log__(self):  # for debugWithYamlLog
        return {'class': type(self).__name__,
                'code': self.code,
                'str': self.str,
                'co_constraint': self.co_constraint}

    def collect(self, questions, all_=True, co_constraints=True):
        """collects the questions in self.

        `questions` is an OrderedSet of Expression
        Questions are the terms and the simplest sub-formula that
        can be evaluated.
        `collect` uses the simplified version of the expression.

        all_=False : ignore expanded formulas
        and AppliedSymbol interpreted in a structure
        co_constraints=False : ignore co_constraints

        default implementation for UnappliedSymbol, AIfExpr, AUnary, Variable,
        Number_constant, Brackets
        """
        for e in self.sub_exprs:
            e.collect(questions, all_, co_constraints)

    def collect_symbols(self, symbols=None, co_constraints=True):
        """ returns the list of symbol declarations in self, ignoring type constraints

        returns Dict[name, Declaration]
        """
        symbols = {} if symbols == None else symbols
        if self.is_type_constraint_for is None:  # ignore type constraints
            if (hasattr(self, 'decl') and self.decl
                and type(self.decl) != Constructor
                and not self.decl.name in RESERVED_SYMBOLS):
                symbols[self.decl.name] = self.decl
            for e in self.sub_exprs:
                e.collect_symbols(symbols, co_constraints)
        return symbols

    def collect_nested_symbols(self, symbols, is_nested):
        """ returns the set of symbol declarations that occur (in)directly
        under an aggregate or some nested term, where is_nested is flipped
        to True the moment we reach such an expression

        returns {SymbolDeclaration}
        """
        for e in self.sub_exprs:
            e.collect_nested_symbols(symbols, is_nested)
        return symbols

    def generate_constructors(self, constructors: dict):
        """ fills the list `constructors` with all constructors belonging to
        open types.
        """
        for e in self.sub_exprs:
            e.generate_constructors(constructors)

    def co_constraints(self, co_constraints):
        """ collects the constraints attached to AST nodes, e.g. instantiated
        definitions

        `co_constraints` is an OrderedSet of Expression
        """
        if self.co_constraint is not None and self.co_constraint not in co_constraints:
            co_constraints.append(self.co_constraint)
            self.co_constraint.co_constraints(co_constraints)
        for e in self.sub_exprs:
            e.co_constraints(co_constraints)

    def is_reified(self): return True

    def is_assignment(self) -> bool:
        """

        Returns:
            bool: True if `self` assigns a rigid term to a rigid function application
        """
        return False

    def has_decision(self):
        # returns true if it contains a variable declared in decision
        # vocabulary
        return any(e.has_decision() for e in self.sub_exprs)

    def type_inference(self):
        # returns a dictionary {Variable : Symbol}
        try:
            return dict(ChainMap(*(e.type_inference() for e in self.sub_exprs)))
        except AttributeError as e:
            if "has no attribute 'sorts'" in str(e):
                msg = f"Incorrect arity for {self}"
            else:
                msg = f"Unknown error for {self}"
            self.check(False, msg)

    def __str1__(self) -> str:
        return ''  # monkey-patched

    def update_exprs(self, new_exprs) -> "Expression":
        return self  # monkey-patched

    def simplify1(self) -> "Expression":
        return self  # monkey-patched

    def substitute(self,
                   e0: "Expression",
                   e1: "Expression",
                   assignments: "Assignments",
                   tag=None) -> "Expression":
        return self  # monkey-patched

    def instantiate(self,
                    e0: List["Expression"],
                    e1: List["Expression"],
                    problem: "Theory"=None
                    ) -> "Expression":
        return self  # monkey-patched

    def instantiate1(self,
                    e0: "Expression",
                    e1: "Expression",
                    problem: "Theory"=None
                    ) -> "Expression":
        return self  # monkey-patched

    def simplify_with(self, assignments: "Assignments") -> "Expression":
        return self  # monkey-patched

    def symbolic_propagate(self,
                           assignments: "Assignments",
                           tag: "Status",
                           truth: Optional["Expression"] = None
                           ):
        return  # monkey-patched

    def propagate1(self,
                   assignments: "Assignments",
                   tag: "Status",
                   truth: Optional["Expression"] = None
                   ):
        return  # monkey-patched

    def translate(self, problem: "Theory", vars={}):
        pass  # monkey-patched

    def reified(self, problem: "Theory"):
        pass  # monkey-patched

    def translate1(self, problem: "Theory", vars={}):
        pass  # monkey-patched

    def as_set_condition(self) -> Tuple[Optional["AppliedSymbol"], Optional[bool], Optional["Enumeration"]]:
        """Returns an equivalent expression of the type "x in y", or None

        Returns:
            Tuple[Optional[AppliedSymbol], Optional[bool], Optional[Enumeration]]: meaning "expr is (not) in enumeration"
        """
        return (None, None, None)

    def split_equivalences(self):
        """Returns an equivalent expression where equivalences are replaced by
        implications

        Returns:
            Expression
        """
        out = self.update_exprs(e.split_equivalences() for e in self.sub_exprs)
        return out

    def add_level_mapping(self, level_symbols, head, pos_justification, polarity):
        """Returns an expression where level mapping atoms (e.g., lvl_p > lvl_q)
         are added to atoms containing recursive symbols.

        Arguments:
            - level_symbols (Dict[SymbolDeclaration, Symbol]): the level mapping
              symbols as well as their corresponding recursive symbols
            - head (AppliedSymbol): head of the rule we are adding level mapping
              symbols to.
            - pos_justification (Bool): whether we are adding symbols to the
              direct positive justification (e.g., head => body) or direct
              negative justification (e.g., body => head) part of the rule.
            - polarity (Bool): whether the current expression occurs under
              negation.

        Returns:
            Expression
        """
        return (self.update_exprs((e.add_level_mapping(level_symbols, head, pos_justification, polarity)
                                   for e in self.sub_exprs))
                    .annotate1())  # update .variables


class Symbol(Expression):
    """Represents a Symbol.  Handles synonyms.

    Attributes:
        name (string): name of the symbol
    """
    TO = {'Bool': BOOL, 'Int': INT, 'Real': REAL,
          '`Bool': '`'+BOOL, '`Int': '`'+INT, '`Real': '`'+REAL,}

    def __init__(self, **kwargs):
        self.name = unquote(kwargs.pop('name'))
        self.name = Symbol.TO.get(self.name, self.name)
        self.sub_exprs = []
        self.decl = None
        super().__init__()
        self.variables = set()
        self.value = self

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)


class Domain(Symbol):
    """ASTNode representing `aType` or `Concept[aSignature]`, e.g., `Concept[T*T->Bool]`

    Args:
        name (Symbol): name of the concept

        ins (List[Symbol], Optional): domain of the signature, e.g., `[T, T]`

        out (Symbol, Optional): range of the signature, e.g., `Bool`
    """

    def __init__(self, **kwargs):
        self.ins = kwargs.pop('ins', None)
        self.out = kwargs.pop('out', None)
        super().__init__(**kwargs)

    def __str__(self):
        return self.name + ("" if not self.ins else
                            f"[{'*'.join(str(s) for s in self.ins)}->{self.out}]")

    def range():
        pass  # monkey-patched


class AIfExpr(Expression):
    PRECEDENCE = 10
    IF = 0
    THEN = 1
    ELSE = 2

    def __init__(self, **kwargs):
        self.if_f = kwargs.pop('if_f')
        self.then_f = kwargs.pop('then_f')
        self.else_f = kwargs.pop('else_f')

        self.sub_exprs = [self.if_f, self.then_f, self.else_f]
        super().__init__()

    @classmethod
    def make(cls, if_f, then_f, else_f):
        out = (cls)(if_f=if_f, then_f=then_f, else_f=else_f)
        return out.annotate1().simplify1()

    def __str1__(self):
        return (f" if   {self.sub_exprs[AIfExpr.IF  ].str}"
                f" then {self.sub_exprs[AIfExpr.THEN].str}"
                f" else {self.sub_exprs[AIfExpr.ELSE].str}")

    def collect_nested_symbols(self, symbols, is_nested):
        return Expression.collect_nested_symbols(self, symbols, True)


class Quantee(Expression):
    """represents the description of quantification, e.g., `x in T` or `(x,y) in P`
    The `Concept` type may be qualified, e.g. `Concept[Color->Bool]`

    Attributes:
        vars (List[List[Variable]): the (tuples of) variables being quantified

        domain (Domain, Optional): a literal Domain to quantify over, e.g., `Color` or `Concept[Color->Bool]`.

        sort (SymbolExpr, Optional): a dereferencing expression, e.g.,. `$(i)`.

        sub_exprs (List[SymbolExpr], Optional): the (unqualified) type or predicate to quantify over,
        e.g., `[Color], [Concept] or [$(i)]`.

        arity (int): the length of the tuple of variables

        decl (SymbolDeclaration, Optional): the (unqualified) Declaration to quantify over, after resolution of `$(i)`.
        e.g., the declaration of `Color`
    """
    def __init__(self, **kwargs):
        self.vars = kwargs.pop('vars')
        self.domain = kwargs.pop('domain') if 'domain' in kwargs else None
        sort = kwargs.pop('sort') if 'sort' in kwargs else None
        if self.domain:
            self.check(not (self.domain.name != CONCEPT and 0 <len(self.domain.ins)),
                   f"Can't use signature after predicate {self.domain.name}")

        self.sub_exprs = ([sort] if sort else
                          [self.domain] if self.domain else
                          [])
        self.arity = None
        for i, v in enumerate(self.vars):
            if hasattr(v, 'vars'):  # varTuple
                self.vars[i] = v.vars
                self.arity = len(v.vars) if self.arity == None else self.arity
            else:
                self.vars[i] = [v]
                self.arity = 1 if self.arity == None else self.arity

        super().__init__()
        self.decl = None

        self.check(all(len(v) == self.arity for v in self.vars),
                    f"Inconsistent tuples in {self}")

    @classmethod
    def make(cls, var, sort):
        out = (cls) (vars=[var], sort=sort)
        return out.annotate1()

    def __str1__(self):
        signature = ("" if len(self.sub_exprs) <= 1 else
                     f"[{','.join(t.str for t in self.sub_exprs[1:-1])}->{self.sub_exprs[-1]}]"
        )
        return (f"{','.join(str(v) for vs in self.vars for v in vs)} "
                f"∈ {self.sub_exprs[0] if self.sub_exprs else None}"
                f"{signature}")


class AQuantification(Expression):
    PRECEDENCE = 20

    def __init__(self, **kwargs):
        self.annotations = kwargs.pop('annotations')
        self.q = kwargs.pop('q')
        self.quantees = kwargs.pop('quantees')
        self.f = kwargs.pop('f')

        self.q = '∀' if self.q == '!' else '∃' if self.q == "?" else self.q
        if self.quantees and not self.quantees[-1].sub_exprs:
            # separate untyped variables, so that they can be typed separately
            q = self.quantees.pop()
            for vars in q.vars:
                for var in vars:
                    self.quantees.append(Quantee.make(var, None))

        self.sub_exprs = [self.f]
        super().__init__()

        self.type = BOOL

    @classmethod
    def make(cls, q, quantees, f, annotations=None):
        "make and annotate a quantified formula"
        out = cls(annotations=annotations, q=q, quantees=quantees, f=f)
        return out.annotate1()

    def __str1__(self):
        if self.quantees:  #TODO this is not correct in case of partial expansion
            vars = ','.join([f"{q}" for q in self.quantees])
            return f"{self.q}{vars} : {self.sub_exprs[0].str}"
        else:
            return self.sub_exprs[0].str

    def copy(self):
        # also called by AAgregate
        out = Expression.copy(self)
        out.quantees = [q.copy() for q in out.quantees]
        return out

    def collect(self, questions, all_=True, co_constraints=True):
        questions.append(self)
        if all_:
            Expression.collect(self, questions, all_, co_constraints)
            for q in self.quantees:
                q.collect(questions, all_, co_constraints)

    def collect_symbols(self, symbols=None, co_constraints=True):
        symbols = Expression.collect_symbols(self, symbols, co_constraints)
        for q in self.quantees:
            q.collect_symbols(symbols, co_constraints)
        return symbols

def FORALL(qs, expr, annotations=None):
    return AQuantification.make('∀', qs, expr, annotations)
def EXISTS(qs, expr, annotations=None):
    return AQuantification.make('∃', qs, expr, annotations)

class Operator(Expression):
    PRECEDENCE = 0  # monkey-patched
    MAP = dict()  # monkey-patched

    def __init__(self, **kwargs):
        self.sub_exprs = kwargs.pop('sub_exprs')
        self.operator = kwargs.pop('operator')

        self.operator = list(map(
            lambda op: "≤" if op == "=<" else "≥" if op == ">=" else "≠" if op == "~=" else \
                "⇔" if op == "<=>" else "⇐" if op == "<=" else "⇒" if op == "=>" else \
                "∨" if op == "|" else "∧" if op == "&" else "⨯" if op == "*" else op
            , self.operator))

        super().__init__()

        self.type = BOOL if self.operator[0] in '&|∧∨⇒⇐⇔' \
               else BOOL if self.operator[0] in '=<>≤≥≠' \
               else None

    @classmethod
    def make(cls, ops, operands, annotations=None):
        """ creates a BinaryOp
            beware: cls must be specific for ops !
        """
        if len(operands) == 0:
            if cls == AConjunction:
                return TRUE
            if cls == ADisjunction:
                return FALSE
            raise "Internal error"
        if len(operands) == 1:
            return operands[0]
        if isinstance(ops, str):
            ops = [ops] * (len(operands)-1)
        out = (cls)(annotations=annotations, sub_exprs=operands, operator=ops)
        if annotations:
            out.annotations = annotations
        return out.annotate1().simplify1()

    def __str1__(self):
        def parenthesis(precedence, x):
            return f"({x.str})" if type(x).PRECEDENCE <= precedence else f"{x.str}"
        precedence = type(self).PRECEDENCE
        temp = parenthesis(precedence, self.sub_exprs[0])
        for i in range(1, len(self.sub_exprs)):
            temp += f" {self.operator[i-1]} {parenthesis(precedence, self.sub_exprs[i])}"
        return temp

    def collect(self, questions, all_=True, co_constraints=True):
        if self.operator[0] in '=<>≤≥≠':
            questions.append(self)
        for e in self.sub_exprs:
            e.collect(questions, all_, co_constraints)

    def collect_nested_symbols(self, symbols, is_nested):
        return Expression.collect_nested_symbols(self, symbols,
                is_nested if self.operator[0] in ['∧','∨','⇒','⇐','⇔'] else True)


class AImplication(Operator):
    PRECEDENCE = 50

    def add_level_mapping(self, level_symbols, head, pos_justification, polarity):
        sub_exprs = [self.sub_exprs[0].add_level_mapping(level_symbols, head, pos_justification, not polarity),
                     self.sub_exprs[1].add_level_mapping(level_symbols, head, pos_justification, polarity)]
        return self.update_exprs(sub_exprs).annotate1()

def IMPLIES(exprs, annotations=None):
    return AImplication.make('⇒', exprs, annotations)

class AEquivalence(Operator):
    PRECEDENCE = 40

    # NOTE: also used to split rules into positive implication and negative implication. Please don't change.
    def split(self):
        posimpl = IMPLIES([self.sub_exprs[0], self.sub_exprs[1]])
        negimpl = RIMPLIES([self.sub_exprs[0].copy(), self.sub_exprs[1].copy()])
        return AND([posimpl, negimpl])

    def split_equivalences(self):
        out = self.update_exprs(e.split_equivalences() for e in self.sub_exprs)
        return out.split()

def EQUIV(exprs, annotations=None):
    return AEquivalence.make('⇔', exprs, annotations)

class ARImplication(Operator):
    PRECEDENCE = 30

    def add_level_mapping(self, level_symbols, head, pos_justification, polarity):
        sub_exprs = [self.sub_exprs[0].add_level_mapping(level_symbols, head, pos_justification, polarity),
                     self.sub_exprs[1].add_level_mapping(level_symbols, head, pos_justification, not polarity)]
        return self.update_exprs(sub_exprs).annotate1()

def RIMPLIES(exprs, annotations):
    return ARImplication.make('⇐', exprs, annotations)

class ADisjunction(Operator):
    PRECEDENCE = 60

    def __str1__(self):
        if not hasattr(self, 'enumerated'):
            return super().__str1__()
        return f"{self.sub_exprs[0].sub_exprs[0].code} in {{{self.enumerated}}}"

def OR(exprs):
    return ADisjunction.make('∨', exprs)

class AConjunction(Operator):
    PRECEDENCE = 70

def AND(exprs):
    return AConjunction.make('∧', exprs)

class AComparison(Operator):
    PRECEDENCE = 80

    def __init__(self, **kwargs):
        self.annotations = kwargs.pop('annotations')
        super().__init__(**kwargs)

    def is_assignment(self):
        # f(x)=y
        return len(self.sub_exprs) == 2 and \
                self.operator in [['='], ['≠']] \
                and isinstance(self.sub_exprs[0], AppliedSymbol) \
                and all(e.value is not None
                        for e in self.sub_exprs[0].sub_exprs) \
                and self.sub_exprs[1].value is not None

def EQUALS(exprs):
    return AComparison.make('=',exprs)

class ASumMinus(Operator):
    PRECEDENCE = 90


class AMultDiv(Operator):
    PRECEDENCE = 100


class APower(Operator):
    PRECEDENCE = 110


class AUnary(Expression):
    PRECEDENCE = 120
    MAP = dict()  # monkey-patched

    def __init__(self, **kwargs):
        self.f = kwargs.pop('f')
        self.operators = kwargs.pop('operators')
        self.operators = ['¬' if c == '~' else c for c in self.operators]
        self.operator = self.operators[0]
        self.check(all([c == self.operator for c in self.operators]),
                   "Incorrect mix of unary operators")

        self.sub_exprs = [self.f]
        super().__init__()

    @classmethod
    def make(cls, op, expr):
        out = AUnary(operators=[op], f=expr)
        return out.annotate1().simplify1()

    def __str1__(self):
        return f"{self.operator}({self.sub_exprs[0].str})"

    def add_level_mapping(self, level_symbols, head, pos_justification, polarity):
        sub_exprs = (e.add_level_mapping(level_symbols, head,
                                         pos_justification,
                                         not polarity
                                         if self.operator == '¬' else polarity)
                     for e in self.sub_exprs)
        return self.update_exprs(sub_exprs).annotate1()

def NOT(expr):
    return AUnary.make('¬', expr)

class AAggregate(Expression):
    PRECEDENCE = 130

    def __init__(self, **kwargs):
        self.aggtype = kwargs.pop('aggtype')
        self.quantees = kwargs.pop('quantees')
        self.f = kwargs.pop('f')

        self.aggtype = "#" if self.aggtype == "card" else self.aggtype
        self.sub_exprs = [self.f]  # later: expressions to be summed
        self.annotated = False  # cannot test q_vars, because aggregate may not have quantee
        self.q = ''
        super().__init__()


    def __str1__(self):
        if not self.annotated:
            vars = "".join([f"{q}" for q in self.quantees])
            out = ((f"{self.aggtype}(lambda {vars} : "
                    f"{self.sub_exprs[0].str}"
                    f")" ) if self.aggtype != "#" else
                   (f"{self.aggtype}{{{vars} : "
                    f"{self.sub_exprs[0].str}"
                    f"}}")
            )
        else:
            out = (f"{self.aggtype}{{"
                   f"{','.join(e.str for e in self.sub_exprs)}"
                   f"}}")
        return out

    def copy(self):
        return AQuantification.copy(self)

    def collect(self, questions, all_=True, co_constraints=True):
        if all_ or len(self.quantees) == 0:
            Expression.collect(self, questions, all_, co_constraints)
            for q in self.quantees:
                q.collect(questions, all_, co_constraints)

    def collect_symbols(self, symbols=None, co_constraints=True):
        return AQuantification.collect_symbols(self, symbols, co_constraints)

    def collect_nested_symbols(self, symbols, is_nested):
        return Expression.collect_nested_symbols(self, symbols, True)


class AppliedSymbol(Expression):
    """Represents a symbol applied to arguments

    Args:
        symbol (Expression): the symbol to be applied to arguments

        is_enumerated (string): '' or 'is enumerated' or 'is not enumerated'

        is_enumeration (string): '' or 'in' or 'not in'

        in_enumeration (Enumeration): the enumeration following 'in'

        decl (Declaration): the declaration of the symbol, if known

        in_head (Bool): True if the AppliedSymbol occurs in the head of a rule
    """
    PRECEDENCE = 200

    def __init__(self, **kwargs):
        self.annotations = kwargs.pop('annotations')
        self.symbol = kwargs.pop('symbol')
        self.sub_exprs = kwargs.pop('sub_exprs')
        if 'is_enumerated' in kwargs:
            self.is_enumerated = kwargs.pop('is_enumerated')
        else:
            self.is_enumerated = ''
        if 'is_enumeration' in kwargs:
            self.is_enumeration = kwargs.pop('is_enumeration')
            if self.is_enumeration == '∉':
                self.is_enumeration = 'not'
        else:
            self.is_enumeration = ''
        if 'in_enumeration' in kwargs:
            self.in_enumeration = kwargs.pop('in_enumeration')
        else:
            self.in_enumeration = None

        super().__init__()

        self.decl = None
        self.in_head = False

    @classmethod
    def make(cls, symbol, args, **kwargs):
        out = cls(annotations=None, symbol=symbol, sub_exprs=args, **kwargs)
        out.sub_exprs = args
        # annotate
        out.decl = symbol.decl
        return out.annotate1()

    @classmethod
    def construct(cls, constructor, args):
        out= cls.make(Symbol(name=constructor.name), args)
        out.decl = constructor
        out.variables = {}
        return out

    def __str1__(self):
        out = f"{self.symbol}({', '.join([x.str for x in self.sub_exprs])})"
        if self.in_enumeration:
            enum = f"{', '.join(str(e) for e in self.in_enumeration.tuples)}"
        return (f"{out}"
                f"{ ' '+self.is_enumerated if self.is_enumerated else ''}"
                f"{ f' {self.is_enumeration} {{{enum}}}' if self.in_enumeration else ''}")

    def copy(self):
        out = Expression.copy(self)
        out.symbol = out.symbol.copy()
        return out

    def collect(self, questions, all_=True, co_constraints=True):
        if self.decl and self.decl.name not in RESERVED_SYMBOLS:
            questions.append(self)
            if self.is_enumerated or self.in_enumeration:
                app = AppliedSymbol.make(self.symbol, self.sub_exprs)
                questions.append(app)
        self.symbol.collect(questions, all_, co_constraints)
        for e in self.sub_exprs:
            e.collect(questions, all_, co_constraints)
        if co_constraints and self.co_constraint is not None:
            self.co_constraint.collect(questions, all_, co_constraints)

    def collect_symbols(self, symbols=None, co_constraints=True):
        symbols = Expression.collect_symbols(self, symbols, co_constraints)
        self.symbol.collect_symbols(symbols, co_constraints)
        return symbols

    def collect_nested_symbols(self, symbols, is_nested):
        if is_nested and (hasattr(self, 'decl') and self.decl
            and type(self.decl) != Constructor
            and not self.decl.name in RESERVED_SYMBOLS):
            symbols.add(self.decl)
        for e in self.sub_exprs:
            e.collect_nested_symbols(symbols, True)
        return symbols

    def has_decision(self):
        self.check(self.decl.block is not None, "Internal error")
        return not self.decl.block.name == 'environment' \
            or any(e.has_decision() for e in self.sub_exprs)

    def type_inference(self):
        if self.symbol.decl:
            self.check(self.symbol.decl.arity == len(self.sub_exprs),
                f"Incorrect number of arguments in {self}: "
                f"should be {self.symbol.decl.arity}")
        try:
            out = {}
            for i, e in enumerate(self.sub_exprs):
                if self.decl and isinstance(e, Variable):
                    out[e.name] = self.decl.sorts[i]
                else:
                    out.update(e.type_inference())
            return out
        except AttributeError as e:
            #
            if "object has no attribute 'sorts'" in str(e):
                msg = f"Unexpected arity for symbol {self}"
            else:
                msg = f"Unknown error for symbol {self}"
            self.check(False, msg)

    def is_reified(self):
        return (self.in_enumeration or self.is_enumerated
                or not all(e.value is not None for e in self.sub_exprs))

    def reified(self, problem: "Theory"):
        return ( super().reified(problem) if self.is_reified() else
                 self.translate(problem) )

    def generate_constructors(self, constructors: dict):
        symbol = self.symbol.sub_exprs[0]
        if hasattr(symbol, 'name') and symbol.name in ['unit', 'heading']:
            constructor = Constructor(name=self.sub_exprs[0].name)
            constructors[symbol.name].append(constructor)

    def add_level_mapping(self, level_symbols, head, pos_justification, polarity):
        assert head.symbol.decl in level_symbols, \
               f"Internal error in level mapping: {self}"
        if self.symbol.decl not in level_symbols or self.in_head:
            return self
        else:
            if DEF_SEMANTICS == Semantics.WELLFOUNDED:
                op = ('>' if pos_justification else '≥') \
                    if polarity else ('≤' if pos_justification else '<')
            elif DEF_SEMANTICS == Semantics.KRIPKEKLEENE:
                op = '>' if polarity else '≤'
            else:
                assert DEF_SEMANTICS == Semantics.COINDUCTION, \
                        f"Internal error: DEF_SEMANTICS"
                op = ('≥' if pos_justification else '>') \
                    if polarity else ('<' if pos_justification else '≤')
            comp = AComparison.make(op, [
                AppliedSymbol.make(level_symbols[head.symbol.decl], head.sub_exprs),
                AppliedSymbol.make(level_symbols[self.symbol.decl], self.sub_exprs)
            ])
            if polarity:
                return AND([comp, self])
            else:
                return OR([comp, self])


class SymbolExpr(Expression):
    def __init__(self, **kwargs):
        self.eval = (kwargs.pop('eval') if 'eval' in kwargs else
                     '')
        self.sub_exprs = [kwargs.pop('s')]
        self.decl = self.sub_exprs[0].decl if not self.eval else None
        super().__init__()

    def __str1__(self):
        return (f"$({self.sub_exprs[0]})" if self.eval else
                f"{self.sub_exprs[0]}")

    def is_intentional(self):
        return self.eval

class UnappliedSymbol(Expression):
    """The result of parsing a symbol not applied to arguments.
    Can be a constructor or a quantified variable.

    Variables are converted to Variable() by annotate().
    """
    PRECEDENCE = 200

    def __init__(self, **kwargs):
        self.s = kwargs.pop('s')
        self.name = self.s.name

        Expression.__init__(self)

        self.sub_exprs = []
        self.decl = None
        self.is_enumerated = None
        self.is_enumeration = None
        self.in_enumeration = None
        self.value = self

    @classmethod
    def construct(cls, constructor: Constructor):
        """Create an UnappliedSymbol from a constructor
        """
        out = (cls)(s=Symbol(name=constructor.name))
        out.decl = constructor
        out.variables = {}
        return out

    def __str1__(self): return self.name

    def is_reified(self): return False


TRUEC = Constructor(name='true')
FALSEC = Constructor(name='false')

TRUE = UnappliedSymbol.construct(TRUEC)
FALSE = UnappliedSymbol.construct(FALSEC)

class Variable(Expression):
    """AST node for a variable in a quantification or aggregate

    Args:
        name (str): name of the variable

        sort (Optional[Symbol]): sort of the variable, if known
    """
    PRECEDENCE = 200

    def __init__(self, **kwargs):
        self.name = kwargs.pop('name')
        sort = kwargs.pop('sort') if 'sort' in kwargs else None
        self.sort = sort
        assert sort is None or isinstance(sort, Domain) or isinstance(sort, Symbol)

        super().__init__()

        self.type = sort.decl.name if sort and sort.decl else ''
        self.sub_exprs = []
        self.variables = set([self.name])

    def __str1__(self): return self.name

    def copy(self): return self

    def annotate1(self): return self


class Number(Expression):
    PRECEDENCE = 200

    def __init__(self, **kwargs):
        self.number = kwargs.pop('number')

        super().__init__()

        self.sub_exprs = []
        self.variables = set()
        self.value = self

        ops = self.number.split("/")
        if len(ops) == 2:  # possible with str_to_IDP on Z3 value
            self.py_value = Fraction(self.number)
            self.type = REAL
        elif '.' in self.number:
            v = (self.number if not self.number.endswith('?') else
                 self.number[:-1])
            if "e" in v:
                self.py_value = float(eval(v))
            else:
                self.py_value = Fraction(v)
            self.type = REAL
        else:
            self.py_value = int(self.number)
            self.type = INT

    def __str__(self): return self.number

    def is_reified(self): return False

    def real(self):
        """converts the INT number to REAL"""
        self.check(self.type in [INT, REAL], f"Can't convert {self} to {REAL}")
        return Number(number=str(float(self.py_value)))


ZERO = Number(number='0')
ONE = Number(number='1')


class Date(Expression):
    PRECEDENCE = 200

    def __init__(self, **kwargs):
        self.iso = kwargs.pop('iso')
        self.date = (date.today() if self.iso == '#TODAY' else
                     date.fromisoformat(self.iso[1:]))

        super().__init__()

        self.sub_exprs = []
        self.variables = set()
        self.value = self

        self.py_value = self.date.toordinal()
        self.type = DATE

    def __str__(self): return f"#{self.date.isoformat()}"

    def is_reified(self): return False


class Brackets(Expression):
    PRECEDENCE = 200

    def __init__(self, **kwargs):
        self.f = kwargs.pop('f')
        self.annotations = kwargs.pop('annotations')
        if not self.annotations:
            self.annotations = {'reading': self.f.annotations['reading']}
        self.sub_exprs = [self.f]

        super().__init__()


    # don't @use_value, to have parenthesis
    def __str__(self): return f"({self.sub_exprs[0].str})"
    def __str1__(self): return str(self)

