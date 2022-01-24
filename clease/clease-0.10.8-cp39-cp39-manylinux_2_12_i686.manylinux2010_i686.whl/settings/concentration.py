"""Class containing a manager for setting up concentrations of species."""
from collections import OrderedDict
from random import choice
import numpy as np
from scipy.optimize import minimize
from clease.jsonio import jsonable
from clease.tools import (remove_redundant_constraints, remove_redundant_equations)

__all__ = ('Concentration',)


class IntConversionNotConsistentError(Exception):
    """
    Exception raised if equality constraints are not satisfied when
    converted to integers.
    """


class InvalidConcentrationError(Exception):
    """Exception raised when no valid concentration could be found."""


class InvalidConstraintError(Exception):
    """Exception raised when user provides invalid constraints."""


# pylint: disable=too-many-instance-attributes
@jsonable('concentration')
class Concentration:
    """
    Specify concentration ranges of consituting elements for cluster
    expansion.
    Concentration range can be specified in three different ways.

        1. specifying the equality and lower bound conditions by specifying
        ``A_lb``, ``b_lb``, ``A_eq`` and ``b_eq`` during initialization,
        2. using ``set_conc_formula_unit()`` method, and
        3. using ``set_conc_ranges()`` method.


    Parameters:

    basis_elements: list
        List of chemical symbols of elements to occupy each basis.
        Even for the cases where there is only one basis (e.g., fcc, bcc, sc),
        a list of symbols should be grouped by basis as in [['Cu', 'Au']]
        (note the nested list form).

    grouped_basis: list (optional, only used when basis are grouped)
        Indices of basis_elements that are considered to be equivalent when
        specifying concentration (e.g., useful when two basis are shared by
        the same set of elements and no distinctions are made between them).
        As an example consider a structure with three sublattices A, B and C.
        If sublattice A and C should be occupied by the same elements and B is
        occupied by a different set of elements. We can group lattice A and C
        by passing [(0, 2), (1,)].


    A_lb: list (optional, only used for linear algebra representation)
        A two-dimention matrix (or nested list) used to specify the lower
        bounds of the concentration ranges.

    b_lb: list (optional, only used for linear algebra representation)
        A list used tp specify the lower bounds of the concentration ranges.

    A_eq: list (optional, only used for linear algegra representation)
        A two-dimention matrix (or nested list) used to specify the equality
        conditions of the concentration ranges.

    b_eq: list (optional, only used for linear algegra representation)
        A list used tp specify the equality condisitons of the concentration
        ranges.

    Example I: Single sublattice

    >>> conc = Concentration(basis_elements=[['Au', 'Cu']])

    Example II: Two sublattices
    >>> conc = Concentration(basis_elements=[['Au', 'Cu'], ['Au', 'Cu', 'X']])

    Example III: Three sublattices where the first and third are grouped
    >>> conc = Concentration(basis_elements=[['Au', 'Cu'], ['Au', 'Cu', 'X'], ['Au', 'Cu']],
    ...                      grouped_basis=[(0, 2), (1,)])
    """

    def __init__(self,
                 basis_elements=None,
                 grouped_basis=None,
                 A_lb=None,
                 b_lb=None,
                 A_eq=None,
                 b_eq=None):
        self.orig_basis_elements = basis_elements
        self.grouped_basis = grouped_basis
        self._check_grouped_basis_elements()

        for basis in basis_elements:
            if not isinstance(basis, (list, tuple)):
                msg = "elements in each basis must be either a list or tuple."
                raise TypeError(msg)
        self.basis_elements = self._get_grouped_basis_elements()

        num_implicit_eq = len(self.basis_elements)
        self.num_concs = len([x for sub in self.basis_elements for x in sub])
        self.fixed_element_constraint_added = False

        if A_lb is not None:
            self.A_lb, self.b_lb = remove_redundant_constraints(np.array(A_lb), np.array(b_lb))
        else:
            self.A_lb = np.empty((0, self.num_concs))
            self.b_lb = np.array([])

        num_usr_eq = 0
        if A_eq is not None:
            A_eq = np.array(A_eq)
            num_usr_eq = A_eq.shape[0]

        self.A_eq = np.zeros((num_implicit_eq, self.num_concs), dtype=int)
        self.b_eq = np.zeros(num_implicit_eq, dtype=int)
        self.orig_num_equality = self.A_eq.shape[0]

        # Ensure concentration in each basis sum to 1
        start_col = 0
        for i, basis in enumerate(self.basis_elements):
            if start_col + len(basis) >= self.A_eq.shape[1]:
                self.A_eq[i, start_col:] = 1
            else:
                self.A_eq[i, start_col:start_col + len(basis)] = 1
            start_col += len(basis)
            self.b_eq[i] = 1

        self._linked_basis = list(range(len(self.basis_elements)))
        if num_usr_eq > 0:
            self.add_usr_defined_eq_constraints(A_eq, b_eq)
        self._get_interbasis_relations()

    def __eq__(self, other):
        return np.allclose(self.A_eq, other.A_eq) and \
            np.allclose(self.b_eq, other.b_eq) and \
            self.basis_elements == other.basis_elements and \
            self.grouped_basis == other.grouped_basis and \
            np.allclose(self.A_lb, other.A_lb) and \
            np.allclose(self.b_lb, other.b_lb)

    def _get_grouped_basis_elements(self):
        if self.grouped_basis is None:
            return self.orig_basis_elements

        gr_basis_elements = []
        for group in self.grouped_basis:
            gr_basis_elements.append(self.orig_basis_elements[group[0]])
        return gr_basis_elements

    def todict(self) -> dict:
        """Return neescary information to store as JSON."""
        data = {
            "A_eq": self.A_eq,
            "b_eq": self.b_eq,
            "A_lb": self.A_lb,
            "b_lb": self.b_lb,
            "basis_elements": self.orig_basis_elements,
        }
        if self.grouped_basis is not None:
            data["grouped_basis"] = self.grouped_basis
        return data

    @classmethod
    def from_dict(cls, data):
        """Initialize data from dictionary."""
        return cls(**data)

    def is_valid_conc(self, conc):
        """Check if the concentration is valid."""
        eq_valid = np.allclose(self.A_eq.dot(conc), self.b_eq)
        ineq_valid = np.all(self.A_lb.dot(conc) - self.b_lb > -1e-6)
        return eq_valid and ineq_valid

    def add_usr_defined_eq_constraints(self, A_eq, b_eq):
        """Add user defined constraints.

        The concentrations are restrictred by the equation
        A_eq*c = b_eq

        Parameters:

        A_eq: nested list of numpy array
            NxM matrix where N is the number of equations and
            M is the overall number of concentrations
        b_eq: list or numpy array
            right hand side vector of the equation length N
        """

        A_eq = np.array(A_eq)
        b_eq = np.array(b_eq)
        if len(A_eq.shape) != 2:
            raise InvalidConstraintError("A_eq has to be a 2D matrix!")
        if len(b_eq.shape) != 1:
            raise InvalidConstraintError("b_eq has to be a 1D vector!")

        if A_eq.shape[1] != self.num_concs:
            raise InvalidConstraintError(
                f"The number of columns in A_eq has to match the number of "
                f"concentration variables. A_eq needs to have "
                f"{self.num_concs} columns")

        if A_eq.shape[0] != len(b_eq):
            raise InvalidConstraintError(
                "The length of b_eq has to be the same as the number of rows "
                "in A_eq.")

        self.A_eq = np.vstack((self.A_eq, A_eq))
        self.b_eq = np.append(self.b_eq, b_eq)
        self.A_eq, self.b_eq = remove_redundant_equations(self.A_eq, self.b_eq)
        self._get_interbasis_relations_for_given_matrix(self.A_eq)

    def _check_ineq_constraints(self, A_lb, b_lb):
        """
        Checks the dimensions of the provided lower bound constraint.
        """
        if A_lb.ndim != 2:
            raise InvalidConstraintError("A_lb has to be a 2D matrix!")

        if b_lb.ndim != 1:
            raise InvalidConstraintError("b_lb has to be a 1D vector!")

        if A_lb.shape[1] != self.num_concs:
            raise InvalidConstraintError(
                f"The number of columns in A_lb has to match the number of "
                f"concentration variables. Hence, A_lb needs to have "
                f"{self.num_concs} columns")

        if A_lb.shape[0] != len(b_lb):
            raise InvalidConstraintError(
                "The length of b_lb has to be the same as the number of rows "
                "in A_lb.")

    def add_usr_defined_ineq_constraints(self, A_lb, b_lb):
        """Add the user defined constraints.

        The concentrations are restrictred by the equation
        A_lb*c > b_lb

        Parameters:

        A_lb: nested list of numpy array
            NxM matrix where N is the number of equations and
            M is the overall number of concentrations
        b_lb: list or numpy array
            right hand side vector of the equation length N
        """
        A_lb = np.array(A_lb)
        b_lb = np.array(b_lb)
        self._check_ineq_constraints(A_lb, b_lb)

        self.A_lb = np.vstack((self.A_lb, A_lb))
        self.b_lb = np.append(self.b_lb, b_lb)
        self.A_lb, self.b_lb = remove_redundant_constraints(self.A_lb, self.b_lb, self.A_eq,
                                                            self.b_eq)
        self._get_interbasis_relations_for_given_matrix(self.A_lb)

    def set_conc_ranges(self, ranges):
        """
        Set concentration range based on lower and upper bounds of each
        element.

        Parameters:

        ranges: list
            Nested list of tuples with the same shape as basis_elements.
            If basis_elements is [["Li", "Ru", "X"], ["O", "X"]], ranges
            coulde be [[(0, 1), (0.2, 0.5), (0, 1)], [(0, 0.8), (0, 0.2)]]
        """
        if len(ranges) != len(self.basis_elements):
            raise InvalidConstraintError(f"The number of bases is wrong. Expected "
                                         f"{len(self.basis_elements)}, got {len(ranges)}")

        for item, basis in zip(ranges, self.basis_elements):
            if len(item) != len(basis):
                raise InvalidConstraintError(
                    f"Inconsistent number of elements in basis. "
                    f"Expected {len(basis)}, got {len(item)}. Basis elements: "
                    f"{self.basis_elements}")
            for rng in item:
                if len(rng) != 2:
                    raise InvalidConstraintError("Provided range needs to be of length 2. "
                                                 "Lower and upper bound")
                if any(x < 0.0 or x > 1.0 for x in rng):
                    raise InvalidConstraintError("Concentrations below 0 or above 1 "
                                                 "can not be used as concentration constraints")

        flatten_rng = [item for sublist in ranges for item in sublist]
        A_lb = np.zeros((2 * self.num_concs, self.num_concs))
        b_lb = np.zeros(2 * self.num_concs)
        for i, item in enumerate(flatten_rng):
            A_lb[2 * i, i] = 1
            A_lb[2 * i + 1, i] = -1
            b_lb[2 * i] = item[0]
            b_lb[2 * i + 1] = -item[1]
        self.add_usr_defined_ineq_constraints(A_lb, b_lb)

    def _get_integers(self, string, variable_range=None):
        """Extract all the integers from a string."""
        # pylint: disable=no-self-use,too-many-branches
        if variable_range is None:
            variable_symbols = []
        else:
            variable_symbols = list(variable_range.keys())
        signs = {"+": 1, "-": -1}
        integers = []
        current_indx = 0
        sum_of_variable_coeff = {k: 0 for k in variable_symbols}
        active_sign = 1
        while current_indx < len(string):
            connected_to_symbol = False
            if string[current_indx] in signs:
                active_sign = signs[string[current_indx]]
            elif string[current_indx] == "<":
                active_sign = 1

            if string[current_indx].isdigit():
                substr = string[current_indx]
                # find how many consecutive digits are there
                indx = current_indx + 1
                while indx < len(string):
                    # end of integer found
                    if not string[indx].isdigit():
                        # case where integer followed by a variable symbol
                        # (e.g., 4x)
                        if string[indx] in variable_symbols:
                            connected_to_symbol = True
                        break
                    substr += string[indx]
                    indx += 1

                # got an integer number
                if not connected_to_symbol:
                    integers.append(int(substr))
                    current_indx = indx
                else:
                    symbol = string[indx]
                    sum_of_variable_coeff[symbol] += active_sign * int(substr)
                    current_indx = indx + 1

            # case where variable symbol is defined without integer
            elif string[current_indx] in variable_symbols:
                symbol = string[current_indx]
                sum_of_variable_coeff[symbol] += active_sign
                current_indx += 1
            else:
                current_indx += 1

        # Ensure valid chemical formula
        for _, value in sum_of_variable_coeff.items():
            if value != 0:
                raise ValueError(f"Invalid formula! {string} {sum_of_variable_coeff}")
        return integers

    def _num_atoms_in_basis(self, formulas, variable_range):
        num_atoms_in_basis = []
        for formula in formulas:
            num_atoms_in_basis.append(np.sum(self._get_integers(formula, variable_range)))
        return num_atoms_in_basis

    def set_conc_formula_unit(self, formulas=None, variable_range=None):
        """Set concentration based on formula unit strings.

        Parameters:

        formulas: list
            List constaining formula strings (e.g.,
            ["Li<x>Ru<1>X<2-x>", "O<3-y>X<y>"], ['Al<4-4x>Mg<3x>Si<x>''])
            1. formula string should be provided per basis.
            2. formula string can only have integer numbers.
            3. only one  dvariable is allowed per basis.
            4. each variable should have at least one instance of 'clean'
            representation (e.g., <x>, <y>)

        variable_range: dict
            Range of each variable used in formulas.
            key is a string, and the value should be int or float
            e.g., {"x": (0, 2), "y": (0, 0.7)}, {'x': (0., 1.)}
        """
        # pylint: disable=too-many-branches
        if formulas is None or variable_range is None:
            raise InvalidConstraintError("formula and variable range has to" " be provided!")

        if len(formulas) != len(self.basis_elements):
            raise InvalidConstraintError(
                f"Inconsistent number of basis passed. "
                f"Expected: {len(self.basis_elements)}, got {len(formulas)}. "
                f"Basis elements: {self.basis_elements}")

        element_conc = self._parse_formula_unit_string(formulas)
        num_atoms_in_basis = self._num_atoms_in_basis(formulas, variable_range)

        A_eq = []
        b_eq = []
        col = 0

        num_elements_with_var = self._num_elements_with_var(variable_range, element_conc)

        # Set equality matrix and vector due to one or more elements has one
        # fixed concentration value.
        # Note: element_conc is an OrderedDict so k, v pairs come in the
        # same order they were added
        for basis, basis_elem in enumerate(element_conc):
            for k, v in basis_elem.items():
                if v.isdigit():
                    row = np.zeros(self.num_concs)
                    row[col] = num_atoms_in_basis[basis]
                    A_eq.append(row)
                    b_eq.append(int(v))
                col += 1

        variables = list(variable_range.keys())
        # get reference_elements: elements with its concentration specified
        # with a clean representation (e.g., <x> or <y>)
        reference_elements = self._reference_elements(element_conc, variables)

        for variable in variable_range.keys():
            num_additional_constraints = num_elements_with_var[variable] - 2
            if num_additional_constraints == 0:
                continue

            ref_element = reference_elements[variable]["symbol"]
            ref_col = reference_elements[variable]["col"]

            if ref_element is None:
                raise RuntimeError(f"Did not find reference element for symbol" f" {variable}")

            # Extract the coefficients of other elements with their
            # concenctrations defined as multiples of the symbol
            # (e.g., <2x>, <3x>)
            ignore_conditions = ["+", "-"]
            col = 0
            for basis_elem in element_conc:
                for k, v in basis_elem.items():
                    if k == ref_element or variable not in v:
                        col += 1
                        continue

                    if any(char in v for char in ignore_conditions):
                        col += 1
                        continue
                    coeff = self._get_coeff(v)
                    row = np.zeros(self.num_concs)
                    row[ref_col] = -coeff
                    row[col] = 1
                    A_eq.append(row)
                    b_eq.append(0)
                    col += 1

        if A_eq:
            A_eq = np.array(A_eq)
            self.add_usr_defined_eq_constraints(A_eq, b_eq)

        self._f_u_neq(variable_range, reference_elements, formulas)

    def _num_elements_with_var(self, variable_range, element_conc):
        """count how many elements have their concentration specified with
        the passed variable."""
        # pylint: disable=no-self-use
        num_elements_with_variable = {k: 0 for k in variable_range.keys()}
        for var in variable_range.keys():
            for basis_elem in element_conc:
                for _, conc in basis_elem.items():
                    if var in conc:
                        num_elements_with_variable[var] += 1
        return num_elements_with_variable

    def _f_u_neq(self, variable_range, reference_elements, formulas):
        A_lb = []
        b_lb = []
        num_atoms_in_basis = self._num_atoms_in_basis(formulas, variable_range)
        # For each element in basis
        # figure out if this is reference
        keys = sorted(variable_range.keys())
        for variable in keys:
            rng = variable_range[variable]
            ref_element = reference_elements[variable]["symbol"]
            basis = self._get_basis_containg_variable(formulas, variable)
            col = self._get_col_of_element_in_basis(basis, ref_element)

            # Add lower bound
            row = np.zeros(self.num_concs)
            row[col] = num_atoms_in_basis[basis]
            A_lb.append(row)
            b_lb.append(rng[0])

            # Add upper bound
            row = np.zeros(self.num_concs)
            row[col] = -num_atoms_in_basis[basis]
            A_lb.append(row)
            b_lb.append(-rng[1])

        if A_lb:
            A_lb = np.array(A_lb)
            b_lb = np.array(b_lb)
            self.add_usr_defined_ineq_constraints(A_lb, b_lb)

    def _reference_elements(self, element_conc, variables):
        """Return the reference element for each variable."""
        # pylint: disable=no-self-use
        # reference element is the one that has its concentration specified
        # with a clean representation (e.g., <x> or <y>)
        ref_elem = {}
        for variable in variables:
            col = 0
            for basis_elem in element_conc:
                for k, v in basis_elem.items():
                    if v == variable and v not in ref_elem:
                        ref_elem[variable] = {"symbol": k, "col": col}
                    col += 1
        return ref_elem

    def _get_basis_containg_variable(self, formulas, variable_symbol):
        """Return index of the basis containing the passed varyable symbol."""
        # pylint: disable=no-self-use
        for basis, formula in enumerate(formulas):
            if variable_symbol in formula:
                return basis

        raise ValueError(f"Did not find any basis containing " f"{variable_symbol}")

    def _get_col_of_element_in_basis(self, basis, element):
        """Return column number in the matrix corresponding to element."""
        col = 0
        for i in range(basis):
            col += len(self.basis_elements[i])

        for elem in self.basis_elements[basis]:
            if elem == element:
                return col
            col += 1

        raise RuntimeError(f"Did not find any column corresponding to "
                           f"{element} in basis {basis}. "
                           f"Current basis_elements are {self.basis_elements}")

    def _get_coeff(self, string):
        """Get the coefficient in front of the symbol.

        Parameters:

        string: str
            string of the following form 3x, 10y, 3z etc.
        """
        # pylint: disable=no-self-use
        if not string[0].isdigit():
            return 1

        number = ""
        for character in string:
            if not character.isdigit():
                break
            number += character
        return int(number)

    def _parse_formula_unit_string(self, formulas):
        element_variable = []
        for basis_num, formula in enumerate(formulas):
            split1 = formula.split("<")
            elements = []
            math = []
            for i, substr in enumerate(split1):
                if i == 0:
                    elements.append(substr)
                elif i == len(split1) - 1:
                    split2 = substr.split(">")
                    math.append(split2[0])
                else:
                    split2 = substr.split(">")
                    elements.append(split2[1])
                    math.append(split2[0])
            if elements != self.basis_elements[basis_num]:
                raise ValueError("elements in 'formulas' and 'basis_elements' should match.")
            element_variable.append(OrderedDict(zip(elements, math)))
        return element_variable

    def _get_constraints(self):
        constraints = []
        for i in range(self.A_eq.shape[0]):
            new_constraint = {
                "type": "eq",
                "fun": equality_constraint,
                "args": (self.A_eq[i, :], self.b_eq[i])
            }
            constraints.append(new_constraint)

        for i in range(self.A_lb.shape[0]):
            new_constraint = {
                "type": "ineq",
                "fun": inequality_constraint,
                "args": (self.A_lb[i, :], self.b_lb[i])
            }
            constraints.append(new_constraint)
        return constraints

    def _add_fixed_element_in_each_basis(self, nib=None):
        """Add constraints corresponding to the fixing elements in basis."""
        if self.fixed_element_constraint_added:
            return
        indices = []
        basis_of_index = []
        start = 0
        ranges = self.get_individual_comp_range()
        min_range = 0.01
        maxiter = 1000
        self.orig_num_equality = self.A_eq.shape[0]
        for i, basis in enumerate(self.basis_elements):
            if self._is_linked_to_other_basis(i):
                start += len(basis)
                continue
            iteration = 0
            rng = 0.5 * min_range
            while rng < min_range and iteration < maxiter:
                iteration += 1
                indx = choice(range(start, start + len(basis)))
                rng = ranges[indx][1] - ranges[indx][0]
            if iteration >= maxiter:
                self.fixed_element_constraint_added = False
                start += len(basis)
                continue
            indices.append(indx)
            basis_of_index.append(i)
            start += len(basis)

        A = np.zeros((len(indices), self.num_concs))
        b = np.zeros(len(indices))
        for i, indx in enumerate(indices):
            A[i, indx] = 1
            rng = ranges[indx][1] - ranges[indx][0]
            b[i] = np.random.rand() * rng + ranges[indx][0]
            if nib is not None:
                # Convert to closest rational number
                n = nib[basis_of_index[i]]
                b[i] = np.round((b[i] * n)) / n

        # Add constraints
        self.A_eq = np.vstack((self.A_eq, A))
        self.b_eq = np.append(self.b_eq, b)
        self.fixed_element_constraint_added = True

    def _remove_fixed_element_in_each_basis_constraint(self):
        """Remove the last rows."""
        if not self.fixed_element_constraint_added:
            return
        self.A_eq = self.A_eq[:self.orig_num_equality, :]
        self.b_eq = self.b_eq[:self.orig_num_equality]
        self.fixed_element_constraint_added = False

    def get_individual_comp_range(self):
        """Return the concentration range of each component."""
        ranges = []
        for i in range(self.num_concs):
            xmin = self.get_conc_min_component(i)
            xmax = self.get_conc_max_component(i)
            ranges.append((xmin[i], xmax[i]))
        return ranges

    def get_random_concentration(self, nib=None) -> np.ndarray:
        """Generate a valid random concentration."""
        assert self.A_eq.shape[0] == len(self.b_eq)

        self._add_fixed_element_in_each_basis(nib=nib)
        # Setup the constraints
        constraints = self._get_constraints()
        x0 = np.random.rand(self.num_concs)
        pinv = np.linalg.pinv(self.A_eq)
        x_init = pinv.dot(self.b_eq)

        # Find the closest vector to x0 that satisfies all constraints
        opt_res = minimize(objective_random,
                           x_init,
                           args=(x0,),
                           method="SLSQP",
                           jac=obj_jac_random,
                           constraints=constraints,
                           bounds=self.trivial_bounds)
        self._remove_fixed_element_in_each_basis_constraint()
        x = opt_res["x"]

        if not self.is_valid_conc(x):
            msg = "Could not find valid concentration. Revise the constraints."
            raise InvalidConcentrationError(msg)
        return x

    def _get_interbasis_relations(self):
        self._linked_basis = list(range(len(self.basis_elements)))
        self._get_interbasis_relations_for_given_matrix(self.A_eq)
        self._get_interbasis_relations_for_given_matrix(self.A_lb)

    def _get_interbasis_relations_for_given_matrix(self, A):
        basis_start_col = [0]
        for i in range(0, len(self.basis_elements) - 1):
            start_col = basis_start_col[-1] + len(self.basis_elements[i])
            basis_start_col.append(start_col)

        # Linked basis
        tol = 1E-6
        for i in range(A.shape[0]):
            lowest_nonzoro_basis = None
            for j, basis_start in enumerate(basis_start_col):
                if j < len(basis_start_col) - 1:
                    b_end = basis_start_col[j + 1]
                    values = A[i, basis_start:b_end]
                else:
                    values = A[i, basis_start:]

                if np.any(np.abs(values) > tol):
                    # There is a non zero entry in the current basis
                    if lowest_nonzoro_basis is None:
                        lowest_nonzoro_basis = j
                    else:
                        # There exists a link between the two basis
                        root = self._get_root_indx(lowest_nonzoro_basis)
                        self._linked_basis[root] = j

    def _get_root_indx(self, indx):
        """Search find the root index of the link tree."""
        while self._linked_basis[indx] != indx:
            indx = self._linked_basis[indx]
        return indx

    def _is_linked_to_other_basis(self, indx):
        return self._linked_basis[indx] != indx

    @property
    def trivial_bounds(self):
        """Return trivial bounds (i.e. 0 <= x <= 1)

           NOTE: One can give stricter bounds, but these
                 trivial bounds are always satisfied
        """
        return [(0, 1) for _ in range(self.num_concs)]

    def _get_conc_component(self, comp, objective_func, objective_jac_func):
        """Generate all end points of the composition domain."""
        if isinstance(comp, int):
            comp = [comp]
        comp = np.array(comp)
        constraints = self._get_constraints()

        x0 = np.random.rand(self.num_concs)

        # Find the closest vector to x0 that satisfies all constraints
        opt_res = minimize(objective_func,
                           x0,
                           args=(comp,),
                           method="SLSQP",
                           jac=objective_jac_func,
                           constraints=constraints,
                           bounds=self.trivial_bounds)

        x = opt_res["x"]
        if not self.is_valid_conc(x):
            msg = "Could not find valid concentration. Revise the constraints."
            raise InvalidConcentrationError(msg)
        return x

    def get_conc_min_component(self, comp):
        """Generate all end points of the composition domain."""
        return self._get_conc_component(comp, objective_component_min, obj_jac_component_min)

    def get_conc_max_component(self, comp):
        """Generate all end points of the composition domain."""
        return self._get_conc_component(comp, objective_component_max, obj_jac_component_max)

    def to_float_conc(self, num_atoms_in_basis, int_conc):
        """
        Convert integer number to float concentration.

        Parameters:

        num_atoms_in_basis: list of int
            Number of sites in each basis (e.g., [27, 27], [64]).

        int_conc: array of int
            Concentration per basis in an integer format, which
            corresponds to the number of corresponding element in that basis.
        """
        conc_index = 0
        x = np.zeros(len(int_conc))
        for i, elem in enumerate(self.basis_elements):
            for _ in range(len(elem)):
                x[conc_index] = int_conc[conc_index] / num_atoms_in_basis[i]
                conc_index += 1
        return x

    def conc_in_int(self, num_atoms_in_basis, conc) -> np.ndarray:
        """
        Convert concentration value to an integer that corresponds to the
        number of corresponding elements.

        Parameters:

        num_atoms_in_basis: list of int
            Number of sites in each basis (e.g., [27, 27], [64]).

        conc: array of float
            Concentration per basis normalized to 1.
            (e.g., arrays returned by self.get_random_concentration,
                   self.get_conc_max_component etc.)
        """

        if len(num_atoms_in_basis) != len(self.basis_elements):
            raise ValueError(f"Number of atoms has to be specified for each "
                             f"basis. Given: {len(num_atoms_in_basis)}. "
                             f"Expected: {len(self.basis_elements)}")

        int_array = np.zeros(self.num_concs, dtype=int)
        start = 0
        b_eq = self.b_eq.copy()
        for i, num in enumerate(num_atoms_in_basis):
            n = len(self.basis_elements[i])
            end = start + n
            if end >= len(int_array):
                int_array[start:] = np.round(conc[start:] * num).astype(np.int32)
            else:
                int_array[start: end] = \
                    np.round(conc[start: end]*num).astype(np.int32)

            # Check that the sum is consistent
            diff = num - np.sum(int_array[start:end])
            if diff > 0:
                min_indx = np.argmin(int_array[start:end])
                int_array[start + min_indx] += diff
            elif diff < 0:
                max_indx = np.argmax(int_array[start:end])
                int_array[start + max_indx] -= abs(diff)

            b_eq[i] *= num
            start += n

        # Make sure that equality constraints are satisfied
        dot_prod = self.A_eq.dot(int_array)
        num_basis = len(num_atoms_in_basis)
        if not np.allclose(dot_prod[:num_basis], b_eq[:num_basis]):
            msg = "The conversion from floating point concentration to int "
            msg += f"is not consistent. Expected: {b_eq}, "
            msg += f"got: {dot_prod}"
            raise IntConversionNotConsistentError(msg)
        return int_array

    def _check_grouped_basis_elements(self):
        # check number of basis
        if self.grouped_basis is None:
            return

        num_basis = len([i for sub in self.grouped_basis for i in sub])
        if num_basis != len(self.orig_basis_elements):
            raise ValueError('grouped_basis do not contain all the basis')

        # check if grouped basis have same elements
        for group in self.grouped_basis:
            ref_elements = self.orig_basis_elements[group[0]]
            for indx in group[1:]:
                if self.orig_basis_elements[indx] != ref_elements:
                    raise ValueError('elements in the same group must be same')

    def get_concentration_vector(self, index_by_basis, atoms):
        """Get the concentration vector."""
        assert len(index_by_basis) == len(self.basis_elements)

        concs = np.zeros(self.num_concs)
        start = 0
        for i, indices in enumerate(index_by_basis):
            symbol_lookuptable = \
                {symb: start+j for j, symb
                 in enumerate(self.basis_elements[i])}
            for indx in indices:
                concs[symbol_lookuptable[atoms[indx].symbol]] += 1
            if start + len(self.basis_elements[i]) >= len(concs):
                concs[start:] /= len(indices)
            else:
                concs[start:start + len(self.basis_elements[i])] /= len(indices)
            start += len(self.basis_elements[i])
        assert np.all(concs <= 1.0)
        return concs

    def is_valid(self, index_by_basis, atoms):
        """Check if the atoms object has a valid concentration.

        Parameters:

        index_by_basis: list
            list where the indices of atoms is grouped by basis

        atoms: Atoms object
            wrappend_and_sorted atoms object
        """
        x = self.get_concentration_vector(index_by_basis, atoms)
        return self.is_valid_conc(x)


