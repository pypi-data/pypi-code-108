from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.config import error_messages, routes
from cnvrgv2.utils.api_list_generator import api_list_generator
from cnvrgv2.utils.validators import attributes_validator, validate_gpu
from cnvrgv2.modules.resources.templates.spark_template import SparkTemplate

required_attributes = [
    'title',
    'cpu',
    'memory',
]

default_attributes = {
    "num_executors": 1.0,
    "compute_type": 'spark_driver'
}


class SparkTemplatesClient:
    def __init__(self, context=None):
        self._context = Context(context=context)
        scope = self._context.get_scope(SCOPE.RESOURCE)
        self._proxy = Proxy(context=self._context)
        self._route = routes.TEMPLATES_BASE.format(
            scope["organization"],
            'spark_driver',
            scope['resource']
        )

    def list(self, sort="-id"):
        """
        List all spark driver compute templates in a specific resource
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields spark driver compute template objects
        """
        return api_list_generator(
            context=self._context,
            route=self._route,
            object=SparkTemplate,
            sort=sort,
        )

    def get(self, slug):
        """
        Retrieves a spark driver compute template by the given slug
        @param slug: The slug of the requested spark driver compute template
        @return: Spark driver compute template object
        """
        if not slug or not isinstance(slug, str):
            raise CnvrgArgumentsError(error_messages.TEMPLATE_GET_FAULTY_SLUG)

        return SparkTemplate(context=self._context, slug=slug)

    def create(
        self,
        title,
        cpu,
        memory,
        **kwargs
    ):
        """
        @param title: Name of the new spark compute template
        @param cpu: CPU cores of the new spark compute template
        @param memory: RAM of the new spark compute template
        @param kwargs: A list of optional attributes for creation
            users: Users with accesss to the new spark compute template
            gpu: GPU Cores for the new spark compute template
            gaudi: Gaudi accelerators num for the new spark compute template
            is_private: is the new spark compute template private or public
            num_executors: number of workers for the new spark compute template
            templates_ids: allowed templates for the new spark compute template worker
            mig_device: mig device type for the new spark compute template
        @return: The newly created spark compute template
        """

        formatted_attributes = {
            "title": title,
            "cpu": float(cpu),
            "memory": float(memory),
            **default_attributes,
            **kwargs,
            "gpu": {
                "count": kwargs.get('gpu'),
                "mig_device": kwargs.get('mig_device')
            },
        }

        formatted_attributes.pop('mig_device', None)

        attributes_validator(
            SparkTemplate.available_attributes,
            formatted_attributes,
            required_attributes
        )

        # Specific instance validations
        validate_gpu(formatted_attributes["gpu"])

        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type='spark_template', attributes=formatted_attributes)
        )

        slug = response.attributes['slug']
        return SparkTemplate(
            context=self._context,
            slug=slug,
            attributes=response.attributes
        )
