# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""model_explanation.py, A file for model explanation classes."""

from urllib import request

ModelExpSupportStr = 'model_exp_support'
ModelExpGithubNBLink = "https://github.com/Azure/MachineLearningNotebooks/blob/" + \
                       "master/how-to-use-azureml/automated-machine-learning/" + \
                       "regression-explanation-featurization/" + \
                       "auto-ml-regression-explanation-featurization.ipynb"


def _convert_explanation(explanation, include_local_importance=True):
    """
    Convert the explanation tuple into a consistent six element tuple.

    :param explanation: a tuple of four or six elements
    :return: a tuple of six elements
    """
    if include_local_importance:
        local_importance_value = explanation.local_importance_values
    expected_value = explanation.expected_values
    overall_summary = explanation.get_ranked_global_values()
    overall_imp = explanation.get_ranked_global_names()
    per_class_summary = None
    per_class_imp = None
    if hasattr(explanation, 'get_ranked_per_class_values'):
        per_class_summary = explanation.get_ranked_per_class_values()
    if hasattr(explanation, 'get_ranked_per_class_names'):
        per_class_imp = explanation.get_ranked_per_class_names()

    if include_local_importance:
        return (local_importance_value, expected_value, overall_summary, overall_imp, per_class_summary, per_class_imp)
    else:
        return (None, expected_value, overall_summary, overall_imp, per_class_summary, per_class_imp)


def _get_valid_notebook_path_link():

    num_try = 0
    while num_try < 3:
        try:
            status = request.urlopen(ModelExpGithubNBLink).code
            if status == 200:
                return ModelExpGithubNBLink
        except Exception:
            pass
        num_try = num_try + 1
    return None
