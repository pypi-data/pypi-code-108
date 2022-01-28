import requests

from sdc_dp_helpers.api_utilities.file_managers import load_file
from sdc_dp_helpers.api_utilities.retry_managers import retry_handler


class CustomFacebookGraphReader:
    """
    Custom reader for the Facebook Graph API.
    """

    def __init__(self, creds_file, config_file=None, **kwargs):
        self._creds = load_file(creds_file, "yml")
        self._config = load_file(config_file, "yml")
        self.version = kwargs.get("version", "v11.0")

        self._request_session = requests.Session()
        self.paging = None
        self.data_set = []

    @retry_handler(
        exceptions=Exception, total_tries=5, should_raise=True, backoff_factor=5
    )
    def _graph_api_request_handler(self):
        """
        Basic handler for the Facebook api response.
        https://developers.facebook.com/docs/marketing-api/insights/parameters/v12.0
        API Parameters:
            action_attribution_windows:
                desc: The attribution window for the actions.
                default_value: default
                d_type: list(1d_view, 7d_view, 28d_view, 1d_click,
                             7d_click, 28d_click, dda, default)
            action_breakdowns:
                desc: How to break down action results.
                default_value: Vec
                d_type: list(action_device, action_canvas_component_name, action_carousel_card_id,
                            action_carousel_card_name, action_destination, action_reaction,
                            action_target_id, action_type, action_video_sound, action_video_type)
            action_report_time:
                desc: Determines the report time of action stats.
                default_value:
                d_type: list(impression, conversion, mixed)
            breakdowns:
                desc: How to break down the result.
                default_value:
                d_type: list(ad_format_asset, age, app_id, body_asset,
                            call_to_action_asset, country,
                            description_asset, gender, image_asset,
                            impression_device, link_url_asset,
                            product_id, region, skan_conversion_id,
                            title_asset, video_asset, dma,
                            frequency_value,
                            hourly_stats_aggregated_by_advertiser_time_zone,
                            hourly_stats_aggregated_by_audience_time_zone,
                            place_page_id, publisher_platform,
                            platform_position, device_platform)
            date_preset:
                desc: Represents a relative time range.
                default_value: last_30d
                d_type: list(today, yesterday, this_month, last_month,
                this_quarter, maximum,
                            last_3d, last_7d, last_14d, last_28d, last_30d,
                            last_90d, last_week_mon_sun,
                            last_week_sun_sat, last_quarter,
                            last_year, this_week_mon_today,
                            this_week_sun_today, this_year)
            default_summary:
                desc: Select fields on the exporting report file.
                default_value:
                d_type: list(bool)
            fields:
                desc: Fields to be retrieved.
                default_value: impressions and spend
                d_type: list(string)
            level:
                desc: Represents the level of result.
                default_value:
                d_type: str(ad, adset, campaign, account)
            time_range:
                desc: A single time range object. UNIX timestamp not supported.
                    This param is ignored if time_ranges is provided.
                default_value: dict('since':YYYY-MM-DD,'until':YYYY-MM-DD)
                d_type:
        """
        print("GET: graph.facebook.com.")
        try:
            response = self._request_session.get(
                # Note the since and until params does not seem to work at all,
                # so filtering after request
                url=f"https://graph.facebook.com/v12.0/{self._creds.get('act')}/insights",
                params={
                    "date_preset": self._config.get("date_preset", "last_30d"),
                    "time_increment": self._config.get("time_increment", 1),
                    "fields": self._config.get(
                        "fields", "impressions,spend,clicks,cpc,ctr,reach"
                    ),
                    "level": self._config.get("level", "adset"),
                    "limit": self._config.get("limit", 1000),
                    "access_token": self._creds["access_token"],
                },
            )

            print(f"Status: {response.status_code}.")
            if response.status_code != 200:
                raise EnvironmentError(f"Reason:{response.json()}.")

            # gather initial request, data and page token
            response_json = response.json()
            self.paging = response_json.get("paging", {}).get("next", None)
            print("Page Token: Initial Request.")
            self.data_set.append(response_json.get("data", []))

            # page through the response data
            while True:
                if self.paging is not None:
                    print(f"Page Token: {self.paging}.")
                    page_response = self._request_session.get(self.paging)
                    page_response_json = page_response.json()
                    if page_response.status_code != 200:
                        raise EnvironmentError(f"Reason:{page_response.json()}.")

                    self.paging = page_response_json.get("paging", None).get(
                        "next", None
                    )
                    self.data_set.append(page_response_json.get("data", []))
                else:
                    print("Paging data complete.")
                    break

            return self.data_set[0]

        except Exception as err:
            raise err

    def run_query(self):
        """
        Get metrics data from Facebook Graph API.
        The Pages API is a set of Facebook Graph API endpoints that apps can
        use to create and manage a Page's settings and content.
        Metric data of public Pages is stored by Facebook for 2 years.
        Metric data of unpublished Pages is stored for only 5 days.
        """
        response = self._graph_api_request_handler()
        if response is not None:
            return response
        else:
            print("Facebook returned no data for given period.")
            return None
