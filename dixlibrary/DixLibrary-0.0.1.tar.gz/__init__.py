from sympy.core.mul import (Mul, prod)
from sympy.matrices.dense import (Matrix, diag)
from sympy.polys.polytools import (Poly, degree_list, rem)
from sympy.simplify.simplify import simplify
from sympy.tensor.indexed import IndexedBase
from sympy.polys.monomials import itermonomials, monomial_deg
from sympy.polys.orderings import monomial_key
from sympy.polys.polytools import poly_from_expr, total_degree
from sympy.functions.combinatorial.factorials import binomial
from itertools import combinations_with_replacement
from sympy.utilities.exceptions import SymPyDeprecationWarning


import sympy as sym
from sympy.polys import subresultants_qq_zz

class DixonResultant():
    """
    A class for retrieving the Dixon's resultant of a multivariate
    system.
    Examples
    ========
    >>> from sympy import symbols
    >>> from sympy.polys.multivariate_resultants import DixonResultant
    >>> x, y = symbols('x, y')
    >>> p = x + y
    >>> q = x ** 2 + y ** 3
    >>> h = x ** 2 + y
    >>> dixon = DixonResultant(variables=[x, y], polynomials=[p, q, h])
    >>> poly = dixon.get_dixon_polynomial()
    >>> matrix = dixon.get_dixon_matrix(polynomial=poly)
    >>> matrix
    Matrix([
    [ 0,  0, -1,  0, -1],
    [ 0, -1,  0, -1,  0],
    [-1,  0,  1,  0,  0],
    [ 0, -1,  0,  0,  1],
    [-1,  0,  0,  1,  0]])
    >>> matrix.det()
    0
    See Also
    ========
    Notebook in examples: sympy/example/notebooks.
    References
    ==========
    .. [1] [Kapur1994]_
    .. [2] [Palancz08]_
    """

    def __init__(self, polynomials, variables):
        """
        A class that takes two lists, a list of polynomials and list of
        variables. Returns the Dixon matrix of the multivariate system.
        Parameters
        ----------
        polynomials : list of polynomials
            A  list of m n-degree polynomials
        variables: list
            A list of all n variables
        """
        self.polynomials = polynomials
        self.variables = variables

        self.n = len(self.variables)
        self.m = len(self.polynomials)

        a = IndexedBase("alpha")
        # A list of n alpha variables (the replacing variables)
        self.dummy_variables = [a[i] for i in range(self.n)]

        # A list of the d_max of each variable.
        self._max_degrees = [max(degree_list(poly)[i] for poly in self.polynomials)
            for i in range(self.n)]

    @property
    def max_degrees(self):
        SymPyDeprecationWarning(feature="max_degrees",
                        issue=17763,
                        deprecated_since_version="1.5").warn()
        return self._max_degrees

    def get_dixon_polynomial(self):
        r"""
        Returns
        =======
        dixon_polynomial: polynomial
            Dixon's polynomial is calculated as:
            delta = Delta(A) / ((x_1 - a_1) ... (x_n - a_n)) where,
            A =  |p_1(x_1,... x_n), ..., p_n(x_1,... x_n)|
                 |p_1(a_1,... x_n), ..., p_n(a_1,... x_n)|
                 |...             , ...,              ...|
                 |p_1(a_1,... a_n), ..., p_n(a_1,... a_n)|
        """
        if self.m != (self.n + 1):
            raise ValueError('Method invalid for given combination.')

        # First row
        rows = [self.polynomials]

        temp = list(self.variables)

        for idx in range(self.n):
            temp[idx] = self.dummy_variables[idx]
            substitution = {var: t for var, t in zip(self.variables, temp)}
            rows.append([f.subs(substitution) for f in self.polynomials])

        A = Matrix(rows)

        terms = zip(self.variables, self.dummy_variables)
        product_of_differences = Mul(*[a - b for a, b in terms])
        dixon_polynomial = (A.det() / product_of_differences).factor()

        return poly_from_expr(dixon_polynomial, self.dummy_variables)[0]

    def get_upper_degree(self):
        SymPyDeprecationWarning(feature="get_upper_degree",
                        useinstead="get_max_degrees",
                        issue=17763,
                        deprecated_since_version="1.5").warn()

        list_of_products = [self.variables[i] ** self._max_degrees[i]
                            for i in range(self.n)]
        product = prod(list_of_products)
        product = Poly(product).monoms()

        return monomial_deg(*product)

    def get_max_degrees(self, polynomial):
        r"""
        Returns a list of the maximum degree of each variable appearing
        in the coefficients of the Dixon polynomial. The coefficients are
        viewed as polys in $x_1, x_2, \dots, x_n$.
        """
        deg_lists = [degree_list(Poly(poly, self.variables))
                     for poly in polynomial.coeffs()]

        max_degrees = [max(degs) for degs in zip(*deg_lists)]

        return max_degrees

    def get_dixon_matrix(self, polynomial):
        r"""
        Construct the Dixon matrix from the coefficients of polynomial
        \alpha. Each coefficient is viewed as a polynomial of x_1, ...,
        x_n.
        """

        max_degrees = self.get_max_degrees(polynomial)

        # list of column headers of the Dixon matrix.
        monomials = itermonomials(self.variables, max_degrees)
        monomials = sorted(monomials, reverse=True,
                           key=monomial_key('lex', self.variables))

        dixon_matrix = Matrix([[Poly(c, *self.variables).coeff_monomial(m)
                                for m in monomials]
                                for c in polynomial.coeffs()])

        # remove columns if needed
        if dixon_matrix.shape[0] != dixon_matrix.shape[1]:
            keep = [column for column in range(dixon_matrix.shape[-1])
                    if any(element != 0 for element
                        in dixon_matrix[:, column])]

            dixon_matrix = dixon_matrix[:, keep]

        return dixon_matrix

    def KSY_precondition(self, matrix):
        """
        Test for the validity of the Kapur-Saxena-Yang precondition.
        The precondition requires that the column corresponding to the
        monomial 1 = x_1 ^ 0 * x_2 ^ 0 * ... * x_n ^ 0 is not a linear
        combination of the remaining ones. In SymPy notation this is
        the last column. For the precondition to hold the last non-zero
        row of the rref matrix should be of the form [0, 0, ..., 1].
        """
        if matrix.is_zero_matrix:
            return False

        m, n = matrix.shape

        # simplify the matrix and keep only its non-zero rows
        matrix = simplify(matrix.rref()[0])
        rows = [i for i in range(m) if any(matrix[i, j] != 0 for j in range(n))]
        matrix = matrix[rows,:]

        condition = Matrix([[0]*(n-1) + [1]])

        if matrix[-1,:] == condition:
            return True
        else:
            return False

    def delete_zero_rows_and_columns(self, matrix):
        """Remove the zero rows and columns of the matrix."""
        rows = [
            i for i in range(matrix.rows) if not matrix.row(i).is_zero_matrix]
        cols = [
            j for j in range(matrix.cols) if not matrix.col(j).is_zero_matrix]

        return matrix[rows, cols]

    def product_leading_entries(self, matrix):
        """Calculate the product of the leading entries of the matrix."""
        res = 1
        for row in range(matrix.rows):
            for el in matrix.row(row):
                if el != 0:
                    res = res * el
                    break
        return res

    def get_KSY_Dixon_resultant(self, matrix):
        """Calculate the Kapur-Saxena-Yang approach to the Dixon Resultant."""
        matrix = self.delete_zero_rows_and_columns(matrix)
        _, U, _ = matrix.LUdecomposition()
        matrix = self.delete_zero_rows_and_columns(simplify(U))

        return self.product_leading_entries(matrix)