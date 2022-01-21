import requests

from .utils import as_list


class AmazonClient(object):
    """AmazonClient - Python SDK.
    ```python
    from amazon_scraper_by_outscraper import AmazonClient
    client = AmazonClient(api_key='SECRET_API_KEY')
    results = client.get_reviews('Trump Tower, NY, USA')
    ```
    https://github.com/outscraper/amazon-scraper-python
    """

    _api_url = 'https://api.app.outscraper.com'
    _api_headers = {}

    def __init__(self, api_key: str) -> None:
        self._api_headers = {
            'X-API-KEY': api_key,
            'client': 'Python Amazon SDK'
        }

    def get_products(self, query: list, limit: int = 24) -> list:
        '''
            Returns information about products on Amazon.

                    Parameters:
                            query (list | str): parameter defines the query you want to search. You can use Amazon products or summary pages URLs. Using a lists allows multiple queries (up to 25) to be sent in one request and save on network latency time.
                            limit (str): parameter specifies the limit of products to get from one query (in case of using summary pages).

                    Returns:
                            list: json result
        '''
        response = requests.get(f'{self._api_url}/amazon/products', params={
            'query': as_list(query),
            'limit': limit,
            'async': False,
        }, headers=self._api_headers)

        if 199 < response.status_code < 300:
            return response.json().get('data', [])

        raise Exception(f'Response status code: {response.status_code}')

    def get_reviews(self, query: list, limit: int = 10, sort: str = 'helpful',
        filterByReviewer: str = 'all_reviews', filterByStar: str = 'all_stars'
    ) -> list:
        '''
            Returns product's reviews from Amazon.

                    Parameters:
                            query (list | str): parameter defines the query you want to search. You can use URLs or ASINs from Amazon products (e.g., https://www.amazon.com/dp/1612680194, 1612680194, etc.).
                            limit (str): parameter specifies the limit of reviews to get from one query.
                            sort (str): parameter specifies one of the sorting types. Available values: "helpful", "recent".
                            filterByReviewer (str): parameter specifies one of the reviewer filter types (All reviewers / Verified purchase only). Available values: "all_reviews" "avp_only_reviews".
                            filterByStar (str): parameter specifies one of the filter types by stars. Available values: "all_stars", "five_star", "four_star", "three_star", "two_star", "one_star", "positive", "critical".
                    Returns:
                            list: json result
        '''
        response = requests.get(f'{self._api_url}/amazon/reviews', params={
            'query': as_list(query),
            'limit': limit,
            'sort': sort,
            'filterByReviewer': filterByReviewer,
            'filterByStar': filterByStar,
            'async': False,
        }, headers=self._api_headers)

        if 199 < response.status_code < 300:
            return response.json().get('data', [])

        raise Exception(f'Response status code: {response.status_code}')
