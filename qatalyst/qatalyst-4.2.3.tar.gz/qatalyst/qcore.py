#
#    (C) Quantum Computing Inc., 2021.
#
#    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE of the Copyright Holder.
#    The contents of this file may not be disclosed to third parties, copied
#    or duplicated in any form, in whole or in part, without the prior written
#    permission of the Copyright Holder.
#
from os import getenv
import numpy as np
import scipy.sparse as sp
from typing import Union
from typing import Optional
from qatalyst.client import ClientService, get_client_kwargs
from qatalyst.result import Result
from qatalyst.utils import *
from qatalyst.process_qubo_data import ProcessQubo
from qatalyst.process_constraint_data import ProcessConstraints
from .constants import QatalystConstants

__all__ = [
    'sample_qubo',
    'sample_constraint_problem',
    'sample_lagrange_optimization'
]


class QatalystCore(ClientService):

    def __init__(
        self,
        username: str = None,
        password: str = None,
        access_token: str = None,
        sampler: str = QatalystConstants.DEFAULT_CLASSICAL_SAMPLER,
        configuration: str = QatalystConstants.CONFIGURATION,
        conf_path: str = None,
        url: str = None,
        ignore_qpu_window: bool = False,
        interruptible: bool = False,
        var_limit: int = 0,
        **kwargs
    ):
        """
        :param username: str
        :param password: str
        :param access_token: str
        :param sampler: str, string representation of the sampler to invoke. Default = 'qonductor'.
        :param configuration: str, configuration name, in case the config file contains multiples
        :param conf_path: str, optional path to local configuration file. By default, HttpClient will check in
               these locations: ('~/.qci.conf', '~/.qci/qci.conf').
        :param url: str, use to specify Portal-API server. If not set, API server will be set in superclass.
        :param ignore_qpu_window: bool, disable user confirmation for situations in which QPUs are only available during limited hours.
        :param interruptible: bool, give up if we hit an exception.  Default = False (keep trying)
        :param var_limit: int, the max number of variables qatalyst should accept
                if var_limit is not specified by the user, qatalyst enforces a limit of ProcessQubo::max_qubit_size
        """
        super().__init__(
            username=username,
            password=password,
            access_token=access_token,
            sampler=sampler,
            configuration=configuration,
            conf_path=conf_path,
            url=url,
            interruptible=interruptible,
            var_limit=var_limit,
            **kwargs
        )

        if not ignore_qpu_window:
            ignore_qpu_window = bool(getenv('QATALYST_IGNORE_QPU_WINDOW'))

        self.ignore_qpu_window = ignore_qpu_window

    def sample_qubo(
        self,
        qubo: Union[dict, np.ndarray, sp.spmatrix],
        initial_guesses: Optional[np.ndarray] = None,
        objective_units: str = QatalystConstants.DEFAULT_OBJECTIVE_FUNCTION_VALUE,
        **params
    ) -> Result:
        """
        See `qcore.sample_qubo` documentation below for docstring.
        """
        # Figure out if we are using a qpu and if the size is compatible with the
        # number of variables in the qubo.
        if self.is_quantum() or self.is_hybrid():
            self._qpu_execution_user_confirm()
            self.set_quantum_params(params)

        job_data = ProcessQubo(
            sampler=self.sampler,
            device=self.device,
            max_qubit_size=self.get_max_qubit_size(),
            problem_type="qubo",
            qubo=qubo,
            initial_guesses=initial_guesses,
            objective_units=objective_units,
            params=params
        )

        # Submit job via requests
        res = self.sendRequest(job_data.message)
        return Result.from_dict_response(res)

    def sample_constraint_problem(
        self,
        objective: Union[np.ndarray, sp.spmatrix],
        constraints: Union[np.ndarray, sp.spmatrix],
        rhs_constraints: Optional[np.ndarray] = None,
        objective_weight: float = 1.0,
        constraint_penalties: Union[np.ndarray, float] = 1.0,
        initial_guesses: Optional[np.ndarray] = None,
        objective_units: str = QatalystConstants.DEFAULT_OBJECTIVE_FUNCTION_VALUE,
        **params
    ) -> Result:
        """
        See `qcore.sample_constraint_problem` documentation below for docstring.
        """
        if self.is_quantum():
            self._qpu_execution_user_confirm()
            self.set_quantum_params(params)

        job_data = ProcessConstraints(
            sampler=self.sampler,
            device=self.device,
            max_qubit_size=self.get_max_qubit_size(),
            problem_type="constraint_problem",
            objective=objective,
            constraints=constraints,
            rhs_constraints=rhs_constraints,
            objective_weight=objective_weight,
            constraint_penalties=constraint_penalties,
            initial_guesses=initial_guesses,
            objective_units=objective_units,
            params=params
        )

        # Submit job via requests
        res = self.sendRequest(job_data.message)
        return Result.from_dict_response(res)

    def sample_lagrange_optimization(
        self,
        objective: Union[np.ndarray, sp.spmatrix],
        constraints: Union[np.ndarray, sp.spmatrix],
        rhs_constraints: Optional[np.ndarray] = None,
        objective_weight: float = 1.0,
        constraint_penalties: Union[np.ndarray, float] = 1.0,
        initial_guesses: Optional[np.ndarray] = None,
        objective_units: str = QatalystConstants.DEFAULT_OBJECTIVE_FUNCTION_VALUE,
        lagrange_maxiter: int = 5,
        **params
    ) -> Result:
        """
        See `qcore.sample_lagrange_optimization` documentation below for docstring.
        """
        self.set_lagrange_params(params)

        if self.is_quantum():
            self._qpu_execution_user_confirm()
            self.set_quantum_params(params)

        job_data = ProcessConstraints(
            sampler=self.sampler,
            device=self.device,
            max_qubit_size=self.get_max_qubit_size(),
            problem_type="lagrange_opt",
            objective=objective,
            constraints=constraints,
            rhs_constraints=rhs_constraints,
            objective_weight=objective_weight,
            constraint_penalties=constraint_penalties,
            initial_guesses=initial_guesses,
            objective_units=objective_units,
            lagrange_maxiter=lagrange_maxiter,
            params=params
        )

        # Submit job via requests
        res = self.sendRequest(job_data.message)
        return Result.from_dict_response(res)


