from ikologikapi.IkologikApiCredentials import IkologikApiCredentials
from ikologikapi.domain.Search import Search
from ikologikapi.services.AbstractIkologikInstallationService import AbstractIkologikInstallationService


class BatchTypeService(AbstractIkologikInstallationService):

    def __init__(self, jwtHelper: IkologikApiCredentials):
        super().__init__(jwtHelper)

    # CRUD Actions

    def get_url(self, customer, installation):
        return f'{self.jwtHelper.get_url()}/api/v2/customer/{customer}/installation/{installation}/batchtype'

    def get_by_name(self, customer: str, installation: str, name):
        search = Search()
        search.add_filter = ("name", "EQ", [name])
        search.add_order("name", "ASC")

        # Query
        result = self.search(customer, installation, search)
        if result and len(result) == 1:
            return result[0]
        else:
            return None
