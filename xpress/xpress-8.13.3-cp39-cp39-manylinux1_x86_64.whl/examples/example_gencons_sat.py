"""
This example solves boolean satisfiability problems (SAT).
Illustrates two different methods of modeling SAT problems using:
    (a) Uses xpress.And and xpress.Or
    (b) xpress.addgencons
(c) 2020 Fair Isaac Corporation
"""

import sys
import xpress as xp


def read_sat_instance(sat_instance):
    """
    Read the cnf file
    CNF file format description c.f. http://www.satcompetition.org/2009/format-benchmarks2009.html
    :param sat_instance: SAT instance in CNF format
    :return:
    """
    lines = []
    n_vars = 0  # Number of variables
    n_clauses = 0  # Number of clauses
    try:
        with open(sat_instance, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError as e:
        print("Input CNF file not found")
        sys.exit(-1)

    count = 0
    for line in lines:
        tokens = line.strip('\n').split()
        if tokens[0] == 'c':
            count += 1
            continue
        elif tokens[0] == 'p':
            if tokens[1] != 'cnf':
                print('error. input file not in cnf format')
                sys.exit(-1)
            n_vars = int(tokens[2])
            n_clauses = int(tokens[3])
            print('number of literals = {}. number of clauses = {}'.format(n_vars, n_clauses))
            count += 1
            break
    return n_vars, n_clauses, lines[count:]


def get_disjunctions(lines, x, nx=None):
    disjunctions = []
    for i in range(len(lines)):
        disjunction = []
        tokens = lines[i].strip('\n').split()
        N = range(len(tokens))
        for j in N:
            val = int(tokens[j])
            if val == 0:
                continue
            if nx is not None:
                expr = nx[-val - 1] if val < 0 else x[val - 1]
            else:
                expr = 1 - x[-val - 1] if val < 0 else x[val - 1]
            disjunction.append(expr)
        disjunctions.append(disjunction)
    return disjunctions


def create_and_solve_model(n_vars, lines):
    """

    :param n_vars: number of literals
    :param lines: lines of the CNF file containing terms of the disjunctions
    :return:
    """
    # Create literals - binary variables
    x = [xp.var(vartype=xp.binary, name='x_{}'.format(i + 1)) for i in range(n_vars)]

    p = xp.problem()
    p.addVariable(x)
    disjunctions = get_disjunctions(lines, x)
    # print("SAT Formula:")
    # print(xp.And(*[xp.Or(*disjunctions[i]) for i in range(len(disjunctions))]))
    p.addConstraint(xp.And(*[xp.Or(*disjunctions[i]) for i in range(len(disjunctions))]) == 1)
    solve(p, x)


def create_and_solve_model_addgencons(n_vars, n_clauses, lines):
    """
    Another way to model SAT using problem.addgencons method
    :param n_vars:
    :param n_clauses:
    :param lines:
    :return:
    """
    # Create literals - binary variables
    x = [xp.var(vartype=xp.binary, name='x_{}'.format(i + 1)) for i in range(n_vars)]
    nx = [xp.var(vartype=xp.binary, name='nx_{}'.format(i + 1)) for i in range(n_vars)]
    # Create variables that will store the result of the disjunctive terms for bookkeeping
    y = [xp.var(vartype=xp.binary, name='y_{}'.format(j + 1)) for j in range(n_clauses)]
    is_satisfiable = xp.var(vartype=xp.binary, name='is_satisfiable')
    p = xp.problem()
    p.addVariable(x, nx, y, is_satisfiable)
    p.addConstraint([x[i] + nx[i] == 1 for i in range(n_vars)])
    disjunctions = get_disjunctions(lines, x, nx)
    con_type = [xp.gencons_or for _ in range(n_clauses)]
    con_type.append(xp.gencons_and)
    resultant = y
    resultant.append(is_satisfiable)
    col_start = []
    cur_count = 0
    for i in range(len(disjunctions)):
        col_start.append(cur_count)
        cur_count += len(disjunctions[i])
    col_start.append(cur_count)
    cols = [item for disjunction in disjunctions for item in disjunction]
    for i in range(n_clauses):
        cols.append(y[i])
    p.addgencons(con_type, resultant, col_start, cols, None, None)
    p.addConstraint(is_satisfiable == 1)
    solve(p, x, y)


def solve(prob, x, y=None):
    prob.setControl('maxtime', -300)  # 5 minutes
    prob.solve()
    prob_status = prob.getProbStatusString()
    print("Problem status is {}".format(prob_status))
    if prob_status == 'nlp_globally_optimal' or prob_status == 'mip_optimal':
        print(prob_status)
        x_sol = prob.getSolution(x)
        y_sol = prob.getSolution(y)
        for i in range(len(x)):
            print('{} = {}'.format(x[i], x_sol[i]))
        if y is not None:
            for j in range(len(y)):
                print('{} = {}'.format(y[j], y_sol[j]))
        print("Formula satisfiable")
    elif prob_status == 'nlp_infeasible' or prob_status == 'mip_infeas':
        print("Formula unsatisfiable ")
    else:
        print("Satisfiability unknown")


def run_sat_solver(sat_instance):
    n_vars, n_clauses, lines = read_sat_instance(sat_instance)
    print("Literals = {}. Clauses = {}".format(n_vars, n_clauses))
    create_and_solve_model(n_vars, lines)
    # create_and_solve_model_addgencons(n_vars, n_clauses, lines)  # Uncomment to run the alternate version


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python gencons_sat.py <cnf-file>", file=sys.stderr)
        sys.exit(-1)
    f_name = sys.argv[1]
    run_sat_solver(f_name)
