"""Implements Typing constraints to config data passed to some modules. For instance, GA and OPS both accepts a configuration Dictionary that follow these rules.
    """

try:
    from typing import TypedDict  # Python >= 3.8
except ImportError:
    from typing_extensions import TypedDict  # Python < 3.8
from qsarmodelingpy.cross_validation_class import CrossValidation
from qsarmodelingpy.external_validation import ExternalValidation
from typing import List, Union


class ConfigGAInterface(TypedDict):
    XMatrix: str
    yvector: str
    varcut: float
    corrcut: float
    max_latent_model: Union[int, None]
    min_vars_model: int
    max_vars_model: int
    population_size: int
    migration_rate: float
    crossover_rate: float
    mutation_rate: float
    generations: int
    yrand: float
    lno: float
    output_matrix: str
    output_cv: str
    output_q2: str
    output_selected: str
    output_PLS_model: Union[str, None]
    autoscale: bool
    lj_transform: bool
    autocorrcut: float


class ConfigOPSInterface(TypedDict):
    XMatrix: str
    yvector: str
    varcut: float
    corrcut: float
    latent_vars_ops: int
    latent_vars_model: int
    ops_window: int
    ops_increment: int
    vars_percentage: float
    models_to_save: int
    yrand: float
    lno: float
    output_matrix: str
    output_cv: str
    output_models: str
    output_PLS_model: Union[str, None]
    lj_transform: bool
    autoscale: bool
    autocorrcut: float
    ops_type: str


class ConfigExtValInterface(TypedDict):
    XMatrix: str
    yvector: str
    test_set: Union[None, int, str, list]
    latent_vars_model: Union[None, int]
    extval_type: int
    autoscale: bool
    lj_transform: bool
    output_extval: str
    output_cv: str
    output_X_train: str
    output_y_train: str
    output_X_test: str
    output_y_test: str


class ExtValResult(TypedDict):
    external_validation: ExternalValidation
    cross_validation: CrossValidation
    train: List[int]
    test: List[int]