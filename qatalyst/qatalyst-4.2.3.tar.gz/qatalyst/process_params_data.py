#
#    (C) Quantum Computing Inc., 2021.
#
#    THIS IS UNPUBLISHED PROPRIETARY SOURCE CODE of the Copyright Holder.
#    The contents of this file may not be disclosed to third parties, copied
#    or duplicated in any form, in whole or in part, without the prior written
#    permission of the Copyright Holder.
#
import re
from dataclasses import dataclass, field
from typing import Dict, Tuple, List, AnyStr
import numpy as np
import scipy.sparse as sp
from scipy.optimize import show_options
import networkx as nx

from .constants import QatalystConstants
from .encoders import encode_data
from .data_processing import AwsDeviceClient


@dataclass
class ProcessParams:
    """
    """
    PROBLEM_TYPES = ['qubo', 'constraint_problem', 'graph', 'lagrange_opt']
    DWAVE_MAX_CLIQUES = {'DW_2000Q_': 64, 'Advantage_system3': 120, 'Advantage_system4': 120}
    DATA_OBJ_FNAME = 'data_obj.npz'
    DATA_CON_FNAME = 'data_con.npz'
    METADATA_FNAME = 'metadata.txt'
    PARAMS_FNAME = 'params.txt'
    INIT_GUESSES_FNAME = 'initial_seeds.npz'
    CONSTRAINT_PENALTIES_FNAME = 'constraint_penalties.npz'
    RHS_CONSTRAINTS_FNAME = 'rhs_constraints.npz'
    shape: Tuple = None
    data_type: str = None
    objective_units: str = QatalystConstants.DEFAULT_OBJECTIVE_FUNCTION_VALUE
    problem_type: str = None
    sampler: str = None
    device: AwsDeviceClient = None
    max_qubit_size: int = None
    checkpoint_interval: int = 30
    params: Dict = None
    metadata: Dict = None
    message: Dict = field(default_factory=dict)

    def __post_init__(self):

        # Verify sampler set
        assert self.sampler is not None, \
            "Sampler not provided"

        if self.sampler not in QatalystConstants.DEFAULT_CLASSICAL_SAMPLERS_LIST:
            if self.sampler.startswith('braket'):
                # Verify the device is set
                assert self.device is not None, \
                    "Device not provided"

        # Verify maximum number of qubits set
        assert self.max_qubit_size is not None, \
            "Maximum number of qubits not set"

        # Verify the user specified a problem type
        assert self.problem_type is not None, \
            "Required arguement 'problem_type' is undefined."

        # Verify checkpoint_interval is defined
        if self.params is None:
            self.params = {QatalystConstants.PARAM_CHECKPOINT_INTERVAL: self.checkpoint_interval}
        elif self.params.get(QatalystConstants.PARAM_CHECKPOINT_INTERVAL) is not None:
            self.checkpoint_interval = self.params.get(QatalystConstants.PARAM_CHECKPOINT_INTERVAL)
        else:
            # Guarantee checkpoint interval available to progress
            self.params[QatalystConstants.PARAM_CHECKPOINT_INTERVAL] = self.checkpoint_interval

    def process_metadata(self):
        """
        Formulate the metadata dictionary based on input parameters and user
            input. We need to inform the backend services what type of problem
            we want to solve, the type of data sent, what sampler to use, and
            (optionally) the shape of the data so an encoded matrix can be
            reconstructed on the server side.

        :return: Add dictionary to requests message containing data
            {
                problem_type,
                data_type,
                sampler,
                checkpoint_interval,
                [shape],
                objective function units
            }
        """
        if self.problem_type not in self.PROBLEM_TYPES:
            raise ValueError(
                '''ERROR: Unexpected problem type.
                 Problem type must be one of {}\n'''.format(self.PROBLEM_TYPES)
            )

        # Generate an error message if data type isn't set
        if self.data_type is None:
            self.get_data_type("bad_data_type")

        # Generate an error if shape not set
        if self.shape is None:
            raise ValueError("The shape of the problem is not defined.")

        self.metadata = {
            QatalystConstants.METADATA_PROBLEM_TYPE: self.problem_type,
            QatalystConstants.METADATA_DATA_TYPE: self.data_type,
            QatalystConstants.METADATA_SAMPLER: self.sampler,
            QatalystConstants.METADATA_CHECKPOINT_INTERVAL: self.checkpoint_interval,
            QatalystConstants.METADATA_SHAPE: self.shape,
            QatalystConstants.METADATA_UNITS: self.objective_units
        }

        # Provide maximization flag for progress plot
        # TODO Remove this once the kernels are finished being rolled out into production
        if self.params.get(QatalystConstants.PARAM_GRAPH_ALGO, 'not_graph') in ["community_detection", "bipartite_community_detection"]:
            self.metadata.update({'is_max_problem': True})
        else:
            self.metadata.update({'is_max_problem': False})

        # Add metadata to the message shipped by requests
        self.message['metadata'] = (
            self.METADATA_FNAME,
            encode_data(self.metadata),
            'text/plain'
        )

    def process_params(self):
        """
        Method  : process_params()
        Purpose : Perform basic checks to validate parameter values that
                :     will be provided to the backend
        Input   : params (dict) - Dictionary containing parameter values
                :     specified by the end user
        Output  : validated parameter values
        """
        if self.sampler != QatalystConstants.DEFAULT_CLASSICAL_SAMPLER:
            is_quantum = True
        else:
            is_quantum = False

        if not self.param_check(self.params, is_quantum=is_quantum):
            raise ValueError(f"Unknown parameter error. Please check kwargs. {self.params}")

        # Add params to the message shipped by requests
        self.message['params'] = (
            self.PARAMS_FNAME,
            encode_data(self.params),
            'text/plain'
        )

    def param_check(self, params: dict, is_quantum: bool = False):
        """
        We check the basic parameters here, outside of sampler, which has been checked and set elsewhere.
        """
        checks = {
            QatalystConstants.PARAM_NUM_SOLUTIONS: (self.mincheck, 0),
            QatalystConstants.PARAM_PROBLEM_NAME: (self.strcheck, None)
        }

        if is_quantum:
            checks.update({
                QatalystConstants.PARAM_NUM_SHOTS: (self.mincheck, 0),
                QatalystConstants.PARAM_NUM_READS: (self.mincheck, 0),
                QatalystConstants.PARAM_DEPTH: (self.mincheck, 1),
                QatalystConstants.PARAM_ALGORITHM: (self.algocheck, ['vqe', 'qaoa']),
                QatalystConstants.PARAM_OPTIMIZER: (self.optimizer_check, self.get_scipy_minimize_methods()),
                QatalystConstants.PARAM_OPTIMIZER_PARAMS: (self.optimizer_options_check, 0) # only set up for 'maxiter' > 0 check
            })

        # loop through params
        for pname, val in params.items():
            if pname not in QatalystConstants.VALID_PARAM_NAMES_LIST:
                raise ValueError(f"'{pname}' is not a recognized parameter name.")
            # get the function from above for a given parameter, else None
            func_param = checks.get(pname)
            if func_param is None:
                continue
            else:
                f, param = func_param
            # is the provided value within the range required
            if not f(param, val):
                if isinstance(param, int):
                    raise ValueError(f"Parameter '{pname}'={val}, must be greater than {param}.")
                elif isinstance(param, dict):
                    raise ValueError(f"Parameter '{pname}'={val}, must be greater than {param}.")
                elif isinstance(val, str):
                    raise ValueError(f"Parameter '{pname}'={val}, must be valid python identifier.")
                else:
                    print(f"Unrecognized parameter {param} ({type(param)}): {val}")
                    raise ValueError(f"Parameter '{pname}={val}', must be one of {param}")
        else:
            return True

    @staticmethod
    def get_scipy_minimize_methods():
        """
        We want to match elements '===' right after the methods in the string returned
        by show_options.
        """
        REGEX = r'[=]+$'
        opts = show_options('minimize', disp=False)
        opts = [x for x in opts.split('\n') if len(x) > 0]
        return [opts[i-1] for i, m in enumerate(opts) if re.match(REGEX, m)]

    @staticmethod
    def mincheck(thresh, val) -> bool:
        """
        Make sure val > threshold
        """
        return val > thresh

    @staticmethod
    def strcheck(param, val) -> bool:
        """
        Make sure val is a string containing only valid characters
        """
        if not val:
            return False

        if not isinstance(val, str):
            raise ValueError(f"Parameter value {val} must be a str.")
            return False

        return val.isidentifier()

    @staticmethod
    def algocheck(options: List[AnyStr], algo: str) -> bool:
        return algo.lower() in options

    @staticmethod
    def optimizer_check(optimizers: List[AnyStr], opt: str) -> bool:
        return opt.lower() in optimizers

    def optimizer_options_check(self, param, opts):
        OPTIONS = {'maxiter': param}
        for opt, val in opts.items():
            if opt in OPTIONS:
                thresh = OPTIONS[opt]
                return self.mincheck(thresh, val)

    @staticmethod
    def get_data_type(data=None):
        """
        """
        if isinstance(data, dict):
            return 'dict'

        elif isinstance(data, np.ndarray):
            return 'dense'

        elif isinstance(data, nx.Graph):
            return 'graph'

        elif isinstance(data, sp.spmatrix):
            return 'sparse'

        else:
            raise TypeError(
                """ERROR: Problem provided is unsupported data type {}.
                Problem should be provided as one of
                    dictionary,
                    np.ndarray,
                    scipy sparse matrix, or
                    NetworkX Graph.""".format(type(data))
            )
