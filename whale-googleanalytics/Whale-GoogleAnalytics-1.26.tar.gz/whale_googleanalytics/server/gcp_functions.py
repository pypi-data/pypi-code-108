"""Google Analytics data to CSV
# gcp_functions.py: Pull Google Analytics from Official API GA4 - @Credit: 4th Whale Marketing 2021
No header is written for the csv generated.
To be used with Airflow to import a Google Analytics data.
"""

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd
import numpy as np
from datetime import timedelta, datetime
from random import randrange, uniform
from whale_googleanalytics.server.helpers.plotly import Plotly

from starlette.config import Config

config = Config(".env")


today = datetime.today()
todayStr = today.strftime("%Y%m%d%H%M")

plot_plotly = Plotly()


def to_save_csv(VIEW_ID, df: object):
    """Parses and prints the Analytics Reporting API V4 response.
    Args:
        Pandas dataframe
    Returns:
        None
    """
    random = str(randrange(0, 10))

    df["viewID"] = VIEW_ID
    df.to_csv(random + "_" + todayStr + "_" + VIEW_ID + ".csv", index=False)


def credentials(VIEW_ID, api):
    """Test API connection
    Args:
        Google Analytics view, api type (ga or mcf)
    Returns:
        API call
    """
    print(config("GOOGLE_APPLICATION_CREDENTIALS"))

    SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
    KEY_FILE_LOCATION = config("GOOGLE_APPLICATION_CREDENTIALS") + VIEW_ID + ".json"

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES
    )

    if api == "ga":
        analytics = build("analyticsreporting", "v4", credentials=credentials)
        return analytics
    elif api == "mcf":
        analytics = build(
            "analytics", "v3", credentials=credentials, cache_discovery=False
        )
        return analytics
    else:
        raise ValueError(
            f"Could not detect API from metric {api}. The metric must start with `ga:` or `mcf:`."
        )


def convert_to_dataframe_ga(response: object):
    """Parses and prints the Analytics Reporting API V4 response.
    Args:
        response: An Analytics Reporting API V4 response.
    Returns:
        Pandas DataFrame
    """
    dataframe = []

    for report in response.get("reports", []):

        columnHeader = report.get("columnHeader", {})
        dimensionHeaders = columnHeader.get("dimensions", [])
        metricHeaders = [
            i.get("name", {})
            for i in columnHeader.get("metricHeader", {}).get("metricHeaderEntries", [])
        ]

        for row in report.get("data", {}).get("rows", []):
            dimensions = row.get("dimensions", [])
            metrics = row.get("metrics", [])[0].get("values", {})

            dict = {}

            for header, dimension in zip(dimensionHeaders, dimensions):
                dict[header] = dimension

            for metricHeader, metric in zip(metricHeaders, metrics):
                dict[metricHeader] = metric

            dataframe.append(dict)

    dataFrame_df = pd.DataFrame(dataframe)

    return dataFrame_df


def convert_to_dataframe_mcf(response, write_header: bool = True):
    """Parses and prints the Analytics Reporting API V3 MCF response.
    Args:
        response: An MCF Reporting API V3 response.
    Returns:
        Pandas DataFrame
    """

    columnHeaders = response.get("columnHeaders", [])

    # write header
    headerRow = []
    for column_header in columnHeaders:
        headerRow.append(column_header["name"])

    dataFrame_df = pd.DataFrame(columns=headerRow)

    # write rows
    row_index = 0
    for raw_row in response.get("rows", []):
        row_single = []
        for cell in raw_row:
            row_single.append(cell["primitiveValue"])
        row_index += 1

        # print(row_index)
        # print(row_single)
        dataFrame_df.loc[row_index] = row_single

    return dataFrame_df


