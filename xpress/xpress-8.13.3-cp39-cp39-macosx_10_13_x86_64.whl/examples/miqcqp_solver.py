# A rudimentary solver for nonconvex MIQCQP problems
#
# (C) Fair Isaac Corp., 1983-2021

import xpress as xp
import sys
import math
import numpy as np

eps = 1e-5

TYPE_OA = 1
TYPE_SECANT = 2
TYPE_MCCORMICK = 3
TYPE_BOUNDREDUCE = 4

var_type = []

# NumPy arrays for faster elaboration
Aux_i   = None
Aux_j   = None
Aux_ind = None

# Compute bounds on bilinear term

def bdprod(lb1, ub1, lb2, ub2):
    """
    Computes lower and upper bound of a product of two terms from
    their respective lower and upper bounds
    """

    assert(lb1 <= ub1)
    assert(lb2 <= ub2)

    if lb1 >= 0 and lb2 >= 0:
        l,u = lb1*lb2, ub1*ub2
    elif lb1 >= 0:
        if ub2 >= 0:
            l,u = ub1*lb2, ub1*ub2
        else:
            l,u = ub1*lb2, lb1*ub2
    elif lb2 >= 0:
        if ub1 >= 0:
            l,u = ub2*lb1, ub2*ub1
        else:
            l,u = ub2*lb1, lb2*ub1
    elif ub1 <= 0 and ub2 <= 0:
        l,u = ub1*ub2, lb1*lb2
    elif ub1 <= 0:
        l,u = lb1*ub2, lb1*lb2
    elif ub2 <= 0:
        l,u = lb2*ub1, lb2*lb1
    else:
        assert (lb1 <= 0)
        assert (lb2 <= 0)
        assert (ub1 >= 0)
        assert (ub2 >= 0)
        l = min(lb1*ub2, lb2*ub1)
        u = max(lb1*lb2, ub1*ub2)

    assert (l == min ([lb1 * lb2, lb1 * ub2, ub1 * lb2, ub1 * ub2]))
    assert (u == max ([lb1 * lb2, lb1 * ub2, ub1 * lb2, ub1 * ub2]))

    l = max(-xp.infinity, l)
    u = min( xp.infinity, u)

    return (l, u)


# Return auxiliary variable

def addaux(aux, p, i, j, lb, ub, vtype):
    """
    Adds auxiliary variable to problem relative to product x[i]*x[j]
    """

    # Find bounds of auxiliary first
    if i != j:
        # bilinear term
        l, u = bdprod(lb[i], ub[i], lb[j], ub[j])
    elif lb[i] >= 0:
        l, u = lb[i]**2, ub[i]**2
    elif ub[i] <= 0:
        l, u = ub[i]**2, lb[i]**2
    else:
        l, u = 0, max([lb[i]**2, ub[i]**2])

    if (l >= xp.infinity) or (u <= -xp.infinity):
        print("inconsistent bounds on {0} {1}".format(i, j))
        exit(-1)

    # Then infer its type from the type of the factors
    if vtype[i] == 'B' and vtype[j] == 'B':
        t = xp.binary
    elif (vtype[i] == 'B' or vtype[i] == 'I') and \
         (vtype[j] == 'B' or vtype[j] == 'I'):
        t = xp.integer
    else:
        t = xp.continuous

    bigU = 1e8

    l = max(l, -bigU)
    u = min(u, bigU)

    # Add auxiliaries
    aux[i, j] = xp.var(lb=l, ub=u, vartype=t,
                       name='aux_{0}_{1}'.format(
                           p.getVariable(i).name.split(' ')[0],
                           p.getVariable(j).name.split(' ')[0]))

    return aux[i, j]


