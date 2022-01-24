# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Methods for AutoML remote runs."""
import logging

try:
    from azureml.train.automl.runtime._remote_script import batch_driver_wrapper
    from azureml.train.automl.runtime._remote_script import driver_wrapper
    from azureml.train.automl.runtime._remote_script import featurization_wrapper
    from azureml.train.automl.runtime._remote_script import fit_featurizers_wrapper
    from azureml.train.automl.runtime._remote_script import model_exp_wrapper
    from azureml.train.automl.runtime._remote_script import model_test_wrapper
    from azureml.train.automl.runtime._remote_script import setup_wrapper
    from azureml.train.automl.runtime._remote_script import hyperparameter_sweeping_driver_wrapper
except Exception:
    logging.warning("Encountered exception when importing one or more remote wrappers.")
