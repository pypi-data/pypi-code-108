from enum import Enum


class QatalystConstants():

    # API endpoints
    BRAKET_CHECK_ENDPOINT = "/braketcheck"
    POST_ENDPOINT = "/queues/submit"
    RESULT_ENDPOINT = "/queues/result?JobID={}"
    STATUS_ENDPOINT = "/queues/status?JobID={}"
    CONFIG_QATALYST_API_URL = "qatalyst_api_url"

    # URLs
    DEFAULT_API_URL = "https://api.qci-prod.com"

    # misc constants
    API_ENV_VAR = "QATALYST_API_URL"
    BRAKET_DWAVE = "braket_dwave"
    BRAKET_DWAVE_ADVANTAGE = "braket_dwave_advantage"
    BRAKET_DWAVE_ADVANTAGE4_1 = "braket_dwave_advantage4_1"
    BRAKET_DWAVE_ADVANTAGE3_2 = "braket_dwave_advantage3_2"
    BRAKET_DWAVE_DEFAULT = BRAKET_DWAVE_ADVANTAGE4_1

    BRAKET_IONQ = "braket_ionq"
    BRAKET_IONQ_S11 = "braket_ionq_s11"
    BRAKET_IONQ_DEFAULT = BRAKET_IONQ_S11

    BRAKET_RIGETTI = "braket_rigetti"
    BRAKET_RIGETTI_ASPEN_11 = "braket_rigetti_aspen_11"
    BRAKET_RIGETTI_DEFAULT = BRAKET_RIGETTI_ASPEN_11
    # less-preferred but still supported/translated:
    BRAKET_RIGETTI_11 = "braket_rigetti_11"

    BRAKET_SIMULATOR = "braket_simulator"
    BRAKET_SIMULATOR_SV1 = "braket_simulator_sv1"
    BRAKET_SIMULATOR_TN1 = "braket_simulator_tn1"
    BRAKET_SIMULATOR_DM1 = "braket_simulator_dm1"
    BRAKET_SIMULATOR_DEFAULT = BRAKET_SIMULATOR_SV1

    CHECKPOINT_INTERVAL = 'checkpoint_interval'
    CONFIGURATION = "default"
    DEFAULT_OBJECTIVE_FUNCTION_VALUE = "Objective Function Value"
    EDGE_WEIGHT_KEY = "weight"

    # ionq sampler names
    IONQ_SIMULATOR = "ionq_simulator"
    IONQ_S11 = "ionq_s11"
    IONQ_S21 = "ionq_s21"

    MAX_CSAMPLE_QUBIT_SIZE = 1000000
    SAMPLER = 'sampler'

    # classical sampler constants
    DEFAULT_CLASSICAL_SAMPLER = "qonductor"
    DEFAULT_CLASSICAL_SAMPLER_LEGACY_BASIC = "csample_basic"
    DEFAULT_CLASSICAL_SAMPLER_LEGACY = "csample"
    DEFAULT_CLASSICAL_SAMPLERS_LIST = [
        DEFAULT_CLASSICAL_SAMPLER,
        DEFAULT_CLASSICAL_SAMPLER_LEGACY,
        DEFAULT_CLASSICAL_SAMPLER_LEGACY_BASIC
    ]

    # quantum sampler constants
    QUANTUM_SAMPLER_DWAVE = 'dwave'
    QUANTUM_SAMPLER_IONQ = 'ionq'
    QUANTUM_SAMPLER_RIGETTI = 'rigetti'
    QUANTUM_SAMPLER_SIMULATOR = 'simulator'

    QUANTUM_SAMPLER_NAMES_LIST = [
        QUANTUM_SAMPLER_DWAVE,
        QUANTUM_SAMPLER_IONQ,
        QUANTUM_SAMPLER_RIGETTI,
        QUANTUM_SAMPLER_SIMULATOR
    ]

    # client kwarg constants
    CLIENT_ACCESS_TOKEN = 'access_token'
    CLIENT_CONFIGURATION = 'configuration'
    CLIENT_CONF_PATH = 'conf_path'
    CLIENT_IGNORE_QPU_WINDOW = 'ignore_qpu_window'
    CLIENT_INTERRUPTIBLE = 'interruptible'
    CLIENT_PASSWORD = 'password'
    CLIENT_SAMPLER = SAMPLER
    CLIENT_USERNAME = 'username'
    CLIENT_URL = 'url'
    CLIENT_VAR_LIMIT = 'var_limit'


    # metadata constants
    METADATA_CHECKPOINT_INTERVAL = CHECKPOINT_INTERVAL
    METADATA_DATA_TYPE = 'data_type'
    METADATA_PROBLEM_TYPE = 'problem_type'
    METADATA_SAMPLER = SAMPLER
    METADATA_SHAPE = 'shape'
    METADATA_UNITS = 'units'

    # CSample param constants (which get passed through qatalyst to CSample and need to pass the qatalyst param check)
    CSAMPLE_PARAM_CHECKPOINT_INTERVAL = CHECKPOINT_INTERVAL
    CSAMPLE_PARAM_NUM_FIND_MAX = 'find_max'
    CSAMPLE_PARAM_NUM_REPEATS = 'num_repeats'
    CSAMPLE_PARAM_NUM_SOLUTIONS = 'num_solutions'
    CSAMPLE_PARAM_QLEN = 'QLEN'
    CSAMPLE_PARAM_SEED = 'seed'                             # seed for random number generator
    CSAMPLE_PARAM_SEED_VECTORS = 'seed_vectors'             # initial guesses
    CSAMPLE_PARAM_SOLVER_LIMIT = 'solver_limit'
    CSAMPLE_PARAM_SOLVER_TYPE = 'solver_type'
    CSAMPLE_PARAM_TARGET = 'target'
    CSAMPLE_PARAM_TIMEOUT = 'timeout'
    CSAMPLE_PARAM_TIMEOUT_NOPROGRESS = 'timeout_noprogress'
    CSAMPLE_PARAM_VERBOSITY = 'verbosity'
    CSAMPLE_PARAM_EXTENDED_TIMES = 'extended_csample_times'


    # param constants
    PARAM_ALGORITHM = 'algorithm'
    PARAM_ALPHA = 'alpha'
    PARAM_BALANCED_PARTITION_WEIGHT = 'balanced_partition_weight'
    PARAM_BETA_OBJ = 'beta_obj'                         # objective_weight
    PARAM_BIPARTITE = 'bipartite'                       # for community detection
    PARAM_BIPARTITE_KEY = 'bipartite_key'               # for community detection
    PARAM_CHAIN_STRENGTH = 'chain_strength'             # for quantum samplers
    PARAM_CHECKPOINT_INTERVAL = CSAMPLE_PARAM_CHECKPOINT_INTERVAL
    PARAM_CHROMATIC_LB = 'chromatic_lb'             # clique cover - chromatic lower bound
    PARAM_CHROMATIC_UB = 'chromatic_ub'             # clique cover - chromatic upper bound
    PARAM_CIRCUIT_DEPTH = 'circuit_depth'
    PARAM_CONSTRAINTS = 'constraints'
    PARAM_CONSTRAINT_PENALTIES = 'constraint_penalties'
    PARAM_CUT_SIZE_WEIGHT = 'cut_size_weight'
    PARAM_DEPTH = 'depth'
    PARAM_GAMMA = 'gamma'
    PARAM_GRAPH = 'G'
    PARAM_GRAPH_ALGO = 'graph_algo'
    PARAM_K = 'k'                                      # partition size (for graph problems)
    PARAM_LAGRANGE_MAXITER = 'lagrange_maxiter'
    PARAM_LAGRANGE_OPTIMIZER = 'lagrange_optimizer'
    PARAM_MAX_DEPTH = 'max_depth'
    PARAM_NUM_COMMUNITIES = 'num_communities'          # for community detection
    PARAM_NUM_READS = 'num_reads'
    PARAM_NUM_SHOTS = 'num_shots'
    PARAM_NUM_SOLUTIONS = CSAMPLE_PARAM_NUM_SOLUTIONS
    PARAM_OBJECTIVE = 'objective'
    PARAM_OBJECTIVE_WEIGHT = 'objective_weight'
    PARAM_OPTIMIZER = 'optimizer'
    PARAM_OPTIMIZER_PARAMS = 'optimizer_params'
    PARAM_PROBLEM_NAME = 'problem_name'
    PARAM_RHS_CONSTRAINTS = 'rhs_constraints'
    PARAM_SOLVER_TYPE = CSAMPLE_PARAM_SOLVER_TYPE
    PARAM_TIMEOUT = CSAMPLE_PARAM_TIMEOUT
    PARAM_TIMEOUT_NOPROGRESS = CSAMPLE_PARAM_TIMEOUT_NOPROGRESS
    PARAM_WEIGHT_KEY = 'weight_key'                     # for community detection, partition

    VALID_PARAM_NAMES_LIST = [
        CSAMPLE_PARAM_CHECKPOINT_INTERVAL,
        CSAMPLE_PARAM_EXTENDED_TIMES,
        CSAMPLE_PARAM_NUM_FIND_MAX,
        CSAMPLE_PARAM_NUM_REPEATS,
        CSAMPLE_PARAM_NUM_SOLUTIONS,
        CSAMPLE_PARAM_QLEN,
        CSAMPLE_PARAM_SEED,
        CSAMPLE_PARAM_SEED_VECTORS,
        CSAMPLE_PARAM_SOLVER_LIMIT,
        CSAMPLE_PARAM_SOLVER_TYPE,
        CSAMPLE_PARAM_TARGET,
        CSAMPLE_PARAM_TIMEOUT,
        CSAMPLE_PARAM_TIMEOUT_NOPROGRESS,
        CSAMPLE_PARAM_VERBOSITY,
        PARAM_ALGORITHM,
        PARAM_ALPHA,
        PARAM_BALANCED_PARTITION_WEIGHT,
        PARAM_BETA_OBJ,
        PARAM_BIPARTITE,
        PARAM_BIPARTITE_KEY,
        PARAM_CHAIN_STRENGTH,
        PARAM_CHROMATIC_LB,
        PARAM_CHROMATIC_UB,
        PARAM_CIRCUIT_DEPTH,
        PARAM_CONSTRAINTS,
        PARAM_CONSTRAINT_PENALTIES,
        PARAM_CUT_SIZE_WEIGHT,
        PARAM_DEPTH,
        PARAM_GAMMA,
        PARAM_GRAPH_ALGO,
        PARAM_K,
        PARAM_LAGRANGE_MAXITER,
        PARAM_LAGRANGE_OPTIMIZER,
        PARAM_MAX_DEPTH,
        PARAM_NUM_COMMUNITIES,
        PARAM_NUM_READS,
        PARAM_NUM_SHOTS,
        PARAM_OBJECTIVE,
        PARAM_OBJECTIVE_WEIGHT,
        PARAM_OPTIMIZER,
        PARAM_OPTIMIZER_PARAMS,
        PARAM_PROBLEM_NAME,
        PARAM_WEIGHT_KEY
    ]

