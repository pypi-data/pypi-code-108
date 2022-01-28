# File Name: get_data.py
# Author: Thomas Siu

import pandas as pd
from datetime import datetime


def get_data(date_from=None, date_to=None, location=None):
    """Get covid data
    Retrieve covid data in pandas dataframe format
    with the time periods and countries provided.

    Parameters
    ----------
    date_from : str, optional
        Start date of the data range with format 'YYYY-MM-DD'.
        By default 'None' is used to represent 7 days prior to today's date
    date_to : str, optional
        End date of data range with format 'YYYY-MM-DD'.
        By default 'None' is used to represent today's date
    location : list, optional
        List of target country names.
        By default 'None' is used for all countries.

    Returns
    -------
    pandas.DataFrame
        Pandas dataframe of the selected covid data.

    Examples
    --------
    >>> get_data(date_from="2022-01-01",
                date_to="2022-01-07",
                location=["Canada", "China"])
    """
    query = "@date_from <= date <= @date_to"
    url = "https://covid.ourworldindata.org/data/owid-covid-data.csv"

    if date_from is None:
        date_from = (
            pd.to_datetime("today").normalize() - pd.to_timedelta(7, unit="d")
        ).strftime("%Y-%m-%d")

    if date_to is None:
        date_to = pd.to_datetime("today").normalize().strftime("%Y-%m-%d")

    try:
        date_from != datetime.strptime(date_from, "%Y-%m-%d").strftime("%Y-%m-%d")
        #            raise ValueError
    except ValueError:
        raise ValueError(
            "Invalid argument value: date_from must be in format of YYYY-MM-DD. Also check if it is a valid date."
        )
    except TypeError:
        raise TypeError(
            "Invalid argument type: date_from must be in string format of YYYY-MM-DD."
        )

    try:
        date_to != datetime.strptime(date_to, "%Y-%m-%d").strftime("%Y-%m-%d")
        #            raise ValueError
    except ValueError:
        raise ValueError(
            "Invalid argument value: date_to must be in format of YYYY-MM-DD. Also check if it is a valid date."
        )
    except TypeError:
        raise TypeError(
            "Invalid argument type: date_to must be in string format of YYYY-MM-DD."
        )

    error_msg = (
        "Invalid values: date_from should be smaller or equal"
        " to date_to (or today's date if date_to is not specified)."
    )

    if pd.to_datetime(date_to) < pd.to_datetime(date_from):
        raise ValueError(
            error_msg,
        )
    if pd.to_datetime(date_to) > pd.to_datetime("today").normalize():
        raise ValueError("Invalid values: date_to should be smaller or equal to today.")

    if location is not None:

        if not (isinstance(location, list)):
            raise TypeError(
                "Invalid argument type: location must be a list of strings."
            )

        for item in location:
            if not (isinstance(item, str)):
                raise TypeError(
                    "Invalid argument type: values inside location list must be a strings."
                )

        query += " and location in @location"

    try:
        covid_df = pd.read_csv(url, parse_dates=["date"])
    except BaseException:
        return "The link to the data is broken."

    covid_df = covid_df.query(query)
    covid_df = covid_df[~covid_df["iso_code"].str.startswith("OWID")]
    return covid_df