####################################
# Entry point functions below
#
def sample_qubo(
    qubo: Union[dict, np.ndarray, sp.spmatrix],
    initial_guesses: Optional[np.ndarray] = None,
    objective_units: str = QatalystConstants.DEFAULT_OBJECTIVE_FUNCTION_VALUE,
    **kwargs
) -> Result:
    """
    Return samples of (near) optimal solutions for a Quadratic Unconstrained Binary Optimization (QUBO) problem.

    :param qubo: Union[dict, np.ndarray, or sp.spmatrix], :math:`n \\times n` QUBO matrix.
        Matrices must be symmetric. Dictionary input can represent the upper triangular portion of a matrix
        (including the diagonal) or the full matrix.
    :param initial_guesses: optional, 2D np.ndarray, binary values containing at least one
        solution, of the correct dimensions, to be used as starting point(s) for the search. The argument contents are checked for binary values and correct dimensions.
    :param objective_units: optional, str, the units to be applied to the y-axis of the progress plot generated from this request. Default = "Objective Function Value".
    :param kwargs: dict, parameters and arguments for the sampler and solver algorithm plus optional login information for the cloud client:

        * See `qcore.sample_constraint_problem` for the common Qatalyst kwargs.


    :return: :meth:`qatalyst.result.Result`, Python object with the following elements:

        * *samples* numpy.ndarray
            np.ndarray of binary variable results per sample
        * *energies* numpy.ndarray
            np.ndarray of objective-function values, per sample
        * *counts* numpy.ndarray
            np.ndarray of frequencies per samples
        * *properties* dict
            Method- and sampler-specific info about problem results
        * *time* dict
            Sampler-specific dict of time consumed by the processing steps
        * *jobinfo* dict
            Dict of various attributes about the request, such as job ID, request size in bytes, start time, etc.

	A common error in constructing a QUBO (or objective matrix) is to take pairwise data, corresponding to
	off-diagonal elements in the QUBO, that was generated symmetrically, pass it to Qatalyst
	as an upper-triangular matrix and neglect to multiply all the off-diagonal elements by a factor of 2,
	or conversely generate pairwise data with an upper-triangular matrix in mind and forget to divide
	the off-diagonal elements by a factor of 2 when converting to a symmetric matrix.

    :Example:

    QUBO function input using a Numpy array (see [GK]_):

    >>> import numpy as np
    >>> from qatalyst import qcore
    >>> # 'qubo' is a symmetric version of a quadratic unconstrained binary optimization (QUBO) problem
    >>> qubo = np.array([[-6, 10, 0, 0], [10, -8, 2, 8], [0, 2, -3, 4], [0, 8, 4, -5]])
    >>> # sample_qubo requires a symmetric matrix
    >>> res = qcore.sample_qubo(
    >>>     qubo,
    >>>     num_solutions=10
    >>> )
    >>> print(res)
    >>>     # Job started with JobID: 5ef37a0d08b481fef4af1d1f.
    >>>     # Problem COMPLETE, returning solution.
    >>>     # Result
    >>>     # samples
    >>>     # [[1. 0. 0. 1.]
    >>>     #  [1. 0. 1. 0.]
    >>>     #  ...
    >>>     #  [0. 0. 1. 1.]]
    >>>     # energies
    >>>     # [-11.  -9.  -8.  -7.  -6.  -6.  -5.  -3.   0.   0.]
    >>>     # counts
    >>>     # [1 1 1 1 1 1 1 1 1 1]
    >>> print(res.samples[0])    # print the first sample 
    >>>     # [1 0 0 1]

    Note that the *samples* values are all binary, following the QUBO definition.

    Running the same problem on AWS Braket is straightforward. Suppose we would like to find an optimal solution
    using QAOA on a gate model machine [FGG]_ with a circuit depth of 2. In order to use Rigetti's current device with changes to the default classical
    optimizer parameters, we call `sample_qubo` with the following additional arguments:

    >>> import numpy as np
    >>> from qatalyst import qcore
    >>> qubo = np.array([[-6, 10, 0, 0], [10, -8, 2, 8], [0, 2, -3, 4], [0, 8, 4, -5]])
    >>> res = qcore.sample_qubo(
    >>>     qubo,
    >>>     sampler='braket_rigetti',
    >>>     algorithm='qaoa',
    >>>     depth=2,
    >>>     optimizer='cobyla',
    >>>     optimizer_params={'maxiter': 5}
    >>> )
    >>> print(res)
    >>>    # Result
    >>>    # samples
    >>>    # [[1 0 0 1]
    >>>    #  [1 0 1 0]
    >>>    #  [0 1 0 0]
    >>>    #  [0 1 1 0]
    >>>    #  [1 0 0 0]
    >>>    #  [1 0 1 1]
    >>>    #  [0 0 0 1]
    >>>    #  [0 0 1 0]
    >>>    #  [0 0 0 0]
    >>>    #  [0 0 1 1]]
    >>>    # energies
    >>>    # [-11.  -9.  -8.  -7.  -6.  -6.  -5.  -3.   0.   0.]
    >>>    # counts
    >>>    # [16 20 17 17 19 25 26 22 22 18]
    >>> print(res.samples[0])    # print the first sample 
    >>>     # [1 0 0 1]
    >>> print(res.properties)    # print the properties dict
    >>>     # {'broken_constraints': {'0': [0, 5, 6, 7, 9, 10, 12, 13, 14, 15], '1': [0, 2, 4, 7, 9,
    >>>     # 11, 12, 13, 14, 15], '2': [0, 3, 8, 9, 10, 11, 12, 13, 14, 15]}}

    Note that the energies and solutions are identical in the classical and QAOA solutions.

    Alternatively, the VQE algorithm [MR]_ uses a similar hybrid approach.

    >>> import numpy as np
    >>> from qatalyst import qcore
    >>> qubo = np.array([[-6, 10, 0, 0], [10, -8, 2, 8], [0, 2, -3, 4], [0, 8, 4, -5]])
    >>> res = qcore.sample_qubo(
    >>>     qubo,
    >>>     sampler='braket_ionq',
    >>>     aLgorithm='vqe',
    >>>     num_shots=10,
    >>>     optimizer='cobyla',
    >>>     optimizer_params={'maxiter': 5}
    >>> )
    >>> print(res)
    >>>     # Result
    >>>     # samples
    >>>     # [[1 0 0 1]
    >>>     #  [1 0 1 0]
    >>>     #  [0 1 0 0]
    >>>     #  [0 1 1 0]
    >>>     #  [1 0 0 0]
    >>>     #  [1 0 1 1]
    >>>     #  [0 0 0 1]
    >>>     #  [0 0 1 0]
    >>>     #  [0 0 0 0]
    >>>     #  [0 0 1 1]]
    >>>     # energies (the Qubo used is random, so energies will differ with each run)
    >>>     # [-11.  -9.  -8.  -7.  -6.  -6.  -5.  -3.   0.   0.]
    >>>     # counts
    >>>     # [16 20 17 17 19 25 26 22 22 18]
    >>> print(res.energies)       # print the energies
    >>>     # [-3. -3. -3. -2. -1.  0.  0.  0.  0.  1.  1.  2.  3.  6.  6.  9.]

    Lastly, we can select one of D-Wave Systems' processors to solve a small 10x10 QUBO:

    >>> import numpy as np
    >>> from qatalyst import qcore
    >>>
    >>> q = np.random.normal(size=(10,10))
    >>> qubo = q + q.T         # make a symmetric matrix
    >>> # defaults to D-Wave's Advantage4.1 system on Braket
    >>> res = qcore.sample_qubo(
    >>>     qubo,
    >>>     sampler='braket_dwave',
    >>>     num_reads=10
    >>> )
    >>> print(res)
    >>>     # Result
    >>>     # samples
    >>>     # [[0. 0. 1. 1. 0. 1. 0. 0. 1. 1.]
    >>>     #  [0. 0. 1. 1. 0. 1. 0. 1. 1. 1.]
    >>>     #  [0. 0. 1. 1. 0. 1. 0. 1. 1. 0.]
    >>>     #  [0. 1. 1. 1. 0. 1. 0. 1. 1. 1.]
    >>>     #  [0. 1. 1. 1. 0. 1. 0. 0. 1. 1.]]
    >>>     # energies (the Qubo used is random, so energies will differ with each run)
    >>>     # [-18.25006755 -18.22989166 -17.23651149 -14.37725584 -13.82046326]
    >>>     # counts
    >>>     # [2 1 4 1 2]

    """
    client_kwargs, param_kwargs = get_client_kwargs(**kwargs)
    client = QatalystCore(**client_kwargs)
    return client.sample_qubo(qubo, initial_guesses, objective_units, **param_kwargs)


