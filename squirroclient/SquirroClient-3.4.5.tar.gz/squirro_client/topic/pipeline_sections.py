import json


class PipelineSectionsMixin:
    def get_pipeline_sections(self, project_id, omit_steps=False):
        """Return all the pipeline sections for project with `project_id`.

        :param project_id: the Id of the project
        :param bool omit_steps: whether to omit the inclusion of steps of every section
        :return: a list of pipeline section dictionaries
        """
        headers = {"Content-Type": "application/json"}

        url = "%(ep)s/v0/%(tenant)s/projects/%(project_id)s/pipeline_sections" % {
            "ep": self.topic_api_url,
            "tenant": self.tenant,
            "project_id": project_id,
        }

        data_dict = dict(omit_steps=omit_steps)

        res = self._perform_request(
            "get", url, data=json.dumps(data_dict), headers=headers
        )

        return self._process_response(res)
