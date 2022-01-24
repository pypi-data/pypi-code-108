from typing import Dict, List
import numpy as np


class GramSchmidtMonimial:
    """
    Class generates an orthogonal basis for an arbitrary number of
    elements.

    If x denotes the fictitious spin variable. For a binary system x typically
    takes the values -1 and 1, for a ternary -1,0,1 and so on.

    The class starts out from the monomial basis
    {1, x, x^2, x^3, x^4,...,x^n}

    If y_i denotes the new orthogonal basis function they are computed by the
    Gram-Schmidt procedure
    y_0 = 1
    y_1 = x - <x,y_0>y_0, then y_1 = y_1/||y_1||
    y_2 = x^2 - <x^2,y_1>y_1 - <x^2,y_2>y_2, then y_2 = y_2/||y_2||
    and so on
    <x,y> denotes the inner product between to functions
    and ||x|| = sqrt(<x,x>) is the norm of the function

    Parameter:

    num_symbols:
        Number of unique symbols
    """

    def __init__(self, num_symbols: int):
        self.values = []
        if num_symbols % 2 == 1:
            highest = (num_symbols - 1) / 2
        else:
            highest = num_symbols / 2

        # Assign spin value for each element
        while highest > 0:
            self.values.append(highest)
            self.values.append(-highest)
            highest -= 1
        if num_symbols % 2 == 1:
            self.values.append(0)

        self.bf_values = []

    def spin_dict(self, symbols: List[str]) -> Dict[str, int]:
        """
        Return a dictionary with the spin variable for each of the
        passed symbols
        """
        return {s: self.values[i] for i, s in enumerate(symbols)}

    def basis_functions(self, symbols: List[str]) -> List[Dict[str, float]]:
        """
        Construct the spin dictionary from a list of symbols
        """
        symbols = sorted(symbols)
        bf_list = []
        for bf in self.bf_values[1:]:
            bf_list.append(dict(zip(symbols, bf)))

        return bf_list

    def build(self):
        """
        Populates the bf_values table
        The bf_value table has the following structure for 2 atoms
        -------------------------------------
        phi_0(values[0]) | phi_0(values[1]) |
        -------------------------------------
        phi_1(values[1]) | phi_1(values[1]) |
        -------------------------------------

        phi_i is the basis function derived by Gram-Schmidt from a monomial
        basis
        """
        # The first basis function is just the constant 1
        self.bf_values.append([1.0 for i in range(len(self.values))])

        # Loop over all basis functions
        num_values = len(self.values)
        for bf1 in range(1, num_values):
            new_bf_values = []
            for i in range(num_values):
                new_bf_values.append(self.evaluate_monomial_basis_function(bf1, self.values[i]))
                for bf2 in range(bf1):
                    new_bf_values[-1] -= self.dot_monomial_bf(bf1, bf2) \
                        * self.bf_values[bf2][i]

            self.bf_values.append(new_bf_values)

            # Normalize
            bf_norm = self.norm(bf1)
            for i in range(num_values):
                self.bf_values[bf1][i] /= bf_norm

    def dot(self, bf1: int, bf2: int) -> float:
        """
        Performs the dot product between two basis functions

        Parameters:

        bf1:
            Index of the first basis function
        bf2:
            Index of the second basis function
        """
        if (bf1 >= len(self.values) or bf2 >= len(self.values)):
            raise ValueError("The provided indices has to be smaller "
                             "than total number of basis functions")

        dot_prod = 0.0
        for i in range(len(self.values)):
            dot_prod += self.bf_values[bf1][i] * self.bf_values[bf2][i]
        return dot_prod / len(self.values)

    def dot_monomial_bf(self, monomial: int, bf: int) -> float:
        """
        Perfmorms the dot product betweeen a monomial basis function and a
        "proper" basis function

        Parameters:

        monomial:
            Integer specifying the power of the monimial

        bf:
            Integer specifying the orthonormal basis function
        """
        dot_prod = 0.0
        for i, value in enumerate(self.values):
            dot_prod += (self.evaluate_monomial_basis_function(monomial, value) *
                         self.bf_values[bf][i])
        return dot_prod / len(self.values)

    def norm(self, bf: List[float]) -> float:
        """
        Computes the norm of a basis function

        Parameter:

        bf:
            List with all the basis function values
        """
        return np.sqrt(self.dot(bf, bf))

    def eval(self, bf: List[float], valueIndex: int) -> float:
        """
        Evaluates the basis function

        Parameter:

        bf:
            List with all basis functions

        valueIndex:
            Index into the array of basis function values for basis function
            determined by bf
        """
        return self.bf_values[bf][valueIndex]

    def evaluate_monomial_basis_function(self, power: int, value: float) -> float:
        """
        Evaluate monimial basis

        Paraeters:

        power:
            Power of the monomial

        value:
            Value to be raised to the given power
        """
        # pylint: disable=no-self-use
        return value**power
