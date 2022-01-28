from typing import List, Union, Tuple
from flowty.constants import ConstrSense
from flowty.interop import ffi, libFlowty, checked


class LinExpr:
    """
    Class to represent linear expressions.

    Expressions are operator overloaded so it is possible to do

    ```python
    expr = 2 * x - y + 4
    expr += 3 * z
    expr *= 2
    expr += otherExpr
    ```
    """

    def __init__(
        self, coefs: List[float] = [], vars: List["Var"] = [], constant: float = 0.0
    ):
        """
        Initialize linear expression

        Parameters:
            coefs: List of coefficients.
            vars: List of variables.
            constant: A constant term

        Raises:
            ValueError: If `coefs` and `vars` do not have the same length.
        """

        if len(coefs) != len(vars):
            raise ValueError("Parameters 'coefs' and 'vars' must have same length.")

        self.__linExpr = ffi.new("FLWT_LinExpr **")
        checked(libFlowty.FLWT_LinExpr_new(self.__linExpr))
        self.__linExpr = self.__linExpr[0]

        self.addConstant(constant)
        for c, v in zip(coefs, vars):
            self.addTerm(c, v)

    def __del__(self):
        checked(libFlowty.FLWT_LinExpr_delete(self.__linExpr))

    def __add__(self, other: Union["Var", "LinExpr", int, float]) -> "LinExpr":
        result = LinExpr(self.coefs, self.vars, self.constant)
        if isinstance(other, Var):
            result.addTerm(1, other)
        elif isinstance(other, LinExpr):
            result.addExpr(other)
        elif isinstance(other, (int, float)):
            result.addConstant(other)
        return result

    def __radd__(self, other: Union["Var", "LinExpr", int, float]) -> "LinExpr":
        return self.__add__(other)

    def __iadd__(self, other: Union["Var", "LinExpr", int, float]) -> "LinExpr":
        if isinstance(other, Var):
            self.addTerm(1, other)
        elif isinstance(other, LinExpr):
            self.addExpr(other)
        elif isinstance(other, (int, float)):
            self.addConstant(other)
        return self

    def __sub__(self, other: Union["Var", "LinExpr", int, float]) -> "LinExpr":
        result = LinExpr(self.coefs, self.vars, self.constant)
        if isinstance(other, Var):
            result.addTerm(-1, other)
        elif isinstance(other, LinExpr):
            result.addExpr(-1 * other)
        elif isinstance(other, (int, float)):
            result.addConstant(-other)
        return result

    def __rsub__(self, other: Union["Var", "LinExpr", int, float]) -> "LinExpr":
        return (-self).__add__(other)

    def __isub__(self, other: Union["Var", "LinExpr", int, float]) -> "LinExpr":
        if isinstance(other, Var):
            self.addTerm(-1, other)
        elif isinstance(other, LinExpr):
            self.addExpr(-1 * other)
        elif isinstance(other, (int, float)):
            self.addConstant(-other)
        return self

    def __mul__(self, other: Union[int, float]) -> "LinExpr":
        assert isinstance(other, (int, float))
        result = LinExpr(self.coefs, self.vars, self.constant)
        c = result.constant
        result.addConstant(c * other - c)

        for c, v in zip(result.coefs, result.vars):
            result.addTerm(c * other - c, v)
        return result

    def __rmul__(self: "LinExpr", other: Union[int, float]) -> "LinExpr":
        return self.__mul__(other)

    def __imul__(self: "LinExpr", other: Union[int, float]) -> "LinExpr":
        assert isinstance(other, (int, float))
        c = self.constant
        self.addConstant(c * other - c)

        for c, v in zip(self.coefs, self.vars):
            self.addTerm(c * other - c, v)
        return self

    def __truediv__(self: "LinExpr", other: Union[int, float]) -> "LinExpr":
        assert isinstance(other, (int, float))
        result = LinExpr(self.coefs, self.vars, self.constant)
        c = result.constant
        result.addConstant(c / other - c)

        for c, v in zip(result.coefs, result.vars):
            result.addTerm(c / other - c, v)
        return result

    def __itruediv__(self: "LinExpr", other: Union[int, float]) -> "LinExpr":
        assert isinstance(other, (int, float))
        c = self.constant
        self.addConstant(c / other - c)

        for c, v in zip(self.coefs, self.vars):
            self.addTerm(c / other - c, v)
        return self

    def __neg__(self: "LinExpr") -> "LinExpr":
        return self.__mul__(-1)

    def __eq__(self, other) -> "LinEqua":
        result = self - other
        return LinEqua(result, sense=ConstrSense.Equal)

    def __le__(self, other: Union["Var", "LinExpr", int, float]) -> "LinEqua":
        result = self - other
        return LinEqua(result, sense=ConstrSense.LessOrEqual)

    def __ge__(self, other: Union["Var", "LinExpr", int, float]) -> "LinEqua":
        result = self - other
        return LinEqua(result, sense=ConstrSense.GreaterOrEqual)

    def addConstant(self, constant: float) -> None:
        """
        Adds a constant to the linear expression.

        Parameters:
            constant: The constant to add.
        """
        checked(libFlowty.FLWT_LinExpr_addConstant(self.__linExpr, constant))

    def addExpr(self, expr: "LinExpr") -> None:
        """
        Adds another expression to the linear expression.

        Parameters:
            expr: The expression to add.
        """
        for c, v in zip(expr.coefs, expr.vars):
            self.addTerm(c, v)
        self.addConstant(expr.constant)

    def addTerm(self, coef: float, var: "Var") -> None:
        """
        Adds a term to the linear expression.

        Parameters:
            coef: The coefficients.
            var: The variable.
        """
        checked(libFlowty.FLWT_LinExpr_addTerm(self.__linExpr, coef, var._Var__var))

    @property
    def constant(self) -> float:
        """The constant term."""
        constant = ffi.new("double *")
        checked(libFlowty.FLWT_LinExpr_getConstant(self.__linExpr, constant))
        return constant[0]

    @property
    def coefs(self) -> List[float]:
        """A list of the coefficients."""
        num = ffi.new("int *")
        checked(libFlowty.FLWT_LinExpr_getNumTerms(self.__linExpr, num))
        num = num[0]
        array = ffi.new("double []", num)
        checked(libFlowty.FLWT_LinExpr_getCoefs(self.__linExpr, array))
        return [array[i] for i in range(num)]

    @property
    def vars(self) -> List["Var"]:
        """A list of the variables."""
        num = ffi.new("int *")
        checked(libFlowty.FLWT_LinExpr_getNumTerms(self.__linExpr, num))
        num = num[0]
        array = ffi.new("FLWT_Var *[]", num)
        checked(libFlowty.FLWT_LinExpr_getVars(self.__linExpr, array))
        return [Var(array[i]) for i in range(num)]


