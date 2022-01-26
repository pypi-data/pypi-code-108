import pickle
from datetime import datetime, timezone, timedelta
from typing import Union

import pandas as pd

from powerbot_backtesting.exceptions import NotInCacheError
from powerbot_backtesting.utils.constants import *


def _process_orderbook(key: str,
                       value: pd.DataFrame,
                       directory: str,
                       shortest_interval: bool,
                       timesteps: int,
                       time_unit: str,
                       timestamp: Union[datetime, None],
                       from_timestamp: bool,
                       orderbook_dict: dict[str, pd.DataFrame],
                       use_cached_data: bool):
    """
    Function to process single order book. Return value is appended to collection of order books.

    Returns:
        pd.Dataframe: single order book
    """
    # Setup Parameters
    units = {"hours": 0, "minutes": 0, "seconds": 0, time_unit: timesteps}
    delivery_start = datetime.strptime(key.replace(f"{str(key).split(' - ')[1]}", "").replace(" - ", ":00"),
                                       DATE_YMD_TIME_HMS).replace(tzinfo=timezone.utc)
    timestamp = timestamp.replace(tzinfo=timezone.utc) if timestamp else None
    file_name = key.replace(f"{str(key).split(' ')[0]}", "").replace(":", "-")
    directory = directory.split('\\')
    directory = '\\'.join(directory)

    try:
        if not use_cached_data:
            raise NotInCacheError("Not loading from cache")
        # Check If Data Already Cached
        time_interval = f"{timesteps}{time_unit[0]}" if not shortest_interval else "shortest"
        order_book_clean = pickle.load(open(f"{directory}\\{file_name}_orderbook_{time_interval}.p", "rb"))
        orderbook_dict[key] = order_book_clean

    except (NotInCacheError, FileNotFoundError):
        # Filter out emtpy revisions
        if "orders" in value:
            order_filter = value.orders.map(lambda x: x if x["bid"] or x["ask"] else None)
            value = value.loc[~value.index.isin(order_filter[order_filter.isna()].index)]
        else:
            value = value.loc[~(value.bids.isna()) & ~(value.asks.isna())]

        # Setting Either Starting Point or Specific Timestamp
        start_time = value.as_of.min().replace(minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        time = timestamp if timestamp and from_timestamp \
            else timestamp + timedelta(**{time_unit: timesteps}) if timestamp and not from_timestamp \
            else start_time + timedelta(**{time_unit: timesteps})
        time = start_time + timedelta(**{time_unit: timesteps}) if start_time > time else time

        order_book = {}

        # Transform orders
        df_bid_asks = _orderbook_data_transformation(value)

        # Set interval
        if not df_bid_asks.empty:
            df_bid_asks.as_of = pd.to_datetime(df_bid_asks.as_of)
            # Shortest interval
            # Extract the timestamps
            time_gen = (t.strftime(DATE_YMD_TIME_HMS_F) for t in df_bid_asks.as_of.to_list())

            # Create a filter to shorten dataframe
            orders_del = set()

            # Main Loop
            while (time <= delivery_start if not shortest_interval else (time := next(time_gen, None))):
                # Shorten Bids_Asks
                if len(orders_del) > 0:
                    df_bid_asks = df_bid_asks.loc[~df_bid_asks.order_id.isin(orders_del)]

                # Create New Temporary Dataframe
                if timestamp and not from_timestamp:
                    df_temp = df_bid_asks.loc[df_bid_asks.as_of <= f'{timestamp}']

                else:
                    df_temp = df_bid_asks.loc[(df_bid_asks.as_of >= f'{start_time}') & (df_bid_asks.as_of <= f'{time}')]

                # Delete all orders before the last delta == False
                if not (df_temp := _delta_filter(df_temp, orders_del)).empty:
                    # Extract Order IDs for Quantity = 0 & Update Set Of Order IDs
                    orders_del.update(df_temp.loc[df_temp.quantity == 0].order_id.tolist())

                    # Check For Uniformity of Contract ID
                    if len((contract_ids := df_temp.contract_id.unique().tolist())) == 1:
                        # QC For Temporary Dataframe
                        # Add Filtered Df To Orderbook
                        if timestamp and not from_timestamp:
                            order_book[f"{timestamp}"] = df_temp.loc[~df_temp.order_id.isin(orders_del)]
                        else:
                            order_book[f"{time}"] = df_temp.loc[~df_temp.order_id.isin(orders_del)]

                    else:
                        # If There Are Multiple Contracts In The Same Orderbook -> Create 2 Separate Orderbooks
                        dataframes = []
                        df_check_1 = df_temp.loc[df_temp.contract_id == contract_ids[0]]
                        dataframes.append(df_check_1)
                        df_check_2 = df_temp.loc[df_temp.contract_id == contract_ids[1]]
                        df_check_2 = df_check_2.loc[df_check_2.as_of > f'{time - timedelta(**units)}'] if not shortest_interval else df_check_2
                        dataframes.append(df_check_2)

                        # Quality Control For Temporary Dataframe
                        temp_dataframe_list = []

                        for nr, val in enumerate(dataframes):
                            # Quality Control For Temporary Dataframe
                            df_check = val.loc[~val.order_id.isin(orders_del)]

                            if not df_check.empty:
                                temp_dataframe_list.append(df_check)  # Add Filtered Df To List

                        if len(temp_dataframe_list) == 1:
                            order_book[f"{timestamp if timestamp and not from_timestamp else time}"] = \
                                temp_dataframe_list[0]
                        else:
                            for nr, val in enumerate(temp_dataframe_list):
                                if not nr:
                                    _time = datetime.strptime(time, DATE_YMD_TIME_HMS_F) if shortest_interval else time
                                    order_book[
                                        f"{(timestamp if timestamp and not from_timestamp else _time) - timedelta(milliseconds=1)}"] = val
                                else:
                                    order_book[f"{timestamp if timestamp and not from_timestamp else time}"] = val

                # Progress In Time Or Break Loop If Timestamp Exists
                if timestamp and not from_timestamp:
                    break

                if not shortest_interval:
                    # Adjust Start Time To New Contract if necessary
                    if time == (delivery_start - timedelta(hours=1)):
                        start_time = time

                    # Time Progression
                    time += timedelta(**units)

            # General Quality Control
            # Delete All Order ID Duplicates & Empty Timesteps
            order_book_clean = {
                key: value.sort_values(by=['as_of'], ascending=False).drop_duplicates(subset="order_id", keep="first",
                                                                                      inplace=False) for (key, value) in
                order_book.items()}
            order_book_clean = {key: value for (key, value) in order_book_clean.items() if not value.empty}

        else:
            order_book_clean = df_bid_asks

    orderbook_dict[key] = order_book_clean


def _orderbook_data_transformation(orders: pd.DataFrame) -> pd.DataFrame:
    """
    Function transforms data in passed dataframe to be compatible with process_orderbooks function

    Args:
        orders (pd.DataFrame): DataFrame containing order data

    Returns:
        pd.Dataframe
    """
    if not isinstance(orders, pd.DataFrame):
        return pd.DataFrame()

    bids_asks = []
    # Processing
    if "orders" in orders.columns:
        orders_all = orders["orders"].to_list()
        dates_all = [str(i) for i in orders["as_of"].to_list()]
        deltas = orders.delta.to_list() if "delta" in orders.columns else [1 for _ in range(len(dates_all))]
        for nr, val in enumerate(orders_all):
            for k, v in val.items():
                if v and k in ["ask", "bid"]:
                    for x in v:
                        x["as_of"] = dates_all[nr]
                        x["type"] = "bid" if k == "bid" else "ask"
                        x["delta"] = val.get("delta", deltas[nr])
                        bids_asks.append(x)

    else:
        for nr, row in orders.iterrows():
            for side in ["bids", "asks"]:
                if row[side] and not isinstance(row[side], float):
                    for entry in row[side]:
                        entry["order_id"] = str(entry["order_id"])
                        entry["type"] = side[:-1]
                        entry["as_of"] = row["as_of"].tz_convert(timezone.utc) if row["as_of"].tzinfo else row["as_of"].tz_localize(timezone.utc)
                        entry["delta"] = row["delta"]
                        bids_asks.append(entry)

    df_bid_asks = pd.DataFrame(bids_asks)
    df_bid_asks = df_bid_asks.drop(columns=["exe_restriction", "delivery_area", "order_entry_time"],
                                   errors="ignore")
    return df_bid_asks


def _delta_filter(orderbook: pd.DataFrame, orders_to_delete: set) -> pd.DataFrame:
    """
    Function filters dataframe by orders that are not delta reports. If delta is False, all orders before this order have to be deleted.

    Since delta: false is assigned to a revision of a contract, it can contain more than just one order. Therefore, all orders in a delta: false
    revision have that flag assigned. This function takes this situation in account, loading the last delta: false and going back until the space
    between two orders that have delta: false is bigger than 1.

    Args:
        orderbook (pd.Dataframe): Preliminary order book
        orders_to_delete (set): Set of order IDs that need to be purged from future order books

    Returns:
        pd.Dataframe
    """
    if not (ind := orderbook[(~orderbook.delta) | (orderbook.delta == 0)].index).empty:
        original = orderbook.copy(deep=True)
        last_delta = ind[-1]

        for i in ind[::-1]:
            if i == (last_delta - 1) or i == last_delta:
                last_delta = i
            else:
                break

        orderbook = orderbook.loc[orderbook.index >= last_delta].drop(columns=["delta"])
        orders_to_delete.update(original.loc[~original.order_id.isin(orderbook.order_id)].order_id.tolist())

        return orderbook

    return orderbook.drop(columns=["delta"])