# Helper function used by the minimization algorithm
def objective_component_min(x, indx):
    return np.sum(x[indx])


def obj_jac_component_min(x, indx):
    jac = np.zeros(len(x))
    jac[indx] = np.sign(x[indx])
    return jac


def objective_component_max(x, indx):
    return -1 * np.sum(x[indx])


def obj_jac_component_max(x, indx):
    jac = np.zeros(len(x))
    jac[indx] = -np.sign(x[indx])
    return jac


def objective_random(x, x0):
    """Return the difference between x and x0."""
    diff = x - x0
    return diff.dot(diff)


def obj_jac_random(x, x0):
    """The jacobian of the objective function."""
    return 2.0 * (x - x0)


def equality_constraint(x, vec, rhs):
    """Equality constraint. Return 0 if constraints are satisfied."""
    return vec.dot(x) - rhs


def eq_jac(x, vec, rhs):
    """Jacobian of the equalitu constraint equation."""
    # pylint: disable=unused-argument
    return vec


def inequality_constraint(x, vec, rhs):
    """Inequality constraints. Return a non-negative number if constraints
       are satisfied."""
    return vec.dot(x) - rhs


def ineq_jac(x, vec, rhs):
    """Jacobian of the inequality constraint equations."""
    # pylint: disable=unused-argument
    return vec
