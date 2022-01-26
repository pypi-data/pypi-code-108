#
# An application of the Xpress callbacks to a Benders decomposition algorithm
#
# Courtesy of Georgios Patsakis (UC Berkeley, Amazon) and Richard L.-Y. Chen (Amazon)
#

################################################################################
##################   BENDERS DECOMPOSITION USING CALLBACKS   ###################
################################################################################
#### NOTE: This example is for illustration/tutorial purposes only. There is no
#### benefit in solving the generic problem defined below using Benders
#### decomposition.

#### Solves the problem:
#### min c1*x + c2*y
#### st  A1*x + A2*y <=b (m constraints)
#### x binary n1-dimensional vector
#### y >=0 continuous n2-dimensional vector

################################################################################
#########################  PROBLEM INITIALIZATIONS   ###########################
################################################################################

#### Import Necessary Packages
import xpress as xp
import sys

#### Initialize Problem Parameters
c1 = [1,6,5,7]                    # n1 x 1
c2 = [9,3,0,2,3]                  # n2 x 1
b  = [-3,-4,1,4,5]                   # m  x 1
A1 = [[0, -2, 3, 2],
      [-5, 0, -3, 1],
      [1, 0, 4, -2],
      [0, -3, 4, -1],
      [-5, -4, 3, 0]]
A2 = [[3, 4, 2, 0, -5],
      [0, 2, 3, -2, 1],
      [2, 0, 1, -3, -5],
      [-5, 3, -2, -3, 0],
      [-2, 3, -1, 2, -4]]
m  = len(b)
n1 = len(c1)
n2 = len(c2)

#### Absolute accuracy for optimal objective
ObjAbsAccuracy=0.00001
################################################################################
#####################       SOLVE ORIGINAL PROBLEM        ######################
################################################################################
#### Solves the problem without decomposing.

#### Define Problem
p = xp.problem()

#### Define Variables
x = [xp.var(vartype=xp.binary) for i in range(n1)]
y = [xp.var() for i in range(n2)] #positive real variable
p.addVariable(x,y)

#### Define Constraints
constr = [xp.Sum(A1[ii][jj]*x[jj] for jj in range(n1)) +                       \
          xp.Sum(A2[ii][jj]*y[jj] for jj in range(n2))                         \
                        <=b[ii] for ii in range(m)]
p.addConstraint(constr)

#### Define Objective
p.setObjective(xp.Sum(c1[jj]*x[jj] for jj in range(n1)) +                      \
               xp.Sum(c2[jj]*y[jj] for jj in range(n2)) ,                      \
               sense=xp.minimize)

#### Solve and retrieve solution
p.solve()

if p.getProbStatus() != xp.mip_optimal:
    raise RuntimeError('Problem could not be solved to MIP optimality')

yopt = p.getSolution(y)
print("The optimal objective is:", p.getObjVal())
print("The first stage variables are:", p.getSolution(x))
print("The second stage variables are:", yopt)
print("The objective of the second stage is:",                                 \
       sum(c2[jj]*yopt[jj] for jj in range(n2)))

################################################################################
#####################      SOLVE DECOMPOSED PROBLEM       ######################
################################################################################
#### We define the following functions:
#### - subproblem: function that solves the subproblem for a given first stage
####   variable xhat. If the subproblem has an optimal solution, it returns the
####   the optimal dual multiplier associated with the non anticipativaty
####   constraint, the optimal objective, and the label "Optimal". If the
####   subproblem is infeasible, it returns the dual ray of unboundedness and
####   the label "Infeasible".
#### - integer_callback: An integer callback is triggered every time an integer
####   solution is found. The function integer_callback is an input to the
####   addcbpreintsol function and has a specified input - output format based
####   on the Xpress documentation. It takes as input the master optimization
####   problem name, a user data structure, a variable that indicates whether
####   the integer solution comes from a heuristic or from a node relaxation,
####   and the proposed update to the upper bound if this integer solution is
####   accepted as feasible. The inputs are populated by the solver when the
####   callback is triggered. The function returns whether the integer solution
####   found should be accepted as feasible and the proposed update to the upper
####   bound if the solution is feasible (which could be the same as the one
####   proposed by the solver as part of the input.)

