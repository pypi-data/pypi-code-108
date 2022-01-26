from typing import Union

import numpy as np
import pandas as pd
import plotly.graph_objects as go


def plot_ohlc(ohlc_data: dict[str, pd.DataFrame],
              visualization: str = "candlestick",
              ohlc_key: Union[int, str] = 0) -> Union[go.Figure, None]:
    """
    Creates a plotly plot of all ohlc data to be displayed by Dash server. Set ohlc_key to change displayed
    dataframe.

    Args:
        ohlc_data (dict{key: DataFrame}): OHLC Data
        visualization (str): Type of visualization, either candlestick or ohlc
        ohlc_key (int/ str): Dictionary key

    Returns:
        Plotly plot
    """
    # Check
    empty_ohlc = [k for k, v in ohlc_data.items() if v.empty]
    ohlc_data = {k: v for k, v in ohlc_data.items() if not v.empty}
    if not ohlc_data:
        raise ValueError("All ohlc objects are empty!")
    if empty_ohlc:
        print(f"Warning: The following ohlc objects are empty and have been removed: {empty_ohlc}")

    visualization = "candlestick" if not visualization in ["candlestick", "ohlc"] else visualization

    mapping = {"candlestick": go.candlestick,
               "ohlc": go.Ohlc}

    # Setup
    try:
        ohlc_key = [*ohlc_data][ohlc_key] if isinstance(ohlc_key, int) else ohlc_key
    except (IndexError, TypeError):
        ohlc_key = [*ohlc_data][0]

    ohlc_data = ohlc_data[ohlc_key]

    # Plotting ohlc-Diagram with Plotly
    try:
        fig = go.Figure(data=mapping[visualization](x=ohlc_data.index,  # Alternative: go.ohlc()
                                            open=ohlc_data['open'],
                                            high=ohlc_data['high'],
                                            low=ohlc_data['low'],
                                            close=ohlc_data['close']))

        fig.update_layout(title='OHLC-Chart', yaxis_title='Price per MWh')
        return fig
    except:
        return None

def plot_orderbook(orderbooks: dict[str, dict[str, pd.DataFrame]],
                   orderbook_key: Union[int, str] = 0,
                   timestamp: Union[int, str] = -1) -> Union[go.Figure, None]:
    """
        Creates a plotly plot of a single order book to be displayed by Dash server. Use order book_key to specify an
        order book and timestamp to specify the timeframe to display.

    Args:
        orderbooks (dict{key: DataFrame}): Order books
        orderbook_key (int): Dictionary key
        timestamp (int): Order book Key

    Returns:
        Plotly plot
    """
    # Check
    empty_ob = [k for k, v in orderbooks.items() if isinstance(v, pd.DataFrame) or not v]
    orderbooks = {k: v for k, v in orderbooks.items() if not isinstance(v, pd.DataFrame) and v}
    if not orderbooks:
        raise ValueError("All order books are empty!")
    if empty_ob:
        print(f"Warning: The following order books are empty and have been removed: {empty_ob}")

    # Setup
    line_shape = 'hv'
    mode = 'lines+markers'
    try:
        orderbook_key = [*orderbooks][orderbook_key] if isinstance(orderbook_key, int) else orderbook_key
    except (IndexError, TypeError):
        orderbook_key = [*orderbooks][0]

    try:
        timestamp = [*orderbooks[orderbook_key]][timestamp] if isinstance(timestamp, int) else timestamp
    except (IndexError, TypeError):
        timestamp = [*orderbooks][0][-1]

    orders = {"bid": {"name": "Bids", "sort_order": [True, False]}, "ask": {"name": "Asks", "sort_order": [True, True]}}

    # Plotting With Plotly
    df_plot = orderbooks[orderbook_key][timestamp].sort_values(by=['price'], ascending=True)
    fig = go.Figure()

    try:
        for i in ["bid", "ask"]:
            prices = df_plot.price[df_plot.type == i].to_list()
            if len(prices) == 0:
                continue
            quantities = df_plot.quantity[df_plot.type == i].to_list()

            # Add Quantities
            if i == "bid":
                quantities_added = np.cumsum(quantities[::-1])[::-1]
            else:
                quantities_added = np.cumsum(quantities)

            temp_dict = {}
            for x, y in enumerate(prices):
                temp_dict[x] = [y, quantities_added[x]]

            df_temp_plot = pd.DataFrame(temp_dict).T.sort_values(by=[0, 1], ascending=orders[i]["sort_order"])
            df_temp_plot.columns = ["price", "quantity"]

            fig.add_trace(
                go.Scatter(x=df_temp_plot.price, y=df_temp_plot.quantity, name=orders[i]["name"], fill='tozeroy',
                           line_shape=line_shape, mode=mode))  # fill down to xaxis

        fig.update_layout(title=f'Orderbook {orderbook_key} - {timestamp.split(" ")[1]}',
                          xaxis_title="Price per MWh", yaxis_title='Quantity')

    except:
        fig = go.Figure()
        fig.add_trace(go.Scatter())
        fig.update_layout(title=f'Orderbook {orderbook_key}', xaxis_title="Price per MWh", yaxis_title='Quantity')

    return fig


def ohlc_table(ohlc_data: dict[str, pd.DataFrame], ohlc_key: int = 0):
    """
    Creates a custom DataFrame to be displayed by Dash server.

    Args:
        ohlc_data (dict{key: DataFrame}): OHLC Data
        ohlc_key (int): Dictionary key

    Returns:
        DataFrame
    """
    # Check
    empty_ohlc = [k for k, v in ohlc_data.items() if v.empty]
    ohlc_data = {k: v for k, v in ohlc_data.items() if not v.empty}
    if not ohlc_data:
        raise ValueError("All ohlc objects are empty!")
    if empty_ohlc:
        print(f"Warning: The following ohlc objects are empty and have been removed: {empty_ohlc}")

    # Setup
    try:
        ohlc_key = [*ohlc_data][ohlc_key]
    except (IndexError, TypeError):
        ohlc_key = [*ohlc_data][0]

    ohlc_contract_data = ohlc_data[ohlc_key].reset_index()
    ohlc_contract_data = ohlc_contract_data.rename(columns={"index": "Timestamp"})

    return ohlc_contract_data


def plot_volume_history(trade_data: dict[str, pd.DataFrame],
                        trade_key: Union[int, str] = 0) -> Union[go.Figure, None]:
    """
    Creates a plotly plot of the trade volume for a single contract to be displayed by Dash server.

    Args:
        trade_data (dict{key: DataFrame}):  Trade Data
        trade_key (int/str): Dictionary key

    Returns:
        Plotly plot
    """
    # Check
    empty_trades = [k for k, v in trade_data.items() if v.empty]
    trade_data = {k: v for k, v in trade_data.items() if not v.empty}
    if not trade_data:
        raise ValueError("There are no trades!")
    if empty_trades:
        print(f"Warning: The following trade collections are empty and have been removed: {empty_trades}")

    line_shape = 'hv'
    mode = 'lines+markers'
    try:
        trade_key = [*trade_data][trade_key] if isinstance(trade_key, int) else trade_key
    except (IndexError, TypeError):
        trade_key = [*trade_data][0]

    df_trade = trade_data[trade_key].sort_values(by=["exec_time"], ascending=[True])
    quantities = np.cumsum(df_trade["quantity"].tolist())

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=df_trade.exec_time, y=quantities, name="trades", fill='tozeroy', line_shape=line_shape, mode=mode,
                   line_color='rgb(34,139,34)'))  # fill down to xaxis
    fig.update_layout(title="Trade Volume", xaxis_title="Time", yaxis_title='Quantity')

    return fig