# De-quadratify quadratic constraint/objective
def convQaux(p, aux, mstart, ind, coef, row, lb, ub, vtype):

    """
    Converts a quadratic objective/row into a linear one by replacing
    bilinear terms with an auxiliary variable
    """

    rcols = []
    rrows = []
    rcoef = []

    for i,__ms in enumerate(mstart[:-1]):
        for j in range(mstart[i], mstart[i+1]):

            J = p.getIndex(ind[j])

            if (i, J) not in aux.keys():
                y = addaux(aux, p, i, J, lb, ub, vtype)
                p.addVariable(y)
            else:
                y = aux[i, J]

            if row < 0:  # objective
                mult = .5
            else:
                mult = 1

            if i != J:
                coe = 2 * mult * coef[j]
            else:
                coe =     mult * coef[j]

            if row < 0:
                p.chgobj([y], [coe])
            else:
                rcols.append(y)
                rrows.append(row)
                rcoef.append(coe)

    if row >= 0:
        # This is a quadratic constraint, not the objective function
        # Add linear coefficients for newly introduced variables
        p.chgmcoef(rrows, rcols, rcoef)
        # Remove quadratic matrix
        p.delqmatrix(row)

    else:

        # Objective: Remove quadratic part
        indI = []
        for i in range(len(mstart) - 1):
            indI.extend([i] * (mstart[i+1] - mstart[i]))
        # Set all quadratic elements to zero
        p.chgmqobj(indI, ind, [0] * mstart[-1])


# Create problem from filename and reformulate it

def create_prob(filename):

    global var_type, Aux_i, Aux_j, Aux_ind

    # Read file, then linearize by replacing all bilinear terms with
    # auxiliary variables

    p = xp.problem()
    p.read(filename)

    n = p.attributes.cols
    m = p.attributes.rows

    # Get original variables' bounds

    lb = []
    ub = []

    p.getlb(lb, 0, n-1)
    p.getub(ub, 0, n-1)

    # Normalize bounds so that we get meaningful McCormick constraints

    btype = []
    bind = []
    bnd = []

    art_bound = 1e5

    for i, b in enumerate(lb):
        if b <= -xp.infinity / 2:
            btype.append('L')
            bind.append(i)
            bnd.append(-art_bound)
            lb[i] = -art_bound

    for i, b in enumerate(ub):
        if b >= xp.infinity / 2:
            btype.append('U')
            bind.append(i)
            bnd.append(art_bound)
            ub[i] = art_bound

    p.chgbounds(bind, btype, bnd)

    # Get original variables' types

    vtype = []
    p.getcoltype(vtype, 0, n-1)

    x = p.getVariable()

    aux = {}  # Dictionary containing the map (x_i,x_j) --> y_ij

    # Read quadratic objective, replace it with its linearization

    # Get size of quadratic part of objective function
    size = p.getmqobj(start=None, colind=None, objqcoef=None,
                      maxcoefs=0, first=0, last=n-1)

    if size:

        # objective is also quadratic
        mstart = []
        ind = []
        obj = []

        # read Q matrix of objective
        size = p.getmqobj(mstart, ind, obj, size, 0, n-1)

        # add auxiliaries if necessary
        convQaux(p, aux, mstart, ind, obj, -1, lb, ub, vtype)

    # Do the same operation on all quadratic rows

    for i in range(m):

        # get size of matrix
        size = p.getqrowqmatrix(row=i, start=None, colind=None,
                                rowqcoef=None, maxcoefs=0, first=0, last=n-1)

        if size == 0:
            continue

        # objective is also quadratic

        mstart = []
        ind = []
        coef = []

        # read Q matrix
        size = p.getqrowqmatrix(i, mstart, ind, coef, size, 0, n-1)

        # add auxiliaries if necessary
        convQaux(p, aux, mstart, ind, coef, i, lb, ub, vtype)

    # Problem is now linear. Add McCormick constraints

    p.addConstraint(
        [aux[i, j] >= lb[j]*x[i] + lb[i]*x[j] - lb[i] * lb[j]
         for (i, j) in aux.keys() if max(-lb[i], -lb[j]) < xp.infinity],
        [aux[i, j] >= ub[j]*x[i] + ub[i]*x[j] - ub[i] * ub[j]
         for (i, j) in aux.keys() if max(ub[i], ub[j]) < xp.infinity],
        [aux[i, j] <= ub[j]*x[i] + lb[i]*x[j] - lb[i] * ub[j]
         for (i, j) in aux.keys() if max(-lb[i], ub[j]) < xp.infinity],
        [aux[i, j] <= lb[j]*x[i] + ub[i]*x[j] - ub[i] * lb[j]
         for (i, j) in aux.keys() if max(ub[i], -lb[j]) < xp.infinity])

    # Make sure the quadratic variables and the auxiliary variables
    # are not touched by the presolver

    securecols = list(aux.values())

    secureorig = set()

    for i, j in aux.keys():
        secureorig.add(i)
        secureorig.add(j)

    securecols += list(secureorig)

    p.loadsecurevecs(rowind=None, colind=securecols)

    var_type = vtype


    # Create numpy vectors containing i, j, and aux(i,j)

    Aux_i = np.array([i[0] for i in aux.keys()])
    Aux_j = np.array([i[1] for i in aux.keys()])
    Aux_ind = np.array([p.getIndex(i) for i in aux.values()])

    return p, aux

