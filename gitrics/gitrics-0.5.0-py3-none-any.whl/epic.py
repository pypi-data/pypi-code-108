import networkx as nx

from glapi import configuration
from glapi.epic import GitlabEpic

class gitricsEpic(GitlabEpic):
    """
    gitricsEpic is a Gitlab Epic with opinionated enrichment for the gitrics ecosystem.
    """

    def __init__(self, id: str = None, iid: str = None, epic: dict = None, group_id: str = None, group_graph: nx.DiGraph = None, token: str = configuration.GITLAB_TOKEN, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            id (string): GitLab Epic id
            iid (string): GitLab Epic iid
            epic (dictionary): GitLab Epic
            group_graph (DiGraph): networkx directional graph
            group_id (string): Gitlab Group id
            token (string): GitLab personal access, ci, or deploy token
            version (string): GitLab API version as base url
        """
        self.gitlab_type = "epic"
        self.group_graph = group_graph
        self.issues = None
        self.count_at_risk = 0
        self.count_on_track = 0
        self.ownership = None
        self.percent_complete = 0
        self.score_at_risk = 0
        self.score_on_track = 0

        # initialize inheritance
        super(gitricsEpic, self).__init__(
            epic=epic,
            group_id=group_id,
            iid=iid,
            token=token,
            version=version
        )

    def calculate_completion(self, epics: list, issues: list = None) -> int:
        """
        Calculate completion based on closed/opened issues and epics.

        Args:
            epics (list): gitricsEpic classes where each represents a GitLab Epic
            list (list): gitricsIssue classes where each represents a GitLab Issue

        Returns:
            An integer of a percent representation as a whole number.
        """

        result = 0

        # calculate subepics
        epics_total = len(epics)
        epics_closed = len([d for d in epics if d.epic["state"] == "closed"])

        # calculate issues
        issues = issues if issues else self.extract_issues()

        # update self since we have to pull issues anyway
        self.issues = issues

        issues_total = len(issues) if issues else 0
        issues_closed = len([d for d in issues if d.issue["state"] == "closed"]) if issues else 0

        # combine epic/issue totals
        total = epics_total + issues_total
        total_closed = epics_closed + issues_closed

        # get percent as decimal
        dec = total_closed / total if total != 0 else None

        # round to nearest int
        if dec: result = int(round(dec * 100))

        return result
