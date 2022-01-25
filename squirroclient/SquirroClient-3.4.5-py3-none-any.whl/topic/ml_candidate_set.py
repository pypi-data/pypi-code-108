import json
import logging

log = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Error in executing a machine learning job"""

    pass


class MLCandidateSetMixin(object):

    #
    #  ML Candidate Set (CS)
    #
    def get_candidate_sets(self, project_id):
        """Return all Candidate Sets for a project.

        :param project_id: Id of the Squirro project.
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/candidate_set" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_candidate_set(self, project_id, candidate_set_id):
        """Return single Candidate Set.

        :param project_id: Id of the Squirro project.
        :param candidate_set_id: id of the candidate set.
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/candidate_set/%(cs_id)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "cs_id": candidate_set_id,
        }
        headers = {"Content-Type": "application/json"}

        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def new_candidate_set(self, project_id, name, query):
        """Create a new Candidate Set.

        :param project_id: Id of the Squirro project.
        :param name: Name of the Candidate Set.
        :param query: Candidate Set Query.

        """

        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/candidate_set" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }
        headers = {"Content-Type": "application/json"}
        cs_params = {"name": name, "query": query}

        res = self._perform_request(
            "post", url, data=json.dumps(cs_params), headers=headers
        )
        return self._process_response(res, [201])

    def modify_candidate_set(self, project_id, candidate_set_id, name, query=None):
        """Modify an existing Candidate Set.

        :param project_id: Id of the Squirro project.
        :param candidate_set_id: Id of the Candidate Set.
        :param name: Name of Candidate Set.
        :param query: candidate set query to be sobstitute.
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/candidate_set/%(cs_id)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "cs_id": candidate_set_id,
        }
        headers = {"Content-Type": "application/json"}
        if not query:
            query - "*"

        cs_update = {}

        # Compose ml_workflow object
        cs_update["name"] = name
        cs_update["query"] = query

        res = self._perform_request(
            "put", url, data=json.dumps(cs_update), headers=headers
        )
        return self._process_response(res, [204])

    def delete_candidate_set(self, project_id, candidate_set_id):
        """Delete Candidate Set

        :param project_id: Id of the Squirro project.
        :param candidate_set_id: Id of the Candidate Set.
        """
        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/candidate_set/%(cs_id)s" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
            "cs_id": candidate_set_id,
        }
        headers = {"Content-Type": "application/json"}
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [204])
