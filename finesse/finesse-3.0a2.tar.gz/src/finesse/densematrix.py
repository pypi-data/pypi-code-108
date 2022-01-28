import logging
import weakref
import numpy as np


from finesse.cmatrix import _Column, _SubMatrix
from numpy.lib.stride_tricks import as_strided

LOGGER = logging.getLogger(__name__)


class DenseMatrix:
    """
    Examples
    --------
    Create a matrix with memory views of different submatrices for giving to components:

        > DM = DenseMatrix("abc")
        >
        > DM.declare_equations(5, 0, 'a')
        > DM.declare_equations(5, 1, 'b')
        > DM.declare_equations(5, 2, 'c')
        > DM.declare_equations(2, 3, 'd')
        >
        > v1 = DM.declare_submatrix_view(0, 1, 'b')
        > v2 = DM.declare_subdiagonal_view(0, 2, 'b')
        > v3 = DM.declare_submatrix_view(3, 1, 'b')
        >
        > DM.construct()
        >
        > v1[:] = 1
        > v2[:] = 0.5
        > v3[:] = 0.75
    """

    class SubMatrixView:
        """This class represents a sub-matrix view of a CCS sparse matrix. This allows
        code to access and set values without worrying about the underlying sparse
        compression being used. Although so far this is just for CCS formats.

        This object will get a view of a n-by-m sub-matrix starting at index (i,j). The
        values of his matrix will be set initially to the coordinates.
        """

        def __init__(self, Matrix, _from, _to, name, mtype):
            self.M = weakref.ref(Matrix)
            self._from = _from
            self._to = _to
            self.type = mtype
            Matrix._declare_submatrix(_from, _to, name, self, mtype)

        @property
        def from_idx(self):
            return self._from

        @property
        def to_idx(self):
            return self._to

        @property
        def view(self):
            return self.A

        def _updateview_(self):
            # This object represents a view of a matrix, this actually gets the
            # submatrix itself to use to fill things
            self.A = self.M().get_submatrix(self._from, self._to)

        def __getitem__(self, key):
            return self.A[key]

        def __setitem__(self, key, value):
            self.A[key] = value

    def __init__(self, name):
        self.__name = name
        self.sub_columns = {}
        self.num_eqs = 0
        self.diag_map = {}  # Maps submatrix index to RHS element index
        self.__callbacks = []

    @property
    def name(self):
        return self.__name

    def declare_submatrix_view(self, from_node, to_node, name):
        return DenseMatrix.SubMatrixView(self, from_node, to_node, name, "m")

    def declare_subdiagonal_view(self, from_node, to_node, name):
        return DenseMatrix.SubMatrixView(self, from_node, to_node, name, "d")

    def declare_equations(self, Neqs, index, name):
        """Adds a submatrix to the matrix along its diagonal. This defines what
        equations exist in the matrix, the submatrix values cannot be changed after
        this, they are always `1` Before other submatrices can be added to the matrix
        the diagonal must be specfied and how many equations it represents.

        Parameters
        ----------
        Neqs : Py_ssize_t
            Number of equations this submatrix represents
        _index : long
            Subcolumn index
        name : unicode
            Name used to indentify this coupling in the matrix for debugging
        """
        if index in self.sub_columns:
            raise Exception(
                "Diagonal elements already specified at index {}".format(index)
            )

        self.sub_columns[index] = _Column(Neqs, index, name)
        self.sub_columns[index].submatrices.append(
            _SubMatrix("d", Neqs, Neqs, index, name)
        )
        # Record what RHS index/number of equations this submatrix will start in
        self.diag_map[index] = self.num_eqs
        self.num_eqs += Neqs

    def add_block(self, Neqs, index, name):
        """
        Parameters
        ----------
        Neqs : Py_ssize_t
            Number of equations this submatrix represents
        _index : long
            Subcolumn index
        name : unicode
            Name used to indentify this coupling in the matrix for debugging
        """
        if index in self.sub_columns:
            raise Exception(
                "Diagonal elements already specified at index {}".format(index)
            )

        self.sub_columns[index] = _Column(Neqs, index, name)
        self.sub_columns[index].submatrices.append(
            _SubMatrix("m", Neqs, Neqs, index, name)
        )
        # Record what RHS index/number of equations this submatrix will start in
        self.diag_map[index] = self.num_eqs
        self.num_eqs += Neqs

    def _declare_submatrix(self, _from, _to, name, callback=None, type_="m"):
        """Adds a submatrix to the matrix. The nomenclature of `_from` and `_to` refer
        to the variable dependency of the equations this submatrix represents, i.e. the
        equations in submatrix `_to` depends on the values in `-from`. Therefore `_from`
        is the subcolumn index and `_to` is the subrow index.

        Parameters
        ----------
        _from : long
            Subcolumn index
        _to : long
            Subcolumn index
        name : unicode
            Name used to indentify this coupling in the matrix for debugging
        callback : function()
            A callback function that will be called once the matrix has been constructed
        type_ : char (optional)
            Either 'm' for a full submatrix or 'd' for a diagonal element only submatrix
        """
        if _from not in self.sub_columns:
            raise Exception(
                "Must add a diagonal submatrix at index {} first for this subcolumn".format(
                    _from
                )
            )
        if _to not in self.sub_columns:
            raise Exception(
                "Must add a diagonal submatrix at index {} first for this subcolumn".format(
                    _to
                )
            )

        _to_size = self.sub_columns[_to].size
        _from_size = self.sub_columns[_from].size

        self.sub_columns[_from].submatrices.append(
            _SubMatrix(type_, _from_size, _to_size, _to, name)
        )

        if callback:
            self.__callbacks.append(callback)

    def construct(self):
        """Constructing the matrix involves taking the metadata submatrix positions
        throughout the matrix and allocating the memory and building the various CCS
        matrix structures.

        After this the matrix can be populated and sovled.
        """
        self.M = -np.eye(self.num_eqs, dtype=complex)
        self.rhs = np.zeros((self.num_eqs, 1), dtype=complex)

        for cb in self.__callbacks:
            cb._updateview_()

    def get_submatrix(self, _from, _to):
        # _to -> row
        # _from -> column

        # Starting indicies
        sfidx = self.diag_map[_from]
        stidx = self.diag_map[_to]

        sm = [_ for _ in self.sub_columns[_from].submatrices if _.to == _to][0]
        to_size = sm.rows
        from_size = sm.columns

        # Only returns diagonal elements if needed
        if sm.type == "m":
            slf = slice(sfidx, sfidx + from_size, 1)
            slt = slice(stidx, stidx + to_size, 1)
            return self.M.view()[slt, slf]

        elif sm.type == "d":
            assert to_size == from_size
            return as_strided(
                self.M[stidx:, sfidx:],
                shape=(to_size,),
                strides=((self.num_eqs + 1) * self.M.itemsize,),
            )
        else:
            raise Exception(f"unexpected submatrix type {sm.type}")

    @property
    def num_equations(self):
        return self.num_eqs

    def get_matrix_elements(self):
        raise self.M

    def print_matrix(self):
        raise NotImplementedError()

    def print_rhs(self):
        raise NotImplementedError()

    def set_rhs(self, index, value):
        self.rhs[index] = value

    def clear_rhs(self):
        self.rhs[:] = 0

    def solve(self, transpose=False, conjugate=False):
        """solve(self, transpose, conjugate)

        Solve the matrix with options for transposing and conjugating.

        If `transpose` is False, solves the linear system :math:`Ax = b` using the
        ``Symbolic`` and ``Numeric`` objects stored by this class.

        Otherwise, solves the linear system :math:`A^T x = b` or :math:`A^H x = b`. The
        `conjugate` option is zero for :math:`A^T x = b` or non-zero for :math:`A^H x = b`.

        Parameters
        ----------
        transpose : bool
            Flag determining whether to solve the transpose of the matrix.

        conjugate : bool
            Flag determining whether to solve :math:`A^T x =b` or :math:`A^H x = b`
            for the transposed linear system.

        Returns
        -------
        out : np.ndarray
            The (negative) solution vector.
        """
        inv = np.linalg.inv(self.M)
        return inv @ self.rhs