def getCBbounds(prob, n):
    """Get lower/upper bound in the original variables space
    """

    lb, ub = [], []

    # Retrieve node bounds
    prob.getlb(lb)
    prob.getub(ub)

    rowmap = []
    colmap = []

    prob.getpresolvemap(rowmap, colmap)

    olb = [-xp.infinity]*n
    oub = [ xp.infinity]*n

    for i, b in enumerate(lb):
        if colmap[i] != -1:
            olb[colmap[i]] = lb[i]
            oub[colmap[i]] = ub[i]

    return olb, oub


# Add rows to branching object

def addrowzip(prob, bo, side, sign, rhs, ind, coef):
    """
    Eliminate zero coefficients from coef and corresponding indices,
    then add row to branching object
    """

    ind2 = []
    coe2 = []

    for i in range(len(coef)):
        if coef[i] != 0:
            coe2.append(coef[i])
            ind2.append(ind[i])

    ind3, coe3 = [], []
    rhs3, status = prob.presolverow(sign, ind2, coe2, rhs, 100, ind3, coe3)

    if len(ind3) == 1:

        if sign == 'G':
            sign = 'L'
        else:
            sign = 'U'

            if coe3[0] < 0:
                if sign == 'L':
                    sign = 'U'
                else:
                    sign = 'L'

        bo.addbounds(side, [sign], [ind3[0]], [rhs3/coe3[0]])

    elif len(ind3) > 1:
        bo.addrows(side, [sign], [rhs3], [0, len(ind3)], ind3, coe3)


# Define callback functions: one for checking if a solution is
# feasible (apart from linearity, all auxiliaries must be equal to
# their respective product); one for adding new McCormick inequalities
# for changed bounds; and finally, one for branching as we might have
# to branch on continuous variables.

