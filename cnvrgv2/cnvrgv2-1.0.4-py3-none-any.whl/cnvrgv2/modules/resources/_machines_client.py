from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.context import Context, SCOPE
from cnvrgv2.utils.validators import attributes_validator
from cnvrgv2.utils.json_api_format import JAF
from cnvrgv2.config import error_messages, routes
from cnvrgv2.utils.api_list_generator import api_list_generator
from cnvrgv2.modules.resources._machine import Machine

required_attributes = [
    'title',
    'ssh_ip',
    'ssh_port',
    'ssh_user'
]

default_attributes = {
    "ram": 1.0,
    "cpu_cores": 1.0
}


class MachinesClient:

    def __init__(self, organization):
        self._context = Context(context=organization._context)
        scope = self._context.get_scope(SCOPE.ORGANIZATION)

        self._proxy = Proxy(context=self._context)
        self._route = routes.MACHINES_BASE.format(scope["organization"])

    def list(self, sort="-id"):
        """
        List all the machines in the organization
        @param sort: key to sort the list by (-key -> DESC | key -> ASC)
        @raise: HttpError
        @return: Generator that yields Machine objects
        """
        return api_list_generator(
            context=self._context,
            route=self._route,
            object=Machine,
            sort=sort,
        )

    def get(self, slug):
        """
        Retrieves a machine by the given slug
        @param slug: The slug of the requested machine
        @return: Machine object
        """
        if not slug or not isinstance(slug, str):
            raise CnvrgArgumentsError(error_messages.MACHINE_GET_FAULTY_SLUG)

        return Machine(context=self._context, slug=slug)

    def create(
        self,
        title,
        ssh_user,
        ssh_ip,
        ssh_port,
        ssh_key=None,
        ssh_password=None,
        **kwargs
    ):

        # --- #
        # A machine will generate a singular template using these values,
        # so we handle creation here and not in the machine templates client
        # --- #

        """
        @param title: Name of the new machine
        @param ssh_user: Credentials for the new machine
        @param ssh_ip: Host of the new machine
        @param ssh_port: Port of the new machine
        @param ssh_key: a ssh key file for the new machine(path to file relative to working dir)
        @param ssh_password: a password for the new machine
        @param kwargs: A list of optional attributes for creation
            cpu_cores: CPU cores for the new machine
            ram: memory for the new machine
            gpu: Does the new machine has a GPU
            gpu_model: What GPU the new machine has
            gpu_cores: GPU Cores for the new machine
            gpu_ram: GPU memory for the new machine
        @return: The newly created machine
        """

        attributes = {
            "title": title,
            "ssh_user": ssh_user,
            "ssh_ip": ssh_ip,
            "ssh_port": ssh_port,
            **default_attributes,
            **kwargs,
        }

        if ssh_key:
            # todo: Add ssh_key file support
            pass
        else:
            attributes["ssh_password"] = ssh_password

        attributes_validator(
            Machine.machine_attributes,
            attributes,
            required_attributes
        )

        # Instance specific validations
        if not ssh_password and not ssh_key:
            raise CnvrgArgumentsError(error_messages.MACHINE_NO_CREDENTIALS.format('create'))

        if not kwargs.get("gpu") and (kwargs.get("gpu_model") or kwargs.get('gpu_cores') or kwargs.get('gpu_ram')):
            raise CnvrgArgumentsError(error_messages.MACHINE_GPU_VALUES_WITHOUT_GPU)

        response = self._proxy.call_api(
            route=self._route,
            http_method=HTTP.POST,
            payload=JAF.serialize(type='machine', attributes=attributes),
        )
        slug = response.attributes['slug']
        return Machine(context=self._context, slug=slug, attributes=response.attributes)
