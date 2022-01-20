from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.config import error_messages, routes
from cnvrgv2.utils.api_list_generator import api_list_generator
from cnvrgv2.utils.validators import attributes_validator, validate_gpu, validate_template_type
from cnvrgv2.modules.resources.templates.kube_template import KubeTemplate

required_attributes = [
    'title',
    'parent_cpu',
    'parent_memory',
]


class KubeTemplatesClient:
    def __init__(self, context=None):
        self._context = Context(context=context)
        scope = self._context.get_scope(SCOPE.RESOURCE)
        self._proxy = Proxy(context=self._context)
        self._route = routes.TEMPLATES_BASE.format(scope["organization"], 'clusters', scope['resource'])

    def list(self, sort="-id"):
        """
        List all kube compute templates in a specific resource
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields kube compute templates objects
        """
        return api_list_generator(
            context=self._context,
            route=self._route,
            object=KubeTemplate,
            sort=sort,
        )

    def get(self, slug):
        """
        Retrieves a kube compute template by the given slug
        @param slug: The slug of the requested kube compute template
        @return: kube compute template object
        """
        if not slug or not isinstance(slug, str):
            raise CnvrgArgumentsError(error_messages.TEMPLATE_GET_FAULTY_SLUG)

        return KubeTemplate(context=self._context, slug=slug)

    def create(
            self,
            title,
            cpu,
            memory,
            **kwargs
    ):
        """

        @param title: Name of the new kube template
        @param cpu: CPU cores of the new kube template
        @param memory: RAM memory of the new kube template
        @param kwargs: A list of optional attributes for creation
            gpu: GPU cores of the new kube template
            gaudi: Gaudi accelerators num of the new kube template
            is_private: is the new kube template private or public
            users: Users with access to the new kube template
            mig_device: mig device type for the new kube template
            template_type: template type of the new kube template
            labels: labels of the new kube template
            taints: taints of the new kube template
            worker_num_executors: num of workers for the new kube template
            worker_cpu: worker CPU cores of the new kube template
            worker_memory: worker RAM memory of the new kube template
            worker_gpu: worker GPU cores of the new kube template
            worker_mig_device: worker mig device type
            worker_labels: worker labels
            worker_taints: worker taints

        @return: The newly created kube template
        """

        formatted_attributes = {
            "title": title,
            "type": kwargs.get("template_type") or 'regular',
            "parent_cpu": float(cpu),
            "parent_memory": float(memory),
            "parent_labels": kwargs.get("labels"),
            "parent_taints": kwargs.get("taints"),
            **kwargs,
            "parent_gpu": {
                "count": kwargs.get("gpu"),
                "mig_device": kwargs.get("mig_device")
            },
            "worker_gpu": {
                "count": kwargs.get("worker_gpu"),
                "mig_device": kwargs.get("worker_mig_device"),
            }
        }

        formatted_attributes.pop('worker_mig_device', None)
        formatted_attributes.pop('mig_device', None)
        formatted_attributes.pop('gpu', None)

        attributes_validator(
            {
                **KubeTemplate.available_attributes,
                # These are being saved in server with the parent_ suffix,
                # so they appear without it in available attributes as well.
                "parent_cpu": float,
                "parent_memory": float,
                "parent_labels": list,
                "parent_taints": list,
                "parent_gpu": dict,
            },
            formatted_attributes,
            required_attributes
        )

        # Instance specific validation
        validate_gpu(formatted_attributes["parent_gpu"])
        validate_gpu(formatted_attributes["worker_gpu"])
        validate_template_type(formatted_attributes["type"])

        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type='kube_template', attributes=formatted_attributes)
        )

        slug = response.attributes['slug']
        return KubeTemplate(
            context=self._context,
            slug=slug,
            attributes=response.attributes
        )
