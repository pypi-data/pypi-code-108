from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.config import error_messages, routes
from cnvrgv2.utils.api_list_generator import api_list_generator
from cnvrgv2 import cnvrg

from cnvrgv2.modules.dataset import Dataset


class DatasetsClient:
    def __init__(self, organization):
        if type(organization) is not cnvrg.Cnvrg:
            raise CnvrgArgumentsError(error_messages.ARGUMENT_BAD_TYPE.format(cnvrg.Cnvrg, type(organization)))
        self._context = Context(context=organization._context)
        scope = self._context.get_scope(SCOPE.ORGANIZATION)

        self._proxy = Proxy(context=self._context)
        self._route = routes.DATASETS_BASE.format(scope["organization"])

    def list(self, filter=None, sort="-id"):
        """
        List all datasets in a specific organization
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @param filter: Filter json
        @raise: HttpError
        @return: Generator that yields dataset objects
        """
        # TODO: implement with commit/query and working_dir
        return api_list_generator(
            context=self._context,
            route=self._route,
            object=Dataset,
            sort=sort,
            filter=filter
        )

    def search(self, slug):
        """
        List all datasets where the slug contains the given slug
        @param slug: Substring of the desired dataset's slug
        @raise: HttpError
        @return: Generator that yields dataset objects
        """
        filter_obj = {
            "operator": "AND",
            "conditions": [
                {
                    "key": "slug",
                    "operator": "like",
                    "value": slug
                }
            ]
        }

        return self.list(filter=filter_obj)

    def get(self, slug):
        """
        Retrieves a dataset by the given slug
        @param slug: The slug of the requested dataset
        @return: Dataset object
        """
        if not slug or not isinstance(slug, str):
            raise CnvrgArgumentsError(error_messages.DATASET_GET_FAULTY_SLUG)

        return Dataset(context=self._context, slug=slug)

    def create(self, name, category="general"):
        """
        Creates a new dataset with the given name
        @param name: Name of the new dataset
        @param category: Dataset category [general, images, audio, video, text, tabular]
        @return: The newly created dataset object
        """
        if not name or not isinstance(name, str):
            raise CnvrgArgumentsError(error_messages.DATASET_CREATE_FAULTY_NAME)

        if not category or not isinstance(category, str):
            raise CnvrgArgumentsError(error_messages.DATASET_CREATE_FAULTY_CATEGORY)

        # TODO: move list to const
        if category not in ["general", "images", "audio", "video", "text", "tabular"]:
            raise CnvrgArgumentsError(error_messages.DATASET_CREATE_FAULTY_CATEGORY_VALUE)

        attributes = {
            "title": name,
            "category": category
        }
        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type="dataset", attributes=attributes)
        )

        slug = response.attributes['slug']
        return Dataset(context=self._context, slug=slug)
