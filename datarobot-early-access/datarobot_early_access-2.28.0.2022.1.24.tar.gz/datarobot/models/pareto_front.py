#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import trafaret as t

from datarobot._compat import Int, String
from datarobot.client import get_client, staticproperty
from datarobot.models.api_object import APIObject
from datarobot.utils import from_api


class Solution(object):
    """Eureqa Solution.

    A solution represents a possible Eureqa model; however not all solutions
    have models associated with them.  It must have a model created before
    it can be used to make predictions, etc.

    Attributes
    ----------
    eureqa_solution_id: str
        ID of this Solution
    complexity: int
        Complexity score for this solution. Complexity score is a function
        of the mathematical operators used in the current solution.
        The Complexity calculation can be tuned via model hyperparameters.
    error: float or None
        Error for the current solution, as computed by Eureqa using the
        'error_metric' error metric. It will be None if model refitted existing solution.
    expression: str
        Eureqa model equation string.
    expression_annotated: str
        Eureqa model equation string with variable names tagged for easy identification.
    best_model: bool
        True, if the model is determined to be the best
    """

    _client = staticproperty(get_client)

    def __init__(
        self,
        eureqa_solution_id,
        complexity,
        error,
        expression,
        expression_annotated,
        best_model,
        project_id,
    ):
        self.eureqa_solution_id = eureqa_solution_id
        self.complexity = complexity
        self.error = error
        self.expression = expression
        self.expression_annotated = expression_annotated
        self.best_model = best_model
        self._project_id = project_id

    def create_model(self):
        """Add this solution to the leaderboard, if it is not already present."""
        url = "projects/{}/eureqaModels/".format(self._project_id)
        data = {"solutionId": self.eureqa_solution_id}
        self._client.post(url, data=data)


class ParetoFront(APIObject):
    """Pareto front data for a Eureqa model.

    The pareto front reflects the tradeoffs between error and complexity for particular model. The
    solutions reflect possible Eureqa models that are different levels of complexity.  By default,
    only one solution will have a corresponding model, but models can be created for each solution.

    Attributes
    ----------
    project_id : str
        the ID of the project the model belongs to
    error_metric : str
        Eureqa error-metric identifier used to compute error metrics for this search. Note that
        Eureqa error metrics do NOT correspond 1:1 with DataRobot error metrics -- the available
        metrics are not the same, and are computed from a subset of the training data rather than
        from the validation data.
    hyperparameters : dict
        Hyperparameters used by this run of the Eureqa blueprint
    target_type : str
       Indicating what kind of modeling is being done in this project, either 'Regression',
       'Binary' (Binary classification), or 'Multiclass' (Multiclass classification).
    solutions : list(Solution)
        Solutions that Eureqa has found to model this data.
        Some solutions will have greater accuracy.  Others will have slightly
        less accuracy but will use simpler expressions.
    """

    _Solution = t.Dict(
        {
            t.Key("eureqa_solution_id"): String,
            t.Key("complexity"): Int,
            t.Key("error"): t.Float() | t.Null,
            t.Key("expression"): String,
            t.Key("expression_annotated"): String,
            t.Key("best_model"): t.Bool,
        }
    ).ignore_extra("*")

    ParetoFrontWrapper = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("error_metric"): String,
            t.Key("hyperparameters"): t.Dict().allow_extra("*"),
            t.Key("target_type"): String,
            t.Key("solutions"): t.List(_Solution),
        }
    ).ignore_extra("*")

    _converter = ParetoFrontWrapper

    def __init__(self, project_id, error_metric, hyperparameters, target_type, solutions):
        self.project_id = project_id
        self.error_metric = error_metric
        self.hyperparameters = hyperparameters
        self.target_type = target_type
        self.solutions = [Solution(project_id=project_id, **soln) for soln in solutions]

    def __repr__(self):
        return "ParetoFront({})".format(self.project_id)

    @classmethod
    def from_server_data(cls, data, keep_attrs=None):
        """
        Instantiate an object of this class using the data directly from the server,
        meaning that the keys may have the wrong camel casing

        Parameters
        ----------
        data : dict
            The directly translated dict of JSON from the server. No casing fixes have
            taken place
        keep_attrs : list
            List of the dotted namespace notations for attributes to keep within the
            object structure even if their values are None
        """
        case_converted = from_api(data, keep_attrs=keep_attrs, keep_null_keys=True)
        return cls.from_data(case_converted)
