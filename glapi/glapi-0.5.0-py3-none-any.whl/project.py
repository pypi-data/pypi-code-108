from glapi import configuration
from glapi.connection import GitlabConnection
from glapi.issue import GitlabIssue

class GitlabProject:
    """
    GitlabProject is a Gitlab Project.
    """

    def __init__(self, id: str = None, project: dict = None, token :str = configuration.GITLAB_TOKEN, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            id (string): GitLab Project id
            project (dictionary): GitLab Project
            token (string): GitLab personal access or deploy token
            version (string): GitLab API version as base url
        """
        self.connection = GitlabConnection(
            token=token,
            version=version
        )
        self.project = project if project else (self.connection.query("projects/%s" % id)["data"] if id and token and version else None)
        self.id = self.project["id"] if self.project else None

    def extract_events(self, actions: list, date_start: str = None, date_end: str = None) -> dict:
        """
        Extract project-specific event data.

        Args:
            actions (list): enums where each represent an event action type https://docs.gitlab.com/ee/user/index.html#user-contribution-events
            date_end (string): iso 8601 date value
            date_start (string): iso 8601 date value

        Returns:
            A dictionary where keys are event action types and corresponding values are lists of dictionaries where each represents a GitLab Event.
        """

        result = None

        # check for connection ready
        if self.id and self.connection.token and self.connection.version:

            # update result
            result = dict()

            # loop through actions
            for action in actions:

                # get events
                result[action] = self.connection.paginate(
                    endpoint="projects/%s/events" % self.id,
                    params={
                        "action": action,
                        "after": date_start,
                        "before": date_end
                    }
                )

        return result

    def extract_issues(self, scope: str = "all", date_start: str = None, date_end: str = None) -> list:
        """
        Extract project-specific issue data.

        Args:
            date_end (string): iso 8601 date value
            date_start (string): iso 8601 date value
            scope (enum): all | assigned_to_me | created_by_me

        Returns:
            A list of dictionaries where each represents a GtiLab Issue.
        """

        result = None

        # check params
        if date_start or date_end or scope: params = dict()
        if date_end: params["created_before"] = date_end
        if date_start: params["created_after"] = date_start
        if scope: params["scope"] = scope

        # check connection params
        if self.id and self.connection.token and self.connection.version:

            # query api
            issues = self.connection.paginate(
                endpoint="projects/%s/issues" % self.id,
                params=params
            )

            # generate GitlabIssue
            result = [GitlabIssue(issue=d) for d in issues]

        return result
