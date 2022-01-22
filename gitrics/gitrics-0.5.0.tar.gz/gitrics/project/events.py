import time

from gitrics import configuration

from glapi.project import GitlabProject

class gitricsProjectEvents(GitlabProject):
    """
    gitricsProjectEvents is a collection of Gitlab Project Events modified and enriched for gitrics ecosystem.
    """

    def __init__(self, project_id: str = None, project: dict = None, date_start: str = None, date_end: str = None, event_actions: list = None, token: str = None, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            date_end (string): iso 8601 date value
            date_start (string): iso 8601 date value
            project (dictionary): key/value pair representing a GitLab Project
            project_id (string): GitLab Project id
            token (string): GitLab personal access or deploy token
            version (string): GitLab API version as base url
        """

        # initialize inheritance
        super(gitricsProjectEvents, self).__init__(
            id=project_id,
            project=project,
            token=token,
            version=version
        )

        # superficial delay for api constraints
        #time.sleep(2)

        # get events
        self.events = self.extract_events(
            actions=event_actions if event_actions else list(),
            date_end=date_end,
            date_start=date_start
        )
