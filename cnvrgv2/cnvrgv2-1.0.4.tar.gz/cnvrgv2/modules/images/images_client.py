from cnvrgv2.modules.images.image import Image
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.config import error_messages, routes
from cnvrgv2.utils.api_list_generator import api_list_generator
from cnvrgv2.utils.url_utils import urljoin


class ImagesClient:
    def __init__(self, organization):
        self._context = Context(context=organization._context)
        scope = self._context.get_scope(SCOPE.ORGANIZATION)

        self._proxy = Proxy(context=self._context)
        self._route = routes.IMAGES_BASE.format(scope["organization"])

    def list(self, sort="-id"):
        """
        List all images in a specific organization
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields image objects
        """
        return api_list_generator(
            context=self._context,
            route=self._route,
            object=Image,
            sort=sort
        )

    def get(self, slug=None, name=None, tag=None):
        """
        Retrieves an Image by the given slug, or name and tag
        @param slug: The slug of the requested image
        @return: Image object
        """

        if slug and isinstance(slug, str):
            return Image(context=self._context, slug=slug)
        elif not slug and (name and tag):
            get_image_by_name_url = urljoin(self._route, routes.GET_BY_NAME_SUFFIX)

            attributes = {
                "image_name": name,
                "image_tag": tag
            }

            res_attributes = self._proxy.call_api(
                route=get_image_by_name_url,
                http_method=HTTP.GET,
                payload=attributes
            ).attributes

            return Image(context=self._context, slug=res_attributes['slug'], attributes=res_attributes)
        else:
            raise CnvrgArgumentsError(error_messages.IMAGE_GET_FAULTY_PARAMS)
