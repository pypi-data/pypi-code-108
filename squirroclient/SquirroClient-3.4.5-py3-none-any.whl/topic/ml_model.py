import json
import logging

log = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Error in executing a machine learning job"""

    pass


class MLModelsMixin(object):

    #
    #  ML Model
    #
    def get_ml_models(self, project_id):
        """Return all ML Models for a project.

        :param project_id: Id of the Squirro project.
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_model" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)["models"]

    def get_ml_model(self, project_id, model_id):
        """Return a single ML Model.

        :param project_id: Id of the Squirro project.
        :param model_id: id of the ML model
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_model/%(model_id)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "model_id": model_id,
        }

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def new_ml_model(
        self,
        project_id,
        name,
        template_id,
        ground_truth_id,
        template_params=None,
        ground_truth_version=None,
        is_incomplete=False,
    ):
        """Create a new ML Model.

        :param project_id: Id of the Squirro project.
        :param name: Name of the ML Model.
        :param template_id: template do be used.
        :param template_params: parameters to initialize the template.
        :param ground_truth_id: id of the grountruth.
        :param ground_truth_version: version of the grountruth if any.
        :param is_incomplete: mark a model as incomplete.
        """

        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_model" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        headers = {"Content-Type": "application/json"}
        # TODO workaround to also allow incomplete models
        model_params = {
            "name": name,
            "template_id": template_id,
            "gt_id": ground_truth_id,
            "template_params": template_params,
            "ground_truth_version": ground_truth_version,
            "token": self.refresh_token,
            "is_incomplete": is_incomplete,
        }

        res = self._perform_request(
            "post", url, data=json.dumps(model_params), headers=headers
        )
        return self._process_response(res, [201])

    def modify_ml_model(
        self,
        project_id,
        model_id,
        name,
        template_id=None,
        template_params=None,
        ground_truth_id=None,
        ground_truth_version=None,
        is_incomplete=None,
    ):
        """Update ML Model

        :param project_id: Id of the Squirro project.
        :param model_id: Id of the Machine Learning workflow.
        :param name: Name of the ML Model.
        :param template_id: template do be used.
        :param template_params: parameters to initialize the template.
        :param ground_truth_id: id of the groundtruth.
        :param ground_truth_version: version of the groundtruth if any
        :param is_incomplete: mark a model as incomplete.
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_model/%(model_id)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "model_id": model_id,
        }
        headers = {"Content-Type": "application/json"}
        # TODO workaround to also allow incomplete models
        model_params = {
            "name": name,
            "template_id": template_id,
            "gt_id": ground_truth_id,
            "template_params": template_params,
            "ground_truth_version": ground_truth_version,
            "token": self.refresh_token,
            "is_incomplete": is_incomplete,
        }
        res = self._perform_request(
            "put", url, data=json.dumps(model_params), headers=headers
        )
        return self._process_response(res, [204])

    def delete_ml_model(self, project_id, model_id):
        """Delete ML Model

        :param project_id: Id of the Squirro project.
        :param model_id: Id of the  ML Model.
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_model/%(model_id)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "model_id": model_id,
        }

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [204])
