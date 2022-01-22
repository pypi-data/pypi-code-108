from gitrics import configuration

from glapi.group import GitlabGroup
from glapi.user import GitlabUser

class gitricsGroupUsers(GitlabGroup):
    """
    gitricsGroupUsers is a collection of Gitlab Group Users modified and enriched for gitrics ecosystem.
    """

    def __init__(self, group_id: str = None, group: dict = None, users: list = None, token: str = configuration.GITLAB_TOKEN, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            group (dictionary): key/value pair representing a GitLab Group
            group_id (string): GitLab Group id
            token (string): GitLab personal access, ci, or deploy token
            users (list): dictionaries of GitLab User
            version (string): GitLab API version as base url
        """
        self.gitrics_type = "users"

        # initialize inheritance
        super(gitricsGroupUsers, self).__init__(
            group=group,
            id=group_id,
            token=token,
            version=version
        )

        # get users
        if users:
            self.users = [GitlabUser(user=d) for d in users]
        else:
            # try to get from api
            data = self.extract_users()

            # format result
            self.users = [GitlabUser(user=d.user) for d in data] if data else None
