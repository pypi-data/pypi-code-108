# gcp_internal.py: Pull Google Analytics from Official API GA4 - @Credit: 4th Whale Marketing 2021
from datetime import timedelta, datetime

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

from whale_googleanalytics.server.enum_list import Metrics, Dimensions

from starlette.config import Config

config = Config(".env")

TESTING = config("TESTING", cast=bool, default=False)

if TESTING:
    config("GOOGLE_APPLICATION_CREDENTIALS")


METRICS = Metrics()
DIMENSIONS = Dimensions()

# Report Settings
METRICS_LIST = [METRICS.USERS]
DIMENSIONS_LIST = [DIMENSIONS.DEVICECATEGORY]


def serializer(object) -> dict:
    return {
        "id": str(object["id"]),
        "data": str(object["data"]),
    }


async def online_connection(id: str):
    """Initializes an Analytics Reporting API V4
    Returns:
        An authorized Analytics Reporting API V4 service object
    """
    # API setup

    SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
    KEY_FILE_LOCATION = config("GOOGLE_APPLICATION_CREDENTIALS") + id + ".json"

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES
    )

    # Build the service object.
    analytics = build("analyticsreporting", "v4", credentials=credentials)

    data = (
        analytics.reports()
        .batchGet(
            body={
                "reportRequests": [
                    {
                        "viewId": id,
                        "dateRanges": [
                            {
                                "startDate": (
                                    datetime.now() - timedelta(days=1)
                                ).strftime("%Y-%m-%d"),
                                "endDate": datetime.today().strftime("%Y-%m-%d"),
                            }
                        ],
                        "metrics": [{"expression": i} for i in METRICS_LIST],
                        "dimensions": [{"name": j} for j in DIMENSIONS_LIST],
                    }
                ]
            }
        )
        .execute()
    )

    return serializer({"id": id, "data": data})
