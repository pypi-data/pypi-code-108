import logging

import pandas as pd
import requests

import go_utils.lc as lc
import go_utils.mhm as mhm
from go_utils.constants import (
    end_date,
    landcover_protocol,
    mosquito_protocol,
    start_date,
)


def parse_api_data(response_json):
    try:
        results = response_json["results"]
        df = pd.DataFrame(results)
    except KeyError:
        raise RuntimeError("Data Download Failed. The GLOBE API is most likely down.")

    # Expand the 'data' column by listing the contents and passing as a new dataframe
    df = pd.concat([df, pd.DataFrame(list(df["data"]))], axis=1)
    # Drop the previously nested data column
    df = df.drop(labels="data", axis=1)

    # Display the dataframe
    return df


def is_valid_latlon_box(latlon_box):

    valid_lat_checks = (
        latlon_box["min_lat"] < latlon_box["max_lat"]
        and latlon_box["max_lat"] <= 90
        and latlon_box["min_lat"] >= -90
    )
    valid_lon_checks = (
        latlon_box["min_lon"] < latlon_box["max_lon"]
        and latlon_box["max_lon"] <= 180
        and latlon_box["min_lon"] >= -180
    )

    return valid_lon_checks and valid_lat_checks


def get_api_data(
    protocol,
    start_date=start_date,
    end_date=end_date,
    is_clean=True,
    latlon_box={"min_lat": -90, "max_lat": 90, "min_lon": -180, "max_lon": 180},
):
    """Utility function for interfacing with the GLOBE API.
    More information about the API can be viewed [here](https://www.globe.gov/es/globe-data/globe-api).

    Parameters
    ----------
    protocol : str
               The desired GLOBE Observer Protocol. Protocols for the App protocols include: `land_covers` (Landcover), `mosquito_habitat_mapper` (Mosquito Habitat Mapper), `sky_conditions` (Clouds), `tree_heights` (Trees).
    start_date : str, default= 2017-05-31
                 The desired start date of the dataset in the format of (YYYY-MM-DD).
    end_date : str, default= today's date in YYYY-MM-DD form.
               The desired end date of the dataset in the format of (YYYY-MM-DD).
    latlon_box : dict of {str, double}, optional
                 The longitudes and latitudes of a bounding box for the dataset. The minimum/maximum latitudes and longitudes must be specified with the following keys: "min_lat", "min_lon", "max_lat", "max_lon". The default value specifies all latitude and longitude coordinates.

    Returns
    -------
    pd.DataFrame
      A DataFrame containing Raw GLOBE Observer Data of the specified parameters
    """

    if is_valid_latlon_box(latlon_box):
        url = f"https://api.globe.gov/search/v1/measurement/protocol/measureddate/lat/lon/?protocols={protocol}&startdate={start_date}&enddate={end_date}&minlat={str(latlon_box['min_lat'])}&maxlat={str(latlon_box['max_lat'])}&minlon={str(latlon_box['min_lon'])}&maxlon={str(latlon_box['max_lon'])}&geojson=FALSE&sample=FALSE"
    else:
        logging.warning(
            "You did not enter any valid/specific coordinates, so we gave you all the observations for your protocol, date_range, and any countryNames you may have specified.\n"
        )
        url = f"https://api.globe.gov/search/v1/measurement/protocol/measureddate/?protocols={protocol}&startdate={start_date}&enddate={end_date}&geojson=FALSE&sample=FALSE"

    # Downloads data from the GLOBE API
    response = requests.get(url)

    if not response:
        raise RuntimeError(
            "Failed to get data from the API. Double check your specified settings to make sure they are valid."
        )

    # Convert measured date data into datetime
    df = parse_api_data(response.json())
    convert_dates_to_datetime(df)

    if is_clean:
        df = default_data_clean(df, protocol)
    return df


def convert_dates_to_datetime(df):
    date_columns = [col for col in df.columns if "Date" in col or "MeasuredAt" in col]
    for column in date_columns:
        df[column] = pd.to_datetime(df[column], errors="coerce")


def default_data_clean(df, protocol):
    module_mapper = {mosquito_protocol: mhm, landcover_protocol: lc}
    if protocol in module_mapper:
        df = module_mapper[protocol].apply_cleanup(df)
        df = module_mapper[protocol].add_flags(df)
    else:
        logging.warning("The protocol you entered is not supported for cleanup.")

    return df
