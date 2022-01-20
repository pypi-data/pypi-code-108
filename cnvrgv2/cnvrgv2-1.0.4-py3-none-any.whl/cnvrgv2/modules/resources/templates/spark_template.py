from cnvrgv2.config import routes
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.validators import attributes_validator, validate_gpu
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes


class SparkTemplate(DynamicAttributes):
    available_attributes = {
        "slug": str,
        "title": str,
        "cpu": float,
        "memory": float,
        "compute_type": str,
        "users": list,
        "gpu": float,
        "mig_device": str,
        "lables": list,
        "taints": list,
        "gaudi": float,
        "is_private": bool,
        "cluster_title": str,
        "num_executors": float,
        "templates_ids": list,
        "worker": dict,
    }

    def __init__(self, context=None, slug=None, attributes=None):
        self._context = Context(context=context)

        # Set current context scope to current template
        if slug:
            self._context.set_scope(SCOPE.TEMPLATE, slug)

        scope = self._context.get_scope(SCOPE.TEMPLATE)

        self._proxy = Proxy(context=self._context)
        self._route = routes.TEMPLATE_BASE.format(
            scope["organization"],
            'spark_driver',
            scope['resource'],
            scope["template"]
        )
        self._attributes = attributes or {}
        self.slug = scope["template"]

    def update(self, **kwargs):
        """
        Updates given attributes of a spark compute template

        @param kwargs: A list of optional attributes to update
            title: Name of the spark compute template
            cpu: CPU cores for the spark compute template
            memory: RAM Memory for the spark compute template
            gpu: GPU Cores for the spark compute template
            users: Users with access to the spark compute template
            gaudi: Gaudi accelerators num for the spark compute template
            is_private: is the spark compute template private or public
            num_executors: number of workers for the spark compute template
            templates_ids: allowed templates for the spark compute template worker
            mig_device: mig device type for the spark compute template

        @return: the updated spark compute template
        """

        updated_attributes = {
            **kwargs,
            "gpu": {
                "count": kwargs.get("gpu") if kwargs.get("gpu")
                else self._attributes["gpu"],
                "mig_device": kwargs.get("mig_device") if kwargs.get("mig_device")
                else self._attributes["mig_device"]
            }
        }

        updated_attributes.pop('mig_device')

        attributes_validator(self.available_attributes, updated_attributes)

        # Instance specific validations
        validate_gpu(updated_attributes["gpu"])

        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.PUT,
            payload=JAF.serialize(type='spark_driver', attributes={"slug": self.slug, **updated_attributes}))

        self._attributes = response.attributes

    def save(self):
        """
        In case of any attribute change, saves the changes
        """
        self.update(**self._attributes)

    def delete(self):
        """
        Deletes the current template
        @return: None
        """
        self._proxy.call_api(route=self._route, http_method=HTTP.DELETE)
