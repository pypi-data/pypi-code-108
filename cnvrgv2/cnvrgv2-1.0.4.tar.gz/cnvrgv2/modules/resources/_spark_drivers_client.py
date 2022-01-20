from cnvrgv2.proxy import Proxy
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.config import error_messages, routes
from cnvrgv2.utils.api_list_generator import api_list_generator
from cnvrgv2.modules.resources._spark_driver import SparkDriver


class SparkDriversClient:
    def __init__(self, organization):
        self._context = Context(context=organization._context)
        scope = self._context.get_scope(SCOPE.ORGANIZATION)

        self._proxy = Proxy(context=self._context)
        self._route = routes.SPARK_DRIVERS_BASE.format(scope["organization"])

    def list(self, sort="-id"):
        """
        List all spark drivers in a specific resource
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields project objects
        """
        return api_list_generator(
            context=self._context,
            route=self._route,
            object=SparkDriver,
            sort=sort
        )

    def get(self, slug):
        """
        Retrieves a spark driver by the given slug
        @param slug: The slug of the requested spark driver
        @return: Spark driver object
        """
        if not slug or not isinstance(slug, str):
            raise CnvrgArgumentsError(error_messages.SPARK_DRIVER_GET_FAULTY_SLUG)

        return SparkDriver(context=self._context, slug=slug)

    # TODO: Add create function
