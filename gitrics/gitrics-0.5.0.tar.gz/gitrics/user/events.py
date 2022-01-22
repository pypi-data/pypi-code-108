from gitrics import configuration

from glapi.user import GitlabUser

class gitricsUserEvents(GitlabUser):
    """
    gitricsUserEvents is a collection of user-specific Gitlab Event objects modified and enriched for gitrics ecosystem.
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
        super(gitricsUserEvents, self).__init__(
            id=user_id,
            token=token,
            user=user,
            version=version
        )

        # get action types from config
        action_types = [item for sublist in [[x for x in configuration.ACTIVITY_TYPES[d]] for d in configuration.ACTIVITY_TYPES] for item in sublist]

        # get events
        self.events = self.extract_events(
            actions=action_types,
            date_end=date_end,
            date_start=date_start
        )

    def prune(self, events: list, project_ids: list = list()) -> list:
        """
        Prune events.

        Args:
            events (list): dictionaries where each is a Gitlab Event
            project_ids (list): integers where each is a Gitlab Project id

        Returns:
            A list of dictionaries where each represents a Gitlab Event object.
        """

        result = list()

        # filter for specific projects
        result = [d for d in events if d["project_id"] in project_ids]

        return result
