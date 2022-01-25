import json
import logging

log = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Error in executing a machine learning job"""

    pass


class MLPublishMixin(object):

    #
    #  ML Publish
    #
    def get_ml_published_models(self, project_id):
        """Returns all the publishing model for a given project.

        :param project_id: Id of the Squirro project.
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_publish" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)["pub_items"]

    def get_ml_published_model(self, project_id, publish_id):
        """Returns the details of the a published model.

        :param project_id: Id of the Squirro project.
        :param publish_id: id of the published model.
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_publish/%(publish_id)s"
            % {
                "ep": self.topic_api_url,
                "tenant": self.tenant,
                "project_id": project_id,
                "publish_id": publish_id,
            }
        )
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def ml_publish_model(
        self,
        project_id,
        published_as,
        description,
        model_id=None,
        model_name=None,
        gt_id=None,
        gt_name=None,
        gt_version=None,
        template_id=None,
        template_name=None,
        workflow_id=None,
        workflow_config=None,
        workflow_name=None,
        tagging_level=None,
        labels=None,
        location=None,
        global_id=None,
        orig_project_id=None,
        external_model=False,
    ):
        """Publish new ML Model.

        :param project_id: Id of the Squirro project.
        :param published_as: Name of the published model.
        :param description: Text to be shown describing the model.
        :param model_id: Id of the model to be published.
        :param model_name: Name of ais model.
        :param gt_id: Id of the groundtruth used for the model.
        :param gt_name: Name of the groundtruth used for the model.
        :param gt_version: Version of the groundtruth used for the model.
        :param template_id: Id of the template used for the model.
        :param template_name: Name of the template used for the model.
        :param workflow_id: Id of the workflow of the model to be published.
        :param workflow_config: Workflow config of the model to be published.
        :param workflow_name: Workflow name of the model to be published.
        :param tagging_level: Tagging level of the model to be published.
        :param labels: Labels of the model to be published.
        :param location: Location of the model to be published.
        :param global_id: Global_id of the model to be published.
        :param orig_project_id: Id of the project where it was publish originally.
        :param external_model: Flag to determine if the published model is from external.

        This function can be used in three cases of publishing a model:

        Case 1: Publish an ais model: saves an ais model in the publish database,
                fetches and save the heritage information (model, gt) while creation.
                Use the param ´external_model´=False and the `model-id` of the
                ais model you want to publish.

        Case 2: Publish a model from external directly to the ingestion pipeline by providing the ml workflow.
                Use ´external_model´=True. Populate ´workflow_config´
                and ´workflow_name´ along with the mandatory params.

        Case 3: Import a model published on another cluster. Use external_model=True,
                and provide the heritage information along with its heritage information
                (´model_id´, ´model_name´, ´gt_id´, ´gt_name´, ´gt_version´, ´template_id´, ´template_name´, ´tagging_level´, ´labels´, ´location´, ´global_id´, ´orig_project_id´)
        """

        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_publish" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        headers = {"Content-Type": "application/json"}
        publish_model_params = {
            "model_id": model_id,
            "published_as": published_as,
            "description": description,
            "token": self.refresh_token,
            "external_model": external_model,
            "workflow_id": workflow_id,
            "workflow_config": workflow_config,
            "model_name": model_name,
            "gt_id": gt_id,
            "gt_name": gt_name,
            "gt_version": gt_version,
            "template_id": template_id,
            "template_name": template_name,
            "workflow_name": workflow_name,
            "tagging_level": tagging_level,
            "labels": labels,
            "location": location,
            "global_id": global_id,
            "orig_project_id": orig_project_id,
        }

        res = self._perform_request(
            "post", url, data=json.dumps(publish_model_params), headers=headers
        )
        return self._process_response(res, [201])

    def modify_published_model(
        self, project_id, publish_id, published_as, description,
    ):
        """Update ML Published model

        :param project_id: Id of the Squirro project.
        :param publish_id: id of the published model.
        :param published_as: Name of the published model.
        :param description: Text to be shown describing the model.
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_publish/%(publish_id)s"
            % {
                "ep": self.topic_api_url,
                "tenant": self.tenant,
                "project_id": project_id,
                "publish_id": publish_id,
            }
        )
        headers = {"Content-Type": "application/json"}

        model_params = {
            "published_as": published_as,
            "description": description,
            "token": self.refresh_token,
        }
        res = self._perform_request(
            "put", url, data=json.dumps(model_params), headers=headers
        )
        return self._process_response(res, [204])

    def unpublish_ml_model(self, project_id, publish_id):
        """Delete ML Model

        :param project_id: Id of the Squirro project.
        :param publish_id: Id of the  published Model.
        """
        url = (
            "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_publish/%(publish_id)s"
            % {
                "ep": self.topic_api_url,
                "tenant": self.tenant,
                "project_id": project_id,
                "publish_id": publish_id,
            }
        )

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [204])
