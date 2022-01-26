from meili_sdk.models.organization import Organization
from meili_sdk.resources.base import BaseResource


class OrganizationResource(BaseResource):
    def get_organizations(self):
        return self.get("api/organizations/", expected_class=Organization)

    def update_organization(self, organization):
        return self.patch(
            f"api/organizations/{organization.uuid}/",
            data=organization,
            expected_class=Organization,
        )

    def delete_organization(self, organization):
        return self.delete(f"api/organizations/{organization.uuid}/")


class SDKOrganizationResource(BaseResource):
    def get_organization(self):
        return self.get("sdk/organization/", expected_class=Organization)
