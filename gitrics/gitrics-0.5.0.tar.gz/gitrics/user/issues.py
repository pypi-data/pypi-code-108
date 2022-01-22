from gitrics import configuration
from gitrics.user.issue_merge_request import gitricsUserIssueMergeRequest

class gitricsUserIssues(gitricsUserIssueMergeRequest):
    """
    gitricsUserIssues is a collection of user-specific Gitlab Issue objects modified and enriched for gitrics ecosystem.
    """

    def __init__(self, user_id: str = None, user: dict = None, date_start: str = None, date_end: str = None, token: str = None, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            date_end (string): iso 8601 date value
            date_start (string): iso 8601 date value
            token (string): GitLab personal access or deploy token
            user (dict): key/values representing a Gitlab User
            user_id (string): GitLab User id
            version (string): GitLab API version as base url
        """

        # initialize inheritance
        super(gitricsUserIssues, self).__init__(
            date_end=date_end,
            date_start=date_start,
            token=token,
            type="issue",
            user=user,
            user_id=user_id,
            version=version
        )
