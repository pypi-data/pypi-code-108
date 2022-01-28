from flowty.interop import libFlowty
import enum


# constraint senses
class ConstrSense(enum.Enum):
    """
    Sense used in building [constraints][flowty.model.Model.addConstr] or
    [linear equations][flowty.entities.LinEqua].
    """

    Equal = libFlowty.FLWT_ConstrSense_Equal
    """Equal."""
    LessOrEqual = libFlowty.FLWT_ConstrSense_LessEqual
    """Less than or equal."""
    GreaterOrEqual = libFlowty.FLWT_ConstrSense_GreaterEqual
    """Greater than or equal."""


# optimization directions
class ObjSense(enum.Enum):
    """
    Objective function sense.
    """

    Minimize = libFlowty.FLWT_ObjSense_Minimize
    """Minimize"""
    Maximize = libFlowty.FLWT_ObjSense_Maximize
    """
    Maximize.

    Note:
        Not implemented for the dynamic programming or path MIP algorithms.
    """


# variable types
class VarType(enum.Enum):
    """
    Variable type
    """

    Binary = "B"
    """Binary variables, either 0 or 1."""
    Continuous = "C"
    """Continuous variables."""
    Integer = "I"
    """Integer variables."""


class OptimizationStatus(enum.Enum):
    """Status of the optimizations"""

    Loaded = libFlowty.FLWT_OptimizationStatus_Loaded
    """The problem is loaded. No optimization has run yet."""
    Optimal = libFlowty.FLWT_OptimizationStatus_Optimal
    """The problem is solved to optimality."""
    Infeasible = libFlowty.FLWT_OptimizationStatus_Infeasible
    """The problem is proven infeasible."""
    InfeasibleOrUnbounded = libFlowty.FLWT_OptimizationStatus_InfeasibleOrUnbounded
    """The problem is infeasible or unbounded."""
    Unbounded = libFlowty.FLWT_OptimizationStatus_Unbounded
    """The problem is unbounded."""
    Cutoff = libFlowty.FLWT_OptimizationStatus_Cutoff
    """The optimization stopped due to cutoff."""
    IterationLimit = libFlowty.FLWT_OptimizationStatus_IterationLimit
    """Stopped due to simplex iterations limit."""
    NodeLimit = libFlowty.FLWT_OptimizationStatus_NodeLimit
    """Stopped due to node limit."""
    TimeLimit = libFlowty.FLWT_OptimizationStatus_TimeLimit
    """Stopped due to time limit."""
    SolutionLimit = libFlowty.FLWT_OptimizationStatus_SolutionLimit
    """Stopped due to maximum solutions found."""
    Interrupted = libFlowty.FLWT_OptimizationStatus_Interrupted
    """Optimization was interrupted by user."""
    Numeric = libFlowty.FLWT_OptimizationStatus_Numeric
    """Stopped due to numerical instability."""
    Feasible = libFlowty.FLWT_OptimizationStatus_Feasible
    """Stopped with a feasible solution but not necessarily optimal solution."""


class Where(enum.Enum):
    """Callback indicator to specify where in the algorithm the callback is invoked."""

    DPInit = libFlowty.FLWT_Where_DPInit
    """In the initialization phase of the dynamic programming algorithm."""
    DPExtend = libFlowty.FLWT_Where_DPExtend
    """In the extension phase of the dynamic programming algorithm."""
    DPDominate = libFlowty.FLWT_Where_DPDominate
    """In the dominance phase of the dynamic programming algorithm."""
    PathMIPSubproblem = libFlowty.FLWT_Where_PathMIPSubproblem
    """Before solving the subproblem in the path MIP algorithm."""
    PathMIPHeuristic = libFlowty.FLWT_Where_PathMIPHeuristic
    """Apply primal heuristic in the path MIP algorithm."""
    PathMIPSolution = libFlowty.FLWT_Where_PathMIPSolution
    """Evaluate a primal solution in the path MIP algorithm."""
    PathMIPInit = libFlowty.FLWT_Where_PathMIPInit
    """Generate a set of initial paths for the path MIP algorithm."""
    PathMIPCuts = libFlowty.FLWT_Where_PathMIPCuts
    """Apply cuts in the path MIP algorithm."""


class DominanceType(enum.Enum):
    """Exact dominance critaria."""

    Exact = libFlowty.FLWT_DominanceType_Exact
    """No resource dominance only dominance criteria on cost."""
    NoResourceDominance = libFlowty.FLWT_DominanceType_NoResourceDominance
    """Dominance criteria on cost and disposable resources."""
    DisposableResourceDominance = (
        libFlowty.FLWT_DominanceType_DisposableResourceDominance
    )
