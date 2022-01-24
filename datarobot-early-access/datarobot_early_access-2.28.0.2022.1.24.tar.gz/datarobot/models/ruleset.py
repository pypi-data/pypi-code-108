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
from datarobot.models.api_object import APIObject
from datarobot.utils import get_id_from_response


class Ruleset(APIObject):
    """ Represents an approximation of a model with DataRobot Prime

    Attributes
    ----------
    id : str
        the id of the ruleset
    rule_count : int
        the number of rules used to approximate the model
    score : float
        the validation score of the approximation
    project_id : str
        the project the approximation belongs to
    parent_model_id : str
        the model being approximated
    model_id : str or None
        the model using this ruleset (if it exists).  Will be None if no such model has been
        trained.

    """

    _converter = t.Dict(
        {
            t.Key("project_id"): String(),
            t.Key("parent_model_id"): String(),
            t.Key("model_id", optional=True): String(),
            t.Key("ruleset_id"): Int(),
            t.Key("rule_count"): Int(),
            t.Key("score"): t.Float(),
        }
    ).allow_extra("*")

    def __init__(
        self,
        project_id=None,
        parent_model_id=None,
        model_id=None,
        ruleset_id=None,
        rule_count=None,
        score=None,
    ):
        self.id = ruleset_id
        self.rule_count = rule_count
        self.score = score
        self.project_id = project_id
        self.parent_model_id = parent_model_id
        self.model_id = model_id

    def __repr__(self):
        return "Ruleset(rule_count={}, score={})".format(self.rule_count, self.score)

    def request_model(self):
        """ Request training for a model using this ruleset

        Training a model using a ruleset is a necessary prerequisite for being able to download
        the code for a ruleset.

        Returns
        -------
        job: Job
            the job fitting the new Prime model
        """
        from . import Job

        if self.model_id:
            raise ValueError("Model already exists for ruleset")
        url = "projects/{}/primeModels/".format(self.project_id)
        data = {"parent_model_id": self.parent_model_id, "ruleset_id": self.id}
        response = self._client.post(url, data=data)
        job_id = get_id_from_response(response)
        return Job.get(self.project_id, job_id)
