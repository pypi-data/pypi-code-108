from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.domain import Dashboard
from ikologikapi.domain.Search import Search
from ikologikapi.services.AbstractIkologikInstallationService import AbstractIkologikInstallationService


class DashboardService(AbstractIkologikInstallationService):

    def __init__(self, jwtHelper: IkologikApiCredentials):
        super().__init__(jwtHelper)

    # CRUD Actions

    def get_url(self, customer, installation):
        return f'{self.jwtHelper.get_url()}/api/v2/customer/{customer}/installation/{installation}/dashboard'

    def get_by_name(self, customer: str, installation: str, name: str) -> Dashboard:
        # Prepare the search
        search = Search()
        search.add_filter("name", "EQ", [name])
        search.add_order("name", "ASC")
        search.set_pagination(0, 1)

        # Query
        result = self.search(customer, installation, search)
        if result and len(result) == 1:
            return result[0]
        else:
            return None
