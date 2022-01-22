from glapi import configuration
from glapi.connection import GitlabConnection
from glapi.issue import GitlabIssue

class GitlabEpic:
    """
    GitlabEpic is a Gitlab Epic.
    """

    def __init__(self, id: str = None, iid: str = None, epic: dict = None, group_id: str = None, get_notes: bool = False, token :str = configuration.GITLAB_TOKEN, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            id (string): GitLab Epic id
            iid (string): GitLab Epic iid
            epic (dictionary): GitLab Epic
            get_notes (boolean): TRUE if notes should be pulled
            group_id (string): Gitlab Group id
            token (string): GitLab personal access, ci, or deploy token
            version (string): GitLab API version as base url
        """
        self.connection = GitlabConnection(
            token=token,
            version=version
        )
        self.epic = epic if epic else (self.connection.query("groups/%s/epics/%s" % (group_id, iid))["data"] if id and token and version else None)
        self.gitlab_type = "epic"
        self.group_id = self.epic["group_id"] if self.epic else None
        self.id = self.epic["id"] if self.epic else None
        self.iid = self.epic["iid"] if self.epic else None
        self.notes = self.extract_notes() if get_notes else None

    def extract_issues(self, scope: str = "all", date_start: str = None, date_end: str = None) -> list:
        """
        Extract epic-specific issue data.

        Args:
            date_end (string): iso 8601 date value
            date_start (string): iso 8601 date value
            scope (enum): all | assigned_to_me | created_by_me

        Returns:
            A list of GitlabIssue classes where each represents a GtiLab Issue.
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
                endpoint="groups/%s/epics/%s/issues" % (
                    self.group_id,
                    self.iid
                ),
                params=params
            )

            # generate GitlabIssue
            result = [GitlabIssue(issue=d) for d in issues]

        return result

    def extract_notes(self) -> list:
        """
        Extract epic-specific note data (comments).

        Returns:
            A list of dictionaries where each represents a GtiLab Note.
        """

        result = None

        # check connection params
        if self.id and self.connection.token and self.connection.version:

            # query api
            result = self.connection.paginate(
                endpoint="groups/%s/epics/%s/notes" % (
                    self.group_id,
                    self.id
                )
            )

        return result
