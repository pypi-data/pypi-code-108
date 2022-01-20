import time

from gitrics import configuration

from glapi.user import GitlabUser

def convert_topics_to_percent(projects: list) -> list:
    """
    Convert topic list to percent format similar to default GitLab Language objects.

    Args:
        projects (list): dictionaries where each represents a GitLab Project

    Returns:
        A list of dictionaries where each represents a GitLab Project.
    """

    # loop through projects
    for project in projects:

        # capture topic object
        topics_list = project["topics"]

        # put topics in same percent format as languages
        project["topics"] = dict()

        # loop through topics
        for topic in topics_list:

            # convert counts to percent
            project["topics"][topic] = (1 / len(topics_list)) * 100

    return projects

class gitricsUserProjects(GitlabUser):
    """
    gitricsUserProjects is a collection of user-specific Gitlab Project objects modified and enriched for gitrics ecosystem.
    """

    def __init__(self, user_id: str = None, user: dict = None, access: int = configuration.USER_ACCESS, simple: bool = configuration.SIMPLE, visibility: str = configuration.VISIBILITY, membership: bool = configuration.MEMBERSHIP, personal: bool = configuration.PERSONAL, token: str = None, version: str = configuration.GITLAB_API_VERSION):
        """
        Args:
            access (integer): minimum access level of a user on a given project
            membership (boolean): TRUE if api should query specific to the user ttached to the access token
            personal (boolean): TRUE if api should return namespace (personal) user projects only
            simple (boolean): TRUE if api return should be minimal
            token (string): GitLab personal access or deploy token
            user (dict): key/values representing a Gitlab User
            user_id (string): GitLab User id
            version (string): GitLab API version as base url
            visibility (enum): internal | private | public
        """

        # initialize inheritance
        super(gitricsUserProjects, self).__init__(
            id=user_id,
            token=token,
            user=user,
            version=version
        )

        # get projects
        self.projects = self.extract_projects(
            access=access,
            membership=membership,
            personal=personal,
            simple=simple,
            visibility=visibility
        )

    def bin(self, bin: str, simple: bool = configuration.SIMPLE, visibility: str = configuration.VISIBILITY, membership: bool = configuration.MEMBERSHIP, personal: bool = configuration.PERSONAL) -> dict:
        """
        Organize projects by membership access level.

        Args:
            bin (enum): access |
            membership (boolean): TRUE if api should query specific to the user ttached to the access token
            personal (boolean): TRUE if api should return namespace (personal) user projects only
            simple (boolean): TRUE if api return should be minimal
            visibility (enum): internal | private | public

        Returns:
            A dictionary where keys are the bin label and corresponding values are lists of dictionaries where each is a Gitlab project which fits the bin criteria.
        """

        result = dict()

        if bin == "access":

            # determine maximum access level
            max_level = int(max(configuration.USER_ACCESS_LEVELS.keys()) / 10)
            min_level = int(min(configuration.USER_ACCESS_LEVELS.keys()) / 10)

            result = dict()
            tracked = list()

            # determine what order to extract projects in
            # based on how gitlab exposes user access level
            # we have to loop through different queries to assemble by user access
            for digit in reversed(range(min_level, max_level + 1)):

                filtered = list()
                level = digit * 10

                # get projects user is a member of
                api_results = self.extract_projects(
                    access=level,
                    membership=membership,
                    personal=personal,
                    simple=simple,
                    visibility=visibility
                )

                # skip maximum level since all those project are valid to that access level
                if digit != max_level:

                    # remove projects of higher levels
                    filtered = [d for d in api_results if d["id"] not in tracked]

                # add ids to track
                for d in api_results:
                    if d["id"] not in tracked:
                        tracked.append(d["id"])

                # set value in map
                result[configuration.USER_ACCESS_LEVELS[level]] = api_results if digit == max_level else filtered

        return result

    def enrich(self, projects: list) -> list:
        """
        Enrich projects with foci, languages, and topics.

        Args:
            projects (list): dictionaries of GitLab Project

        Returns:
            A list of dictionaries where each represents an enriched GitLab Project.
        """

        # add languages
        projects = self.enrich_languages(projects)

        # add topics
        projects = self.enrich_topics(projects)

        # add members
        projects = self.enrich_membership(projects)

        # add foci
        projects = self.enrich_foci(projects)

        # add effort
        projects = self.enrich_effort(projects)

        # try to assign effort name if a known effort name shows up in topic list
        projects = self.extract_effort(projects)

        # clean up topics to remove effort and foci keys
        projects = self.prune_topics(projects)

        # conver topic counts to percents
        return convert_topics_to_percent(projects)

    def enrich_effort(self, projects: list) -> list:
        """
        Enrich projects with effort.

        Args:
            projects (list): dictionaries of GitLab Project

        Returns:
            A list of dictionaries where each represents an enriched GitLab Project.
        """

        result = list()

        for project in projects:

            # determine effort based on namespace
            effort = [d for d in project["path_with_namespace"].split("/")[0:-1] if d in project["name"]]

            p = project

            # add more data to new object
            p["effort"] = effort[0] if len(effort) > 0 else project["name"]

            # add to result
            result.append(p)

        return result

    def enrich_foci(self, projects: list) -> list:
        """
        Enrich projects with foci.

        Args:
            projects (list): dictionaries of GitLab Project

        Returns:
            A list of dictionaries where each represents an enriched GitLab Project.
        """

        result = list()

        for project in projects:

            p = project

            # add more data to new object
            p["foci"] = [configuration.FOCI_TERMS[d.lower()] for d in project["topics"] if d.lower() in configuration.FOCI_TERMS] if configuration.FOCI_TERMS else list()

            # add to result
            result.append(p)

        return result

    def enrich_languages(self, projects: list) -> list:
        """
        Enrich projects with languages.

        Args:
            projects (list): dictionaries of GitLab Project

        Returns:
            A list of dictionaries where each represents an enriched GitLab Project.
        """

        result = list()

        for project in projects:

            # pull languages from api
            languages = self.connection.query("projects/%s/languages" % project["id"])["data"]

            # artifical delay for api constraints
            #time.sleep(2)

            p = project

            # add more data to new object
            p["languages"] = languages

            # add to result
            result.append(p)

        return result

    def enrich_topics(self, projects: list) -> list:
        """
        Enrich projects with topics.

        Args:
            projects (list): dictionaries of GitLab Project

        Returns:
            A list of dictionaries where each represents an enriched GitLab Project.
        """

        result = list()

        for project in projects:

            # get list of languages
            languages = [d.lower() for d in project["languages"]]

            # get topics and filter out languages from topics
            topics = [d.lower() for d in project["tag_list"] if d.lower() not in languages]

            p = project

            # add more data to new object
            p["topics"] = topics

            # add to result
            result.append(p)

        return result

    def enrich_membership(self, projects: list) -> list:
        """
        Determine membership for a collection of GitLab Projects.

        Args:
            projects (list): dictionaries where each is a GitLab Project

        Returns:
            A list of dictionaries where each represents a GitLab project.
        """

        result = list()

        # loop through project ids list
        for project in projects:

            p = project

            # add more data to new object
            p["members"] = self.connection.paginate("projects/%s/members/all" % project["id"])

            # superficial delay for api constraints
            #time.sleep(2)

            # add to result
            result.append(p)

        return result

    def extract_effort(self, projects: list) -> list:
        """
        Set effort name when known effort is found in topics.

        Args:
            projects (list): dictionaries where each represent a GitLab Project

        Returns:
            A dictionary of key/value paris representing efforts.
        """

        # get effort names
        effort_names = [d["effort"].lower() for d in projects]

        # loop through projects
        for project in projects:

            # when the effort names matches the project name
            # it has been determined to be a one-off project
            # if the topic list has an existing effort name
            # this project could belong to an effort but exists in a group which isn't named for the effort
            if project["effort"] == project["name"]:

                # loop through effort names
                for effort_name in effort_names:

                    # loop through topics
                    for topic in project["topics"]:

                        # topic matches an effort
                        if topic.lower() == effort_name:

                            # update project effort
                            project["effort"] = effort_name

        return projects

    def prune(self, projects: list, filter_for_events: list = None, filter_project_ids: list = configuration.FILTER_PROJECT_IDS, filter_project_names: list = configuration.FILTER_PROJECT_NAMES, filter_project_names_startswith: list = configuration.FILTER_PROJECT_NAMES_STARTSWITH, filter_group_namespaces: list = configuration.FILTER_GROUP_NAMESPACES) -> list:
        """
        Prune projects.

        Args:
            filter_for_events (list): integers where each is a Gitlab project id with events
            filter_group_namespaces (list): strings where each is a Gitlab Group full namespace
            filter_project_ids (list): integers where each is a Gitlab Project id
            filter_project_names (list): strings where each is a Gitlab Project name
            filter_project_names_startswith (list): strings where each is a prefix of a Gitlab Project name
            projects (list): dictionaries where each is a Gitlab Project

        Returns:
            A list of dictionaries where each represents a Gitlab project.
        """

        # filter by explicit id
        result = [d for d in projects if d["id"] not in filter_project_ids]

        # filter by explicit name
        result = [d for d in result if d["name"] not in filter_project_names]

        # loop through project name prefixes
        for prefix in filter_project_names_startswith:

            # filter by name starts with
            result = [d for d in result if not d["name"].startswith(prefix)]

        # loop through group namespaces
        for namespace in filter_group_namespaces:

            # loop through group name spaces
            result = [d for d in result if namespace not in  d["path_with_namespace"]]

        # filter for projects with events
        if filter_for_events:
            result = [d for d in result if d["id"] in filter_for_events]

        return result

    def prune_topics(self, projects: list) -> list:
        """
        Remove efforts and foci from topics.

        Args:
            projects (list): dictionaries where each represents a GitLab Project

        Returns:
            A list of dictionaries where each represent a GitLab Project.
        """

        # get effort names
        effort_names = [d["effort"].lower() for d in projects]

        # loop through projects
        for project in projects:

            # loop through topics
            for topic in project["topics"]:

                # remove effort name from topics
                project["topics"] = [d for d in project["topics"] if d.lower() not in effort_names]

                # remove foci from topics
                project["topics"] = [d for d in project["topics"] if d.lower() not in list(configuration.FOCI_TERMS.keys())] if configuration.FOCI_TERMS else list()

        return projects
