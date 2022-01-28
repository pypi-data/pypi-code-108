import pandas as pd
import altair as alt
from dateutil.parser import parse


def plot_summary(
    df,
    var="location",
    val="new_cases",
    fun="sum",
    date_from=None,
    date_to=None,
    top_n=5,
):
    """Generate summary plot
    Create a horizontal bar chart summarising a specified variable and value
    within a time period

    Parameters
    ----------
    df  : Pandas dataframe
        Pandas dataframe of the selected covid data from get_data()
    var : str, optional
        Qualitative values to segment data. Must be a categorical variable.
        Also known as a 'dimension'. By default 'location'
    val : str, optional
        Quantitative values to be aggregated. Must be numeric variable.
        Also known as a 'measure'. By default 'new_cases'
    fun : str, optional
        Aggregation function for val, by default 'sum'
    date_from : str, optional
        Start date of the data range with format 'YYYY-MM-DD'. By default 'None' is used to represent 7 days prior to today's date
    date_to : str, optional
        End date of data range with format 'YYYY-MM-DD'. By default 'None' is used to represent today's date
    top_n : int, optional
        Specify number of qualitative values to show, by default 5

    Returns
    -------
    altair.Chart
        Altair bar plot for the specified variables and period

    Example
    -------
    >>> plot_summary(df, var="location", var="new_cases", fun="sum", date_from="2022-01-01", date_to="2022-01-15", top_n=10)
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
        raise FileNotFoundError("Data not found! There may be a problem with data URL.")

    if not isinstance(var, str):
        raise TypeError("var needs to be of str type!")

    if not isinstance(val, str):
        raise TypeError("val needs to be of str type!")

    if not isinstance(fun, str):
        raise TypeError("fun needs to be of str type!")

    if df[var].dtypes.kind != "O":
        raise TypeError("var needs to be a categorical variable!")

    if df[val].dtypes.kind == "O":
        raise TypeError("val needs to be a numeric variable!")

    if not isinstance(top_n, int) or top_n <= 0:
        raise ValueError("top_n must be an integer bigger than zero")

    if pd.to_datetime(date_to) < pd.to_datetime(date_from):
        raise ValueError(
            "Invalid values: date_from should be smaller or equal to date_to (or today's date if date_to is not specified)."
        )
    if pd.to_datetime(date_to) > pd.to_datetime("today").normalize():
        raise ValueError("Invalid values: date_to should be smaller or equal to today.")

    # Parse date, else raise ValueError
    date_from = parse(date_from)
    date_to = parse(date_to)

    # Convert 'date' to date format
    df["date"] = pd.to_datetime(df["date"])

    # Filter by date
    df = df.query("date >= @date_from & date <= @date_to")

    # Remove aggregated locations
    df = df[~df["iso_code"].str.startswith("OWID")]

    # Aggregation
    df_plot = df.groupby(var).agg({val: fun})[val].nlargest(top_n)
    df_plot = df_plot.to_frame().reset_index()

    y_lab = var.replace("_", " ").title()
    x_lab = val.replace("_", " ").title()
    title = f"Top {top_n} {y_lab} by {x_lab}"

    return (
        alt.Chart(df_plot, title=title)
        .mark_bar()
        .encode(y=alt.Y(var, sort="x", title=y_lab), x=alt.X(val, title=x_lab))
    )
