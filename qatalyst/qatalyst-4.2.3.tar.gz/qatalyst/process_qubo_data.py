#
#    (C) Quantum Computing Inc., 2021.
#
#    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE of the Copyright Holder.
#    The contents of this file may not be disclosed to third parties, copied
#    or duplicated in any form, in whole or in part, without the prior written
#    permission of the Copyright Holder.
#
from dataclasses import dataclass
from typing import Union
import numpy as np
import scipy.sparse as sp
import networkx as nx
from itertools import chain
from .encoders import encode_data
from .process_params_data import ProcessParams
from .constants import QatalystConstants


@dataclass
class ProcessQubo(ProcessParams):
    """
    """
    qubo: Union[np.ndarray, sp.spmatrix, dict] = None
    initial_guesses: np.ndarray = None

    def __post_init__(self):
        super().__post_init__()

        # Process Qubo if problem specified
        if self.problem_type == 'qubo':

            # Verify the Qubo is provided by the user
            assert self.qubo is not None, \
                "Required parameter 'qubo' is unspecified."

            # Validate the user provided Qubo and attach to requests message
            self.process_qubo()

            # Add metadata to the requests message
            self.process_metadata()

            # Add params to the requests message
            self.process_params()

            # Process Initial Guesses if provided by user
            if self.initial_guesses is not None:
                self.process_initial_guesses()

    def process_qubo(self):
        """
        Method : process_qubo()
        Purpose: Process user provided Qubo and append it to the requests
               :     message.
        Input  : Qubo as Numpy Array, SciPy sparse array, or dictionary.
        Output : Qubo as binary appended to messages diectionary.
        """
        # Deal with Qubo as dict is necessary
        if isinstance(self.qubo, dict):
            assert len(self.qubo.keys()) == len(set(self.qubo.keys())), \
                "\nERROR: Repeated key in dictionary used to specify Qubo.\n"

            # Verify the indices are integers
            indices = sorted(set(chain(*self.qubo.keys())))
            self.__check_dict_indices(indices)

            # Determine is qubo is upper triangular
            is_upper_triangular = self.__check_upper_triangular()

            # Convert qubo to sparse matrix
            self.qubo = self.convert_dict_to_sparse_qubo(
                is_upper_triangular, indices
            )

        # QUBO now assumed to be either NumPy array or SciPy sparse array
        #print("\nChecking validity of objective function... ")
        self.check_objective(data=self.qubo)

        # Set the value for the Qubo's shape
        self.shape = self.qubo.shape

        # Set the data type for the problem
        self.data_type = self.get_data_type(self.qubo)

        # Add Qubo to the message shipped by requests
        self.message['data_obj'] = (
            self.DATA_OBJ_FNAME,
            encode_data(self.qubo),
            'application/octet-stream'
        )

    def process_initial_guesses(self):
        """
        Method : process_initial_guesses()
        Purpose: Process user provided initial guesses, and append it to
               :     the requests message.
        Input  : Numpy Array containing binary variable values.
        Output : Initial guesses as binary appended to messages diectionary.
        """
        # Verify the initial guesses NumPy object of correct dimensions
        self.check_initial_guesses()

        # Verify the variables are integers
        self.initial_guesses = np.array(
            [[int(var) for var in guess] for guess in self.initial_guesses]
        ).astype(np.int8)

        # Add initial guesses to requests message
        self.message['initial_seeds'] = (
            self.INIT_GUESSES_FNAME,
            encode_data(self.initial_guesses),
            'application/octet-stream'
        )

    @staticmethod
    def __check_dict_indices(indices):
        assert min(indices) == 0, \
            "QUBO keys must be integers in [0, 1, ..., n-1]."

        assert all(map(lambda m: isinstance(m, int), indices)), \
            "QUBO keys must be integers in [0, 1, ..., n-1]."

    def __check_upper_triangular(self):
        indices = sorted(set(self.qubo.keys()))

        return all(map(lambda m: m[0] <= m[1], indices))

    @staticmethod
    def __qubo_val_from_dict(is_upper_triangular):
        if is_upper_triangular:
            return lambda row, col, v: 1.0 * v if row == col else v / 2.0
        else:
            return lambda row, col, v: 1.0 * v

    @staticmethod
    def __check_symmetric_sparse(data, tol=1e-10):
        """
        See the most excellent post here:
        https://stackoverflow.com/questions/48798893/error-in-checking-symmetric-sparse-matrix
        """
        return (abs(data - data.T) > tol).nnz == 0

    def convert_dict_to_sparse_qubo(self, is_upper_triangular, indices):
        """
        Convert dictionary to sparse matrix format.

        :param qubo: dict, QUBO

        :return: COO matrix

        """
        get_val = self.__qubo_val_from_dict(is_upper_triangular)

        # Initialize storage for Qubo
        n = max(indices)
        mat = sp.dok_matrix((n + 1, n + 1), dtype=float)

        # Transform Qubo to a sparse matrix
        for i, j in self.qubo.keys():
            if not is_upper_triangular:
                assert self.qubo[i, j] == self.qubo[j, i]
            mat[i, j] = mat[j, i] = get_val(i, j, self.qubo[i, j])

        # Return sparse matrix
        return mat.tocoo()

    def check_objective(self, data):
        """
        Verify the QUBO is formulated as expected
        """
        assert (
            isinstance(data, np.ndarray) or
            isinstance(data, sp.spmatrix)
        ), "QUBO or Objective must be of type ndarray or sparse matrix."

        assert data.ndim == 2, \
            "QUBO or Objective must be a 2-dimensional array."

        # check QUBO problems is square
        assert data.shape[0] == data.shape[1], \
            "QUBO or Objective must be square.\n\
             SHAPE: {}".format(data.shape)

        # check QUBO size is less than or equal to 50k (Qatalyst 2.0)
        assert data.shape[0] <= self.max_qubit_size, \
            "QUBO or Objective must contain fewer than {} variables.\n\
             QUBO SHAPE: {}".format(self.max_qubit_size, data.shape)

        # these only get called if qubo is square
        if isinstance(data, np.ndarray):
            assert np.all(data == data.T), \
                "\nERROR: QUBO or Objective is not symmetric.\n"

            # Assert every number is finite
            assert np.isfinite(data).all(), \
                "\nERROR: NAN entry in QUBO or objective matrix.\n"
        else:
            assert self.__check_symmetric_sparse(data=data), \
                "\nERROR: QUBO or Objective is not symmetric.\n"

            # Chech for nan values in the objective matrix
            # see https://stackoverflow.com/questions/39378363/remove-nan-rows-in-a-scipy-sparse-matrix
            nan_rows = [i for i, row in enumerate(data.data) if not np.isfinite(row).all()]
            assert len(nan_rows) == 0, \
                "\nERROR: NAN entry in QUBO or objective matrix.\n"

        # Check problems size against DWave if Dwave sampler selected
        if QatalystConstants.QUANTUM_SAMPLER_DWAVE in self.sampler:
            self.__check_dwave_size(data=data)

    def __check_dwave_size(self, data):
        """
        data: Union[nx.Graph, np.ndarray, sp.spmatrix]

        :return: bool
        """
        # print("Checking basic size thresholds for D-Wave QPUs...")
        max_fully_connected = [self.DWAVE_MAX_CLIQUES[k]
                               for k in self.DWAVE_MAX_CLIQUES if k in self.device.name]

        # Convert graph to array
        if isinstance(data, nx.Graph):
            arr = nx.to_numpy_array(data)
        else:
            arr = data.copy()

        if isinstance(arr, sp.spmatrix):
            arr = arr.toarray()

        d_idx = np.diag_indices_from(arr)
        arr[d_idx] = 0
        size = arr.shape[0]

        #######
        # after replacing diag with 0, all nonzeros should be off the diagonal
        #
        nnz_offdiag = np.count_nonzero(arr)
        max_offdiag_nnz = arr.shape[0]**2 - arr.shape[0]

        is_fully_connected = (nnz_offdiag - max_offdiag_nnz == 0)

        if is_fully_connected and size > max_fully_connected[0]:
            raise ValueError(
                f"The D-Wave Systems QPU can only run fully connected problems "
                f"with less then or equal to {max_fully_connected} logical qubits. Problem size is "
                f"{size} qubits."
            )

    def check_initial_guesses(self):
        """
        Method : check_initial_guesses()
        Purpose: Validate user provided initial guesses, or generate error.
        Input  : Numpy Array containing binary variable values.
        Output : NA
        """
        # Verify the initial guesses are NumPy arrays
        assert isinstance(self.initial_guesses, np.ndarray), \
            "ERROR: Initial guesses must be specified as a \
             NumPy array of Numpy arrays."

        # Verify the initial guesses are represented as 2D array
        assert len(self.initial_guesses.shape) == 2, \
            "ERROR: Initial guesses must be provided as 2D Numpy array."

        # Verify the initial guesses have the correct dimensions
        assert self.initial_guesses.shape[1] == self.shape[0], \
            """ERROR DIMENSION MISMATCH:\n
            Qubo/objective: {}\n
            Initial guesses: {}""".format(
                self.shape[0],
                self.initial_guesses.shape[1]
        )

        # Verify every value is 0/1
        assert set(np.unique(self.initial_guesses.tolist())) in [{0, 1}, {0}, {1}], \
            "ERROR: Variable values for initial guess must be either 0 or 1."
