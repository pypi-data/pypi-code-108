from cnvrgv2.config import routes
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.validators import attributes_validator, validate_gpu, validate_template_type
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes


class KubeTemplate(DynamicAttributes):
    available_attributes = {
        "slug": str,
        "title": str,
        "cpu": float,
        "memory": float,
        "users": list,
        "gpu": dict,
        "mig_device": str,
        "gaudi": float,
        "is_private": bool,
        "compute_type": str,
        "labels": list,
        "taints": list,
        "worker": dict,
        "cluster_title": str,
        "num_executors": int,
        "templates_ids": list
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
            'clusters',
            scope['resource'],
            scope["template"]
        )
        self._attributes = attributes or {}
        self.slug = scope["template"]

    def update(self, **kwargs):
        """
        Updates given attributes of a kube compute template

        @param kwargs: A list of optional attributes to update
            title: Name of the kube template
            cpu: CPU cores of the kube template
            memory: RAM memory of the kube template
            users: Users with access to the kube template
            gpu: GPU cores of the kube template
            gaudi: Gaudi accelerators num of the kube template
            is_private: is the kube template private or public
            mig_device: mig device type for the kube template
            type: template type of the kube template
            labels: labels of the kube template
            taints: taints of the kube template
            worker_num_executors: num of workers for the kube template
            worker_cpu: worker CPU cores of the kube template
            worker_memory: worker RAM memory of the kube template
            worker_gpu: worker GPU cores of the kube template
            worker_mig_device: worker mig device type
            worker_labels: worker labels
            worker_taints: worker taints

        """

        updated_attributes = {
            **kwargs,
            "parent_gpu": {
                "count": kwargs.get("gpu") if kwargs.get("gpu")
                else self._attributes["gpu"],
                "mig_device": kwargs.get("mig_device") if kwargs.get("mig_device")
                else self._attributes["mig_device"]
            },
            "worker_gpu": {
                "count": kwargs.get("worker_gpu") if kwargs.get("worker_gpu")
                else self._attributes["worker"]["gpu"],
                "mig_device": kwargs.get("worker_mig_device") if kwargs.get("worker_mig_device")
                else self._attributes["worker"]["mig_device"]
            }
        }

        updated_attributes.pop('gpu')
        updated_attributes.pop('worker_gpu')
        updated_attributes.pop('mig_device')
        updated_attributes.pop('worker_mig_device')

        attributes_validator(
            self.available_attributes,
            updated_attributes,
            'kube compute template',
            'update'
        )

        # Instance specific validations
        validate_gpu(updated_attributes["parent_gpu"])
        validate_gpu(updated_attributes["worker_gpu"])
        validate_template_type(updated_attributes['type'])

        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.PUT,
            payload=JAF.serialize(type='kube_template', attributes={"slug": self.slug, **updated_attributes}))

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
