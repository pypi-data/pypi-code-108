import pandas as pd
import numpy as np
import altair as alt


def plot_price(df):
    """
    Plot the price of the cryptocurrenty inputted over window specified.

    Parameters
    ----------
    df : pandas DataFrame
        Data frame with cryptocurrency name, date and close price.

    Returns
    -------
    plot: plot object
        An altair plot object.

    Examples
    >>> df = retrieve_data(symbol:str="BTC-USDT",
                      time_period:str="1day",
                      start_date:str="2018-01-01",
                      end_date:str="2022-01-10",
                     )
    >>> plot_price(df)
    """
    if "Symbol" not in df.columns:
        raise ValueError(
        "The input data frame does not contain the Symbol column."
        )
    if "Date" not in df.columns:
        raise ValueError(
        "The input data frame does not contain the Date column."
        )
    if "Close" not in df.columns:
        raise ValueError(
        "The input data frame does not contain the Close column."
        )

    Symbol = df.Symbol[0]
    chart = alt.Chart(df).mark_line().encode(
        x=alt.X('Date', title = 'Date'),
        y=alt.Y('Close', title = 'Close Price')
    ).properties(title = Symbol + ': historical close price over time period'
                ).configure_title(fontSize = 18,
                                  anchor = 'start'
                                 ).configure_axis(labelFontSize=10,
                                                  titleFontSize=15
                                                 )
    return chart
