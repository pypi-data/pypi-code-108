from cnvrgv2.config import routes, error_messages
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.utils.validators import attributes_validator
from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.modules.base.dynamic_attributes import DynamicAttributes


class Machine(DynamicAttributes):
    # TOOD: Add sshkey support
    available_attributes = {
        "slug": str,
        "title": str,
        "ssh_user": str,
        "ssh_ip": str,
        "ssh_port": str,
        "cpu_cores": float,
        "status": str,
        "ram": float,
        "gpu": bool,
        "gpu_cores": float,
        "gpu_model": str,
        "gpu_ram": float,
    }

    def __init__(self, context=None, slug=None, attributes=None):
        self._context = Context(context=context)

        # Set current context scope to current machine
        if slug:
            self._context.set_scope(SCOPE.RESOURCE, slug)

        scope = self._context.get_scope(SCOPE.RESOURCE)

        self._proxy = Proxy(context=self._context)
        self._route = routes.MACHINE_BASE.format(scope["organization"], scope["resource"])
        self._attributes = attributes or {}
        self.slug = scope["resource"]

    def update(self, **kwargs):
        """
        Updates given attributes of a machine

        @kwargs: A list of optional attributes to update
            title: Name of the new machine
            ssh_user: Credentials for the new machine
            ssh_ip: Host of the new machine
            ssh_port: Port of the new machine
            ssh_key: a ssh key file for the new machine(path to file relative to working dir)
            ssh_password: a password for the new machine
            cpu_cores: CPU cores for the new machine
            ram: Memroy for the new machine
            gpu: Does the new machine has a GPU
            gpu_model: What GPU the new machine has
            gpu_cores: GPU Cores for the new machine
            gpu_ram: GPU memroy for the new machine

        @return: the updated machine
        """

        # Validate attributes
        attributes_validator(self.available_attributes, kwargs)

        # Specific instance validations
        if (not kwargs.get('gpu') and not self._attributes['gpu'] and
                kwargs.get('gpu_model') or kwargs.get('gpu_cores') or kwargs.get('gpu_ram')):
            raise CnvrgArgumentsError(error_messages.MACHINE_GPU_VALUES_WITHOUT_GPU)

        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.PUT,
            payload=JAF.serialize(type='machine', attributes={"slug": self.slug, **kwargs}))

        self._attributes = response.attributes

    def save(self):
        """
        In case of any attribute change, saves the changes
        """
        self.update(**self._attributes)

    def delete(self):
        """
        Deletes the current machine
        @return: None
        """
        self._proxy.call_api(route=self._route, http_method=HTTP.DELETE)