################################################################################
#### Subproblem Solver Function
def subproblem(xhat):
    # Input
    # - xhat: n1x1a array is the first stage variable,
    # passed to the subproblem
    #
    # Output:
    # return (lamb: n1x1 array, beta: scalar, flag:string)
    # - If the subproblem is Infeasible, the flag is 'Infeasible', and
    #   lamb (n1x1) and beta (1x1) are the components of the dual ray of
    #   unboundedness necessary to write a feasibility cut of the form:
    #       sum(x[i]*lamb[i] for all i) +beta >= 0
    # - If the subproblem is Optimal, the flag is 'Optimal', beta (1x1) is the
    #   optimal objective, and lamb (n1x1) is the optimal dual multiplier
    #   associated with the non anticipativaty constraint, so that the
    #   optimality cut will have the form:
    #       theta >= sum(x[i]*lamb[i] for all i) + beta

    # IMPORTANT NOTE: The subproblem needs to ensure tha upper bounds or non
    # zero lower bounds should ONLY BE DEFINED THROUGH CONSTRAINTS, not as part
    # of the variable definition. This is to ensure the feasibility cuts are
    # correct.
    # Side Note: It is a good practice to ensure that the subproblem is always
    # feasible through modeling, by say adding slacks to all the constraints,
    # hence avoiding feasibility cuts completely. This is because feasibility
    # cuts tend to be extremely slow. In this code we implemented feasibility
    # cuts for reasons of completeness.

    #### Define and Solve Subproblem

    # Initialize Problem
    r=xp.problem()

    # Define Variables
    y=[xp.var() for i in range(n2)] # positive real variable - second stage
    z=[xp.var(lb=-xp.infinity) for i in range(n1)] # dummy copy variable
                                        # must have the exact shape as xhat
    epsilon=xp.var(lb=-xp.infinity) # dummy variable to extract part of the
                                    # infeasibility ray (if infeasible)
    r.addVariable(y,z,epsilon)

    # Define Constraints
    # Dummy cosntraint for optimality/feasibility cuts
    # Note: make sure the index of the variable and of the position in the
    # constraint array is the same (or has a known mapping)
    dummy1= [z[i]==xhat[i] for i in range(n1)]
    # Dummy constraint for feasibility cut
    dummy2= epsilon==1
    # Second stage constraints, where RHS b has been multiplied by epsilon
    constr=[xp.Sum(A1[ii][jj]*z[jj] for jj in range(n1)) +                     \
            xp.Sum(A2[ii][jj]*y[jj] for jj in range(n2))                       \
            - epsilon*b[ii]<=0 for ii in range(m)]
    r.addConstraint(constr,dummy1,dummy2)

    # Define Objective
    r.setObjective(xp.Sum(c2[jj]*y[jj] for jj in range(n2))                    \
                                        ,sense=xp.minimize)

    # Disable presolve. The only reason to do this is because in the case of
    # an infeasible problem, the presolve might identify infeasibility of the
    # problem without running simplex. Because of that, no dual infeasibility
    # certificate will be found, hence a dual ray of unboundedness will not be
    # returned, which means that a feasibility cut can not be formed. In
    # practice, we should avoid infeasibility cuts alltogether through modeling
    # and have presolve on for a better performance in the subproblem. If an
    # infeasibility cut can not be avoided, formulating the dual explicitly is
    # the only option.
    r.setControl({"presolve":0})

    # Silence output
    r.setControl ('outputlog', 0)
    # Solve optimization
    r.solve()

    # Find the indices of constraint dummy1, which will be used to access the
    # dual multipliers corresponding to the entries of xhat
    xind1=[r.getIndex(dummy1[ii]) for ii in range(n1)]

    # Take cases depending on subproblem status
    if r.getProbStatus()==xp.lp_optimal:
        # Optimal subproblem
        print("Optimal Subproblem")
        # Retrieve optimal dual multiplier and objective and return
        dualmult=r.getDual()
        lamb=[dualmult[ii] for ii in xind1]
        beta=r.getObjVal()
        return(lamb,beta,'Optimal')

    elif r.getProbStatus()==xp.lp_infeas:
        # Infeasible subproblem
        print("Infeasible Subproblem")
        if not r.hasdualray ():
            print ("Could not retrieve a dual ray, return no good cut instead:")
            # This is just a cheat if the subproblem is found infeasible and
            # the optimizer fails to find a dual ray. Since all the first stage
            # variables are binary, we add a No-Good-Cut to exclude the point
            # xhat instead of an infeasibility cut.
            xhatones=set(ii for ii in range(n1) if xhat[ii]>=0.5)
            lamb=[2*xhat[ii]-1 for ii in range(n1)]
            beta=-sum(xhat)+1
        else:
            # Extract the dual ray
            dray = []
            r.getdualray (dray)
            print ("Dual Ray:", dray)
            # Extract the part of the dual ray corresponding to the first stage
            # variables xhat
            lamb=[dray[ii] for ii in xind1]
            # Extract the constant from the dual ray entry of constraint dummy 2
            beta=dray[r.getIndex(dummy2)]
        return(lamb,beta,'Infeasible')
    else:
        print("ERROR: Subproblem not optimal or infeasible. Terminating.")
        sys.exit()

