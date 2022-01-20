from cnvrgv2.modules.images.image import Image
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.context import Context
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.config import error_messages, routes
from cnvrgv2.utils.api_list_generator import api_list_generator
from cnvrgv2.utils.url_utils import urljoin


class WorkflowsBase:
    def __init__(self, object, type, context=None):
        """
        Base class for all kind of workflows
        @param object: The current workflow object type
        @param type: String represents the resource type to be created
        @param context: The context object
        """
        self._object = object
        self._type = type
        self._context = Context(context=context)
        self._proxy = Proxy(context=self._context)

    def list(self, sort="-id"):
        """
        List all workflows of a specific type in a specific organization
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields project objects
        """
        return api_list_generator(
            context=self._context,
            route=urljoin(self._route, routes.WORKFLOW_LIST_TYPE_SUFFIX.format(self._type)),
            object=self._object,
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

        return self._object(context=self._context, slug=slug)

    def create(self, title, templates, *args, **kwargs):
        """
        Creates a new workflow
        @param title: Name of the workflow
        @param templates: List of template names to be used
        @param args: optional arguments
        @param kwargs: Dictionary. Rest of optional attributes for creation
            image: Image object to create workflow with
            queue: Name of the queue to run this job on
        @return: The newly created workflow object
        """

        if isinstance(kwargs.get("image"), Image):
            kwargs["image_slug"] = kwargs.get("image").slug
            del kwargs["image"]

        if kwargs.get("queue", False):
            kwargs["queue_name"] = kwargs.get("queue", False)
            del kwargs["queue"]

        attributes = {
            "title": title,
            "template_names": templates,
            **kwargs
        }

        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

        slug = response.attributes['slug']
        return self._object(context=self._context, slug=slug)

    def delete(self, slugs):
        """
        Deleting multiple workflows
        @param slugs: List of workflow slugs to be deleted
        @return: None
        """
        delete_url = urljoin(self._route)

        attributes = {
            "workflow_slugs": slugs
        }

        self._proxy.call_api(
            route=delete_url,
            http_method=HTTP.DELETE,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

    def stop(self, slugs, sync=False):
        """
        Stopping multiple workflows
        @param slugs: List of workflow slugs to be stopped
        @param sync: Sync workflow before stopping. Default: false
        @return: None
        """
        stop_url = urljoin(self._route, routes.WORKFLOW_STOP_SUFFIX)

        attributes = {
            "workflow_slugs": slugs,
            "sync": sync
        }

        self._proxy.call_api(
            route=stop_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )

    def sync_remote(self, slugs, commit_msg=None):
        """
        Syncing multiple workflows
        @param slugs: List of workflow slugs to be synced
        @param commit_msg: Commit message to add
        @return: None
        """
        sync_url = urljoin(self._route, routes.WORKFLOW_SYNC_SUFFIX)

        attributes = {
            "workflow_slugs": slugs
        }

        if commit_msg:
            attributes["commit_msg"] = commit_msg

        self._proxy.call_api(
            route=sync_url,
            http_method=HTTP.POST,
            payload=JAF.serialize(type=self._type, attributes=attributes)
        )
