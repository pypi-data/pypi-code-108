#
#    (C) Quantum Computing Inc., 2021.
#
#    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE of the Copyright Holder.
#    The contents of this file may not be disclosed to third parties, copied
#    or duplicated in any form, in whole or in part, without the prior written
#    permission of the Copyright Holder.
#
from dataclasses import dataclass
from typing import Union, Dict, Tuple, List, AnyStr
import numpy as np
import scipy.sparse as sp
from .encoders import encode_data
from .process_qubo_data import ProcessQubo
from .constants import QatalystConstants


@dataclass
class ProcessConstraints(ProcessQubo):
    """
    """
    lagrange_maxiter: int = 5
    objective: Union[np.ndarray, sp.spmatrix] = None
    objective_weight: float = 1.0
    constraints: Union[np.ndarray, sp.spmatrix] = None
    constraint_penalties: Union[np.ndarray, float, int] = 1.0
    rhs_constraints: Union[np.ndarray, sp.spmatrix] = None

    def __post_init__(self):
        super().__post_init__()

        assert(
            (self.problem_type == "constraint_problem") or
            (self.problem_type == "lagrange_opt")
        ), "\nERROR: ProcessConstraints only valid for constraint and Lagrang optimization problems.\n"

        # Verify the objective weight is added to the parameters
        self.__check_objective_weight()

        # Verify max depth added to parameter for lagrangian optimization
        if self.problem_type == "lagrange_opt":
            self.__check_lagrange_maxiter()

        # Validate the objective and attach it to the requests message
        self.process_objective()

        # Validate the constraints and attach it to the requests message
        self.process_constraints()

        # Add metadata to the requests message
        self.process_metadata()

        # Add params to the requests message
        self.process_params()

        # Add constraint penalties to the requests message
        self.process_constraint_penalties()

        # Add rhs to the constraints if provided by the user
        if self.rhs_constraints is not None:
            self.process_rhs_constraints()

        # Process Initial Guesses if provided by user
        if self.initial_guesses is not None:
            self.process_initial_guesses()

    def process_objective(self):
        """
        Method : process_objective()
        Purpose: Process user provided objective matrix and append it to
               :     the requests message.
        Input  : Qubo as Numpy Array, SciPy sparse array, or dictionary.
        Output : Qubo as binary appended to messages diectionary.
        """
        if self.objective is None:
            "\nNOTE: Objective matrix not specified by user.\n"
        else:
            # Verify the objective is the expected data type
            self.check_objective(data=self.objective)

            # Define the shape of the problem
            self.shape = self.objective.shape

            # Set the data type for the problem
            self.data_type = self.get_data_type(self.objective)

            # Add objective to the message shipped by requests
            self.message['data_obj'] = (
                self.DATA_OBJ_FNAME,
                encode_data(self.objective),
                'application/octet-stream'
            )

    def process_constraints(self):
        """
        Method : process_constraints()
        Purpose: Process user provided constraints matrix and append it to
               :     the requests message.
        Input  : Constraints as Numpy or SciPy sparse array.
        Output : Constraints as binary appended to messages diectionary.
        """
        assert self.constraints is not None, \
            "\nERROR: Missing required constraints matrix.\n"

        # Validate the user provided constraint object
        # print(f"Checking validity of constraints...")
        self.__check_constraints()

        # Add constraints to the message shipped by requests
        self.message['data_con'] = (
            self.DATA_CON_FNAME,
            encode_data(self.constraints),
            'application/octet-stream'
        )

    def __check_constraints(self):

        if self.objective is not None:
            # Make sure the data type is correct
            if isinstance(self.objective, np.ndarray):
                assert isinstance(self.constraints, np.ndarray), \
                    "\nThe constraints and objective matrices must the same type. \
                     The objective was specified as an NumPy array.\n"
            else:
                assert isinstance(self.constraints, sp.spmatrix), \
                    "\nThe constraints and objective matrices must the same type. \
                     The objective was specified as an SciPy sparse array.\n"

            # Verify the constraints have the correct dimensions
            if self.rhs_constraints is not None:
                assert self.constraints.shape[1] == self.objective.shape[1], \
                    "\nThe constraint and objective matrices must contain the \
                     same number of variables.\n \
                     Input: constraint.shape = {}, objective.shape = {}".format(
                        self.constraints.shape,
                        self.objective.shape
                    )
            else:
                assert self.constraints.shape[1] == self.objective.shape[1] + 1, \
                    "\nThe constraints are of the form Ax-b = 0.\n \
                     Column dimension of constraint matrix must equal objective.shape[1] + 1.\n \
                     Input: constraint.shape = {}, objective.shape = {}".format(
                        self.constraints.shape,
                        self.objective.shape
                    )
        else:
            # Objective not provided. Thus specify shape and data_type
            self.data_type = self.get_data_type(self.constraints)

            # Set the shape of the problem for the metadata
            if self.rhs_constraints is not None:
                self.shape = (
                    self.constraints.shape[1],
                    self.constraints.shape[1]
                )
            else:
                self.shape = (
                    self.constraints.shape[1] - 1,
                    self.constraints.shape[1] - 1
                )

        # Assert the values in the constraint matrix are finite
        if isinstance(self.constraints, np.ndarray):
            assert np.isfinite(self.constraints).all(), \
                "\nERROR: NAN entry in constraint matrix.\n"
        else:
            nan_rows = [i for i, row in enumerate(self.constraints.data) if not np.isfinite(row).all()]
            assert len(nan_rows) == 0, \
                "\nERROR: NAN entry in constraint matrix.\n"

    def process_constraint_penalties(self):
        """
        Method   : process_constraint_penalties()
        Purpose. : Generate a constraint penalty object, via user provided or
                 :     default values, and append it to the requests message.
        Input    : Constraint penalty as constant or Numpy array.
        Output   : NumPy array of constraint penalty values as a binary object
                 :     appended to messages diectionary.
        Revisions: Created March 2, 2021
        """
        # TODO: Enabling maximization requires negative constraint penalties
        if self.params.get('constraint_penalties') is not None:
            self.constraint_penalties = self.params.get('constraint_penalties')

        # Account for instances when constraint penalties called alpha
        if self.params.get(QatalystConstants.PARAM_ALPHA) is not None:
            self.constraint_penalties = self.params.pop(QatalystConstants.PARAM_ALPHA)

        # Convert the constraint penalties to vector set to constant
        if isinstance(self.constraint_penalties, (int, float)):
            assert self.constraint_penalties > 0.0, \
                "\nERROR: The constraint_penalties are required to be positive.\n"

            self.constraint_penalties = self.constraint_penalties * \
                np.ones((self.constraints.shape[0], 1), dtype=float)
        else:
            self.__check_constraint_penalties()

        # Add constraint penalties to the message shipped by requests
        self.message['constraint_penalties'] = (
            self.CONSTRAINT_PENALTIES_FNAME,
            encode_data(self.constraint_penalties),
            'application/octet-stream'
        )

    def __check_constraint_penalties(self):
        """
        Method   : __check_constraint_penalties()
        Purpose  : Verify the constraint penalties are contained within the
                 :     correct object, and have the correct dimensions.
        Input    : Constraint penalty as constant or Numpy array.
        Output   : NumPy array of constraint penalty valeus as a binary object
                 :     appended to messages diectionary.
        Revisions: Created March 2, 2021
        """
        # Verify the constraint penalties are provided within a NumPy array
        assert isinstance(self.constraint_penalties, np.ndarray), \
            "\nERROR: Individual constraint penalties must be provided within a NumPy array.\n"

        # Verify there is one constraint penalty per constraint
        assert self.constraint_penalties.shape == (self.constraints.shape[0], 1), \
            "\nERROR: Constraint penalties dimension misalignment:\n \
             Expected: {}\n Received: {}\n".format(
                (self.constraints.shape[0], 1),
                self.constraint_penalties.shape
            )

        # Verify each constraint penalty value is positive as required for our
        #     current minimization formulation
        # TODO: Enable maximization, which requires each value to be negative
        assert (self.constraint_penalties > 0.0).all(), \
            "ERROR: The constraint_penalties are required to be positive.\n"

    def process_rhs_constraints(self):
        """
        """
        self.__check_rhs_constraints()

        # Add constraint limits to the message shipped by requests
        self.message['rhs_constraints'] = (
            self.RHS_CONSTRAINTS_FNAME,
            encode_data(self.rhs_constraints),
            'application/octet-stream'
        )

    def __check_rhs_constraints(self):
        """
        """
        # Verify the constraint boundaries are provided within a NumPy array
        assert isinstance(self.rhs_constraints, (np.ndarray, sp.spmatrix)), \
            "\nERROR: Constraint limits must be provided within a NumPy array.\n"

        # Verify there is one value per constraint
        assert self.rhs_constraints.shape == (self.constraints.shape[0], 1), \
            "\nERROR: Constraint limits dimension misalignment:\n \
             Expected: {}\n Received: {}\n".format(
                (self.constraints.shape[0], 1),
                self.rhs_constraints.shape
            )

        if isinstance(self.rhs_constraints, np.ndarray):
            assert np.isfinite(self.rhs_constraints).all(), \
                "\nERROR: NAN entry in rhs_constraints arguement.\n"
        else:
            nan_rows = [i for i, row in enumerate(self.rhs_constraints.data) if not np.isfinite(row).all()]
            assert len(nan_rows) == 0, \
                "\nERROR: NAN entry in rhs_constraints arguement.\n"

    def __check_lagrange_maxiter(self):
        # Add lagrange_maxiter to self.porams if not already provided by user
        if self.params.get(QatalystConstants.PARAM_LAGRANGE_MAXITER) is None:
            self.params[QatalystConstants.PARAM_LAGRANGE_MAXITER] = self.lagrange_maxiter

        # Process lagrange_maxiter now that is in the set of parameters
        assert isinstance(self.params.get(QatalystConstants.PARAM_LAGRANGE_MAXITER), int), \
            "\nERROR: lagrange_maxiter is expected to be an integer.\n"

        assert self.params.get(QatalystConstants.PARAM_LAGRANGE_MAXITER) > 0, \
            "\nERROR: lagrange_maxiter is expected to be a > 0.\n"

    def __check_objective_weight(self):
        # Add the objective weight to the parameters if not user provided
        if self.params.get(QatalystConstants.PARAM_OBJECTIVE_WEIGHT) is not None:
            self.objective_weight = self.params.get(QatalystConstants.PARAM_OBJECTIVE_WEIGHT)

        if self.params.get(QatalystConstants.PARAM_BETA_OBJ) is not None:
            self.objective_weight = self.params.get(QatalystConstants.PARAM_BETA_OBJ)

        # Process objective weight now that it is in the set of parameters
        if isinstance(self.objective_weight, int):
            self.objective_weight = 1.0 * self.objective_weight

        assert isinstance(self.objective_weight, float), \
            "\nERROR: Objective weight is expected to be a positive floating point number.\n"

        assert self.objective_weight > 0.0, \
            "\nERROR: Objective weight is expected to be a positive floating point number.\n"

        # Map the objective weight to the value expected in the backend
        self.params[QatalystConstants.PARAM_BETA_OBJ] = self.objective_weight
