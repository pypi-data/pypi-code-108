import datetime

from collections import Counter

import networkx as nx

from glapi.group import GitlabGroup
from glapi.epic import GitlabEpic
from glapi.user import GitlabUser

from gitrics import configuration
from gitrics.epic import gitricsEpic
from gitrics.issue import gitricsIssue

class gitricsItemSet:
    def __init__(self, type: str):
        self.items = None
        self.graph = None
        self.gitlab_type = type

class gitricsGroup(GitlabGroup):
    """
    gitricsGroup is an abstraction of the GitLab Group data object specific to the requirements of the gitrics ecosystem.
    """

    def __init__(self, id: str = None, group: dict = None, epics: gitricsItemSet = None, issues: gitricsItemSet = None, users: list = None, date_start: str = None, date_end: str = None, token: str = configuration.GITLAB_TOKEN, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            date_end (string): iso 8601 date value
            date_start (string): iso 8601 date value
            group (dict): key/values representing a Gitlab Group
            id (string): GitLab Group id
            epics (gitricsItemSet): classes of gitricsEpic
            issues (gitricsItemSet): classes of gitricsIssue
            token (string): GitLab personal access or deploy token
            users (list): dictionaries of GitLab User
            version (string): GitLab API version as base url
        """

        self.date_end = date_end
        self.date_start = date_start

        # initialize inheritance
        super(gitricsGroup, self).__init__(
            group=group,
            id=id,
            token=token,
            version=version
        )

        self.epics = epics if epics else gitricsItemSet("epics")
        self.issues = issues if issues else gitricsItemSet("issues")

        # get users
        self.users = self.extract_users()

    def determine_most_at_risk(self, items: list) -> list:
        """
        Determine which Epics are most at risk based on health status at_risk attributes.

        Args:
            items (list): classes of gitricsEpic

        Returns:
            A list of giticsEpic objects where each represents a GitLab Epic.
        """

        # generate maps of ids to scores
        atriskmap = { k.id: k.score_at_risk for k in items }

        # determine scoring ranks
        return [d for d in items if d.score_at_risk == atriskmap[max(atriskmap, key=atriskmap.get)]]

    def determine_most_on_track(self, items: list) -> list:
        """
        Determine which Epics are most on track based on health status on_track attributes.

        Args:
            items (list): classes of gitricsEpic

        Returns:
            A list of giticsEpic objects where each represents a GitLab Epic.
        """

        # generate maps of ids to scores
        ontrackmap = { k.id: k.score_on_track for k in items }

        # determine scoring ranks
        return [d for d in items if d.score_on_track == ontrackmap[max(ontrackmap, key=ontrackmap.get)]]

    def determine_ownership(self, item) -> list:
        """
        Determine opinionated ownership based on formal assignment via GitLab or highest note (comments) count.

        Args:
            item (enum): gitricsEpic || GitlabIssue

        Returns:
            A list of dictionaries where each is a GitlabUser.
        """

        result = None
        ids = list()
        subitem = getattr(item, item.gitlab_type)

        # check for notes
        if item.notes:

            # assign ownership by participation
            ids = [x[0] for x in Counter(d["author"]["id"] for d in item.notes).most_common(3)]

        # check for assignees
        if "assignees" in subitem and subitem["assignees"]:

            # add as assignees
            ids = [d["id"] for d in subitem["assignees"]]

        # replace ids with full user objects
        result = [d for d in self.users if d.id in ids] if self.users else list()

        return result

    def determine_status(self, item: dict) -> str:
        """
        Determine human-readable opinionated status based on start/end/due dates and state.

        Args:
            item (dictionary): key/value pairs representing a GitLab Epic or Issue

        Returns:
            A string representing a status related to start/end time.
        """

        result = "ongoing"
        now = datetime.datetime.now()

        # opened
        if item["state"] == "opened":

            # ending date
            if "end_date" in item or "due_date" in item:

                # normalize between data types
                edate = item["end_date"] if "end_date" in item else item["due_date"]

                # end/due date in the past
                if edate and datetime.datetime.strptime(edate, configuration.DATE_ISO_8601) < now:
                    result = "past due"

            # starting date
            if "start_date" in item or "due_date" in item:

                # normalize between data types
                sdate = item["start_date"] if "start_date" in item else item["due_date"]

                # start date in the future
                if sdate and datetime.datetime.strptime(sdate, configuration.DATE_ISO_8601) > now:
                    result = "upcoming"

        # closed
        else:
            result = "complete"

        return result

    def determine_top_blockers(self, graph: nx.DiGraph):
        """
        Determine which issues are blocking the most issues inside the group.

        Args:
            graph (DiGraph): networkx directional graph

        Returns:
            A list of gitricsIssue where each represents a GitLab Issue.
        """

        # calculate degree centrality
        degreecentralitymap = nx.degree_centrality(graph)

        # remove root node
        degreecentralitymap.pop(0)

        # get max value
        max_block_centrality = max(degreecentralitymap, key=degreecentralitymap.get)

        # update individual issues with score
        for i in self.issues.items:
            i.score_degree_centrality = degreecentralitymap[i.id] if i.id in degreecentralitymap else 0

        # get any nodes with max value
        # sort by nest level which assumes that nodes with an even score that the higher in the tree the more of a blocker it is
        return sorted([
            d for d in self.issues.items
            if d.score_degree_centrality > 0 and
            degreecentralitymap[d.id] == degreecentralitymap[max_block_centrality]
        ], key=lambda d: nx.descendants(graph, d.id), reverse=True)

    def initialize_epics(self, epics: list) -> list:
        """
        Initialize epics as gitrics objects.

        Args:
            epics (list): dictionaries of GitLab Epic

        Returns:
            A tuple (0, 1) where 0 is a list of gitricsEpic objects where each represents a GitLab Epic and 1 is a networkx directional graph object representing the parent/child relationships in the set of epics.
        """

        graph = None
        items = None

        # build tuples of parent nodes
        parents = [(d.epic["parent_id"], d.id) for d in epics if d.epic["parent_id"]]

        # build tuples of unlinked nodes
        # i.e. direct children of root
        unlinked = [(0, d.id) for d in epics if d.epic["parent_id"] is None]

        # combine into list of links
        links = parents + unlinked

        # generate graph
        if links: graph = nx.DiGraph(links)

        # format result for gitrics
        items = [gitricsEpic(epic=d.epic, group_graph=graph) for d in epics]

        return (items, graph)

    def initialize_issues(self, issues: list = None) -> list:
        """
        Initialize issues as gitrics objects.

        Args:
            issues (list): dictionaries of GitLab Issue

        Returns:
            A list of gitricsIssue objects where each represents a GitLab Issue.
        """

        graph = None
        items = None

        # build blocker tuples
        blockers = [
            x for y in [
                [
                    (d.id, i["id"])
                    for i in d.links
                    if i["link_type"] == "blocks"
                ]
                for d in issues if d.links
            ] for x in y
        ] if issues else list()

        # build tuples of blockers which are unblocked themselves
        # i.e. these nodes are direct children of the root
        unblocked_blockers = [
            (0, d.id) for d in issues
            if d.links and len([i for i in d.links if i["link_type"] == "is_blocked_by"]) == 0 and len([i for i in d.links if i["link_type"] == "blocks"]) > 0
        ] if issues else list()

        # build tuples for complete unlinked issues
        # i.e. nodes are direct children of the root
        unlinked = [(0, d.id) for d in issues if not d.links] if issues else list()

        # combine list
        links = blockers + unblocked_blockers + unlinked

        # generate graph
        if links: graph = nx.DiGraph(links)

        # format result for gitrics
        items = [gitricsIssue(issue=d.issue, group_graph=graph) for d in issues]

        return (items, graph)

    def prune(self, items: list, param: dict) -> list:
        """
        Prune data by provided parameter.

        Args:
            items (list): classes of gitricsEpic or GitlabIssue
            param (dict): key/value pairs where each key is an attribute to filter on and corresponding value is the desired query value

        Returns:
            A list of where each represents a gitricsEpic or GitlabIssue, depending on the input.
        """

        result = items

        # loop through param keys
        for key in param:

            # determine attribute type to filter against
            class_type = "user" if key == "ownership" else None

            # reduce list by value
            subset = [
                d for d in result
                if getattr(d, key) and param[key] in [
                    getattr(x, class_type)["id"]
                    for x in getattr(d, key)
                ]
            ]

            # update result
            result = subset

        return result
