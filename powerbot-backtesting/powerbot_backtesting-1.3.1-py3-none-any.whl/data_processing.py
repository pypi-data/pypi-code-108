import gzip
import json
import re
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
from datetime import datetime, timezone
from typing import Union

import numpy as np
import pandas as pd
from powerbot_client import ApiClient, ContractApi
from tqdm import tqdm

from powerbot_backtesting.data_acquisition import get_public_trades_by_days
from powerbot_backtesting.models import HistoryApiClient
from powerbot_backtesting.utils import _find_cache, _cache_data, _process_orderbook
from powerbot_backtesting.utils.constants import *


def get_orders(contract_hist_data: dict[str, pd.DataFrame],
               append_all: bool = False) -> dict[str, pd.DataFrame]:
    """
    Extracts all order data from contract history as is, without performing any quality control. If necessary, orders for all contracts can be
    appended to a single dataframe.

    Args:
        contract_hist_data (dict): Dictionary of Dataframes containing Contract History Data
        append_all (bool): True if one dataframe containing all orders should be returned

    Returns:
        dict{key: pd.DataFrame}: Dictionary of DataFrames
    """
    order_list = {}

    for key, value in tqdm(contract_hist_data.items(), desc="Extracting Orders", unit="time periods", leave=False):
        value.replace(np.nan, 0, inplace=True)
        bids_asks = []
        if "orders" in value:
            orders_all = value["orders"].to_list()
            for nr, orders in enumerate(orders_all):
                for k, v in orders.items():
                    if v and k in ["bid", "ask"]:
                        for x in v:
                            x["type"] = k
                            x["order_id"] = str(x["order_id"])
                            x["best_bid"] = round(value.loc[nr, "best_bid_price"], 2)
                            x["best_bid_qty"] = round(value.loc[nr, "best_bid_quantity"], 2)
                            x["best_ask"] = round(value.loc[nr, "best_ask_price"], 2)
                            x["best_ask_qty"] = round(value.loc[nr, "best_ask_quantity"], 2)
                            try:
                                x["vwap"] = round(value.loc[nr, "vwap"], 2)
                            except:
                                pass
                            x["as_of"] = value.loc[nr]["as_of"].tz_convert(timezone.utc) if value.loc[nr]["as_of"].tzinfo else \
                                value.loc[nr]["as_of"].tz_localize(timezone.utc)
                            bids_asks.append(x)
        else:
            value = [v.to_dict() for r, v in value.iterrows()]
            for nr, coll in enumerate(value):
                for k, v in coll.items():
                    if v and k in ["bids", "asks"]:
                        for x in v:
                            x["type"] = k[:-1]
                            x["order_id"] = str(x["order_id"])
                            x["best_bid"] = round(value[nr].get("best_bid", 0), 2)
                            x["best_bid_qty"] = round(value[nr].get("best_bid_qty", 0), 2)
                            x["best_ask"] = round(value[nr].get("best_ask", 0), 2)
                            x["best_ask_qty"] = round(value[nr].get("best_ask_qty", 0), 2)
                            x["vwap"] = round(value[nr].get("vwap", 0), 2)
                            x["as_of"] = value[nr]["as_of"].tz_convert(timezone.utc) if value[nr]["as_of"].tzinfo else \
                                value[nr]["as_of"].tz_localize(timezone.utc)
                            bids_asks.append(x)

        order_list[key] = bids_asks

    orders = {k: pd.DataFrame(v) for k, v in order_list.items()}

    if append_all:
        all_orders = []

        for k, v in orders.items():
            v["time_range"] = k
            all_orders.append(v)
        return pd.concat(all_orders)

    return orders


