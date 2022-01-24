import sympy as sp


class Step:
    equation: sp.Eq

    def __init__(self, a, b) -> None:
        if isinstance(a, str):
            a = sp.Symbol(a)
        if isinstance(b, str):
            b = sp.Symbol(b)
        self.equation = sp.Eq(a, b, evaluate=False)

    def __str__(self) -> str:
        return str(self.equation)
