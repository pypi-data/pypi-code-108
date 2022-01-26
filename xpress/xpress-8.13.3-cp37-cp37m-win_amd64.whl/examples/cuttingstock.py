'''
Cutting stock model with column generation
(c) 2020 Fair Isaac Corporation
'''

import xpress as xp
import numpy as np

# Problem data
# widths = [17.0, 21.0, 22.5, 24.0, 29.5]
# demand = [150, 96, 48, 108, 227]
# max_width = 94.0
widths = [6, 11, 17, 21, 24, 28, 30, 33, 42, 49, 56, 69, 74, 87, 91]
demand = [9, 6, 20, 30, 17, 19, 25, 12, 8, 20, 5, 14, 15, 18, 10]
max_width = 100
eps = 1e-6
max_cols = 100


def solve_knapsack_problem(n_item_types, profit, resource_consumed, total_resource, demand):
    """
    Solve knapsack subproblem

    :param n_item_types: Total number of items
    :param profit: Profit of each item. 1-d numpy array
    :param resource_consumed: Resource consumed by each item. 1-d numpy array
    :param total_resource: total available resource
    :param demand: Demand for each item. 1-d numpy array
    :return:
        xbest: Number of items of type i used in an optimal solution
        zbest: Value of the optimial solution
    """
    N = range(n_item_types)
    p = xp.problem(name="knapsack")
    p.setControl('outputlog', 0)

    # Create a NumPy array of variable; specify dtype=xp.npvar to
    # ensure NumPy recognizes an array of Xpress variables rather than
    # objects.

    x = np.array([xp.var(name='use_{}'.format(i), lb=0, ub=demand[i], vartype=xp.integer) for i in N], dtype=xp.npvar)
    p.addVariable(x)
    p.addConstraint(xp.Dot(resource_consumed, x) <= total_resource)
    p.setObjective(xp.Dot(profit, x), sense=xp.maximize)
    p.solve()
    xbest = []
    p.getmipsol(xbest)
    return p.getObjVal(), xbest


def cutting_stock_model():
    """Solve a cutting stock problem by defining master problem and
    subproblem.

    :return:

    """
    n_widths = len(widths)
    N = range(n_widths)
    p = xp.problem(name='CutStock')
    patterns = np.zeros((n_widths, n_widths))
    for j in N:
        patterns[j][j] = int(max_width / widths[j])

    # Create array of variables using the dtype=xp.npvar keyword
    # argument.
    v_patterns = np.array([xp.var(name='pat_{}'.format(i), lb=0,
                                  ub=int(float(demand[i] / patterns[i][i]) + 1)) for i in N], dtype=xp.npvar)
    p.addVariable(v_patterns)
    p.setObjective(xp.Dot(np.ones(n_widths), v_patterns), sense=xp.minimize)
    p.addConstraint(xp.Dot(patterns, v_patterns) >= demand)
    p.setControl('outputlog', 0)

    for npass in range(max_cols):
        print('=============Iteration {}==========='.format(npass))
        p.solve()
        cs_lp_sol = []
        duals = []
        p.getlpsol(cs_lp_sol, None, duals, None)
        obj_val = p.getObjVal()
        #p.write('test_{}.lp'.format(npass), 'lp')
        z, x_best = solve_knapsack_problem(n_widths, np.array(duals), np.array(widths), max_width, demand)
        if z < 1 + eps:
            print('No profitable column found')
            break
        print('New pattern found with marginal cost {}'.format(z - 1));
        print(x_best)
        cur_pat = xp.var(name='pat_{}'.format(n_widths + npass), vartype=xp.continuous)
        p.addVariable(cur_pat)
        for i in N:
            p.chgcoef(i, cur_pat, x_best[i])
        p.chgobj([cur_pat], [1.0])

    print("LP Solution after column generation. Obj: {}, Sol = {}".format(obj_val, cs_lp_sol))
    n_final_patterns = p.getAttrib('cols')
    print('Number of patterns in the final LP = {}'.format(n_final_patterns))
    # Change the variables to integers
    p.chgcoltype([i for i in range(n_final_patterns)], ['I' for _ in range(n_final_patterns)])
    p.solve()
    integer_obj_val = p.getObjVal()
    int_sol = []
    p.getmipsol(int_sol)
    print("MIP Solution with final columns. Obj: {}, Sol = {}".format(integer_obj_val, int_sol))


if __name__ == '__main__':
    cutting_stock_model()