class LinEqua:
    """
    Class to represent linear equations.

    Equations are primarily used as temporary objects when adding linear expressions to
    models. It should not be necessary to use them by themselves.

    The equation consists of an [LinExpr][flowty.entities.LinExpr] and a
    [ConstrSense][flowty.constants.ConstrSense] such that

    ```python
    expr = 2 * x + 3 * y + 6
    equa = LinEqua(expr, 'L') # 2 * x + 3 * y <= 6
    equa = expr <= 0 # 2 * x + 3 * y <= 6
    ```

    The [LinEqua][flowty.entities.LinEqua] derives from
    [LinExpr][flowty.entities.LinExpr] and can be manipulated in the same fashion.
    """

    def __init__(
        self,
        expr: Union["LinExpr", "LinEqua"],
        sense: ConstrSense = ConstrSense.Equal,
        rhs: float = 0,
    ):
        """
        Initialize linear equation

        Parameters:
            expr: An expression or copy from another equation
            sense: The constraints sense as either
                [Equal][flowty.constants.ConstrSense.Equal],
                [LessOrEqual][flowty.constants.ConstrSense.LessOrEqual], or
                [GreaterOrEqual][flowty.constants.ConstrSense.GreaterOrEqual].
        """
        self.__linEqua = ffi.new("FLWT_LinEqua **")

        if isinstance(expr, LinEqua):
            checked(libFlowty.FLWT_LinEqua_copy(self.__linEqua, expr._LinEqua__linEqua))
        else:
            checked(
                libFlowty.FLWT_LinEqua_new(
                    self.__linEqua, expr._LinExpr__linExpr, sense.value, rhs
                )
            )
        self.__linEqua = self.__linEqua[0]

    def __del__(self):
        checked(libFlowty.FLWT_LinEqua_delete(self.__linEqua))

    @property
    def sense(self) -> float:
        """The right-hand-side."""
        sense = ffi.new("FLWT_ConstrSense *")
        checked(libFlowty.FLWT_LinEqua_getSense(self.__linEqua, sense))
        sense = sense[0]
        return ConstrSense(sense)

    @property
    def rhs(self) -> float:
        """The right-hand-side."""
        constant = ffi.new("double *")
        checked(libFlowty.FLWT_LinEqua_getRhs(self.__linEqua, constant))
        return constant[0]

    @property
    def coefs(self) -> List[float]:
        """A list of the coefficients."""
        num = ffi.new("int *")
        checked(libFlowty.FLWT_LinEqua_getNumTerms(self.__linEqua, num))
        num = num[0]
        array = ffi.new("double []", num)
        checked(libFlowty.FLWT_LinEqua_getCoefs(self.__linEqua, array))
        return [array[i] for i in range(num)]

    @property
    def vars(self) -> List["Var"]:
        """A list of the variables."""
        num = ffi.new("int *")
        checked(libFlowty.FLWT_LinEqua_getNumTerms(self.__linEqua, num))
        num = num[0]
        array = ffi.new("FLWT_Var *[]", num)
        checked(libFlowty.FLWT_LinEqua_getVars(self.__linEqua, array))
        return [Var(array[i]) for i in range(num)]