def cbbranch(prob, aux, branch):
    """Branch callback. Receives branch in input and, if it finds
    continuous branches that are violated, adds them.
    """

    sol = []

    if (prob.attributes.presolvestate & 128) == 0:
        return branch

    # Retrieve node solution
    try:
        prob.getlpsol(x=sol)
    except:
        return branch

    lb, ub = getCBbounds(prob, len(sol))

    assert(len(lb) == len(ub))
    assert(len(sol) == len(lb))

    x = prob.getVariable()  # presolved variables

    rowmap = []
    colmap = []

    prob.getpresolvemap(rowmap, colmap)

    invcolmap = [-1 for _ in lb]

    for i, m in enumerate(colmap):
        invcolmap[m] = i

    # make sure all dimensions match

    assert (len(lb) == len(ub))
    assert (len(sol) == len(lb))
    assert (len(invcolmap) == len(lb))

    # Check if all auxiliaries are equal to their respective bilinear
    # term. If so, we have a feasible solution

    sol = np.array(sol)

    discr = sol[Aux_ind] - sol[Aux_i] * sol[Aux_j]
    discr[Aux_i == Aux_j] = np.maximum(0, discr[Aux_i == Aux_j])
    maxdiscind = np.argmax(np.abs(discr))

    if abs(discr[maxdiscind]) < eps:
        return branch

    i,j = Aux_i[maxdiscind], Aux_j[maxdiscind]

    yind = prob.getIndex(aux[i, j])

    if i == j:

        # Test of violation is done on the original
        # space. However, the problem variables are scrambled with invcolmap

        if sol[i] > lb[i] + eps and \
           sol[i] < ub[i] - eps and \
           sol[yind] > sol[i]**2 + eps and \
           sol[yind] - lb[i]**2 <= (ub[i] + lb[i]) * (sol[i] - lb[i]) - eps:

            # Can't separate, must branch. Otherwise OA or secant
            # cut separated above should be enough

            brvarind = invcolmap[i]
            brpoint = sol[i]
            brvar = x[brvarind]
            brleft = brpoint
            brright = brpoint

            assert(brvarind >= 0)

            if brvar.vartype in [xp.integer, xp.binary]:
                brleft = math.floor(brpoint + 1e-5)
                brright = math.ceil(brpoint - 1e-5)

            b = xp.branchobj(prob, isoriginal=False)

            b.addbranches(2)

            addrowzip(prob, b, 0, 'L', brleft,  [i], [1])
            addrowzip(prob, b, 1, 'G', brright, [i], [1])

            # New variable bounds are not enough, add new McCormick
            # inequalities for y = x**2: suppose x0,y0 are the current
            # solution values for x,y, yp = x0**2 and xu,yu = xu**2 are their
            # upper bound, and similar for lower bound. Then these two
            # rows must be added, one for each branch:
            #
            # y - yp <= (yl-yp)/(xl-x0) * (x - x0)  <===>
            # (yl-yp)/(xl-x0) * x - y >= (yl-yp)/(xl-x0) * x0 - yp
            #
            # y - yp <= (yu-yp)/(xu-x0) * (x - x0)  <===>
            # (yu-yp)/(xu-x0) * x - y >= (yu-yp)/(xu-x0) * x0 - yp
            #
            # Obviously do this only for finite bounds

            ypl = brleft**2
            ypr = brright**2

            if lb[i] > -1e7 and sol[i] > lb[i] + eps:

                yl = lb[i]**2
                coeff = (yl - ypl) / (lb[i] - sol[i])

                if coeff != 0:
                    addrowzip(prob, b, 0, 'G', coeff*sol[i] - ypl,
                              [i, yind], [coeff, -1])

            if ub[i] < 1e7 and sol[i] < ub[i] - eps:

                yu = ub[i]**2
                coeff = (yu - ypr) / (ub[i] - sol[i])

                if coeff != 0:
                    addrowzip(prob, b, 1, 'G', coeff*sol[i] - ypr,
                              [i, yind], [coeff, -1])

            return b

    else:

        lbi0, ubi0 = lb[i], ub[i]
        lbi1, ubi1 = lb[i], ub[i]

        lbj0, ubj0 = lb[j], ub[j]
        lbj1, ubj1 = lb[j], ub[j]

        # No cut violated, must branch
        if min(sol[i] - lb[i], ub[i] - sol[i]) / (1 + ub[i] - lb[i]) > \
           min(sol[j] - lb[j], ub[j] - sol[j]) / (1 + ub[j] - lb[j]):
            lbi1 = sol[i]
            ubi0 = sol[i]
            brvar = i
        else:
            lbj1 = sol[j]
            ubj0 = sol[j]
            brvar = j

        alpha = 0.2

        brvarind = invcolmap[brvar]
        brpoint = sol[brvar]
        brleft = brpoint
        brright = brpoint

        if x[brvarind].vartype in [xp.integer, xp.binary]:
            brleft = math.floor(brpoint + 1e-5)
            brright = math.ceil(brpoint - 1e-5)

        b = xp.branchobj(prob, isoriginal=False)

        b.addbranches(2)

        addrowzip(prob, b, 0, 'L', brleft,  [brvar], [1])
        addrowzip(prob, b, 1, 'G', brright, [brvar], [1])

        # As for the i==j case, the variable branch is
        # insufficient, so add updated McCormick inequalities.
        # There are two McCormick inequalities per changed bound:
        #
        # y >= lb[j] * x[i] + lb[i] * x[j] - lb[j] * lb[i] ---> add to branch 1
        # y >= ub[j] * x[i] + ub[i] * x[j] - ub[j] * ub[i] ---> add to branch 0
        # y <= lb[j] * x[i] + ub[i] * x[j] - lb[j] * ub[i] ---> add to branch 1 if x[brvarind] == j, 0 if x[brvarind] == i
        # y <= ub[j] * x[i] + lb[i] * x[j] - ub[j] * lb[i] ---> add to branch 1 if x[brvarind] == i, 0 if x[brvarind] == j

        addrowzip(prob, b, 0, 'G', - ubi0 * ubj0, [yind, i, j], [1, -ubj0, -ubi0])
        addrowzip(prob, b, 1, 'G', - lbi1 * lbj1, [yind, i, j], [1, -lbj1, -lbi1])

        if brvarind == i:
            addrowzip(prob, b, 0, 'L', - lbj0 * ubi0, [yind, i, j], [1, -lbj0, -ubi0])
            addrowzip(prob, b, 1, 'L', - ubj1 * lbi1, [yind, i, j], [1, -ubj1, -lbi1])
        else:
            addrowzip(prob, b, 0, 'L', - ubj0 * lbi0, [yind, i, j], [1, -ubj0, -lbi0])
            addrowzip(prob, b, 1, 'L', - lbj1 * ubi1, [yind, i, j], [1, -lbj1, -ubi1])
        return b

    # If no branching rule was found, return none
    return branch