def get_ohlc_data(trade_data: dict[str, pd.DataFrame],
                  timesteps: int,
                  time_unit: str,
                  delivery_area: str = None,
                  api_client: Union[ApiClient, HistoryApiClient] = None,
                  use_cached_data: bool = True,
                  caching: bool = True,
                  gzip_files: bool = True,
                  one_file: bool = False) -> dict[str, pd.DataFrame]:
    """
    Converts trade data into Open-High-Low-Close format in the specified timesteps.

    Args:
        trade_data (dict{key: DataFrame}): Dictionary of Dataframes containing Contract Trade Data
        timesteps (int): Timesteps to group Trades by
        time_unit (str): Time units for timesteps (either hours, minutes or seconds)
        delivery_area (str): Area Code for Delivery Area (not needed when loading from historic cache)
        api_client: PowerBot ApiClient
        use_cached_data (bool): If True, function tries to load data from cache wherever possible
        caching (bool): True if data should be cached
        gzip_files (bool): True if cached files should be gzipped
        one_file (bool): True if data should be cached in a single JSON file

    Returns:
        dict{key: DataFrame}: Dictionary of DataFrames
    """
    # Setup Parameters
    all_ohlc_data = {}
    host = api_client.configuration.host if isinstance(api_client, ApiClient) else None
    environment = host.split("/")[2].split(".")[0] if host else "prod"
    exchange = host.split("/")[4] if host else api_client.exchange if isinstance(api_client, HistoryApiClient) else \
        list(trade_data.values())[0].exchange[0]
    file_ending = ".gz" if gzip_files else ""
    delivery_area = api_client.delivery_area if isinstance(api_client, HistoryApiClient) else delivery_area

    # Check if __cache__ already exists
    cache_path = _find_cache()

    for key, value in tqdm(trade_data.items(), desc="Processing Trades", unit="time periods", leave=False):
        # Check If Data Already Cached
        delivery_date = datetime.strptime(key.split(" ")[0], DATE_YMD)
        year_month = delivery_date.strftime(DATE_YM)
        day_month = delivery_date.strftime(DATE_MD)
        file_name = key.replace(f"{str(key).split(' ')[0]}", "").replace(":", "-")
        data_ohlc = None

        if use_cached_data:
            for i in [".json.gz", ".json"]:
                if cache_path.joinpath(f'{environment}\\{exchange}_{delivery_area}\\{year_month}\\{day_month}'
                                       f'\\processed\\{file_name}_ohlc_{timesteps}{time_unit[0]}{i}').exists():
                    data_ohlc = pd.read_json(cache_path.joinpath(f'{environment}\\{exchange}_{delivery_area}\\'
                                                                 f'{year_month}\\{day_month}\\processed\\'
                                                                 f'{file_name}_ohlc_{timesteps}{time_unit[0]}{i}'),
                                             dtype=False)

        if isinstance(data_ohlc, pd.DataFrame):
            data_ohlc.rename(columns={0: 'exec_time'}, inplace=True)
            all_ohlc_data[key] = data_ohlc

        else:
            data_ohlc = value.set_index('exec_time')
            data_ohlc = data_ohlc['price'].resample(f'{timesteps}{time_unit[0]}').ohlc() if time_unit != "minutes" \
                else data_ohlc['price'].resample(f'{timesteps}{time_unit[:3]}').ohlc()
            data_ohlc = data_ohlc.dropna(how='all')

            # Append to complete OHLC collection
            all_ohlc_data[key] = data_ohlc

    # Cache Data as JSON
    if caching:
        _cache_data("ohlc", all_ohlc_data, delivery_area, exchange=exchange, api_client=api_client,
                    gzip_files=gzip_files, timesteps=timesteps, time_unit=time_unit[0], as_csv=False)

    # Saving Complete OHLC Data as JSON
    if one_file and trade_data:
        # Take Day of Delivery Start
        # Parameters
        contract_times = sorted([i for i in [*trade_data]])
        first_contract = datetime.strptime(
            contract_times[0].replace(f"{str(contract_times[0]).split(' - ')[1]}", "").replace(" - ", ":00"),
            DATE_YMD_TIME_HMS)
        last_contract = datetime.strptime(
            contract_times[-1].replace(f"{str(contract_times[-1]).split(' ')[1]}", "").replace(" - ", "") + ":00",
            DATE_YMD_TIME_HMS)

        year_month = first_contract.strftime(DATE_YM)
        day_month = first_contract.strftime(DATE_MD)

        if len(contract_times) == 1:
            first_contract = first_contract.strftime(DATE_YMD_TIME_HMS_ALT)
            last_contract = None
        else:
            if first_contract.strftime(DATE_D) != last_contract.strftime(DATE_D):
                first_contract = first_contract.strftime(DATE_YMD_TIME_HM_ALT)
                last_contract = last_contract.strftime(DATE_YMD_TIME_HM_ALT)
            else:
                first_contract = first_contract.strftime(TIME_HM_ALT)
                last_contract = last_contract.strftime(TIME_HM_ALT)

        filename = f'all_ohlc_{first_contract} - {last_contract}_{timesteps}{time_unit[0]}.json.gz' \
            if last_contract else f'all_ohlc_{first_contract}_{timesteps}{time_unit[0]}.json{file_ending}'

        if not cache_path.joinpath(
                f"{environment}\\{exchange}_{delivery_area}\\{year_month}\\{day_month}\\processed\\{filename}").exists():
            if "gz" in file_ending:
                with gzip.open(cache_path.joinpath(
                        f"{environment}\\{exchange}_{delivery_area}\\{year_month}\\{day_month}\\processed\\{filename}"),
                        'wt', encoding="ascii") as f:
                    json.dump(
                        {key: {k: v.to_json() for (k, v) in value.items()} for (key, value) in all_ohlc_data.items()},
                        f, default=str)
            else:
                with open(cache_path.joinpath(
                        f"{environment}\\{exchange}_{delivery_area}\\{year_month}\\"
                        f"{day_month}\\processed\\{filename}"), 'wt',
                        encoding="ascii") as f:
                    json.dump(
                        {key: {k: v.to_json() for (k, v) in value.items()} for (key, value) in all_ohlc_data.items()},
                        f, default=str)

    return all_ohlc_data


