import json
import logging

log = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Error in executing a machine learning job."""

    pass


class MLUserFeedbackMixin(object):

    #
    #  User Feedback
    #
    def get_feedbacks(
        self,
        project_id,
        user_name=None,
        user_id=None,
        model_id=None,
        groundtruth_id=None,
        label=None,
        extract_query=None,
        item_id=None,
        processed=None,
        exclude_body=True,
        count=100,
        start=0,
    ):
        """Return the user feedbacks for a project in a list.

        :param project_id: Id of the Squirro project
        :param user_name: user_name to filter by
        :param user_id: user_id to filter by
        :param model_id: Id of the Model to filter by
        :param groundtruth_id: Id of the GroundTruth to filter by
        :param label: label to filter GroundTruth by
        :param extract_query: text to filter the feedback extracts by
        :param item_id: item_id to filter by
        :param processed: processed flag to filter by
        :param exclude_body: Exclude body in the return of a document level feedback
        :param count: Max number of feedbacks return per result
        :param start: Zero based starting point
        :return:
        """

        base_url = "{}/v0/{}/projects/{}/feedbacks"
        headers = {"Content-Type": "application/json"}
        data = {
            "user_name": user_name,
            "user_id": user_id,
            "model_id": model_id,
            "groundtruth_id": groundtruth_id,
            "item_id": item_id,
            "label": label,
            "extract_query": extract_query,
            "processed": processed,
            "exclude_body": exclude_body,
            "count": count,
            "start": start,
        }
        url = base_url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request("get", url, headers=headers, params=data)
        return self._process_response(res)

    def get_feedback(self, project_id, feedback_id):
        """Get a single User Feedback.

        :param project_id: Id of the Squirro project.
        :param feedback_id: Id of the User Feedback
        """
        base_url = "{}/v0/{}/projects/{}/feedbacks/{}"
        headers = {"Content-Type": "application/json"}

        url = base_url.format(self.topic_api_url, self.tenant, project_id, feedback_id)
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def new_feedback(
        self,
        project_id,
        feedback,
        action,
        suggested_label=None,
        suggested_model_id=None,
    ):
        """Create a new User Feedback.

        :param project_id: Id of the Squirro project.
        :param feedback: Dictionary of the feedback element
        :param action: Dictionary of the user assessment
        :param suggested_label: Suggested label for the feedback element
        :param suggested_model_id: Model identifier of the suggested label
        :return:
        """

        base_url = "{}/v0/{}/projects/{}/feedbacks"
        headers = {"Content-Type": "application/json"}

        url = base_url.format(self.topic_api_url, self.tenant, project_id)

        feedback_params = {
            "feedback": feedback,
            "action": action,
            "suggested_label": suggested_label,
            "suggested_model_id": suggested_model_id,
        }

        res = self._perform_request(
            "post", url, data=json.dumps(feedback_params), headers=headers
        )
        return self._process_response(res, [201])

    def modify_feedback(
        self,
        project_id,
        feedback_id,
        action=None,
        suggested_label=None,
        suggested_model_id=None,
        groundtruth_label_id=None,
        selected_label=None,
        processed=None,
        state=None,
    ):
        """Modify an existing User Feedback.

        :param project_id: Id of the Squirro project.
        :param feedback_id: Id of the User Feedback
        :param action: Dictionary of the user assessment
        :param suggested_label: Suggested label for the feedback element
        :param suggested_model_id: Model identifier of the suggested label
        :param groundtruth_label_id: Id of the label that was created from this feedback
        :param selected_label: label tag that was selected from this feedback
        :param processed: Indication flag of a processed feedback
        :param state: State of the feedback element
        :return:
        """

        url = "{}/v0/{}/projects/{}/feedbacks/{}"
        headers = {"Content-Type": "application/json"}

        feedback_update = {
            "action": action,
            "suggested_label": suggested_label,
            "suggested_model_id": suggested_model_id,
            "groundtruth_label_id": groundtruth_label_id,
            "selected_label": selected_label,
            "processed": processed,
            "state": state,
        }

        url = url.format(self.topic_api_url, self.tenant, project_id, feedback_id)
        res = self._perform_request(
            "put", url, data=json.dumps(feedback_update), headers=headers
        )
        return self._process_response(res, [204])

    def delete_feedback(self, project_id, feedback_id):
        """Delete User Feedback.

        :param project_id: Id of the Squirro project.
        :param feedback_id: Id of the User Feedback.
        """
        url = "{}/v0/{}/projects/{}/feedbacks/{}"
        headers = {"Content-Type": "application/json"}

        url = url.format(self.topic_api_url, self.tenant, project_id, feedback_id)
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [204])

    def get_labels_per_model(self, project_id, model_id=None):
        """Get the classification labels of models.

        :param project_id: Id of the Squirro project.
        :param model_id: Id of a Model. If it is not given, then the labels of all the
                         the models in the given project are returned.
        """
        base_url = "{}/v0/{}/projects/{}/feedbacks/labels"
        headers = {"Content-Type": "application/json"}
        params = {"model_id": model_id}

        url = base_url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request("get", url, headers=headers, params=params)
        return self._process_response(res)
