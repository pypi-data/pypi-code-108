import itertools
from bisect import bisect
from cross_validation_class import CrossValidation
import pandas as pd


def systematic_search(X: pd.DataFrame, y: pd.DataFrame, min_var: int, max_var: int, max_models: int) -> dict:
    """Run a Systematic Search in the dataframe. The systematic search tries
    every combination of variables between `min_var` and `max_var` variables. Be
    aware that the computational cost of this is incredibly large. For example,
    for a dataset with 20 variables, if you want to generate all models between
    4 and 10 variables, the program will test 615315 models! Because of that,
    this is only intended to be used as a refining strategy, after a preliminar
    selection.

    Args:
        X (pd.DataFrame): the descriptors matrix
        y (pd.DataFrame): the bioactivity vector
        min_var (int): the minimum of variables to use
        max_var (int): the maximum of variables to use
        max_models (int): the maximum number of models to save

    Returns:
        dict: a dict containing the Q2 and the variables selected for each saved
            model. To get the best model, find the index of the minimum Q2 and use
            it to find the variables.
    """
    _, n = X.shape
    variables = range(n)
    models = {}
    models["Q2"] = []
    models["var_sel"] = []
    Q2 = []
    var_sel = []
    for n_var in range(min_var, max_var + 1):
        for subset in itertools.combinations(variables, n_var):
            Xev = X.iloc[:, list(subset)]
            cv = CrossValidation(Xev.values, y.values)
            p = bisect(Q2, -max(cv.Q2()))
            Q2.insert(p, -max(cv.Q2()))
            var_sel.insert(p, subset)
            if len(Q2) > max_models:
                # if the maximum number of model is reached, remove the worst (the last)
                Q2.pop()
                var_sel.pop()
    models["Q2"] = [-q for q in Q2]
    models["var_sel"] = var_sel
    return models
