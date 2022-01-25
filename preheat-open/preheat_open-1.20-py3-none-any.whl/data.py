import math
from functools import reduce

import numpy as np
import pandas as pd

from .api import (
    DATETIME_FORMAT,
    MAX_POINTS_PER_REQ,
    TIMEZONE,
    APIDataExtractError,
    api_get,
)
from .helpers import list_to_string, sanitise_datetime_input


def load_box_data(
    component_map, start_date, end_date, time_resolution="minute"
) -> pd.DataFrame:
    # Parse strings to datetime object

    start_date = sanitise_datetime_input(start_date)
    end_date = sanitise_datetime_input(end_date)
    __check_start_end_date(start_date, end_date)

    path = "measurements"
    cid_key = "cids"
    cids = list(component_map.keys())

    if not cids:
        return pd.DataFrame()

    resp = __perform_requests(
        path, cid_key, cids, start_date, end_date, time_resolution, "csv"
    )

    return __extract_data(resp, "cid", component_map, "csv")


def load_model_data(
    component_map, start_date, end_date, time_resolution="raw"
) -> pd.DataFrame:
    # Parse strings to datetime object
    start_date = sanitise_datetime_input(start_date)
    end_date = sanitise_datetime_input(end_date)
    __check_start_end_date(start_date, end_date)

    path = "units/measurements"
    id_key = "ids"
    ids = list(component_map.keys())

    if not ids or len(ids) == 0:
        return pd.DataFrame()

    if time_resolution != "raw":
        # Do chunked requests
        resp = __perform_requests(
            path, id_key, ids, start_date, end_date, time_resolution, "csv"
        )
    else:
        # Do single request
        resp = __make_request(
            path, {id_key: ids}, start_date, end_date, time_resolution, "csv"
        )

    return __extract_data(resp, "id", component_map, "csv")


def load_weather_data(
    location_id,
    component_map,
    start_date,
    end_date,
    time_resolution="hour",
    components=None,
) -> pd.DataFrame:
    # Parse strings to datetime object
    start_date = sanitise_datetime_input(start_date)
    end_date = sanitise_datetime_input(end_date)
    __check_start_end_date(start_date, end_date)

    path = f"weather/{location_id}"
    cid_key = "type_ids"
    cids = list(component_map.keys())

    # If minutes, then we need to resample
    if time_resolution in ["minute", "5min", "raw"]:
        time_resolution = "hour"
        resample = True
    else:
        resample = False

    resp = __perform_requests(
        path, cid_key, cids, start_date, end_date, time_resolution, "csv"
    )

    if resample:
        return (
            __extract_data(resp, "type_id", component_map, "csv")
            .resample("5min")
            .ffill()
        )

    return __extract_data(resp, "type_id", component_map, "csv")


def perform_requests(
    path, cid_key, cids, start_date, end_date, time_resolution, format="csv"
):
    return __perform_requests(
        path, cid_key, cids, start_date, end_date, time_resolution, format
    )


def __perform_requests(
    path, cid_key, cids, start_date, end_date, time_resolution, format="csv"
):
    # Split CIDs into chunks
    # NOTE: we reduce number of CIDs pr. REQ to confine w. MAX_POINTS_PER_REQ
    # This sets the limit to 90000 points on a single CID; which for 5min.
    # is roughly 300 days of data.
    time_lookup = {
        "raw": 10,
        "minute": 300,
        "5min": 300,
        "hour": 3600,
        "day": 86400,
        "week": 604800,
        "month": 16934400,
        "year": 6181056000,
    }

    end_date_in = sanitise_datetime_input(end_date)
    start_date_in = sanitise_datetime_input(start_date)

    dt = end_date_in - start_date_in

    N_points_requested = len(cids) * dt.total_seconds() / time_lookup[time_resolution]

    if N_points_requested < 1:
        reqs = []
    else:
        cid_chunk_size = (MAX_POINTS_PER_REQ / N_points_requested) * len(cids)

        cid_chunks = [
            cids[x : x + max(int(cid_chunk_size), 1)]
            for x in range(0, len(cids), max(int(cid_chunk_size), 1))
        ]
        time_chunks = math.ceil(1 / cid_chunk_size)
        dt_chunk = (end_date_in - start_date_in) / np.fmax(1, time_chunks)

        reqs = []
        for cid_chunk in cid_chunks:
            for i in range(time_chunks):
                reqs.append(
                    __make_request(
                        path,
                        {cid_key: list_to_string(cid_chunk)},
                        start_date + i * dt_chunk,
                        start_date + (i + 1) * dt_chunk,
                        time_resolution,
                        format,
                    )
                )

    return reqs


def __make_request(path, payload, start_date, end_date, time_resolution, format="csv"):
    payload["start_time"] = start_date.isoformat()
    payload["end_time"] = end_date.isoformat()

    if time_resolution == "5min":
        time_resolution = "minute"

    payload["time_resolution"] = time_resolution

    return api_get(path, payload=payload, out=format)


def extract_data(resp, id_key, component_map, format="csv"):
    return __extract_data(resp, id_key, component_map, format)


def __extract_data(resp, id_key, component_map, format="csv"):

    kwargs_to_datetime = dict(utc=True, format=DATETIME_FORMAT)
    # If this is having an issue, use "infer_datetime_format=True" instead of "format=..."

    if len(resp) < 1:
        # Short circuit all in case of empty response
        return pd.DataFrame()
    elif format == "json":
        if isinstance(resp, list):
            # Initialize empty response that we can append to
            resp_new = {cid: [] for cid in component_map.keys()}
            for req in resp:
                for cid, values in req.items():
                    resp_new[cid] += values
            resp = resp_new

        if "message" in resp:
            raise APIDataExtractError(resp["message"])

        dfs = []
        for cid, name in component_map.items():
            time = pd.to_datetime(
                [data["time"] for data in resp[cid]], **kwargs_to_datetime
            )
            value = [data["value"] for data in resp[cid]]

            df_i = pd.DataFrame(value, columns=[name], index=time)
            dfs.append(df_i)

    elif format == "csv":
        # Join response into one
        if isinstance(resp, list):
            resp_new = None
            for df in resp:
                resp_new = df if resp_new is None else resp_new.append(df)
            resp = resp_new

        # Split
        dfs = []
        for cid, name in component_map.items():
            df_i = resp[(resp[id_key] == int(cid))].copy()
            df_i.loc[:, "time"] = pd.to_datetime(df_i["time"], **kwargs_to_datetime)
            df_i = df_i.set_index("time")
            df_i = df_i.filter(items=["value"])
            df_i = df_i.rename(columns={"value": name})
            df_i.index = df_i.index.rename(None)
            dfs.append(df_i)

    elif format == "dataframe":
        # Split
        dfs = []
        for cid, name in component_map.items():
            df_i = resp[(resp[id_key] == int(cid))].copy()
            df_i.loc[:, "time"] = pd.to_datetime(df_i["time"], **kwargs_to_datetime)
            df_i = df_i.set_index("time")
            df_i = df_i.filter(items=["value"])
            df_i = df_i.rename(columns={"value": name})
            df_i.index = df_i.index.rename(None)
            dfs.append(df_i)

    else:
        raise TypeError("Unsupported format")

    df = reduce(
        lambda x, y: pd.merge(x, y, left_index=True, right_index=True, how="outer"), dfs
    )
    return df


def __check_start_end_date(start, end):
    if end < start:
        raise ValueError("End date must be AFTER start date")
