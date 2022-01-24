from fastapi import APIRouter, Body
from fastapi.encoders import jsonable_encoder

from whale_googleanalytics.server.models.model_gcp import (
    ErrorResponseModel,
    ResponseModel,
    TestingModel,
    DataModel,
    MCFModel,
)

# Testing functions
from whale_googleanalytics.server.test_api import online_connection

# Create ETL & plotly figures
from whale_googleanalytics.server.gcp_functions import (
    get_ga_analytics,
    get_mcf_analytics,
    plotly_generator,
)

router = APIRouter()

# Validate if th key are connecting to GCP
@router.post("/online/", response_description="Test GCP API connection & keys")
async def online_connection_data(data: TestingModel = "105048203"):
    online_status = await online_connection(data.id)

    if online_status:
        return ResponseModel(online_status, "API connected successfully")

    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the data.",
    )


# Generate a csv and a plotly html
@router.post(
    "/ga_single/",
    callbacks=router.routes,
    response_description="Create a 1d barchart CSV and HTML plotly file",
)
async def get_ga_analytics_1d_data(data: DataModel):

    data_status = await get_ga_analytics(
        data.id,
        data.start_date,
        data.end_date,
        data.metrics_list,
        data.dimensions_list,
        data.secondary_metrics,
        data.chart,
        data.to_csv,
    )

    data_df1 = data_status["response"]
    fig1 = data_status["fig"]

    if data.chart == True:
        data = await plotly_generator(data_df1, fig1, "pass", "pass")

    return data_df1


# Generate a csv and a plotly html
@router.post(
    "/mcf_single",
    callbacks=router.routes,
    response_description="Create a 2d (secondary axis) barchart CSV and HTML plotly file",
)
async def report_mcf_dataframe_2d_data(data: MCFModel):

    data_status = await get_mcf_analytics(
        data.ids,
        data.start_date,
        data.end_date,
        data.metrics,
        data.dimensions,
        data.chart,
        data.to_csv,
    )

    data_df1 = data_status["response"]
    fig1 = data_status["fig"]

    if data.chart == True:
        data = await plotly_generator(data_df1, fig1, "pass", "pass")

    return data_df1


# Generate a csv and a plotly html
@router.get(
    "/mobile_report/",
    callbacks=router.routes,
    response_description="Create a 2d (secondary axis) barchart CSV and HTML plotly file",
)
async def mobile_report_data():

    data_status = await get_ga_analytics(
        "13406065",
        "2021-10-01",
        "2021-10-31",
        ["ga:users"],
        ["ga:deviceCategory"],
        "ga:sessions",
        False,
        False,
    )
    data_df_users = data_status["response"]
    fig_users = data_status["fig"]

    data_status_bounce = await get_ga_analytics(
        "13406065",
        "2021-10-01",
        "2021-10-31",
        ["ga:sessions", "ga:users"],
        ["ga:deviceCategory"],
        "ga:bounceRate",
    )
    data_df_br = data_status_bounce["response"]
    fig_br = data_status_bounce["fig"]

    data = await plotly_generator(data_df_users, fig_users, data_df_br, fig_br)

    return data
