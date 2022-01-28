# File Name: plot_spec.py
# Author: Rong Li

import pandas as pd
from datetime import datetime
import altair as alt
from dateutil.parser import parse


def plot_spec(
    df, location=["Canada"], val="new_cases", date_from=None, date_to=None, title=None
):
    """
    Create a line chart presenting specific country/countries COVID information
    within a time period

    Parameters
    ----------
    df  : Pandas dataframe
        Pandas dataframe of the selected covid data from get_data()
    location : list, optional
        List of target country names or . By default ["Canada"]
    val : str, optional
        Quantitative values of interests. Must be numeric variable.
        Also known as a 'measure'. By default 'new_cases'
    date_from : str, optional
        Start date of the data range with format in "YYYY-MM-DD" format. By
        default 'None' is used to represent 7 days prior to today's date
    date_to : str, optional
        End date of data range with format in "YYYY-MM-DD" format. By default
        'None' is used to represent today's date
    title : str, optional
        The title of the plot. By default 'None' will be generated based on val

    Returns
    -------
    plot
        Altair line chart created

    Examples
    --------
    >>> plot_spec(df, location=["Canada", "Turkey"], val="new_cases", date_from="2022-01-01", date_to="2022-01-07")

    """
    # init dates if None
    if date_from is None:
        date_from = (
            pd.to_datetime("today").normalize() - pd.to_timedelta(7, unit="d")
        ).strftime("%Y-%m-%d")

    if date_to is None:
        date_to = pd.to_datetime("today").normalize().strftime("%Y-%m-%d")

    # Exception Handling
    if not isinstance(df, pd.DataFrame):
        raise FileNotFoundError("Data not found. There may be a problem with data URL.")

    if not isinstance(location, list):
        raise TypeError("Invalid argument type: location must be a list of strings.")
    for item in location:
        if not (isinstance(item, str)):
            raise TypeError(
                "Invalid argument type: values inside location list must be strings."
            )

    if not isinstance(val, str):
        raise TypeError("Invalid argument type: val must be a string.")

    if df[val].dtypes.kind == "O":
        raise TypeError("Invalid argument type: val must be a numeric variable.")

    try:
        date_from != datetime.strptime(date_from, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(
            "Invalid argument value: date_from must be in format of YYYY-MM-DD. Also check if it is a valid date."
        )

    try:
        date_to != datetime.strptime(date_to, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError(
            "Invalid argument value: date_to must be in format of YYYY-MM-DD. Also check if it is a valid date."
        )

    if pd.to_datetime(date_to) < pd.to_datetime(date_from):
        raise ValueError(
            "Invalid values: date_from should be smaller or equal to date_to (or today's date if date_to is not specified)."
        )
    if pd.to_datetime(date_to) > pd.to_datetime("today").normalize():
        raise ValueError("Invalid values: date_to should be smaller or equal to today.")

    if title is not None:
        if not isinstance(title, str):
            raise TypeError("Invalid argument type: title must be a string.")

    # Parse date
    date_from = parse(date_from)
    date_to = parse(date_to)

    # Convert 'date' to date format
    df["date"] = pd.to_datetime(df["date"])

    # Filter by date
    df = df.query("date >= @date_from & date <= @date_to")

    # Filter by country
    df = df.query("location in @location")

    # Remove aggregated locations
    df = df[~df["iso_code"].str.startswith("OWID")]

    # Create Y axis label
    val_label = val.replace("_", " ").title()

    # init plot title if None
    if title is None:
        title = f"COVID-19 {val_label}"

    # Create line plot
    line = (
        alt.Chart(df, title=title)
        .mark_line()
        .encode(
            x=alt.X(
                "yearmonthdate(date):T", axis=alt.Axis(format="%e %b, %Y"), title="Date"
            ),
            y=alt.Y(val, title=val_label),
            color=alt.Color("location", legend=None),
            tooltip=["location", val],
        )
    )

    # Use direct labels
    order = df.loc[df["date"] == df["date"].max()].sort_values(val, ascending=False)

    text = (
        alt.Chart(order)
        .mark_text(dx=20)
        .encode(
            x=alt.X(
                "yearmonthdate(date):T", axis=alt.Axis(format="%e %b, %Y"), title="Date"
            ),
            y=alt.Y(val, title=val_label),
            text="location",
            color="location",
        )
    )
    plot = line + text
    return plot