def get_orderbooks(contract_hist_data: dict[str, pd.DataFrame],
                   delivery_area: str = None,
                   timesteps: int = 15,
                   time_unit: str = "minutes",
                   shortest_interval: bool = False,
                   timestamp: list[datetime] = None,
                   from_timestamp: bool = False,
                   api_client: Union[ApiClient, HistoryApiClient] = None,
                   use_cached_data: bool = True,
                   caching: bool = True,
                   as_json: bool = False,
                   concurrent: bool = False) -> dict[str, pd.DataFrame]:
    """
    Converts contract history data into order books in the specified timesteps. If no API client is passed, the function will automatically assume
    that the data is production data.

    Please be aware that optimally only data from one exchange at a time should be used (e.g. only EPEX).

    To generate specific order books for a position closing algorithm, the timestamp and from_timestamp parameters can
    be used.

    Args:
        contract_hist_data (dict{key: DataFrame}): Dictionary of Dataframes containing Contract History Data
        delivery_area (str): Area Code for Delivery Area (not needed when loading from historic cache)
        timesteps (int): Timesteps to group order books by
        time_unit (str): Time units for timesteps (either hours, minutes or seconds)
        timestamp (list[datetime]): List of timestamps to generate order books at/ from
        from_timestamp (bool): True if timestamp serves as starting point for order book generation
        api_client: PowerBot ApiClient
        use_cached_data (bool): If True, function tries to load data from cache wherever possible
        caching (bool): True if single order books should be cached as JSON
        as_json (bool): True if complete order book should be cached as JSON
        concurrent (bool): True if processing should be multithreaded -> possible performance gain on big datasets and good CPU

    Returns:
        dict{key: DataFrame}: Dictionary of DataFrames
    """
    # Initial check
    if not contract_hist_data:
        raise ValueError("Warning: Provided order data is empty")
    if concurrent and len(contract_hist_data) < 20:
        print("Warning: using multithreading on a small dataset might increase processing time. Minimum recommended size: >20 contract periods\n"
              "Defaulting to normal processing.")

    # Setup
    all_order_books = {}
    host = api_client.configuration.host if isinstance(api_client, ApiClient) else None
    environment = host.split("/")[2].split(".")[0] if host else "prod"
    exchange = host.split("/")[4] if host else api_client.exchange if isinstance(api_client, HistoryApiClient) else \
        list(contract_hist_data.values())[0].exchange[0]
    delivery_area = api_client.delivery_area if isinstance(api_client, HistoryApiClient) else delivery_area

    # Parameters
    contract_times = sorted([i for i in [*contract_hist_data]])
    first_contract = datetime.strptime(
        contract_times[0].replace(f"{str(contract_times[0]).split(' - ')[1]}", "").replace(" - ", ":00"), DATE_YMD_TIME_HMS)
    last_contract = datetime.strptime(
        contract_times[-1].replace(f"{str(contract_times[-1]).split(' ')[1]}", "").replace(" - ", "") + ":00", DATE_YMD_TIME_HMS)

    year_month = first_contract.strftime(DATE_YM)
    day_month = first_contract.strftime(DATE_MD)

    if len(contract_times) == 1:
        first_contract = first_contract.strftime(DATE_YMD_TIME_HM_ALT)
        last_contract = None
    else:
        if first_contract.strftime(DATE_D) != last_contract.strftime(DATE_D):
            first_contract = first_contract.strftime(DATE_YMD_TIME_HM)
            last_contract = last_contract.strftime(DATE_MD_TIME_HM)
        else:
            first_contract = first_contract.strftime(TIME_HM_ALT)
            last_contract = last_contract.strftime(TIME_HM_ALT)

    # Check if __cache__ already exists
    cache_path = _find_cache()
    new_dir = cache_path.joinpath(f"{environment}\\{exchange}_{delivery_area}\\{year_month}\\{day_month}\\processed")

    if concurrent and len(contract_hist_data) >= 20:
        # Define a simple function to submit to thread pool executor
        def process_multiple(contract_hist_data):
            for nr, (key, value) in enumerate(
                    tqdm(contract_hist_data.items(), desc="Processing Orders (multithreading)", position=0, unit="time periods", leave=False)):
                _process_orderbook(key, value, str(new_dir), shortest_interval, timesteps, time_unit, timestamp[nr] if timestamp else None,
                                   from_timestamp,
                                   all_order_books, use_cached_data)

        # Define a splitter function that splits data into appropriately sized chunks without losing data
        def splitter(data, split):
            counter = 0
            out = []
            while counter != split:
                out.append({k: v for k, v in data.items() if k in [*data][int(len(data) / split) * counter:int(len(data) / split) * (counter + 1)]})
                counter += 1

            # Distribute rest of data
            if len(data) % split:
                rest = len(data) - sum([len(i) for i in out])
                for i in range(rest):
                    out[i] |= {[*data][-(i + 1)]: data[[*data][-(i + 1)]]}
            return out

        # Processing Concurrently with ThreadPoolExecutor & waiting for results
        executor = ThreadPoolExecutor()
        results = [executor.submit(process_multiple, chunk) for chunk in splitter(contract_hist_data, executor._max_workers)]
        wait(results, return_when=ALL_COMPLETED)

    else:
        # Processing Synchronously
        for nr, (key, value) in enumerate(tqdm(contract_hist_data.items(), desc="Processing Orders", unit="time periods", leave=False)):
            _process_orderbook(key, value, str(new_dir), shortest_interval, timesteps, time_unit, timestamp[nr] if timestamp else None,
                               from_timestamp, all_order_books,
                               use_cached_data)

    # Cache Data as pickle
    if caching:
        _cache_data("orderbook", all_order_books, delivery_area, exchange=exchange, api_client=api_client, gzip_files=False, timesteps=timesteps,
                    time_unit=time_unit[0], shortest_interval=shortest_interval, as_json=False, as_pickle=True)

    # Saving Complete Orderbook as JSON
    if as_json:
        new_dir.mkdir(parents=True, exist_ok=True)

        filename = f'orderbook_{first_contract} - {last_contract}_{timesteps}{time_unit[0]}.json.gz' \
            if last_contract else f'orderbook_{first_contract}_{timesteps}{time_unit[0]}.json.gz'
        with gzip.open(new_dir.joinpath(filename), 'wt', encoding="ascii") as f:
            json.dump({key: {k: v.to_json() for (k, v) in value.items()} for (key, value) in all_order_books.items()},
                      f, default=str)

    return all_order_books


