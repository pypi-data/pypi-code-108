from gitrics import configuration

from glapi.user import GitlabUser

class gitricsUserIssueMergeRequest(GitlabUser):
    """
    gitricsUserIssueMergeRequest is an abstraction of the GitLab Issue and GitLab Merge Request data objects specific to the requirements of the gitrics ecosystem.
    """

    def __init__(self, type: str, user_id: str = None, user: dict = None, date_start: str = None, date_end: str = None, token: str = None, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            date_end (string): iso 8601 date value
            date_start (string): iso 8601 date value
            token (string): GitLab personal access or deploy token
            type (enum): issue | merge_request
            user (dict): key/values representing a Gitlab User
            user_id (string): GitLab User id
            version (string): GitLab API version as base url
        """

        self.assigned_to_user = None
        self.created_by_user = None
        self.items = None

        # initialize inheritance
        super(gitricsUserIssueMergeRequest, self).__init__(
            id=user_id,
            token=token,
            user=user,
            version=version
        )

        # get items
        self.created_by_user = self.extract_merge_requests(
            date_end=date_end,
            date_start=date_start,
            scope="created_by_me"
        ) if type == "merge_request" else self.extract_issues(
            date_end=date_end,
            date_start=date_start,
            scope="created_by_me"
        )
        self.created_by_user = self.created_by_user if self.created_by_user else list()

        # get items
        self.assigned_to_user = self.extract_merge_requests(
            date_end=date_end,
            date_start=date_start,
            scope="assigned_to_me"
        ) if type == "merge_request" else self.extract_issues(
            date_end=date_end,
            date_start=date_start,
            scope="assigned_to_me"
        )
        self.assigned_to_user = self.assigned_to_user if self.assigned_to_user else list()

        # update self
        self.items = self.created_by_user + self.assigned_to_user

    def format(self, items: list) -> dict:
        """
        Generate key/value map for user id to correlated user objects to represent connected GitLab Users.

        Args:
            items (list): dictionaries where each is a GitLab MergeRequest or Issue

        Returns:
            A dictionary where each key is a user id representing an issue author or assignee the core user has interaction with and the corresponding values are the count of connections and the GitLab User object for the connected user id.
        """

        result = dict()

        # check for items
        if items:

            # loop through GitLab objects
            for item in items:

                # pull current ids
                assignee_id = item["assignee"]["id"] if item["assignee"] else None
                author_id = item["author"]["id"] if item["author"] else None

                # if there is an assignee and it's not the core user
                if assignee_id and hasattr(self, "user") and assignee_id != self.user["id"]:

                    # check for existing key
                    if assignee_id not in result:

                        # add key
                        result[assignee_id] = {
                            "count": 0,
                            "user": item["assignee"]
                        }

                    # iterate count
                    result[assignee_id]["count"] += 1

                # if there is an author and it's not the core user
                if author_id and hasattr(self, "user") and author_id != self.user["id"]:

                    # check for existing key
                    if author_id not in result:

                        # add key
                        result[author_id] = {
                            "count": 0,
                            "user": item["author"]
                        }

                    # iterate count
                    result[author_id]["count"] += 1

        return result

    def prune(self, items: list) -> list:
        """
        Prune items which are both created by and assigned to user.

        Args:
            items (list): dictionaries where each is a Gitlab MergeRequest or Issue

        Returns:
            A list of dictionaries where each represents a Gitlab MergeRequest or Issue.
        """

        result = list()

        # check for items
        if items:

            # filter out created by user and assigned to user
            created_filtered = [
                d for d in self.items
                if d["assignee"] and hasattr(self, "user") and d["assignee"]["id"] != self.user["id"]
              ]

            # filter out created by user and assigned to user
            assigned_filtered = [
                d for d in self.items
                if d["author"] and hasattr(self, "user") and d["author"]["id"] != self.user["id"]
            ]

            # update result
            result = created_filtered + assigned_filtered

        return result