def get_ga_single(
    id,
    start_date,
    end_date,
    metrics_list,
    dimensions_list,
    secondary_metrics,
    analytics: object,
):
    """Queries the Analytics Reporting API V4.
    Args:
        analytics: An authorized Analytics Reporting API V4 service object.
    Returns:
        The Analytics Reporting API V4 response.
    """
    metric_list_all = [{"expression": i} for i in metrics_list]

    if secondary_metrics:
        metric_list_all.append({"expression": secondary_metrics})

    return (
        analytics.reports()
        .batchGet(
            body={
                "reportRequests": [
                    {
                        "viewId": id,
                        # "filtersExpression": "ga:eventCategory==Opensite,ga:eventCategory==OutboundLink,ga:eventCategory==Outbound Click",
                        # "dimensionFilterClauses": dimensionFilterClauses,
                        # "samplingLevel": "LARGE",
                        # "pageSize": num_results,
                        "dateRanges": [{"startDate": start_date, "endDate": end_date}],
                        "metrics": metric_list_all,
                        "dimensions": [{"name": j} for j in dimensions_list],
                    }
                ]
            }
        )
        .execute()
    )


def get_mcf_single(
    ids: str, start_date: str, end_date: str, metrics: str, dimensions: str
):
    """Parses and the Multi Channel Funnel V3 API
    Args:
        MCF/GA view, start date, end date, metrics (obj), dimensions (obj)
    Returns:
        response: An MCF API V3 response.
    """
    # print(analytics.__dict__)
    analytics_v3 = credentials(ids, "mcf")
    return (
        analytics_v3.data()
        .mcf()
        .get(
            ids=f"ga:{ids}",
            start_date=start_date,
            end_date=end_date,
            metrics=",".join(metrics),
            dimensions=dimensions,
        )
        .execute()
    )


async def get_ga_analytics(
    VIEW_ID: str,
    start_date: str,
    end_date: str,
    metrics_list: object,
    dimensions_list: object,
    secondary_metrics: object,
    chart: bool,
    to_csv: bool,
):
    """Parses and the Analytics V4 API
    Args:
        MCF/GA view, start date, end date, metrics (obj), dimensions (obj), secondary axis if needed
    Returns:
        response: An GA API V4 response.
    """
    if VIEW_ID:
        global view_id
        view_id = VIEW_ID
    else:
        raise ValueError(
            f"Could not detect API from view {VIEW_ID}. The metric must start with Google Analytics GA or MCF."
        )

    data = get_ga_single(
        view_id,
        start_date,
        end_date,
        metrics_list,
        dimensions_list,
        secondary_metrics,
        credentials(view_id, "ga"),
    )

    data_df = convert_to_dataframe_ga(data)

    if chart == True:
        fig1 = plot_plotly.barchart_1d(
            data_df, metrics_list, dimensions_list, secondary_metrics
        )
    else:
        fig1 = ""

    if to_csv == True:
        to_save_csv(view_id, data_df)

    return {"response": data_df, "fig": fig1}


async def get_mcf_analytics(
    ids: str,
    start_date: str,
    end_date: str,
    metrics: str,
    dimensions: str,
    chart: bool,
    to_csv: bool,
):
    """Dataframe and fig for Analytics V3 API
    Args:
        MCF/GA view, start date, end date, metrics (obj), dimensions (obj), secondary axis if needed
    Returns:
        response: single report dataframe and corresponding chart and it saves the DF as a csv
    """
    data = get_mcf_single(ids, start_date, end_date, metrics, dimensions)

    data_df = convert_to_dataframe_mcf(data, write_header=True)

    if chart == True:
        fig1 = plot_plotly.barchart_1d(data_df, metrics, dimensions)
    else:
        fig1 = ""

    if to_csv == True:
        to_save_csv(ids, data_df)

    return {"response": data_df, "fig": fig1}


async def plotly_generator(*args):
    """Dataframe and fig for Analytics V3 API
    Args:
        the dataframe and fig for each story
    Returns:
        response: string
    """
    plot_plotly.html_report(*args)

    return {"response": "Html generated"}