class Var:
    """
    The variable class.

    Variables are created by adding variables to a model using the either the
    [addVar][flowty.model.Model.addVar] method to create a single variable or the
    [addGraph][flowty.model.Model.addGraph] method to add a graph with corresponding
    edge variables stored in the [Graph.vars][flowty.entities.Graph.vars]
    property.

    For an edge variable this class offers the possibility to query for source and
    target vertices or the edge in the graph.
    """

    BUFFER_SIZE = 512

    def __init__(self, var: ffi.CData = ffi.NULL):
        self.__var = var
        self.__str_buffer = ffi.new("char[{}]".format(self.BUFFER_SIZE))

    def __add__(self, other: Union["Var", LinExpr, int, float]) -> LinExpr:
        if isinstance(other, Var):
            return LinExpr([1, 1], [self, other])
        elif isinstance(other, LinExpr):
            return LinExpr([1], [self]) + other
        elif isinstance(other, (int, float)):
            return LinExpr([1], [self], other)

    def __radd__(self, other: Union["Var", LinExpr, int, float]) -> LinExpr:
        return self.__add__(other)

    def __sub__(self, other: Union["Var", LinExpr, int, float]) -> LinExpr:
        if isinstance(other, Var):
            return LinExpr([1, -1], [self, other])
        elif isinstance(other, LinExpr):
            return LinExpr([1], [self]) - other
        elif isinstance(other, (int, float)):
            return LinExpr([1], [self], -other)

    def __rsub__(self, other: Union["Var", LinExpr, int, float]) -> LinExpr:
        if isinstance(other, Var):
            return LinExpr([-1, 1], [self, other])
        elif isinstance(other, LinExpr):
            return other - LinExpr([1], [self])
        elif isinstance(other, (int, float)):
            return LinExpr([-1], [self], other)

    def __mul__(self, other: Union[int, float]) -> LinExpr:
        assert isinstance(other, (int, float))
        return LinExpr([other], [self])

    def __rmul__(self, other: Union[int, float]) -> LinExpr:
        return self.__mul__(other)

    def __truediv__(self, other: Union[int, float]) -> LinExpr:
        assert isinstance(other, (int, float))
        return self.__mul__(1.0 / other)

    def __neg__(self) -> LinExpr:
        return LinExpr([-1.0], [self])

    def __eq__(self, other) -> LinEqua:
        if isinstance(other, Var):
            expr = LinExpr([1, -1], [self, other])
            return LinEqua(expr, sense=ConstrSense.Equal)
        elif isinstance(other, LinExpr):
            return other == self
        elif isinstance(other, (int, float)):
            expr = LinExpr([1], [self])
            if other != 0:
                return LinEqua(expr, sense=ConstrSense.Equal, rhs=1 * other)
            return LinEqua(expr, sense=ConstrSense.Equal)

    def __le__(self, other: Union["Var", LinExpr, int, float]) -> LinEqua:
        if isinstance(other, Var):
            expr = LinExpr([1, -1], [self, other])
            return LinEqua(expr, sense=ConstrSense.LessOrEqual)
        elif isinstance(other, LinExpr):
            return other >= self
        elif isinstance(other, (int, float)):
            expr = LinExpr([1], [self])
            if other != 0:
                return LinEqua(expr, sense=ConstrSense.LessOrEqual, rhs=1 * other)
            return LinEqua(expr, sense=ConstrSense.LessOrEqual)

    def __ge__(self, other: Union["Var", LinExpr, int, float]) -> LinEqua:
        if isinstance(other, Var):
            expr = LinExpr([1, -1], [self, other])
            return LinEqua(expr, sense=ConstrSense.GreaterOrEqual)
        elif isinstance(other, LinExpr):
            return other <= self
        elif isinstance(other, (int, float)):
            expr = LinExpr([1], [self])
            if other != 0:
                return LinEqua(expr, sense=ConstrSense.GreaterOrEqual, rhs=1 * other)
            return LinEqua(expr, sense=ConstrSense.GreaterOrEqual)

    @property
    def lb(self) -> float:
        """The lower bound."""
        value = ffi.new("double *")
        checked(libFlowty.FLWT_Var_getLb(self.__var, value))
        return value[0]

    @property
    def ub(self) -> float:
        """The upper bound."""
        value = ffi.new("double *")
        checked(libFlowty.FLWT_Var_getUb(self.__var, value))
        return value[0]

    @property
    def obj(self) -> float:
        """The objective coefficient."""
        value = ffi.new("double *")
        checked(libFlowty.FLWT_Var_getObj(self.__var, value))
        return value[0]

    @property
    def type(self) -> str:
        """The type given with [VarType][flowty.constants.VarType]."""
        value = ffi.new("char *")
        checked(libFlowty.FLWT_Var_getType(self.__var, value))
        return value[0]

    @property
    def name(self) -> str:
        """
        The variable name.
        """
        checked(
            libFlowty.FLWT_Var_getName(self.__var, self.__str_buffer, self.BUFFER_SIZE)
        )
        return ffi.string(self.__str_buffer).decode("utf-8")

    @property
    def x(self) -> float:
        """The value in the current solution"""
        value = ffi.new("double *")
        checked(libFlowty.FLWT_Var_getX(self.__var, value))
        return value[0]

    @property
    def idx(self) -> int:
        """The unique id of the variable in the model."""
        value = ffi.new("int *")
        checked(libFlowty.FLWT_Var_getIdx(self.__var, value))
        return value[0]

    @property
    def graphIdx(self) -> int:
        """
        The id of the graph the variable is associated to.

        Raises:
            ValueError: If the variable is not associated with a graph.
        """
        value = ffi.new("int *")
        checked(libFlowty.FLWT_Var_getGraphIdx(self.__var, value))

        if value == -1:
            raise ValueError("No associated graph")

        return value[0]

    @property
    def source(self) -> int:
        """
        The source vertex of a edge variable.

        Raises:
            ValueError: If the variable is not associated with a graph.
        """
        value = ffi.new("int *")
        checked(libFlowty.FLWT_Var_getEdgeSource(self.__var, value))

        if value == -1:
            raise ValueError("No associated graph")

        return value[0]

    @property
    def target(self) -> int:
        """
        The target vertex of a edge variable.

        Raises:
            ValueError: If the variable is not associated with a graph.
        """
        value = ffi.new("int *")
        checked(libFlowty.FLWT_Var_getEdgeTarget(self.__var, value))

        if value == -1:
            raise ValueError("No associated graph")

        return value[0]

    @property
    def edge(self) -> Tuple[int, int]:
        """
        The edge of a edge variable.

        Raises:
            ValueError: If the variable is not associated with a graph.
        """
        source = ffi.new("int *")
        target = ffi.new("int *")
        checked(libFlowty.FLWT_Var_getEdge(self.__var, source, target))

        if source == -1 or target == -1:
            raise ValueError("No associated graph")

        return (source[0], target[0])