def calc_trade_vwap(api_client: ApiClient,
                    contract_time: str,
                    delivery_area: str,
                    trade_data: dict[str, pd.DataFrame] = None,
                    time_from: datetime = None,
                    previous_days: int = 10,
                    contract_id: str = None,
                    index: str = "ID3") -> pd.DataFrame:
    """
    Function gets trades for a certain contract for X previous days in the same delivery period and calculates their VWAP for ID3 or ID1 or all.
    Generates a new list of trades for these contracts. Can take either a time period or a specific contract ID to load data for.

    If previous days is 0, only the trades for the original time period/ contract will be loaded.

    Can also be called directly from get_public_trades with parameter 'add_vwap' to add VWAP to loaded trades.

    Args:
        api_client: PowerBot ApiClient
        contract_time (str): hourly, half-hourly or quarter-hourly
        delivery_area (str): Area Code for Delivery Area
        trade_data (dict[str, pd.DataFrame]: Dictionary of Dataframes containing Contract Trade Data
        time_from (str/ datetime): yyyy-mm-dd hh:mm:ss
        previous_days (int): Amount of previous days to load data
        contract_id (str): ID of specific Contract
        index (str): all, ID3, ID1

    Returns:
        DataFrame: Trade Data with added calculated fields
    """
    if not trade_data and contract_time == "all":
        raise ValueError("Contract time can only be one of hourly, half-hourly or quarter-hourly if no trade data is given")

    # Setup
    indices = {"all": 1980, "ID3": 180, "ID1": 60}
    contract_api = ContractApi(api_client)

    # Create Empty Dataframe
    all_trade_data = []

    # Get Delivery Start If Contract ID was passed
    if contract_id:
        if not isinstance(contract_id, str):
            raise TypeError("contract_id has to be a string")
        time_from = str(contract_api.find_contracts(contract_id=[contract_id])[0].delivery_start).replace("+00:00", "")

    # Get Trade Data
    trade_data = trade_data if trade_data else get_public_trades_by_days(api_client=api_client,
                                                                         time_from=time_from,
                                                                         previous_days=previous_days,
                                                                         delivery_area=delivery_area,
                                                                         contract_time=contract_time)

    # Processing
    for key, value in tqdm(trade_data.items(), desc="Calculating Trade VWAPs", unit="time periods", leave=False):
        # Time Difference In Minutes
        time = datetime.strptime(key.replace(f"{str(key).split(' - ')[1]}", "").replace(" - ", ":00"),
                                 DATE_YMD_TIME_HMS)
        time_diff = [round((time.replace(tzinfo=None) - i.replace(tzinfo=None)).total_seconds() / 60, 2) for i in
                     value.exec_time]
        value["time_diff"] = time_diff
        all_trade_data.append(value)

    all_trade_data = pd.concat(all_trade_data)
    all_trade_data = all_trade_data.loc[all_trade_data["time_diff"] <= indices[index]].sort_values(by=['time_diff'],
                                                                                                   ascending=False)
    total_quantity = all_trade_data.quantity.sum()
    all_quantities = all_trade_data.quantity.tolist()
    all_prices = all_trade_data.price.tolist()

    target_volume = []
    cumulated_quantities = []
    calculated_vwaps = []
    cum_weighted_price = 0

    for nr, item in enumerate(all_quantities):
        cum_sum = round(sum(all_quantities[:nr + 1]), 2)
        cum_weighted_price += all_prices[nr] * all_quantities[nr]
        calculated_vwaps.append(round(cum_weighted_price / cum_sum, 2))
        cumulated_quantities.append(cum_sum)
        target_volume.append(round(cum_sum / total_quantity, 4))

    all_trade_data["cumulated_quantity"] = cumulated_quantities
    all_trade_data["target_volume"] = target_volume
    all_trade_data["vwap"] = calculated_vwaps

    return all_trade_data.reset_index(drop=True)


