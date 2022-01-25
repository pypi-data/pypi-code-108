import json


class ProjectGuideFilesMixin(object):
    def new_guide_file(self, project_id, guide_content):
        """Creates a new Project Guide file.

        :param project_id: ID of the project.
        :param guide_content: Javascript content of the guide file as a
            string. The content is expected to be of type 'str', if guide_content
            of type 'bytes' is passed, we try to decode it using 'utf-8'.
        """
        url = "/".join(
            [
                self.topic_api_url,
                self.version,
                self.tenant,
                "projects",
                project_id,
                "guidefile",
            ]
        )

        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        if isinstance(guide_content, bytes):
            guide_content = guide_content.decode()

        data = {"data": {"guide_content": guide_content}}
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def get_guide_file(self, project_id):
        """Gets the Project Guide file.

        :param project_id: ID of the project.
        """
        url = "/".join(
            [
                self.topic_api_url,
                self.version,
                self.tenant,
                "projects",
                project_id,
                "guidefile",
            ]
        )

        headers = {"Accept": "application/javascript"}
        res = self._perform_request("get", url, headers=headers)
        return {"content": res.content, "headers": res.headers}

    def delete_guide_file(self, project_id):
        """Deletes the Project Guide file.

        :param project_id: ID of the project.
        """
        url = "/".join(
            [
                self.topic_api_url,
                self.version,
                self.tenant,
                "projects",
                project_id,
                "guidefile",
            ]
        )

        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res)

    def update_guide_file(self, project_id, guide_content):
        """Updates the content of Project Guide file.

        :param project_id: ID of the project.
        :param guide_content:  Javascript content of the guide file as a
            string.
        """
        self.new_guide_file(project_id, guide_content)
