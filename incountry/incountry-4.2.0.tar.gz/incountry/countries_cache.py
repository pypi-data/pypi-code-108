import time

from incountry.models import HttpCountriesData

from .exceptions import StorageCountryNotSupportedException, StorageServerException
from .models import HttpOptions
from .validation import validate_http_response
from .http_request import http_request


class CountriesCache:
    DEFAULT_COUNTRIES_ENDPOINT = "https://portal-backend.incountry.com/countries"
    DEFAULT_CACHE_TTL = 300

    def __init__(
        self,
        countries_endpoint: str = None,
        options: HttpOptions = None,
        ttl: int = DEFAULT_CACHE_TTL,
    ):
        self.countries_endpoint = countries_endpoint or CountriesCache.DEFAULT_COUNTRIES_ENDPOINT
        self.ttl = ttl
        self.countries = {}
        self.cache_expires_at = time.time()

        if options is None:
            self.options = HttpOptions()
        else:
            self.options = options if isinstance(options, HttpOptions) else HttpOptions(**options)

    def set_countries_cache_from_server_data(self, countries_data):
        if len(countries_data["countries"]) == 0:
            return

        self.countries = {}

        for country_data in countries_data["countries"]:
            self.countries[country_data["id"]] = {
                "is_midpop": country_data["direct"] is True,
                "region": country_data["region"],
            }

    def update_countries_cache(self):
        (data, _) = self.fetch_countries_data()
        self.set_countries_cache_from_server_data(data)

    @validate_http_response(HttpCountriesData)
    def fetch_countries_data(self, request_options={}):
        try:
            params = {
                "method": "GET",
                "url": self.countries_endpoint,
                "headers": request_options.get("http_headers", {}),
                "timeout": self.options.timeout,
            }

            return http_request(params, scope="fetching countries list")
        except StorageServerException as e:
            if e.status_code == 429:
                raise
            return ({"countries": []}, None)

    def get_country_details(self, country):
        country = country.lower()
        if self.cache_expires_at <= time.time():
            self.update_countries_cache()
            self.cache_expires_at = time.time() + self.ttl

        if len(self.countries) == 0:
            raise StorageServerException("Country list is empty")

        if country not in self.countries:
            raise StorageCountryNotSupportedException(country=country)

        return self.countries[country]