def vwap_by_depth(objects: dict[str, pd.DataFrame],
                  desired_depth: float,
                  min_depth: float = None) -> dict[str, float]:
    """
    This method can be used to calculate the weighted average price for a dictionary of dataframes (e.g. orders, trades) at a desired depth.
    The output is a singular value for each dataframe. This function does not load any data, therefore the already existing data object has to
    be passed as an argument.

    Args:
        objects (dict[str, DataFrame): A dictionary of dataframes, each of which needs to have a 'quantity' and a 'price' field.
        desired_depth (float): The depth (in MW) specifying how many of the objects should be taken into consideration.
        min_depth (float): The required minimum depth (in percent of the desired depth). If this requirement is not met, return value is 0.

    Returns:
        dict[str, float]: The weighted average price for the desired depth for each key in the dictionary.
    """
    if min_depth and min_depth > 0.99:
        raise Exception("The minimum depth has to be given as percentage of the desired depth.")

    vwaps = {k: 0 for k in [*objects]}

    for key, obj in tqdm(objects.items(), desc="Calculating Single VWAPs", unit="time periods", leave=False):
        available_depth = 0
        total_value = 0

        for ind, row in obj.iterrows():
            if available_depth + row.quantity < desired_depth:
                available_depth = available_depth + row.quantity
                total_value += row.quantity * row.price
            else:
                total_value += (desired_depth - available_depth) * row.price
                available_depth += desired_depth - available_depth
                available_depth = round(available_depth, 2)
                break

        # If the 'min_depth' parameter is set, then the available depth on the market has to fulfill the minimum requirements.
        if min_depth and available_depth and available_depth > desired_depth * min_depth \
                or not min_depth and available_depth:
            vwaps[key] = round(total_value / available_depth, 2)

    return vwaps