################################################################################
#### Integer Callback Function
def integer_callback(p, data, isheuristic, cutoff):
    # Input
    # NOTE: the input is populated by the solver when an integer solution is
    # found.
    # - p: an xp.problem() (the master problem from which the callbacks were
    # trigger)
    # - data: structure that is passed to the callback from the
    #   problem, and is specified in the addcbpreintsol function. No
    #   data is needed here, so the addcbpreintnode() call uses None.
    # - isheuristic: 0 if the integer solution was found by a node relaxation,
    # and not 0 if the integer solution was found by a heuristic
    # - cutoff: the integer solution found by the solver is associated with an
    # upper bound, if this integer solution is feasible to full problem. cutoff
    # is the upper bound (slightly decreased) associated with that integer
    # solution. If the user decides that the integer solution is indeed feasible,
    # the user can modify that cutoff, if the default solver value misrepresents
    # the upper bound, and return a new cutoff (newcutoff)
    # Output
    # return (isreject, newcutoff)
    # - isreject: True to reject integer solution, False to accept it
    # - newcutoff: in case isreject is False, possible update to the cutoff.

    print("Entering Integer Callback.")
    if isheuristic ==0:
        # In this case the integer solution was found by a node relaxation of
        # the B&B tree, so we accept it as is. The node callback has taken
        # care of ensuring the solution is feasible to the subproblem.
        print("Integer solution from optimal node relaxation.")
        print("Solution accepted. Cutoff:", cutoff)
        return(False,None)
    else:
        print("Integer solution found from heuristic. Checking subproblem.")
        # In any other case, we need to solve the subproblem.

        # Retrieve heuristic solution in vectorized form
        s=[]
        p.getlpsol(s,None,None,None) # This will load the solution to array s

        # Obtain indices of x and theta in the original problem
        xind=[p.getIndex(x[ii]) for ii in range(n1)]
        thetaind=[p.getIndex(theta)]

        # Construct xhat and thetahat based on the vector s where the full
        # solution was stored and the variable indices
        xhat=[s[ii] for ii in xind]
        thetahat=s[thetaind[0]]
        print("Solution tested x=",xhat, "and theta=",thetahat)
        print("Cutoff is:",cutoff)

        # Solve the subproblem
        (dual_mult,opt,status)=subproblem(xhat)

        if status=='Infeasible':
            # In the case of an infeasible subproblem, simply reject the solution found
            return (True,None)
        elif status=='Optimal':
            if thetahat>=opt-ObjAbsAccuracy:
                # In this case the vector (xhat,thetahat) is feasible, so accept
                # it and accept the cutoff
                print("Accepting pair x=",xhat,",theta=",thetahat )
                print("Accept new cutoff:",cutoff)
                return(False,None)
            else:
                # In this case the solution (xhat,thetahat) is infeasible so
                # reject it
                return (True,None)
        else:
            print("We shouldn't reach this point.")
            print("Rejecting pair x=",xhat,",theta=",thetahat )
            return(True,None)

