"""
This example builds a Pseudoboolean optimization solver that uses
the Xpress Optimizer library's General Constraints

c.f. http://www.cril.univ-artois.fr/PB16/
http://www.cril.univ-artois.fr/PB16/format.pdf
Parser loosely based on http://www.cril.univ-artois.fr/PB16/parser/SimpleParser.cc
(c) 2020 Fair Isaac Corporation
"""

import sys
import re
import xpress as xp


class Term:
    def __init__(self, cons, conj):
        """
        :param cons: coefficient
        :param conj: list of variables in the product
        """
        self.constant = cons
        self.conjunction = conj


class Constraint:
    def __init__(self, trms, sns, r):
        """

        :param trms: List of terms in the constraint
        :param sns: Sense
        :param r: RHS
        """
        self.terms = trms
        self.sense = sns
        self.rhs = r


def ignore_ws(fh):
    """
    Skip whitespaces.
    :param fh: file object
    :return:
    """
    while True:
        ch = fh.read(1)
        if ch == ' ':
            continue
        else:
            move_back(fh)
            break


def read_constant(fh):
    """

    :param fh: file object
    :return: coefficient before a term in an expression
    """
    constant = ''
    while True:
        ch = fh.read(1)
        if ch == 'x' or ch == '~' or ch == ' ' or ch == ';':
            move_back(fh)
            break
        else:
            constant += ch
    return float(constant) if constant != '' else 1.0


def move_back(fh):
    """
    move file ptr one step back
    :param fh: file object
    :return:
    """
    fh.seek(fh.tell() - 1)


def read_variable(fh):
    """
    read the variable indentifier
    :param fh: file object
    :return: variable as string
    """
    ch = fh.read(1)
    if ch != 'x':
        print("Error. No variable identifier after negation at fpos {}".format(fh.tell() - 1))
        sys.exit(-1)
    # read the variable index
    index = ''
    while True:
        ch = fh.read(1)
        if ch == ' ':
            move_back(fh)
            break
        index += ch
    if index == ' ':
        print("Error. No index after identifier at fpos {}".format(fh.tell() - 1))
        sys.exit(-1)
    return 'x' + index


def read_conj(fh):
    """
    read the terms in a conjunction
    :param fh: file object
    :return: list of variables (with negations identified by '~' preceding the variable)
    """
    conj = []
    while True:
        ignore_ws(fh)
        ch = fh.read(1)
        if ch == '+' or ch == '-' or ch == '=' or ch == '<' or ch == '>' or ch == ';':
            move_back(fh)
            break
        if ch == '~':
            conj.append('~' + read_variable(fh))
        else:
            move_back(fh)
            conj.append(read_variable(fh))
    return conj


def read_term(fh):
    """
    read the entire term of an expression
    :param fh: file object
    :return: term of an expression, including the constant
    """
    constant = read_constant(fh)
    ignore_ws(fh)
    conj = read_conj(fh)
    if conj is []:
        print("Error. Term returned zero or constant at pos {}".format(fh.tell()))
        sys.exit(0)
    return Term(constant, conj)


def get_objective(fh):
    """
    get the objective term
    :param fh: file object
    :return: objective sense, list of terms in the objective
    """
    o_terms = []
    o_sense = None
    # Ignore comments
    ch = ''
    while True:
        ch = fh.read(1)
        if ch == '*':
            fh.readline()
        else:
            break
    # Read objective:
    if ch == 'm':
        s = fh.read(2)
        o_sense = ch + s
        fh.read(1)  # skip the colon
        while True:
            ignore_ws(fh)
            ch = fh.read(1)
            if ch == ';':
                fh.read(1)  # skip newline
                break
            else:
                move_back(fh)
                term = read_term(fh)
                o_terms.append(term)

    return o_sense, o_terms


def get_constraint(fh):
    """
    reads all constraints
    :param fh: file object
    :return: list of constraint objects
    """
    cons = []
    c_sense = ''
    c_rhs = None
    c_expr = []

    while True:
        ignore_ws(fh)
        ch = fh.read(1)
        if ch == '\n':
            break
        elif ch == ';':
            cons.append(Constraint(c_expr, c_sense, c_rhs))
            if len(cons) % 10000 == 0:
                print("Read ", len(cons), "cons")
            c_sense = ''
            c_rhs = None
            c_expr = []
            fh.read(1)  # skip newline
        elif ch == '*':
            fh.readline()
        elif ch == '>':
            c_sense = '>='
            fh.read(1)
            ignore_ws(fh)
            c_rhs = read_constant(fh)
        elif ch == '<':
            fh.read(1)
            c_sense = '<='
            ignore_ws(fh)
            c_rhs = read_constant(fh)
        elif ch == '=':
            ignore_ws(fh)
            c_sense = '='
            c_rhs = read_constant(fh)
        else:
            move_back(fh)
            term = read_term(fh)
            c_expr.append(term)

    return cons


def build_expr(terms, variables):
    """

    :param terms: List of Term objects in the expression
    :param variables: Xpress variables expressed in a dictionary
    :return: Xpress expression
    """
    expr = None
    for term in terms:
        coeff = term.constant
        conjunction = term.conjunction
        if len(conjunction) == 1:  # linear
            expr = coeff * variables[conjunction[0]] if expr is None else expr + coeff * variables[conjunction[0]]
        else:
            conj_terms = []
            for item in conjunction:
                if item.startswith('~'):
                    conj_terms.append(1 - variables[item[1:]])
                else:
                    conj_terms.append(variables[item])
            expr = coeff * xp.And(*conj_terms) if expr is None else expr + coeff * xp.And(*conj_terms)
    return expr


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('A MIP-based Pseudoboolean solver')
        print('Usage: python example_gencons_pbo_solver.py <filename.opb>')
        sys.exit(-1)
    else:
        fname = sys.argv[1]
    try:
        with open(fname, 'r') as pbo:
            line = pbo.readline()
            # Read metadata
            pat = re.compile(r'#variable= (\d+)\s+#constraint= (\d+)')
            match = re.search(pat, line)
            if match:
                n_vars = int(match.group(1))
                n_cons = int(match.group(2))
                print(line)
            else:
                print('Problem metadata not provided on line 1')
                sys.exit(-1)
            pbo.seek(0)
            obj_sense, obj_terms = get_objective(pbo)
            print("Reading objective complete")
            constraints = get_constraint(pbo)
            print("Reading constraints complete")
            # Create the problem
            p = xp.problem()
            # Define the variables
            var_keys = ['x{}'.format(i) for i in range(1, n_vars + 1)]
            x = {i: xp.var(vartype=xp.binary) for i in var_keys}
            p.addVariable(x)
            # Add objective
            if len(obj_terms) > 1:
                obj_expr = build_expr(obj_terms, x)
                xp_sense = xp.minimize if obj_sense == 'min' else xp.maximize
                p.setObjective(obj_expr, sense=xp_sense)
            # Add constraints
            for constraint in constraints:
                cons_expr = build_expr(constraint.terms, x)
                rhs = constraint.rhs
                sense = constraint.sense
                # print(cons_expr, sense, rhs)
                if sense == '<=':
                    p.addConstraint(cons_expr <= rhs)
                elif sense == '>=':
                    p.addConstraint(cons_expr >= rhs)
                else:
                    p.addConstraint(cons_expr == rhs)
            print('Finished adding constraints')
            # Set a time limit (no limit otherwise)
            # p.setControl('maxtime', -900)
            p.solve()

    except FileNotFoundError:
        print("PBO instance file not found")
        sys.exit(-1)
