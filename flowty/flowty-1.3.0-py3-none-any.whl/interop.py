from pathlib import Path
from sys import maxsize, platform
from cffi import FFI
import flowty

os_is_64_bit = maxsize > 2 ** 32

path = Path(flowty.__file__).parent
pathlib = Path(path, "lib")
libfile = None
if "linux" in platform.lower():
    if os_is_64_bit:
        libfile = Path(pathlib, "libflowty.so")
elif platform.lower().startswith("win"):
    if os_is_64_bit:
        libfile = Path(pathlib, "flowty.dll")

if not libfile:
    raise Exception("You operating system/platform is not supported")

ffi = FFI()

try:
    libFlowty = ffi.dlopen(str(libfile))
except Exception:
    libFlowty = ffi.dlopen(None)

ffi.cdef(
    """
typedef enum {
    FLWT_ObjSense_Minimize = 0,
    FLWT_ObjSense_Maximize = 1,
} FLWT_ObjSense;

typedef enum {
    FLWT_ConstrSense_LessEqual = 0,
    FLWT_ConstrSense_Equal = 1,
    FLWT_ConstrSense_GreaterEqual = 2,
} FLWT_ConstrSense;

typedef enum {
  FLWT_OptimizationStatus_Loaded =  1,
  FLWT_OptimizationStatus_Optimal =  2,
  FLWT_OptimizationStatus_Infeasible =  3,
  FLWT_OptimizationStatus_InfeasibleOrUnbounded =  4,
  FLWT_OptimizationStatus_Unbounded =  5,
  FLWT_OptimizationStatus_Cutoff =  6,
  FLWT_OptimizationStatus_IterationLimit =  7,
  FLWT_OptimizationStatus_NodeLimit =  8,
  FLWT_OptimizationStatus_TimeLimit =  9,
  FLWT_OptimizationStatus_SolutionLimit =  10,
  FLWT_OptimizationStatus_Interrupted =  11,
  FLWT_OptimizationStatus_Numeric =  12,
  FLWT_OptimizationStatus_Feasible =  13,
} FLWT_OptimizationStatus;

typedef enum{
  FLWT_Where_DPInit = 0,
  FLWT_Where_DPExtend = 1,
  FLWT_Where_DPDominate = 2,
  FLWT_Where_DPConcatenate = 3,
  FLWT_Where_PathMIPSubproblem = 4,
  FLWT_Where_PathMIPHeuristic = 5,
  FLWT_Where_PathMIPSolution = 6,
  FLWT_Where_PathMIPInit = 7,
  FLWT_Where_PathMIPCuts = 8,
} FLWT_Where;

typedef enum {
  FLWT_DominanceType_Exact = 0,
  FLWT_DominanceType_NoResourceDominance = 1,
  FLWT_DominanceType_DisposableResourceDominance = 2,
} FLWT_DominanceType;

typedef enum {
  FLWT_Error_InvalidArgument = 10002,
  FLWT_Error_NotSupported = 10003,
  FLWT_Error_UnkownParameter = 10004,
  FLWT_Error_NoLicense = 10005,
} FLWT_Error;

typedef struct FLWT_Var FLWT_Var;
typedef struct FLWT_Constr FLWT_Constr;
typedef struct FLWT_Column FLWT_Column;
typedef struct FLWT_LinExpr FLWT_LinExpr;
typedef struct FLWT_LinEqua FLWT_LinEqua;
typedef struct FLWT_Model FLWT_Model;
typedef struct FLWT_VarResource FLWT_VarResource;
typedef struct FLWT_ConstrResource FLWT_ConstrResource;
typedef struct FLWT_Graph FLWT_Graph;
typedef struct FLWT_Path FLWT_Path;
typedef struct FLWT_Solution FLWT_Solution;
typedef struct FLWT_CallbackModel FLWT_CallbackModel;
typedef struct FLWT_CallbackGraphWeightReturn FLWT_CallbackGraphWeightReturn;
typedef int FLWT_Callback(FLWT_CallbackModel *callbackModel, int where,
                          void *userdata);
typedef int FLWT_CallbackGraphWeight(
    char **states, double *values, int numStates, int source, int target,
    FLWT_CallbackGraphWeightReturn *returnObject, void *userdata);

// Linear modelling entities
int FLWT_Var_getName(FLWT_Var *var, char *name, int size);
int FLWT_Var_getType(FLWT_Var *var, char *type);
int FLWT_Var_getLb(FLWT_Var *var, double *lb);
int FLWT_Var_getUb(FLWT_Var *var, double *ub);
int FLWT_Var_getObj(FLWT_Var *var, double *obj);
int FLWT_Var_getX(FLWT_Var *var, double *x);
int FLWT_Var_getIdx(FLWT_Var *var, int *idx);
int FLWT_Var_getGraphIdx(FLWT_Var *var, int *idx);
int FLWT_Var_getEdgeSource(FLWT_Var *var, int *source);
int FLWT_Var_getEdgeTarget(FLWT_Var *var, int *target);
int FLWT_Var_getEdge(FLWT_Var *var, int *source, int *target);

int FLWT_Constr_getName(FLWT_Constr *constr, char **name, int size);
int FLWT_Constr_getIdx(FLWT_Constr *constr, int *idx);

int FLWT_LinExpr_new(FLWT_LinExpr **expr);
int FLWT_LinExpr_delete(FLWT_LinExpr *expr);
int FLWT_LinExpr_addTerm(FLWT_LinExpr *expr, double coef, FLWT_Var *var);
int FLWT_LinExpr_addConstant(FLWT_LinExpr *expr, double constant);
int FLWT_LinExpr_getConstant(FLWT_LinExpr *expr, double *constant);
int FLWT_LinExpr_getNumTerms(FLWT_LinExpr *expr, int *num);
int FLWT_LinExpr_getCoefs(FLWT_LinExpr *expr, double *coefs);
int FLWT_LinExpr_getVars(FLWT_LinExpr *expr, FLWT_Var **vars);
int FLWT_LinEqua_new(FLWT_LinEqua **equa, FLWT_LinExpr *expr, FLWT_ConstrSense sense,
                     double rhs);
int FLWT_LinEqua_delete(FLWT_LinEqua *equa);
int FLWT_LinEqua_getSense(FLWT_LinEqua *expr, FLWT_ConstrSense *sense);
int FLWT_LinEqua_getRhs(FLWT_LinEqua *expr, double *constant);
int FLWT_LinEqua_getNumTerms(FLWT_LinEqua *expr, int *num);
int FLWT_LinEqua_getCoefs(FLWT_LinEqua *expr, double *coefs);
int FLWT_LinEqua_getVars(FLWT_LinEqua *expr, FLWT_Var **vars);

// Graph
int FLWT_Graph_getIdx(FLWT_Graph *graph, int *idx);
int FLWT_Graph_getNumVars(FLWT_Graph *graph, int *num);
int FLWT_Graph_getVars(FLWT_Graph *graph, FLWT_Var **vars);
int FLWT_Graph_getN(FLWT_Graph *graph, int *num);
int FLWT_Graph_getM(FLWT_Graph *graph, int *num);
int FLWT_Graph_getSource(FLWT_Graph *graph, int *source);
int FLWT_Graph_getSink(FLWT_Graph *graph, int *sink);

// Path
int FLWT_Path_getIdx(FLWT_Path *path, int *idx);
int FLWT_Path_getGraphIdx(FLWT_Path *path, int *idx);
int FLWT_Path_getNumVars(FLWT_Path *path, int *num);
int FLWT_Path_getVars(FLWT_Path *path, FLWT_Var **vars);
int FLWT_Path_getObj(FLWT_Path *path, double *obj);
int FLWT_Path_getX(FLWT_Path *path, double *x);

// Solution
int FLWT_Solution_getIdx(FLWT_Solution *solution, int *idx);
int FLWT_Solution_getNumVars(FLWT_Solution *solution, int *num);
int FLWT_Solution_getVars(FLWT_Solution *solution, FLWT_Var **vars);
int FLWT_Solution_getNumPaths(FLWT_Solution *solution, int *num);
int FLWT_Solution_getPaths(FLWT_Solution *solution, const FLWT_Path **paths);
int FLWT_Solution_getObjectiveValue(FLWT_Solution *solution, double *value);

// Model
int FLWT_Model_new(FLWT_Model **model);
int FLWT_Model_delete(FLWT_Model *model);
int FLWT_Model_read(FLWT_Model *model, char *filename);
int FLWT_Model_write(FLWT_Model *model, char *filename);
int FLWT_Model_addVar(FLWT_Model *model, double lb, double ub, double obj,
                      char type, char *name, FLWT_Var **var);
int FLWT_Model_addConstr(FLWT_Model *model, FLWT_LinEqua *equa, char *name,
                         FLWT_Constr **constr);
int FLWT_Model_setObjective(FLWT_Model *model, FLWT_LinExpr *expr,
                            FLWT_ObjSense sense);
int FLWT_Model_setName(FLWT_Model *model, char *name);
int FLWT_Model_getName(FLWT_Model *model, char *name, int size);
int FLWT_Model_addGraph(FLWT_Model *model, int directed, double *obj, int *from,
                        int *to, int m, int source, int sink, int L,
                        int U, char type, char **names, FLWT_Graph **graph);
int FLWT_Model_addResourceDisposable(FLWT_Model *model, FLWT_Graph *graph,
                                     char consumptionType, double *weight,
                                     char boundsType, double *lb, double *ub,
                                     double *obj, char *name);
int FLWT_Model_addResourceNonDisposable(FLWT_Model *model, FLWT_Graph *graph,
                                        char consumptionType, double *weight,
                                        char boundsType, double *lb, double *ub,
                                        double *obj, char *name);
int FLWT_Model_addResourceCustom(FLWT_Model *model, FLWT_Graph *graph,
                                 char *name);
int FLWT_Model_addPackingSet(FLWT_Model *model, FLWT_Var **var, int size);
int FLWT_Model_getNumVars(FLWT_Model *model, int *num);
int FLWT_Model_getVars(FLWT_Model *model, FLWT_Var **vars);
int FLWT_Model_getNumConstrs(FLWT_Model *model, int *num);
int FLWT_Model_getConstrs(FLWT_Model *model, FLWT_Constr **constrs);
int FLWT_Model_getNumGraphs(FLWT_Model *model, int *num);
int FLWT_Model_getGraphs(FLWT_Model *model, FLWT_Graph **graphs);
int FLWT_Model_getNumSolutions(FLWT_Model *model, int *num);
int FLWT_Model_getSolutions(FLWT_Model *model, FLWT_Solution **solutions);
int FLWT_Model_getObjectiveValue(FLWT_Model *model, double *value);
int FLWT_Model_getObjectiveBound(FLWT_Model *model, double *value);
int FLWT_Model_optimize(FLWT_Model *model,
                        FLWT_OptimizationStatus *optimizationStatus);
int FLWT_Model_setParam(FLWT_Model *model, char *key, char *value);
int FLWT_Model_setParamInt(FLWT_Model *model, char *key, int value);
int FLWT_Model_setParamDbl(FLWT_Model *model, char *key, double value);
int FLWT_Model_setCallback(FLWT_Model *model, FLWT_Callback callback,
                           void *userdata);
int FLWT_Model_setCallbackGraphWeight(FLWT_Model *model, FLWT_Graph *graph,
                                      char **stateResourceNames, int num,
                                      FLWT_CallbackGraphWeight callback,
                                      void *userdata);
int FLWT_Model_setCallbackDominancePenalty(FLWT_Model *model, FLWT_Graph *graph,
                                           const char *resourceName,
                                           double coefficient);
int FLWT_CallbackGraphWeight_return(
    FLWT_CallbackGraphWeightReturn *returnObject, char **returnStates,
    double *returnValues, int returnNum);
int FLWT_Model_setLicenseKey(FLWT_Model *model, char *user, char *key);

// Callback model
int FLWT_CallbackModel_getResource(FLWT_CallbackModel *callbackModel,
                                   char *name, double *value);
int FLWT_CallbackModel_getResourceOther(FLWT_CallbackModel *callbackModel,
                                        char *name, double *other);
int FLWT_CallbackModel_setResource(FLWT_CallbackModel *callbackModel,
                                   char *name, double value);
int FLWT_CallbackModel_keep(FLWT_CallbackModel *callbackModel);
int FLWT_CallbackModel_skip(FLWT_CallbackModel *callbackModel);
int FLWT_CallbackModel_getVertex(FLWT_CallbackModel *callbackModel, int *i);
int FLWT_CallbackModel_getEdge(FLWT_CallbackModel *callbackModel, int *e);
int FLWT_CallbackModel_getX(FLWT_CallbackModel *callbackModel, double *x,
                            int size);
int FLWT_CallbackModel_haveArtificialCost(FLWT_CallbackModel *callbackModel,
                                          int *haveArtificialCost);
int FLWT_CallbackModel_addCut(FLWT_CallbackModel *callbackModel,
                              FLWT_LinEqua *equa);
int FLWT_CallbackModel_getReducedCost(FLWT_CallbackModel *callbackModel,
                                      double *reducedCost, int size);
int FLWT_CallbackModel_getConvexDual(FLWT_CallbackModel *callbackModel,
                                     double *convexDual);
int FLWT_CallbackModel_getNumZeroEdges(FLWT_CallbackModel *callbackModel,
                                       int *numZeroEdges);
int FLWT_CallbackModel_getZeroEdges(FLWT_CallbackModel *callbackModel,
                                    int *zeroEdges);
int FLWT_CallbackModel_setStatus(FLWT_CallbackModel *callbackModel,
                                 FLWT_OptimizationStatus status);
int FLWT_CallbackModel_addPathReducedCost(FLWT_CallbackModel *callbackModel,
                                          double reducedCost, double cost,
                                          int *edges, int size);
int FLWT_CallbackModel_addPath(FLWT_CallbackModel *callbackModel, double cost,
                               int *edges, int size);
int FLWT_CallbackModel_addSolution(FLWT_CallbackModel *callbackModel,
                                   double objValue, double *x, int size);
int FLWT_CallbackModel_getK(FLWT_CallbackModel *callbackModel, int *k);
int FLWT_CallbackModel_getDominanceType(FLWT_CallbackModel *callbackModel,
                                        FLWT_DominanceType *dominanceType);

// Misc
int FLWT_Version(int *major, int *minor, int *patch, int *tweak);

"""
)


def checked(returnCode: int) -> None:
    if returnCode == 0:
        return
    elif returnCode == libFlowty.FLWT_Error_InvalidArgument:
        raise ValueError(f"InvalidArgument ({libFlowty.FLWT_Error_InvalidArgument})")
    elif returnCode == libFlowty.FLWT_Error_NotSupported:
        raise TypeError(f"NotSupported ({libFlowty.FLWT_Error_NotSupported})")
    elif returnCode == libFlowty.FLWT_Error_UnkownParameter:
        raise ValueError(f"UnkownParameter ({libFlowty.FLWT_Error_UnkownParameter})")
    elif returnCode == libFlowty.FLWT_Error_NoLicense:
        raise Exception(f"NoLicense ({libFlowty.FLWT_Error_NoLicense})")

    raise Exception(f"Unknown error {returnCode}")
