from meili_sdk.clients.base import BaseAPIClient
from meili_sdk.resources.forms import SDKFormResource
from meili_sdk.resources.organizations import SDKOrganizationResource
from meili_sdk.resources.tasks import TaskResource
from meili_sdk.resources.teams import SDKTeamResource
from meili_sdk.resources.vehicles import SDKVehicleResource


class SDKClient(BaseAPIClient):
    AUTHORIZATION_TOKEN_HEADER = "SDK-Key"  # nosec

    def get_organization_resources(self):
        return SDKOrganizationResource(self)

    def get_team_resources(self):
        return SDKTeamResource(self)

    def get_user_resources(self):
        raise NotImplemented("SDK Client cannot access user resources")

    def get_vehicle_resources(self):
        return SDKVehicleResource(self)

    def get_task_resources(self):
        return TaskResource(self)

    def get_form_resources(self):
        return SDKFormResource(self)