def sample_constraint_problem(
    objective: Union[np.ndarray, sp.spmatrix],
    constraints: Union[np.ndarray, sp.spmatrix],
    rhs_constraints: Optional[np.ndarray] = None,
    objective_weight: float = 1.0,
    constraint_penalties: Union[np.ndarray, float] = 1.0,
    initial_guesses: Optional[np.ndarray] = None,
    objective_units: str = QatalystConstants.DEFAULT_OBJECTIVE_FUNCTION_VALUE,
    **kwargs
) -> Result:
    """
    Return samples of a constraint problem on binary variables with an objective function and linear equality constraints.

    :param objective: np.ndarray or sp.spmatrix, :math:`n \\times n` symmetric cost function matrix.
    :param constraints: np.ndarray or sp.spmatrix, :math:`m \\times n+1` constraint matrix if the right hand side
        of the equality constraints :math:`Ax = b` are provided with the *rhs_constraints* parameter; otherwise, a
        :math:`m \\times n+1` matrix is expected with the last column containing the vector :math:`-b` as the constraints
        are of the form :math:`Ax-b=0`.
    :param rhs_constraints: optional, 2D np.ndarray or sp.spmatrix, the array containing the right-hand side of
        constraints :math:`Ax=b`.
    :param objective_weight: optional, float,  the constant used for scaling the objective matrix. Default = 1.0.
    :param constraint_penalties: optional, 2D np.ndarray, float, or int, the constraint penalty parameter
        referenced in https://arxiv.org/pdf/1811.11538.pdf. The penalty is applied to all constraints if a
        constant value > 0 is provided. Alternatively, a penalty parameter > 0 can be specified for each
        constraint by providing an :math:`m \\times 1` np.ndarray. Default = 1.0.
    :param initial_guesses: optional, 2D np.ndarray, binary values containing at least one
        solution, of the correct dimensions, to be used as starting point(s) for the search. The argument contents are checked for binary values and correct dimensions.
    :param objective_units: optional, str, the units to be applied to the y-axis of the progress plot generated from this request. Default = "Objective Function Value".

    :param kwargs: dict, parameters and arguments for the sampler and solver algorithm.

        * *num_solutions* int, default = 100.  
            The number of solutions to return.  Qatalyst will
            return the *num_solutions* best solutions as sorted by objective-function value.
        * *timeout* int, default = 1200.
            The maximum time, in seconds, the request should be
            permitted to run.
        * *timeout_noprogress* int, default = 200.  
            The maximum time, in seconds, the request should be
            permitted to run without finding a better result as measured by objective-function value.
        * *access_token* str, default = None.
            Retrieved from .qci.conf file unless provided.
        * *conf_path* str, default = None.
            Path to .qci.conf file on local system. Defaults to `~/.qci.conf` on Linux/Mac.
        * *configuration* str, default = 'default'.
            Specific configuration to use, in case multiple tokens and configurations are provided in the configuration file `~/.qci.conf`.
        * *url* str, default = https://api.qci-prod.com.
            URL for Qatalyst web-service
        * *sampler* str, default= 'qonductor'.
            The sampler to call.  Available classical and quantum samplers are obtainable through `utils.print_available_samplers`.
            Use 'target_name' to specify `sampler` argument.
            List of available samplers: `braket_rigetti`, `braket_ionq`, `braket_dwave_advantage`, `braket_dwave_2000Q`, `braket_simulator`, `braket_simulator_tn1`, braket_simulator_dm1`, and `qonductor`.
            Braket's simulator comes in three flavors: SV1 (state vector simulator), TN1 (based on tensor networks), and DM1 (density matrix simulator);
            the SV1 is a general-purpose quantum circuit simulator, TN1 is only suitable for certain
            types of quantum circuits, and DM1 is a fully managed, density matrix simulator,
            which can be used to simulate quantum circuits with noise and experiment with the effect of noise on quantum algorithms
             and experiment with mitigation strategies (see Braket documentation for further information).
            `braket_simulator` calls SV1 while `braket_simulator_tn1` calls TN1 abd braket_simulator_dm1 calls DM1.
        * *optimizer* str
            For calls that need a classical optimizer, the implementation uses algorithms found in `scipy.minimize` and additional stochastic versions of such optimizers. If sampler is of hybrid type, defaults to 'cobyla',
            otherwise defaults to None.
        * *optimizer_params* dict = None.
            A dictionary of options to pass to the optimizer. Default will be set in the backend if argument is None. Example: `options = {'disp': False, 'maxiter': 5}`.
            If sampler is of hybrid type, defaults to {'maxiter': 5}, otherwise defaults to None.
        * *algorithm* str,
            Variational algorithm to run with a hybrid 'sampler' and classical 'optimizer'. Both of QAOA or VQE are implemented (see [FGG]_, [PM]_, [MR]_). Select with 'qaoa' or 'vqe'. Defaults to 'qaoa' when sampler is of hybrid type.
        * *num_shots* int
            Number of samples taken per iteration on gate-based QPU samplers.

    :return: :meth:`qatalyst.result.Result`, Python object with the following elements:

        * *samples* numpy.ndarray
            np.ndarray of binary variable results, per sample.  
            **Note**:  The samples returned in *samples* may be a mix of feasible and infeasible
            solutions.  Often callers will want to focus mainly on
            feasible solutions, but good infeasible solutions may also be returned.  If only infeasible
            solutions are returned, it does not mean there are no feasible solutions, only that Qatalyst
            did not find any during this request. 
        * *energies* numpy.ndarray
            np.ndarray of objective-function values, per sample.  Qatalyst does not provide any
            information about how close to optimal the returned objective-function values are.
        * *counts* numpy.ndarray
            np.ndarray of frequencies per samples
        * *is_feasible* list(bool)
            Indicates whether or not a solution (at a given index) is feasible
        * *properties* dict
            Method- and sampler-specific info about problem results

			* *broken_constraints* dict, indexed by sample number, with the value being a list of the indices of the constraints that are violated for that sample
        * *time* dict
            Sampler-specific dict of time consumed by the processing steps
        * *jobinfo* dict
            Dict of various attributes about the request, such as job ID, request size in bytes, start time, etc.


    :Example:

    We want to pick 2-person beach-volleyball teams, where the constraints on each team are that it must have a) 2 players, b) 1 player with international playing experience, and c) one player under age 30.  Within those constraints, we want the team with the best players that play well together.
    We number the players from 0 to 3 and create binary variables :math:`x_i` each representing whether player :math:`i` is on the team or not, and create an objective matrix where the linear or diagonal elements represent the individual player's quality and the quadratic or off-diagonal elements represent the pairwise player effectiveness.  Note that smaller (closer to negative infinity) values are better.
    The first (*objective* = ...) line of the example below represents the objective function.

    Similarly for constraints, besides enforcing each team having two players, we know that players 0, 1, and 2 have international playing experience and that players 1, 2, and 3 are under age 30.

        :math:`x_0 + x_1 + x_2 + x_3 - 2 = 0`

        :math:`x_0 + x_1 + x_2\:\:\:\:\:\:\,\,\,\,- 1 = 0`

        :math:`\:\:\:\:\:\:\,\,\,\,x_1 + x_2 + x_3 - 1 = 0`

    Stating those in matrix form yields the third (*contraints* = ...) line of the following example.

    >>> import numpy as np
    >>> objective = np.array([[0,0,1,-1], [0,-1,1,-1], [1,1,-3,1], [-1,-1,1,-1]])
    >>> constraints = np.array([[1,1,1,1,-2], [1, 1, 1, 0, -1], [0, 1, 1, 1, -1]])
    >>> A = constraints[:, :-1]        # i.e., all but the last column
    >>> b = np.array(([2],[1],[1]))


    The *objective* matrix is an :math:`n \\times n` cost function, where :math:`n` is the number of variables (players), and the *constraints* matrix is an :math:`m \\times (n+1)` matrix, where :math:`m` is the number of constraints, composed of a system of linear constraints. One can think of constraints as an *augmented* system of linear constraints.  For this example, this would generate the third (*A* = ...) line in the above example.

    Lastly, representing the final column is the last (*b* = ...) line of the above example,
    giving *constraints* = [A | -b].

    If you want to solve a problem that has only constraints and no objective function,
    you can pass an *objective* matrix that is all zeroes, with dimensions equal
    to the number of variables represented by the *constraints* matrix.
    Similarly, if you want to solve a problem that has an objective function but no
    constraints, you can pass a *constraints* matrix that is all zeros, most simply with
    a single row, and one more column than the *objective* matrix.
    This would be equivalent to calling the `qcore:sample_qubo` function.
    The objective matrix is of the same form as the QUBO passed to `qcore:sample_qubo`.


    A common error in constructing an objective matrix is to take pairwise data, corresponding to
    off-diagonal elements in the objective matrix, that was generated symmetrically, pass it to Qatalyst
    as an upper-triangular matrix and neglect to multiply all the off-diagonal elements by a factor of 2,
    or conversely generate pairwise data with an upper-triangular matrix in mind and forget to divide
    the off-diagonal elements by a factor of 2 when converting to a symmetric matrix.

    In addition to the classical sampler, various quantum backends are also available. For instance,
    setting :code:`sampler='braket_dwave'`, will construct a QUBO from the objective and
    constraint matrices and sample the problem on D-Wave Systems' Advantage processor to obtain the result in :code:`res`.

    >>> import numpy as np
    >>> from qatalyst import qcore
    >>> objective = np.array([[-6, 10, 0, 0], [10, -8, 2, 8], [0, 2, -3, 4], [0, 8, 4, -5]])
    >>> constraints = np.array([[1, 1, 1, 1, -1], [0, 1, 1, 1, -1]])
    >>> alpha = 2
    >>> res = qcore.sample_constraint_problem(
    >>>     objective,
    >>>     constraints,
    >>>     constraint_penalties=alpha,
    >>>     num_solutions=5,
    >>>     sampler='braket_dwave'
    >>> )
    >>> print(res.samples[0])    # print the first sample 
    >>>     # [1 1 0 1]
    >>> print(res.properties)    # print the properties dict
    >>>     # {'broken_constraints': {'0': [0, 5, 6, 7, 9, 10, 12, 13, 14, 15], '1': [0, 2, 4, 7, 9,
    >>>     # 11, 12, 13, 14, 15], '2': [0, 3, 8, 9, 10, 11, 12, 13, 14, 15]}}

    Alternatively, a variational algorithm can be used to sample the resultant QUBO, as detailed in the code snippet
    that follows:

    >>> import numpy as np
    >>> from qatalyst import qcore
    >>> objective = np.array([[-6, 10, 0, 0], [10, -8, 2, 8], [0, 2, -3, 4], [0, 8, 4, -5]])
    >>> constraints = np.array([[1, 1, 1, 1, -1], [0, 1, 1, 1, -1]])
    >>> alpha = 2
    >>> res = qcore.sample_constraint_problem(
    >>>     objective,
    >>>     constraints,
    >>>     constraint_penalties=alpha,
    >>>     num_solutions=5,
    >>>     sampler='braket_rigetti',
    >>>     algorithm='qaoa',
    >>>     optimizer='cobyla',
    >>>     num_shots=10,
    >>>     optimizer_params={'maxiter': 5}
    >>> )
    >>> print(res.energies)       # print the energies
    >>>     # [-3. -3. -3. -2. -1.  0.  0.  0.  0.  1.  1.  2.  3.  6.  6.  9.]

    The `is_feasible` attribute allows easy access to whether a solution is feasible, that is whether a solution satisfies all constraints.
    The following is a small example illustrating this feature. The boolean value of `response.is_feasible[i]` indicates whether or not
    `response.samples[i]` is a feasible solution:

    >>> objective = np.array([[1, 0.5], [0.5, 2]])
    >>> constraint = np.array([[2, 2, -2]])
    >>> response = qcore.sample_constraint_problem(objective, constraint)
    >>> response.is_feasible
    >>> # array([ True,  True,  True,  True,  True,  True, False, False, False,
    >>> #         False, False, False])

    See :ref:`Quantum Algorithms and Devices` for more details on QPU options and available parameters.

    """
    client_kwargs, param_kwargs = get_client_kwargs(**kwargs)
    client = QatalystCore(**client_kwargs)
    return client.sample_constraint_problem(
        objective=objective,
        constraints=constraints,
        rhs_constraints=rhs_constraints,
        objective_weight=objective_weight,
        constraint_penalties=constraint_penalties,
        initial_guesses=initial_guesses,
        objective_units=objective_units,
        **param_kwargs
    )


