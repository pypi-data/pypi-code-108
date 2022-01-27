from datetime import datetime

from gateways.apis.api_base_class import ApiBase


class ApiAccountCost(ApiBase):
    def breakdown(self, frm: datetime, until: datetime, criteria: str = 'blueprint'):
        return self.build_route(
            "cost/breakdown?criteria={criteria}&from={frm}&to={until}".format(**locals()))