# Callback for checking a solution. Returns tuple (refuse, cutoff)
# where refuse=1 if solution is deemed infeasible and cutoff is the
# actual value of the solution if deemed feasible

def cbchecksol(prob, aux, soltype, cutoff):

    """
    Callback for checking if solution is truly feasible. The optimizer
    already has check integrality, we need to see if auxiliaries are
    respected
    """

    global Aux_i, Aux_j, Aux_ind

    if (prob.attributes.presolvestate & 128) == 0:
        return (1, cutoff)

    sol = []

    # Retrieve node solution
    try:
        prob.getlpsol(x=sol)
    except:
        return (1, cutoff)

    sol = np.array(sol)

    # Check if all auxiliaries are equal to their respective bilinear
    # term. If so, we have a feasible solution

    refuse = 1 if np.max(np.abs(sol[Aux_i] * sol[Aux_j] - sol[Aux_ind])) > eps else 0

    # Return with refuse != 0 if solution is rejected, 0 otherwise;
    # and same cutoff
    return (refuse, cutoff)

def cbfindsol(prob, aux):
    """Callback for finding a feasible solution. Returns tuple (refuse,
    cutoff) where refuse=1 if solution is deemed infeasible and cutoff
    is the actual value of the solution if deemed feasible. Note that
    the solution must be feasible as otherwise it gets regenerated
    every time.

    """

    if (prob.attributes.presolvestate & 128) == 0:
        return 0

    sol = []

    try:
        prob.getlpsol(x=sol)
    except:
        return 0

    xnew = sol[:]

    # Round solution to nearest integer
    for i,t in enumerate(var_type):
        if t == 'I' or t == 'B' and \
           xnew[i] > math.floor(xnew[i] + prob.controls.miptol) + prob.controls.miptol:
            xnew[i] = math.floor(xnew[i] + .5)

    for i, j in aux.keys():
        yind = prob.getIndex(aux[i, j])
        xnew[yind] = xnew[i] * xnew[j]

    prob.addmipsol(xnew)

    return 0


# Callback for adding cuts. Can use addcuts(). Checks feasibility of
# the Y=xx' equation and attempts at adding Outer Approximation,
# secant, or McCormick inequalities.

