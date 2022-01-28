import pandas as pd
import altair as alt
import datetime
from datetime import date
from bccovideda.get_data import get_data
alt.data_transformers.enable('data_server')
alt.renderers.enable('html')


def plot_hist_by_cond(startDate, endDate, condition):
    """
    Plots the number of Covid19 cases with respect to the condition(per Age Group
    or Region) using histogram for the period specified by startDate and endDate

    Parameters
    ----------
    startDate : string
                the start date of the period 
                (no earlier than '2020-01-29')
    endDate   : string
                the end date of the period 
                (no later than today)
    condition : string
                Available condition - Age, Region

    Returns
    -------
    plot : altair.Chart object
           An altair plot object displaying histogram

    Examples
    --------
    >>> plot_hist_by_cond("2021-01-01", "2021-12-31", "Age")
    """

    # test input type
    if not isinstance(startDate, str):
        raise TypeError("'startDate' should be string.")
    if not isinstance(endDate, str):
        raise TypeError("'endDate' should be string.")
    if not isinstance(condition, str):
        raise TypeError("'endDate' should be string.")

    # test input format
    try:
        datetime.datetime.strptime(startDate, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")
    try:
        datetime.datetime.strptime(endDate, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")

    covid = get_data()

    start_dt = date.fromisoformat(startDate)
    end_dt = date.fromisoformat(endDate)
    earliest_dt = date.fromisoformat("2020-01-29")

    # test input value
    if start_dt > end_dt:
        raise ValueError("startDate should not be later than endDate")
    if start_dt < earliest_dt:
        raise ValueError("startDate should not be earlier than 2020-01-29")
    if end_dt > date.today():
        raise ValueError("endDate should not be later than today")

    mask = (covid["Reported_Date"] > startDate) & (
        covid["Reported_Date"] <= endDate)
    temp = covid.loc[mask]

    age_group_label = [
        '90+', '80-89', '70-79', '60-69', '50-59', '40-49', '30-39',
        '20-29', '10-19', '<10'
    ]

    region_label = [
        'Fraser', 'Vancouver Coastal', 'Vancouver Island', 'Interior',
        'Northern', 'Out of Canada'
    ]

    plot = 0   # plot initialized to prevent UnboundLocalError

    if condition == "Age":
        plot = alt.Chart(temp, title="Number of Cases by Age Group").mark_bar().encode(
            y=alt.Y("Age_Group", sort=age_group_label, title="Age Group"),
            x=alt.X("count()", title="Number of Cases"))
    elif condition == "Region":
        plot = alt.Chart(temp, title="Number of Cases by Region").mark_bar().encode(
            y=alt.Y("HA", sort=region_label, title="Region"),
            x=alt.X("count()", title="Number of Cases"))
    else:
        raise ValueError('Condition should be "Age" or "Region"')

    return plot
