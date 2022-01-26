"""
Transportation problem  with piecewise linear costs
This example illustrates two ways of modeling piecewise linear functions
  (a) Using the problem.addpwlcons method.
  (b) Using xpress.pwl
Based on the model Figure 17-3a, Chapter 17 from the book
R.Fourer, DM. Gay, BW Kerninghan AMPL: A modeling language for mathematical programming
(c) 2020 Fair Isaac Corporation
"""
import xpress as xp

formulate_using_addpwlcons = True  # If True - will use problem.addpwlcons, else -  will use xpress.pwl

'''
PROBLEM DATA
'''
# Specify the sources and destinations
sources = ['Gary', 'Cleveland', 'Pittsburgh']
destinations = ['Framingham', 'Detroit', 'Lansing', 'Windsor', 'St.Louis', 'Fremont', 'Lafayette']

# Supply from each source
supply = {'Gary': 1400, 'Cleveland': 2600, 'Pittsburgh': 2900}

# Demands at destinations
demand = {'Framingham': 900, 'Detroit': 1200, 'Lansing': 600, 'Windsor': 400,
          'St.Louis': 1700, 'Fremont': 1100, 'Lafayette': 1000}
# Maximum demand
max_demand = 1700

# Quantity intervals and unit shipping rates
# This is specified as dictionary of origin-destination : quantity limits and shipping rates.

pw_transp_costs = {('Gary', 'Framingham'): ((500, 1000), (39, 50, 70)),
                   ('Gary', 'Detroit'): ((500, 1000), (14, 17, 33)),
                   ('Gary', 'Lansing'): ((500, 1000), (11, 12, 23)),
                   ('Gary', 'Windsor'): ((1000,), (14, 17)),
                   ('Gary', 'St.Louis'): ((500, 1000), (16, 23, 40)),
                   ('Gary', 'Fremont'): ((1000,), (82, 98)),
                   ('Gary', 'Lafayette'): ((500, 1000), (8, 16, 24)),
                   ('Cleveland', 'Framingham'): ((500, 1000), (27, 37, 47)),
                   ('Cleveland', 'Detroit'): ((500, 1000), (9, 19, 24)),
                   ('Cleveland', 'Lansing'): ((500, 1000), (12, 32, 39)),
                   ('Cleveland', 'Windsor'): ((500, 1000), (9, 14, 21)),
                   ('Cleveland', 'St.Louis'): ((500, 1000), (26, 36, 47)),
                   ('Cleveland', 'Fremont'): ((500, 1000), (95, 105, 129)),
                   ('Cleveland', 'Lafayette'): ((500, 1000), (8, 16, 24)),
                   ('Pittsburgh', 'Framingham'): ((1000,), (24, 34)),
                   ('Pittsburgh', 'Detroit'): ((1000,), (14, 24)),
                   ('Pittsburgh', 'Lansing'): ((1000,), (17, 27)),
                   ('Pittsburgh', 'Windsor'): ((1000,), (13, 23)),
                   ('Pittsburgh', 'St.Louis'): ((), (28,)),
                   ('Pittsburgh', 'Fremont'): ((1000,), (99, 140)),
                   ('Pittsburgh', 'Lafayette'): ((), (20,))}


def get_breakpoints(limits, rates, max_val):
    """
    Given the limits, rates and an upper bound, return the breakpoints and function values.
    For example, limits = (500,1000), rates = (1,2,3), maxval = 2000 returns
        breakpoints = (0,500,1000,200), values = (0,500,2000,6000)
    :param limits: Tuple of limits
    :param rates: Tuple of Rates
    :param max_val: An upper limit breakpoint
    :return: Lists of breakpoints and function values at breakpoints
    """
    assert (len(limits) + 1 == len(rates))
    # Cost to ship 0 units is 0
    xvals = [0]
    yvals = [0]
    # Add the remaining breakpoints and values
    n = len(limits)
    N = range(n)
    for i in N:
        xvals.append(limits[i])
        yvals.append(limits[i] * rates[i])
    xvals.append(max_val)
    yvals.append(max_val * rates[n])
    return xvals, yvals


eps = 1e-6


def get_line(x1, y1, x2, y2):
    """
    :param x1: x-coordinate of the 1st point
    :param y1: y-coordinate of the 2nd point
    :param x2: x-coordinate of the 2nd point
    :param y2: y-coordinate of the 2nd point
    :return: Slope and intercept
    """
    assert (abs(x1 - x2) > eps)
    slope = (y2 - y1) / (x2 - x1)
    intercept = -slope * x1 + y1
    return slope, intercept


def get_pwl_functions(limits, rates, max_val):
    '''
    :param limits: Tuple of limits
    :param rates: Tuple of rates
    :param max_val: An upper limit of demand
    :return: Intervals, slope and intercept of the linear function in the interval
    '''
    xvals, yvals = get_breakpoints(limits, rates, max_val)
    N = range(len(xvals) - 1)
    intervals = []
    functions = []
    for i in N:
        slope, intercept = get_line(xvals[i], yvals[i], xvals[i + 1], yvals[i + 1])
        intervals.append((xvals[i], xvals[i + 1]))
        functions.append((slope, intercept))
    return intervals, functions


'''
MODEL FORMULATION
'''
tp = xp.problem()
tp.setprobname('Transportation Problem with PWL Costs')

# Create the variables
trans = {(i, j): xp.var(vartype=xp.continuous, name='trans_{}_{}'.format(i, j)) for i in sources for j in destinations}
tp.addVariable(trans)

# Total shipped from a source must equal supply
for i in sources:
    tp.addConstraint(xp.Sum(trans[(i, j)] for j in destinations) == supply[i])

# Total received at a destination must equal demand
for j in destinations:
    tp.addConstraint(xp.Sum(trans[i, j] for i in sources) == demand[j])

if formulate_using_addpwlcons:  # Using the problem.addpwlcons method to formulate the objective
    # Add auxiliary variables to store the resultant
    y_trans = {(i, j): xp.var(vartype=xp.continuous, name='y_trans_{}_{}'.format(i, j)) for i in sources for j in
               destinations}
    tp.addVariable(y_trans)
    col = []
    resultant = []
    start = [0]
    xval = []
    yval = []
    count = 0
    for key in pw_transp_costs.keys():
        col.append(trans[key])
        resultant.append(y_trans[key])
        xv, yv = get_breakpoints(pw_transp_costs[key][0], pw_transp_costs[key][1], max_demand)
        count += len(xv)
        start.append(count)
        xval.extend(xv)
        yval.extend(yv)
    start = start[:-1]
    tp.addpwlcons(col, resultant, start, xval, yval)
    tp.setObjective(xp.Sum(y_trans[key] for key in pw_transp_costs.keys()), sense=xp.minimize)

else:  # Using xpress.pwl method to formulate the objective
    obj_expr = 0
    for key in pw_transp_costs.keys():
        intvls, funcs = get_pwl_functions(pw_transp_costs[key][0], pw_transp_costs[key][1], max_demand)
        cur_expr = {}
        for i in range(len(intvls)):
            cur_expr[intvls[i]] = funcs[i][0] * trans[key] + funcs[i][1]
        obj_expr += xp.pwl(cur_expr)
    tp.setObjective(obj_expr)

# Solve the problem
tp.solve()

# Retrieve and print the solution
print('------- Solution -------')
print("Total Cost  = {}".format(tp.getObjVal()))
sol = tp.getSolution(trans)
for key in sol.keys():
    print('Trans{} = {}'.format(key, sol[key]))