def cbaddmccormickcuts(prob, aux, sol):
    """
    Callback to add tighter McCormick inequalities arising from
    tighter lower/upper bounds on the original variables
    """

    lb, ub = getCBbounds(prob, len(sol))

    cuts = []

    # Check if all auxiliaries are equal to their respective bilinear
    # term. If so, we have a feasible solution
    for i, j in aux.keys():

        yind = prob.getIndex(aux[i, j])

        if i == j:

            # Separate quadratic term

            if sol[yind] < sol[i]**2 - eps and \
               abs(sol[i]) < xp.infinity / 2:

                # Find the right point for separation, which should be
                # minimum-distance point from the current solution
                # (sol[i], sol[yind]) to the region (y >= x**2).
                #
                # For the square function, this amounts to solving a
                # "depressed cubic" equation (depressed as the square
                # term has zero coefficient)
                #
                # 4x^3 + (2-4y0) x - 2x0 = 0
                #
                # Solve this with a few iterations of Newton's method. @todo

                xk = sol[i]

                #for _ in range(5):
                #    xk -= (4*xk**3 + 2*(1-2*sol[yind])*xk - 2*sol[i]) / (12*xk**2 + 2*(1 - 2*sol[yind]))

                ox = xk
                oy = ox ** 2

                # Add Outer Approximation cut y >= xs^2 + 2xs*(x-xs)
                # <===> y - 2xs*x >= -xs^2
                cuts.append((TYPE_OA, 'G', - ox**2, [yind, i],
                             [1, -2*ox]))

            # Otherwise, check if secant can be of help: y0 - xl**2 >
            # (xu**2 - xl**2) / (xu - xl) * (x0 - xl)
            elif sol[yind] > sol[i]**2 + eps and \
                 sol[yind] - lb[i]**2 > (ub[i] + lb[i]) * (sol[i] - lb[i]) \
                 + eps and abs(lb[i] + ub[i]) < xp.infinity / 2:
                cuts.append((TYPE_SECANT, 'L',
                             lb[i]**2 - (ub[i] + lb[i]) * lb[i],
                             [yind, i], [1, - (lb[i] + ub[i])]))

        elif abs(sol[yind] - sol[i]*sol[j]) > eps:

            # Separate bilinear term, where i != j.  There might be at
            # least one cut violated

            if sol[yind] < lb[j]*sol[i] + lb[i]*sol[j] - lb[i]*lb[j] - eps:
                if lb[i] > -xp.infinity / 2 and lb[j] > -xp.infinity / 2:
                    cuts.append((TYPE_MCCORMICK, 'G', - lb[i] * lb[j],
                                 [yind, i, j], [1, -lb[j], -lb[i]]))
            elif sol[yind] < ub[j]*sol[i] + ub[i]*sol[j] - ub[i]*ub[j] - eps:
                if ub[i] < xp.infinity / 2 and ub[j] < xp.infinity / 2:
                    cuts.append((TYPE_MCCORMICK, 'G', - ub[i] * ub[j],
                                 [yind, i, j], [1, -ub[j], -ub[i]]))
            elif sol[yind] > lb[j]*sol[i] + ub[i]*sol[j] - ub[i]*lb[j] + eps:
                if ub[i] < xp.infinity / 2 and lb[j] > -xp.infinity / 2:
                    cuts.append((TYPE_MCCORMICK, 'L', - ub[i] * lb[j],
                                 [yind, i, j], [1, -lb[j], -ub[i]]))
            elif sol[yind] > ub[j]*sol[i] + lb[i]*sol[j] - lb[i]*ub[j] + eps:
                if lb[i] > -xp.infinity / 2 and ub[j] < xp.infinity / 2:
                    cuts.append((TYPE_MCCORMICK, 'L', - lb[i] * ub[j],
                                 [yind, i, j], [1, -ub[j], -lb[i]]))

    # Done creating cuts. Add them to the problem

    for (t, s, r, I, C) in cuts:  # cuts might be the empty list
        mcolsp, dvalp = [], []
        drhsp, status = prob.presolverow(s, I, C, r, prob.attributes.cols,
                                         mcolsp, dvalp)
        if status >= 0:
            prob.addcuts([t], [s], [drhsp], [0, len(mcolsp)], mcolsp, dvalp)

    return 0

