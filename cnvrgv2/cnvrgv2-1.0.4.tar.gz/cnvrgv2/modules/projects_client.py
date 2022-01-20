from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.config import error_messages, routes
from cnvrgv2.utils.api_list_generator import api_list_generator
from cnvrgv2 import cnvrg
from cnvrgv2.modules.project import Project
from cnvrgv2.utils.url_utils import urljoin


class ProjectsClient:
    def __init__(self, organization):
        if type(organization) is not cnvrg.Cnvrg:
            raise CnvrgArgumentsError(error_messages.ARGUMENT_BAD_TYPE.format(cnvrg.Cnvrg, type(organization)))
        self._context = Context(context=organization._context)
        scope = self._context.get_scope(SCOPE.ORGANIZATION)

        self._proxy = Proxy(context=self._context)
        self._route = routes.PROJECTS_BASE.format(scope["organization"])

    def list(self, sort="-id"):
        """
        List all projects in a specific organization
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields project objects
        """
        return api_list_generator(
            context=self._context,
            route=self._route,
            object=Project,
            sort=sort
        )

    def get(self, slug):
        """
        Retrieves a project by the given slug
        @param slug: The slug of the requested project
        @return: Project object
        """
        if not slug or not isinstance(slug, str):
            raise CnvrgArgumentsError(error_messages.PROJECT_GET_FAULTY_SLUG)

        return Project(context=self._context, slug=slug)

    def create(self, name):
        """
        Creates a new project with the given name
        @param name: name of the new project
        @return: the newly created project object
        """
        if not name or not isinstance(name, str):
            raise CnvrgArgumentsError(error_messages.PROJECT_CREATE_FAULTY_NAME)

        attributes = {"title": name}
        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type="project", attributes=attributes)
        )

        slug = response.attributes['slug']
        return Project(context=self._context, slug=slug)

    def delete(self, slugs):
        """
        Deleting multiple projects
        @param slugs: List of workflow slugs to be deleted
        @return: None
        """
        delete_url = urljoin(self._route, routes.PROJECT_BULK_DELETE_SUFFIX)

        attributes = {
            "project_slugs": slugs
        }

        self._proxy.call_api(
            route=delete_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type="Project", attributes=attributes)
        )