def sample_lagrange_optimization(
    objective: Union[np.ndarray, sp.spmatrix],
    constraints: Union[np.ndarray, sp.spmatrix],
    rhs_constraints: Optional[np.ndarray] = None,
    objective_weight: float = 1.0,
    constraint_penalties: Union[np.ndarray, float] = 1.0,
    initial_guesses: Optional[np.ndarray] = None,
    objective_units: str = QatalystConstants.DEFAULT_OBJECTIVE_FUNCTION_VALUE,
    lagrange_maxiter: int = 5,
    **kwargs
) -> Result:
    """
    Return samples of an optimal solution to a constrained optimization problem on binary variables with an objective function
    and a system of linear constraints.

    Consider the problem defined by an objective function represented by an :math:`n \\times n` matrix, and an :math:`m \\times n+1`
    constraint matrix. See :meth:`sample_constraint_problem` for details on the *objective* and *constraints* matrices.
    The Lagrange multiplier is designed to balance the scales of the objective function and the system of constraints.

    Ideally, the Lagrangian, :math:`\\alpha`, reflects the importance of the constraints, and can be a vector.
    Lagrange Optimization is an iterative approach for choosing the ideal :math:`\\alpha` such that the constraints are satisfied, allowing the
    sampler to focus on minimizing the energy of the objective function.

    :Example:

    >>> objective = np.array([[-6, 10, 0, 0], [10, -8, 2, 8], [0, 2, -3, 4], [0, 8, 4, -5]])
    >>> constraints = np.array([[1, 0, 1, 1, -1], [1, 1, 0, 1, -1]])

    To compute the QUBO we combine the objective and constraints.

    Lagrange optimization runs the chosen sampler up to `lagrange_maxiter` times to determine the :math:`\\alpha` that
    minimizes *Q* while simultaneously satisfying constraints, e.g., :math:`Av_0 == 0`, where :math:`v_0` is the
    minimum energy sample returned by the sampler.

    Lagrange optimization is more involved, and returns an additional non-empty `properties` attribute in the
    Result object. In `properties['alpha']`,
    the :math:`m`-dimensional vectors record the updates to `alpha`, which are performed on a
    per-constraint basis, where :math:`m` is the dimension of the row space of the constraint matrix, :math:`A`.
    The  `properties['constraint_evals']` values record the result of :math:`Av_0` for each iteration.

    :param objective: np.ndarray or sp.spmatrix,
        :math:`n \\times n` symmetric cost-function matrix.
    :param constraints:  np.ndarray or sp.spmatrix, :math:`m \\times n+1` constraint matrix if the right hand side
        of the equality constraints :math:`Ax = b` are provided with the *rhs_constraints* parameter; otherwise, an
        :math:`m \\times n+1` matrix is expected with the last column containing the vector :math:`-b` as the constraints
        are of the form :math:`Ax-b=0`.
    :param rhs_constraints: optional, 2D np.ndarray or sp.spmatrix, the array containing the right-hand side of
        constraints :math:`Ax=b` when provided.
    :param objective_weight: optional, float,  the constant used for scaling the objective matrix. Default = 1.0
    :param constraint_penalties: optional, 2D np.ndarray, float, or int, the constraint penalty parameter
        referenced in https://arxiv.org/pdf/1811.11538.pdf. The penalty is applied to all constraints if a
        constant value > 0 is provided. Alternatively, a penalty parameter > 0 can be specified for each
        constraint by providing an :math:`m \\times 1` np.ndarray. Default = 1.0.
    :param initial_guesses: optional, 2D np.ndarray, binary values containing at least one
        solution, of the correct dimensions, to be used as starting point(s) for the search. The argument contents are checked for binary values and correct dimensions.
    :param objective_units: optional, str, the units to be applied to the y-axis of the progress plot generated from this request. Default = "Objective Function Value".
    :param lagrange_maxiter: optional, int, the total number of iterations allowed
        for updating the constraint_penalty parameters in the optimization loop. Default = 5.
    :param kwargs: dict, Parameters and arguments for the sampler and solver algorithm.

        * See `qcore.sample_constraint_problem` for the common Qatalyst kwargs.


    :return: :meth:`qatalyst.result.Result`, Python object with the following elements:

        * *samples* numpy.ndarray
            np.ndarray of binary variable results, per sample.  
            **Note**:  The samples returned in *samples* may be a mix of feasible and infeasible
            solutions.  Often callers will want to focus mainly on
            feasible solutions, but good infeasible solutions may also be returned.  If only infeasible
            solutions are returned, it does not mean there are no feasible solutions, only that Qatalyst
            did not find any during this request. 
        * *energies* numpy.ndarray
            np.ndarray of objective-function values, per sample.  Qatalyst does not provide any
            information about how close to optimal the returned objective-function values are.
        * *counts* numpy.ndarray
            np.ndarray of frequencies per samples
        * *is_feasible* list(bool)
            Indicates whether or not a solution (at a given index) is feasible
        * *properties* dict
            * *alpha* list
                List of alpha values per variable
            * *constraint_evals* list
                List of the values of each alpha times the corresponding row of the constraint matrix
        * *time* dict
            Sampler-specific dict of time consumed by the processing steps
        * *jobinfo* dict
            Dict of various attributes about the request, such as job ID, request size in bytes, start time, etc.

    A common error in constructing an objective matrix is to take pairwise data, corresponding to
    off-diagonal elements in the objective matrix, that was generated symmetrically, pass it to Qatalyst
    as an upper-triangular matrix and neglect to multiply all the off-diagonal elements by a factor of 2,
    or conversely generate pairwise data with an upper-triangular matrix in mind and forget to divide
    the off-diagonal elements by a factor of 2 when converting to a symmetric matrix.

    :Examples:

    >>> import numpy as np
    >>> from qatalyst import qcore
    >>> objective = np.array([[ 3.4 ,  1.1 , -1.7 , -1.6 ], [ 1.1 ,  4.5 ,  2.25,  2.25],  [-1.7 ,  2.25,  2.1 ,  0.5 ],  [-1.6 ,  2.25,  0.5 , -2.4 ]])
    >>> constraints = np.array([[1, 0, 1, 1, -1], [1, 1, 0, 1, -1]])
    >>> res = qcore.sample_lagrange_optimization(
    >>>     objective,
    >>>     constraints,
    >>>     lagrange_maxiter=5,
    >>>     num_solutions=5
    >>> )
    >>> print(res.properties)    
    >>>     # {'broken_constraints': {'0': [0, 5, 6, 7, 9, 10, 12, 13, 14, 15], '1': [0, 2, 4, 7, 9,
    >>>     # 11, 12, 13, 14, 15], '2': [0, 3, 8, 9, 10, 11, 12, 13, 14, 15]}}


    Given objectives and constraints, :math:`\\alpha` can be optimized on a QPU as well. This is of interest for
    D-Wave's processors, where finding an effective Lagrangian can take time by hand. Here we run the constraint problem
    on the D-Wave Advantage system, limiting the number of iterations used to find optimal constraint penalties
    (also known as `alpha`) to `lagrange_maxiter=5`.

    >>> import numpy as np
    >>> from qatalyst import qcore
    >>> objective = np.array([[-6, 10, 0, 0], [10, -8, 2, 8], [0, 2, -3, 4], [0, 8, 4, -5]])
    >>> constraints = np.array([[1, 1, 1, 1, -1], [0, 1, 1, 1, -1]])
    >>> res = qcore.sample_lagrange_optimization(
    >>>     objective,
    >>>     constraints,
    >>>     lagrange_maxiter=5,
    >>>     sampler='braket_dwave_advantage',
    >>>     num_reads=1000
    >>> )

    It is also possible to optimize the Lagrangian parameter used to construct a QUBO for a variational algorithm
    such as VQE or QAOA. For instance,

    >>> import numpy as np
    >>> from qatalyst import qcore
    >>> objective = np.array([[-6, 10, 0, 0], [10, -8, 2, 8], [0, 2, -3, 4], [0, 8, 4, -5]])
    >>> constraints = np.array([[1, 1, 1, 1, -1], [0, 1, 1, 1, -1]])
    >>> res = qcore.sample_lagrange_optimization(
    >>>     objective,
    >>>     constraints,
    >>>     lagrange_maxiter=5,
    >>>     sampler='braket_rigetti',
    >>>     algorithm='qaoa',
    >>>     num_shots=10,
    >>>     optimizer='cobyla',
    >>>     optimizer_params={'maxiter': 5}
    >>> )
    >>> print(res.samples[0])
    >>>     # [1 0 0 1]
    """
    client_kwargs, param_kwargs = get_client_kwargs(**kwargs)
    client = QatalystCore(**client_kwargs)
    return client.sample_lagrange_optimization(
        objective=objective,
        constraints=constraints,
        rhs_constraints=rhs_constraints,
        objective_weight=objective_weight,
        constraint_penalties=constraint_penalties,
        initial_guesses=initial_guesses,
        objective_units=objective_units,
        lagrange_maxiter=lagrange_maxiter,
        **param_kwargs
    )