def cbboundreduce(prob, aux, sol):
    """
    Callback to reduce bounds that might have been propagated through
    the problem.
    """

    cuts = []

    lb, ub = getCBbounds(prob, len(sol))

    # Check if bounds on original variables can be reduced based on
    # bounds on auxiliary ones. The other direction is already taken
    # care of by McCormick and tangent/secant cuts.

    feastol = prob.controls.feastol

    for (i,j),a in aux.items():

        auxind = prob.getIndex(a)

        lbi = lb[i]
        ubi = ub[i]
        lba = lb[auxind]
        uba = ub[auxind]

        if i == j:  # check if upper bound is tight w.r.t. bounds on
                    # x[i]

            # Forward propagation: from new independent variable
            # bounds, infer new bound for dependent variable.

            if uba > max(lbi**2, ubi**2) + feastol:
                cuts.append((TYPE_BOUNDREDUCE, 'L', max(lbi**2, ubi**2), [auxind], [1]))

            if lbi > 0 and lba < lbi**2 - feastol:
                cuts.append((TYPE_BOUNDREDUCE, 'G', lbi**2, [auxind], [1]))
            elif ubi < 0 and lba < ubi**2 - feastol:
                cuts.append((TYPE_BOUNDREDUCE, 'G', ubi**2, [auxind], [1]))

            if uba < -feastol:
                return 1  # infeasible node
            else:
                if uba < lbi**2 - feastol:
                    if lbi > 0:
                        return 1  # infeasible node
                    else:
                        cuts.append((TYPE_BOUNDREDUCE, 'G', -math.sqrt(uba), [i], [1]))
                if uba < ubi**2 - feastol:
                    if ubi < - feastol:
                        return 1
                    else:
                        cuts.append((TYPE_BOUNDREDUCE, 'L', math.sqrt(uba), [i], [1]))

            if lba > prob.controls.feastol and lbi > 0 and lbi**2 < lba - feastol:
                cuts.append((TYPE_BOUNDREDUCE, 'G', math.sqrt(lba), [i], [1]))

        else:

            tlb, tub = bdprod(lb[i], ub[i], lb[j], ub[j])

            if lba < tlb - feastol:
                cuts.append((TYPE_BOUNDREDUCE, 'G', tlb, [auxind], [1]))

            if uba > tub + feastol:
                cuts.append((TYPE_BOUNDREDUCE, 'L', tub, [auxind], [1]))

            # For simplicity let's just assume lower bounds are nonnegative

            lbj = lb[j]
            ubj = ub[j]

            if lbj >= 0 and lbi >= 0:

                if lbi*ubj < lba - feastol:
                    cuts.append((TYPE_BOUNDREDUCE, 'G', lba / ubj, [i], [1]))
                if lbj*ubi < lba - feastol:
                    cuts.append((TYPE_BOUNDREDUCE, 'G', lba / ubi, [j], [1]))

                if lbi*ubj > uba + feastol:
                    cuts.append((TYPE_BOUNDREDUCE, 'L', uba / lbi, [j], [1]))
                if lbj*ubi > uba + feastol:
                    cuts.append((TYPE_BOUNDREDUCE, 'L', uba / lbj, [i], [1]))

    # Done creating cuts. Add them to the problem

    for (t, s, r, I, C) in cuts:  # cuts might be the empty list

        mcolsp, dvalp = [], []
        drhsp, status = prob.presolverow(s, I, C, r, prob.attributes.cols,
                                         mcolsp, dvalp)
        if status >= 0:

            if len(mcolsp) == 0:
                continue
            elif len(mcolsp) == 1:
                if s == 'G':
                    btype = 'L'
                elif s == 'L':
                    btype = 'U'
                else:  # don't want to add an equality bound reduction
                    continue

                assert(dvalp[0] > 0)

                prob.chgbounds(mcolsp,[btype],[drhsp/dvalp[0]])
            else:
                prob.addcuts([t], [s], [drhsp], [0, len(mcolsp)], mcolsp, dvalp)

    return 0


def cbaddsdpcuts(prob, aux, sol):
    return 0



def cbaddcuts(prob, aux):

    sol = []

    if (prob.attributes.presolvestate & 128) == 0:
        return 0

    try:
        prob.getlpsol(x=sol)
    except:
        return 0

    retval = \
             cbboundreduce(prob, aux, sol) or \
             cbaddmccormickcuts(prob, aux, sol) or \
             cbaddsdpcuts(prob, aux, sol)

    return retval

def solveprob(p, aux):

    # The above callbacks are run within the branch-and-bound. Assign
    # them to specific points in the BB

    p.addcbpreintsol(cbchecksol, aux, 1)
    # p.addcboptnode(cbfindsol, aux, 3)
    p.addcboptnode(cbaddcuts, aux, 3)
    p.addcbchgbranchobject(cbbranch, aux, 1)

    # Start branch-and-bound

    try:
        p.mipoptimize()
        sol = p.getSolution()
    except:
        print("No solution found or MIP optimization went wrong")
    else:
        print("Solution:", sol)

        nviol = 0

        for i, j in aux.keys():
            y = p.getIndex(aux[i, j])
            if (abs(sol[y] - sol[i] * sol[j]) > 1e-8):
                nviol += 1
                print("violation ({0},{1},{2}): ".format(i, j, y),
                      abs(sol[y] - sol[i] * sol[j]))

        print (nviol, 'violations')


# main script

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Needs an argument: mps or lp file with quadratic instance")
        exit(-1)

    p, aux = create_prob(sys.argv[1])
    # p.controls.maxtime = -120
    # p.controls.maxnode = 40
    # p.controls.threads = 1
    # p.controls.callbackfrommasterthread = 1
    solveprob(p, aux)
