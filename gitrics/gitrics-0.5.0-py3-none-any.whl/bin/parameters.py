import os

from gitrics import configuration

def param_accent_color(parser):
    """
    Add accent color parameter.
    """

    parser.add_argument("--accent-color",
        type=str,
        help="Valid CSS color value (hex, rgb, core css color name, hsl, --var)."
    )

def param_access(parser):
    """
    Add access parameter.
    """

    parser.add_argument("--access",
        type=int,
        default=configuration.USER_ACCESS,
        help="Minimum user access when querying for projects (30 = developer, 40 = maintainer, 50 = owner)."
    )

def param_api(parser):
    """
    Add api parameter.
    """

    parser.add_argument("--api",
        type=str,
        default=configuration.GITLAB_API_VERSION,
        help="GitLab instance-specific API version in the form of a base URL."
    )

def param_date_end(parser):
    """
    Add date-end parameter.
    """

    parser.add_argument("--date-end",
        type=str,
        default=configuration.DATE_END,
        help="ISO 8601 date value."
    )

def param_date_start(parser):
    """
    Add date-start parameter.
    """

    parser.add_argument("--date-start",
        type=str,
        default=configuration.DATE_START,
        help="ISO 8601 date value."
    )

def param_filter_group_namespaces(parser):
    """
    Add filter-group-namespaces parameter.
    """

    parser.add_argument("--filter-group-namespaces",
        type=str,
        default=configuration.FILTER_GROUP_NAMESPACES,
        help="Comma-delimited Gitlab Group namespaces."
    )

def param_filter_project_ids(parser):
    """
    Add filter-project-ids parameter.
    """

    parser.add_argument("--filter-project-ids",
        type=str,
        default=configuration.FILTER_PROJECT_IDS,
        help="Comma-delimited Gitlab Project ids."
    )

def param_filter_project_names(parser):
    """
    Add filter-project-names parameter.
    """

    parser.add_argument("--filter-project-names",
        type=str,
        default=configuration.FILTER_PROJECT_NAMES,
        help="Comma-delimited Gitlab Project names."
    )

def param_filter_project_names_starts_with(parser):
    """
    Add filter-project-names-starts-with parameter.
    """

    parser.add_argument("--filter-project-names-startswith",
        type=str,
        default=configuration.FILTER_PROJECT_NAMES_STARTSWITH,
        help="Comma-delimited Gitlab Project name prefixes."
    )

def param_gitlab_name(parser):
    """
    Add gitlab-name parameter.
    """

    parser.add_argument("--gitlab-name",
        type=str,
        default=configuration.GITLAB_NAME,
        help="Label for GitLab instance."
    )

def param_gitlab_url(parser):
    """
    Add gitlab-url parameter.
    """

    parser.add_argument("--gitlab-url",
        type=str,
        default=configuration.GITLAB_URL,
        help="GitLab instance url."
    )

def param_gitrics_user(parser):
    """
    Add gitrics-user parameter.
    """

    parser.add_argument("--gitrics-user",
        type=str,
        default=configuration.FILEPATH_GITRICS_USER,
        help="gitrics-user metadata file path."
    )

def param_group(parser):
    """
    Add group parameter.
    """

    parser.add_argument("--group",
        type=str,
        help="GitLab Group id."
    )

def param_member_only(parser):
    """
    Add member-only parameter.
    """

    parser.add_argument("--member-only",
        action="store_true",
        default=configuration.MEMBERSHIP,
        help="Only query for projects user is a member of."
    )

def param_personal_only(parser):
    """
    Add personal-only parameter.
    """

    parser.add_argument("--personal-only",
        action="store_true",
        default=configuration.PERSONAL,
        help="Only query for personal projects (i.e. those in the user namepsace)."
    )

def param_return_data(parser):
    """
    Add return-data parameter.
    """

    parser.add_argument("--return-data",
        action="store_true",
        default=False,
        help="Whether or not to return user data object."
    )

def param_simple(parser):
    """
    Add simple parameter.
    """

    parser.add_argument("--simple",
        action="store_true",
        default=configuration.SIMPLE,
        help="Whether or not to query Gitlab for simplified data from endpoints. The same number of records are returned with smaller key/value footprints."
    )

def param_token(parser):
    """
    Add token parameter.
    """

    parser.add_argument("--token",
        type=str,
        default=configuration.GITLAB_TOKEN,
        help="GitLab Personal Access Token or Deploy Token to authenticate API requests."
    )

def param_user(parser):
    """
    Add user parameter.
    """

    parser.add_argument("--user",
        type=str,
        required=True,
        help="GitLab user id."
    )

def param_visibility(parser):
    """
    Add visibility parameter.
    """

    parser.add_argument("--visibility",
        type=str,
        default=configuration.VISIBILITY,
        help="What visibility level (internal, public, private) to query for from Gitlab."
    )
