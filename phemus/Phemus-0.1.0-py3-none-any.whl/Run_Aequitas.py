from .Retrain_Sklearn import retrain_sklearn
from .Aequitas_Fully_Directed_Sklearn import aequitas_fully_directed_sklearn
from .Generate_Sklearn_Classifier import generate_sklearn_classifier
from .utils import get_input_bounds
from .utils import get_column_names
from .utils import get_idx_of_col_to_be_predicted


def run_aequitas_fully_direct(num_params, sensitive_param_idx, sensitive_param_name, perturbation_unit, threshold, \
                  global_iteration_limit, local_iteration_limit, pkl_dir, csv_dir, \
                  improved_pkl_dir, num_trials, samples, col_to_be_predicted):

    column_names = get_column_names(csv_dir)
    input_bounds = get_input_bounds(csv_dir, col_to_be_predicted)
    col_to_be_predicted_idx = get_idx_of_col_to_be_predicted(csv_dir, col_to_be_predicted)
    
    generate_sklearn_classifier(csv_dir, pkl_dir, sensitive_param_name, col_to_be_predicted)

    aequitas_fully_directed_sklearn(num_params, sensitive_param_idx, sensitive_param_name, perturbation_unit, threshold, \
                  global_iteration_limit, local_iteration_limit, input_bounds, pkl_dir, csv_dir, column_names)

    retrain_sklearn(pkl_dir, improved_pkl_dir, csv_dir, num_trials, samples,\
                            sensitive_param_idx, num_params, input_bounds, col_to_be_predicted_idx)