class Constr:
    """
    The constraint class.

    Constraints are created by adding linear equations to a model using the
    [addConstr][flowty.model.Model.addConstr] method.
    """

    BUFFER_SIZE = 512

    def __init__(self, constr: ffi.CData = ffi.NULL):
        self.__constr = constr
        self.__str_buffer = ffi.new("char[{}]".format(self.BUFFER_SIZE))

    @property
    def name(self) -> str:
        """
        The constraint name.
        """
        checked(
            libFlowty.FLWT_Constr_getName(
                self.__var, self.__str_buffer, self.BUFFER_SIZE
            )
        )
        return ffi.string(self.__str_buffer).decode("utf-8")

    @property
    def idx(self) -> int:
        """The unique id of the constraint in the model."""
        value = ffi.new("int *")
        checked(libFlowty.FLWT_Constr_getIdx(self.__constr, value))
        return value[0]


class Graph:
    """
    The graph class.

    Graphs are created by adding them to a model using the the
    [addGraph][flowty.model.Model.addGraph] method.
    """

    def __init__(self, graph: ffi.CData = ffi.NULL):
        self.__graph = graph

    @property
    def vars(self) -> List["Var"]:
        """The edge variables associated to the graph"""
        num = ffi.new("int *")
        checked(libFlowty.FLWT_Graph_getNumVars(self.__graph, num))
        num = num[0]
        array = ffi.new("FLWT_Var *[]", num)
        checked(libFlowty.FLWT_Graph_getVars(self.__graph, array))
        return [Var(array[i]) for i in range(num)]

    @property
    def n(self) -> int:
        """The number of vertices."""
        num = ffi.new("int *")
        checked(libFlowty.FLWT_Graph_getN(self.__graph, num))
        return num[0]

    @property
    def m(self) -> int:
        """The number of edges."""
        num = ffi.new("int *")
        checked(libFlowty.FLWT_Graph_getM(self.__graph, num))
        return num[0]

    @property
    def idx(self) -> int:
        """The unique id of the graph in the model."""
        value = ffi.new("int *")
        checked(libFlowty.FLWT_Graph_getIdx(self.__graph, value))
        return value[0]

    @property
    def source(self) -> int:
        """The source vertex of the graph."""
        value = ffi.new("int *")
        checked(libFlowty.FLWT_Graph_getSource(self.__graph, value))
        return value[0]

    @property
    def sink(self) -> int:
        """The sink vertex of the graph."""
        value = ffi.new("int *")
        checked(libFlowty.FLWT_Graph_getSink(self.__graph, value))
        return value[0]


