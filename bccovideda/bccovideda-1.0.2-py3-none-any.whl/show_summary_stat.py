import pandas as pd
from datetime import date
from bccovideda.get_data import get_data


def show_summary_stat(startDate, endDate):
    """
    Shows summary statistics for the Covid19 cases in BC for the period
    specified by startDate and endDate (format: YYYY-MM-DD).

    Parameters
    ----------
    startDate : string
                the start date of the period 
                (no earlier than '2020-01-29')
    endDate   : string
                the end date of the period 
                (no later than today)


    Returns
    -------
    pandas.DataFrame
        Data frame containing summary statistics with the followings:
        total_cases_count, latest_date, latest_daily_cases_count, 
        max_date, max_daily_cases_count, min_date, min_daily_cases_count, 
        max_age_group, max_age_group_count, min_age_group, min_age_group_count,
        max_region, max_region_count, min_region, min_region_count
    None if there is no data matching the specified date range

    Examples
    -------
    >>> show_summary_stat("2022-01-01", "2022-01-13")

    """
    # input validation
    if not isinstance(startDate, str):
        raise TypeError("'startDate' should be of type 'str'.")
    if not isinstance(endDate, str):
        raise TypeError("'endDate' should be of type 'str'.")

    start_dt = date.fromisoformat(startDate)
    end_dt = date.fromisoformat(endDate)
    earliest_dt = date.fromisoformat("2020-01-29")

    if start_dt > end_dt:
        raise ValueError("startDate should not be later than endDate")
    if start_dt < earliest_dt:
        raise ValueError("startDate should not be earlier than 2020-01-29")
    if end_dt > date.today():
        raise ValueError("endDate should not be later than today")

    # download data
    df = get_data()

    mask = (df["Reported_Date"] >= startDate) & (
        df["Reported_Date"] <= endDate)
    df = df.loc[mask]

    # return None if it is an empty dataframe
    if len(df) == 0:
        return None

    # total_cases_count
    total = len(df)

    # count by date
    count_df = df["Reported_Date"].value_counts(sort=True, ascending=True)
    count_df_len = len(count_df)
    # latest_date, latest_daily_cases_count
    latest_date = count_df.index[count_df_len - 1]
    latest_date_count = count_df.iloc[count_df_len - 1]

    # max_date, max_daily_cases_count
    max_date = count_df.idxmax()
    max_daily_cases_count = count_df.max()
    # min_date, min_daily_cases_count
    min_date = count_df.idxmin()
    min_daily_cases_count = count_df.min()

    # count by age group
    age_df = df["Age_Group"].value_counts()
    # max_age_group, max_age_group_count
    max_age_group = age_df.idxmax()
    max_age_group_count = age_df.max()
    # min_age_group, min_age_group_count
    min_age_group = age_df.idxmin()
    min_age_group_count = age_df.min()

    # count by region
    region_df = df["HA"].value_counts()
    # max_region, max_region_count
    max_region = region_df.idxmax()
    max_region_count = region_df.max()

    # min_region, min_region_count,
    min_region = region_df.idxmin()
    min_region_count = region_df.min()

    summary_df = pd.DataFrame(
        {
            "total_cases_count": [total],
            "latest_date": [latest_date],
            "latest_daily_cases_count": [latest_date_count],
            "max_date": [max_date],
            "max_daily_cases_count": [max_daily_cases_count],
            "min_date": [min_date],
            "min_daily_cases_count": [min_daily_cases_count],
            "max_age_group": [max_age_group],
            "max_age_group_count": [max_age_group_count],
            "min_age_group": [min_age_group],
            "min_age_group_count": [min_age_group_count],
            "max_region": [max_region],
            "max_region_count": [max_region_count],
            "min_region": [min_region],
            "min_region_count": [min_region_count],
        }
    )

    return summary_df
