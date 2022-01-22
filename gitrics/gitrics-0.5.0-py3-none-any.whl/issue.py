import networkx as nx

from glapi import configuration
from glapi.issue import GitlabIssue

class gitricsIssue(GitlabIssue):
    """
    gitricsIssue is a Gitlab Issue with opinionated enrichment for the gitrics ecosystem.
    """

    def __init__(self, id: str = None, iid: str = None, issue: dict = None, group_id: str = None, group_graph: nx.DiGraph = None, token: str = configuration.GITLAB_TOKEN, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            id (string): GitLab Issue id
            iid (string): GitLab Issue iid
            group_id (string): Gitlab Group id
            group_graph (DiGraph): networkx directional graph
            issue (dictionary): GitLab Issue
            token (string): GitLab personal access, ci, or deploy token
            version (string): GitLab API version as base url
        """
        self.gitlab_type = "issue"
        self.group_graph = group_graph
        self.ownership = None

        # initialize inheritance
        super(gitricsIssue, self).__init__(
            issue=issue,
            token=token,
            version=version
        )