def vwap_by_timeperiod(objects: pd.DataFrame,
                       timestamp: str,
                       time_spec: str = "60T-60T-0T") -> float:
    """
    Function to calculate the value-weighted average price at the given point in time for the last X minutes.

    To specify the time period precisely, the time_spec parameter should be used. The pattern is always as follows:

    {60/30/15/0}T-{60/45/30/15}T-{45/30/15/0}T

    Explanation:
        {60/30/15/0}T -> Floor, will count back to the last full hour/ half-hour/ quarter-hour / last minute and act as starting point
        {60/45/30/15}T -> Execution From, determines the minutes that should be subtracted from Floor to reach starting point for calculation
        {45/30/15/0}T -> Execution To, determines the minutes that should be subtracted from Floor to reach end point for calculation

    Examples:
        Current Time: 16:23:30
        60T-60T-0T  <--> VWAP of the previous trading hour (15:00-16:00).
        60T-15T-0T  <--> VWAP of the last quarter-hour of the previous trading hour (15:45-16:00).
        60T-30T-15T <--> VWAP of third quarter-hour of the previous trading hour (15:30-15:45).
        15T-60T-0T  <--> VWAP of last hour calculated from last quarter hour (15:15-16:15).
        0T-60T-30T  <--> VWAP of first half of the last hour calculated from current timestamp (15:23-15:53).

    Args:
        objects (pd.DataFrame): Collection of trades/ orders
        timestamp (str): Current timestamp
        time_spec (str): String of time specification as explained above

    Returns:
        float
    """
    if objects is None or isinstance(objects, pd.DataFrame) and objects.empty or not bool(
            re.search("((60|30|15|0)T-(60|45|30|15)T-(45|30|15|0)T)", time_spec)):
        return 0

    # Parse time specification
    timestamp = pd.Timestamp(timestamp, tz="utc")
    time_periods = [int(t) for t in time_spec.replace("T", "").split("-")]
    recalculation_point = timestamp.floor(freq=f"{time_periods[0] or ''}T")
    execution_from = recalculation_point - pd.Timedelta(minutes=time_periods[1])
    execution_to = recalculation_point - pd.Timedelta(minutes=time_periods[2])

    # Filter and check dataframe
    field = "exec_time" if "exec_time" in objects.columns else "as_of"

    if (filtered := objects.loc[(objects[field] >= execution_from) & (objects[field] < execution_to)]).empty:
        return 0

    return round(sum(values["price"] * values["quantity"] for row, values in filtered.iterrows()) / sum(filtered.quantity), 2)


