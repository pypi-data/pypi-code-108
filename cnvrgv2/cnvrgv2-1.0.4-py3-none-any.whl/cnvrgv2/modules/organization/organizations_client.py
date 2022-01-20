from cnvrgv2.proxy import Proxy, HTTP
from cnvrgv2.errors import CnvrgArgumentsError
from cnvrgv2.config import error_messages, routes


# The organization client is for internal use and is unsupported
class OrganizationsClient:
    def __init__(self, domain, token):
        self._domain = domain
        self._token = token
        self._proxy = Proxy(domain=domain, token=token)

    def get(self, slug):
        """
        Retrieves an organization by the given slug
        @param slug: The slug of the requested organization
        @return: Organization object
        """
        if not slug or not isinstance(slug, str):
            raise CnvrgArgumentsError(error_messages.ORGANIZATION_GET_FAULTY_SLUG)

        org_api = routes.ORGANIZATION_BASE.format(slug)

        response = self._proxy.call_api(
            route=org_api,
            http_method=HTTP.GET,
        )
        return response.attributes

    def create(self, name):
        """
        Creates a new organization with the provided name
        @param name: The name of the new organization
        @return: True if the organization was successfully created
        """
        if not name or not isinstance(name, str):
            raise CnvrgArgumentsError(error_messages.ORGANIZATION_CREATE_FAULTY_NAME)

        response = self._proxy.call_api(
            route=routes.ORGANIZATION_CREATE,
            http_method=HTTP.POST,
            payload={"title": name}
        )
        return response.attributes