################################################################################
#### Node Callback Function
def node_callback(p, data):
    # Input
    # Note: the input is populated by the solver when the relaxation of a node
    # is solved
    # - p: the xp.problem corresponding to the master problem, from which the
    # callback is triggered.
    # - data: structure that is passed to the callback from the
    #   problem, and is specified in the addcboptnode function. No
    #   data is needed here, so the addcboptnode() call uses None.
    # Output
    # return 0

    print("We entered a node callback")

    # Obtain node relaxation solution
    s=[]
    p.getlpsol(s,None,None,None)
    xind=[p.getIndex(x[ii]) for ii in range(n1)]
    thetaind=[p.getIndex(theta)]
    xhat=[s[ii] for ii in xind]
    thetahat=s[thetaind[0]]
    print("Solution tested x=",xhat, "and theta=",thetahat)

    # Now let's see if the solution satisfies the subproblem induced constraints
    # Solve the subproblem
    (dual_mult,opt,status)=subproblem(xhat)
    if status=='Infeasible':
        # Create feasibility cut to add to node
        coefficients=dual_mult
        rhs=-opt
        print("Add cut. Cut stats:")
        print("coefficients:",coefficients)
        print("<=rhs:",rhs)
        print("column indices:",xind)
        # Add the cut (this will reject the point)
        p.addcuts([1],['L'],[rhs],[0,len(xhat)],xind,coefficients)
        print("Rejecting pair x=",xhat,",theta=",thetahat, "with a cut." )
        return 0
    elif status=='Optimal':
        if thetahat>=opt-ObjAbsAccuracy:
            # In this case the vector (xhat,thetahat) is feasible, so accept
            print("Accepting pair x=",xhat,",theta=",thetahat )
            print("An integer callback will be triggered for that pair later.")
            return 0
        else:
            # In this case the solution (xhat,thetahat) is infeasible so reject
            # it and add an optimality cut
            coefficients=[1]+[-dual_mult[ii] for ii in range(len(dual_mult))]
            rhs=opt-sum(dual_mult[ii]*xhat[ii] for ii in range(len(dual_mult)))
            print("Store cut. Cut stats:")
            print("coefficients:",coefficients)
            print(">=rhs:",rhs)
            print("column indices:",thetaind+xind)
            # Add the cut (this will reject the point)
            p.addcuts([1],['G'],[rhs],[0,len(xhat)+1],thetaind+xind,coefficients)
            print("Rejecting pair x=",xhat,",theta=",thetahat,"with a cut." )
            return 0
    else:
        print("ERROR: Subproblem not optimal or infeasible. Terminating.")
        sys.exit()

################################################################################
#### Master Problem

# Define master problem
p=xp.problem()

# Define first stage variables
x=[xp.var(vartype=xp.binary) for i in range(n1)]
theta=xp.var() # (positive) second stage cost - change the default lower
               # bound if second stage cost may not be positive.
p.addVariable(x,theta)

# Define objective
p.setObjective(xp.Sum(c1[jj]*x[jj] for jj in range(n1)) +  theta               \
               ,sense=xp.minimize)

# Add Integer callback. i.e., when an integer solution is found, the function
# integer_callback will be called by the solver.
p.addcbpreintsol (integer_callback, None, 0)

# Add node_callback. i.e., when a node relaxation is solved, the function
# node_callback will be called by the solver.
p.addcboptnode (node_callback, None, 0)

# Deactivate presolve. This is to ensure that the solver will not eliminate
# variables, so the indices we retrieve for the variables and the cuts we add
# correspond to/contain existing optimization variables. Presolve can be
# activated, but additional steps are required for that (presolving the cuts
# the same way as the rows of the matrix.)
p.setControl({"presolve":0,"mippresolve":0,"symmetry":0})

# Solve the master problem
p.solve()

if p.getProbStatus() == xp.lp_optimal:

    # Print results
    print("The optimal objective is:",p.getObjVal())
    print("The first stage variables are:",p.getSolution(x))
else:
    print("Could not solve the problem")
