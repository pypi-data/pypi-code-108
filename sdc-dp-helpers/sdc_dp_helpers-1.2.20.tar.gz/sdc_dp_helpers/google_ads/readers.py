import proto
from google.ads.googleads.client import GoogleAdsClient

from sdc_dp_helpers.api_utilities.file_managers import load_file


class CustomGAdsReader:
    """
    Custom Google Ads Reader
    """

    def __init__(self, creds_path, config_path, **kwargs):
        self.creds_path = creds_path
        self.config_path = config_path

        self.config = load_file(config_path, "yml")

        self.customer_id = str(self.config.get("customer_id"))
        self.query = str(self.config.get("query"))
        self.client = GoogleAdsClient.load_from_storage(
            path=creds_path, version=kwargs.get("version", "v8")
        )

    def run_query(self):
        """
        Query run for the GoogleAdsService endpoint.
        Use this page to build a GAQL query that selects fields from the given resource.
        This includes all of the resources, fields, segments, and metrics that are selectable when
        the resource is in the FROM clause of your GAQL query.

        Query can be built here: https://developers.google.com/google-ads/api/fields/v8/
        """
        service = self.client.get_service("GoogleAdsService")
        response = service.search_stream(customer_id=self.customer_id, query=self.query)

        data_set = []
        for batch in response:
            for row in batch.results:
                data = proto.Message.to_dict(row)
                data_set.append(data)

        return data_set