def calc_rolling_vwap(trades: dict[str, pd.DataFrame],
                      rolling_interval: int = 1,
                      rolling_time_unit: str = "hour") -> dict[str, pd.DataFrame]:
    """
    This method can be used to calculate the rolling weighted average price for trades.
    Every item in the given dataframe will be assigned the specific value weighted average price of all previous items that were executed in
    the given time window (counting from the execution time of the current item).

    Args:
        trades (dict[str, DataFrame): A dictionary of dataframes containing trades
        rolling_interval (int): The interval time that should be considered when calculating an items specific VWAP
        rolling_time_unit (str): The time unit that VWAP should be calculated for. Possible: hour, minute, second

    Returns:
        dict[str, pd.Dataframe]: Original dictionary of dataframes, extended by weighted average price for the set time interval for each item
    """
    t_map = {"hour": "h", "minute": "min", "second": "s"}

    for k, v in tqdm(trades.items(), desc="Calculating Rolling VWAPs", unit="time periods", leave=False):
        t = f"{rolling_interval}{t_map[rolling_time_unit]}"

        # Set index on temporary dataframe
        v_temp = v.set_index("exec_time").sort_values(by="exec_time")

        # Calculate vwap
        ptq = v_temp.price * v_temp.quantity
        quant_sum = v_temp.rolling(window=t)["quantity"].sum()
        ptq_sum = ptq.rolling(window=t).sum()

        # Add to original df
        v[f"vwap_{t}"] = round(ptq_sum / quant_sum, 2).to_list()

    return trades


def calc_orderbook_vwap(orderbook: dict[str, pd.DataFrame], depth: Union[int, float] = 0) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Function to calculate value-weighted average prices for a single order book for bids and asks respectively.

    Args:
        orderbook (dict): Single order book
        depth (int/float): Depth in MW to calculate average price for

    Returns:
        tuple(vwap_asks, vwap_bids)
    """
    # Add new column for cumulative quantity
    asks = {k: df.insert(1, "cum_quant", value=df.quantity.cumsum()) or df for k, v in orderbook.items() if not (df := v.loc[v.type == "ask"].sort_values(by=['price'], ascending=True)).empty}
    bids = {k: df.insert(1, "cum_quant", value=df.quantity.cumsum()) or df for k, v in orderbook.items() if not (df := v.loc[v.type == "bid"].sort_values(by=['price'], ascending=False)).empty}

    # takes all orders up to desired depth or the first order if it exceeds depth or all orders if depth is 0
    vwap_asks = pd.DataFrame({k: {
        "vwap": round(sum((df := df_t if not (df_t := v.loc[v.cum_quant <= (depth if depth else max(v.cum_quant))]).empty else v.head(1)).price * df.quantity) / sum(
            df.quantity), 2),
        "depth": sum(v.quantity)} for k, v in asks.items()}).T

    vwap_bids = pd.DataFrame({k: {
        "vwap": round(sum((df := df_t if not (df_t := v.loc[v.cum_quant <= (depth if depth else max(v.cum_quant))]).empty else v.head(1)).price * df.quantity) / sum(
            df.quantity), 2),
        "depth": sum(v.quantity)} for k, v in bids.items()}).T

    return vwap_asks, vwap_bids