class Path:
    """
    The path class.

    Paths represents a list of edge variables for a graph in a
    [solution][flowty.entities.Solution]. Obtain the paths of a solution using the
    [path][flowty.entities.Solution.paths] property.
    """

    def __init__(self, path: ffi.CData = ffi.NULL):
        self.__path = path

    @property
    def idx(self) -> int:
        """The unique id of the path in a solution."""
        value = ffi.new("int *")
        checked(libFlowty.FLWT_Path_getIdx(self.__path, value))
        return value[0]

    @property
    def graphIdx(self) -> int:
        """The id of the graph the path is associated to."""
        value = ffi.new("int *")
        checked(libFlowty.FLWT_Path_getGraphIdx(self.__path, value))
        return value[0]

    @property
    def vars(self) -> List["Var"]:
        """The edge variables associated to the path."""
        num = ffi.new("int *")
        checked(libFlowty.FLWT_Path_getNumVars(self.__path, num))
        num = num[0]
        array = ffi.new("FLWT_Var *[]", num)
        checked(libFlowty.FLWT_Path_getVars(self.__path, array))
        return [Var(array[i]) for i in range(num)]

    @property
    def obj(self) -> float:
        """The objective coefficient."""
        value = ffi.new("double *")
        checked(libFlowty.FLWT_Path_getObj(self.__path, value))
        return value[0]

    @property
    def x(self) -> float:
        """The value in the current solution."""
        value = ffi.new("double *")
        checked(libFlowty.FLWT_Path_getX(self.__path, value))
        return value[0]


class Solution:
    """
    The solution class.

    A solution holds a list of non-zero [variables][flowty.entities.Var] and a (if
    applicable) a list of [paths][flowty.entities.Path]. Obtain the solutions from the
    model using the [solutions][flowty.model.Model.solutions] property.
    """

    def __init__(self, solution: ffi.CData = ffi.NULL):
        self.__solution = solution

    @property
    def idx(self) -> int:
        """The unique id of the solution."""
        value = ffi.new("int *")
        checked(libFlowty.FLWT_Solution_getIdx(self.__solution, value))
        return value[0]

    @property
    def vars(self) -> List["Var"]:
        """The variables in the solution. Including edge variables."""
        num = ffi.new("int *")
        checked(libFlowty.FLWT_Solution_getNumVars(self.__solution, num))
        num = num[0]
        array = ffi.new("FLWT_Var *[]", num)
        checked(libFlowty.FLWT_Solution_getVars(self.__solution, array))
        return [Var(array[i]) for i in range(num)]

    @property
    def paths(self) -> List["Path"]:
        """The paths associated to the solution."""
        num = ffi.new("int *")
        checked(libFlowty.FLWT_Solution_getNumPaths(self.__solution, num))
        num = num[0]
        array = ffi.new("FLWT_Path *[]", num)
        checked(libFlowty.FLWT_Solution_getPaths(self.__solution, array))
        return [Path(array[i]) for i in range(num)]

    @property
    def objectiveValue(self) -> float:
        """The objective value of the solution."""
        value = ffi.new("double *")
        checked(libFlowty.FLWT_Solution_getObjectiveValue(self.__solution, value))
        return value[0]
