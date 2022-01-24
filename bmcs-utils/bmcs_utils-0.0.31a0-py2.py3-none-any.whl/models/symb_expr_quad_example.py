import sympy as sp
import traits.api as tr
import numpy as np
from models.symb_expr import SymbExpr, InjectSymbExpr

class QuadraticSym(SymbExpr):
    # -------------------------------------------------------------------------
    # Symbolic derivation of variables
    # -------------------------------------------------------------------------
    x = sp.Symbol(
        r'x', real=True,
    )

    # -------------------------------------------------------------------------
    # Model parameters
    # -------------------------------------------------------------------------
    a, b, c = sp.symbols(
        r'a, b, c', real=True,
    )

    # -------------------------------------------------------------------------
    # Expressions
    # -------------------------------------------------------------------------

    y_x = a * x ** 2 + b * x + c

    dy_dx = y_x.diff(x)

    #-------------------------------------------------------------------------
    # Declaration of the lambdified methods
    #-------------------------------------------------------------------------

    symb_model_params = ['a', 'b', 'c']

    # List of expressions for which the methods `get_`
    symb_expressions = [
        ('y_x', ('x',)),
        ('dy_dx', ('x',)),
    ]

class QuadraticModel(InjectSymbExpr):

    symb_class = QuadraticSym

    a = tr.Float(8, param=True)
    b = tr.Float(3, param=True)
    c = tr.Float(8, param=True)

qm = QuadraticModel()
print(qm.symb.get_y_x(3))
print(qm.symb.get_dy_dx(np.linspace(0,10,11)))