from atlassian import Jira as Jira_
from loguru import logger


class Jira(object):
    def __init__(self, username: str, token: str):
        self.username = username
        self.token = token
        self.api_client = Jira_(url='https://zadgroup.atlassian.net',
                                username=username, password=token)

    @logger.catch
    def create_project(self, specs: {str, str, str, str, str, str, str}):
        """
        :param specs:
            {
                "description": "AMKMB",
                "leadAccountId": "557058:2c9c859c-34fb-4119-a88c-5ef8ae3c1d0e",
                "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-simplified-scrum-classic",
                "name": "AMKMB",
                "assigneeType": "PROJECT_LEAD",
                "projectTypeKey": "software",
                "key": "AMKMB"
            }
        :return:
            {'self': 'https://zadgroup.atlassian.net/rest/api/2/project/17689',
             'id': 17689,
             'key': 'AMKMB'}
        """
        return self.api_client.create_project_from_raw_json(specs)

    @logger.catch
    def delete_project(self, key: str):
        """

        :param key: Jira project key e.g IQV
        :return: nothing
        """
        return self.api_client.delete_project(key)

    @logger.catch
    def create_project_from_template(self, project_id: str, key: str,
                                     name: str, lead: str, ):
        """

        :param project_id: Project id to use as a template
        :param key: New project key
        :param name: New project name
        :param lead: New project lead username
        :return: json object specs for newly created project
        """
        return self.api_client.create_project_from_shared_template(project_id, key, lead, name)
