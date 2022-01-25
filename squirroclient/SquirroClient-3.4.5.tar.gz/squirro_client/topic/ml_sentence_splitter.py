import logging

log = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Error in executing a machine learning job"""

    pass


class MLSentenceSplitterMixin(object):

    #
    #  ML Sentence Splitter
    #
    def get_sentence_splitters(self, project_id):
        """Return all available Sentence Splitter.

        :param project_id: Id of the Squirro project.
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/ml_sentence_splitter" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)
