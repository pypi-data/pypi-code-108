import os
import pickle
from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Union

import pandas as pd
from powerbot_client import ApiClient, TradesApi, SignalsApi, Signal, Trade, InternalTrade, OrdersApi, OwnOrder

from powerbot_backtesting.models import HistoryApiClient
from powerbot_backtesting.utils.constants import *


def _get_private_data(api_client: ApiClient,
                      data_type: str,
                      time_from: datetime = None,
                      time_till: datetime = None,
                      delivery_area: str = None,
                      portfolio_id: list[str] = None,
                      contract_ids: Union[list[str], dict[str, str]] = None,
                      active_only: bool = False) -> list[Union[InternalTrade, OwnOrder, Trade, Signal]]:
    """
    Underlying function of all private data requests to PowerBot. Loads the specified collection according to the parameters given.

    Args:
        api_client: PowerBot ApiClient
        data_type (str): Either internal_trade, own_trade, own_order or signal
        time_from (datetime): YYYY-MM-DD hh:mm:ss
        time_till (datetime): YYYY-MM-DD hh:mm:ss
        delivery_area (str): EIC Area Code for Delivery Area
        portfolio_id (list[str]): List of specific portfolio IDs to load trades from. If left out, will load from all IDs.
        contract_ids (list/dict): Collection of contract IDs to specifically load own orders for
        active_only (bool):  True if only active orders should be loaded. If False, loads also hibernate and inactive.

    Returns:
        list[Union[InternalTrade, OwnOrder, Trade, Signal]]
    """
    contract_ids = [i for v in contract_ids.values() for i in v] if isinstance(contract_ids, dict) else contract_ids

    param_mapping = {
        "internal_trade": {"delivery_within_start": time_from, "delivery_within_end": time_till, "limit": 100},
        "own_trade": {"delivery_within_start": time_from, "delivery_within_end": time_till, "limit": 500},
        "own_order": {"contract_id": contract_ids, "active_only": active_only, "limit": 500},
        "signal": {"received_from": time_from, "received_to": time_till, "limit": 500}
    }
    func_mapping = {
        "internal_trade": TradesApi(api_client).get_internal_trades,
        "own_trade": TradesApi(api_client).get_trades,
        "own_order": OrdersApi(api_client).get_own_orders,
        "signal": SignalsApi(api_client).get_signals
    }

    coll = []
    more_obj = True
    offset = 0
    params = {**param_mapping[data_type]}

    if portfolio_id:
        params["portfolio_id"] = portfolio_id
    if delivery_area:
        params["delivery_area"] = delivery_area

    while more_obj:
        new_objs = func_mapping[data_type](offset=offset, **params)
        if len(new_objs):
            coll += new_objs
            offset += len(new_objs)
        else:
            more_obj = False
        sleep(0.2)

    return coll


def _cache_data(data_type: str,
                data: dict[str, pd.DataFrame],
                delivery_area: str,
                exchange: str = None,
                api_client: Union[ApiClient, HistoryApiClient] = None,
                timesteps: int = 0,
                time_unit: str = None,
                shortest_interval: bool = False,
                gzip_files: bool = True,
                as_json: bool = True,
                as_csv: bool = False,
                as_pickle: bool = False):
    """
    Function to be called by data request functions to cache loaded data in a reusable format. Automatically generates
    a folder to cache loaded files, if it cannot find an existing one.

    Args:
        data_type (str): One of the following: trades, ordhist, ohlc, orderbook
        data (dict): Dictionary of DataFrames
        delivery_area (str): EIC Area Code for Delivery Area
        exchange (str): Exchange e.g. epex, nordpool, southpool, etc.
        api_client: PowerBot ApiClient
        timesteps (int): only necessary if data_type is ohlc or orderbooks
        time_unit (str): only necessary if data_type is ohlc or orderbooks
        gzip_files (bool): True if cached files should be gzipped
        as_json (bool): True per default, except for orderbooks (optional feature)
        as_csv (bool): if True, will save files as CSV, additionally to JSON
        as_pickle (bool): False per default, except for orderbooks
    """
    # Setup
    host = api_client.configuration.host if isinstance(api_client, ApiClient) else None
    environment = "staging" if host and host.split("/")[2].split(".")[0] == "staging" else "prod"
    exchange = host.split("/")[4] if host else api_client.exchange if isinstance(api_client, HistoryApiClient) else exchange
    folder = "raw" if data_type in ["trades", "ordhist", "contracts"] else "processed"
    compression = "gzip" if gzip_files else "infer"
    file_ending = ".gz" if gzip_files else ""

    # Caching
    for key, value in data.items():
        delivery_date = datetime.strptime(key.split(" ")[0], "%Y-%m-%d")
        year_month = delivery_date.strftime("%Y-%m")
        day_month = delivery_date.strftime("%m-%d")
        file_name = key.replace(f"{str(key).split(' ')[0]}", "").replace(":", "-")
        time_intervals = f"{timesteps}{time_unit}" if not shortest_interval else "shortest"

        file_name = f"{file_name}_{data_type}" if folder == "raw" else f"{file_name}_{data_type}_{time_intervals}"
        file_name = f"{delivery_date.date()}{file_name}" if file_name.startswith("_") else file_name

        # Check if __cache__ already exists
        cache_path = _find_cache().joinpath(
            f"{environment}\\{exchange}_{delivery_area}\\{year_month}\\{day_month}\\{folder}")

        # Assure That Directory Exists
        cache_path.mkdir(parents=True, exist_ok=True)

        # Cache File If It Doesn't Exist Yet
        if as_json and not cache_path.joinpath(f"{file_name}.json{file_ending}").exists():
            value.to_json(cache_path.joinpath(f"{file_name}.json{file_ending}"), date_format="iso", date_unit="us",
                          compression=compression)

        if as_csv and not cache_path.joinpath(f"{file_name}.csv").exists():
            value.to_csv(cache_path.joinpath(f"{file_name}.csv{file_ending}"), sep=";", compression=compression)

        if as_pickle and not cache_path.joinpath(f"{file_name}.p").exists():
            pickle.dump(value, open(cache_path.joinpath(f"{file_name}.p"), "wb"))


def _find_cache() -> Path:
    """
    Functions returns location of __cache__ directory if it can be found within 3 parent directories based on the
    location of the file backtesting functions are called from.

    If multiple projects lie within a directory that can be reached within 3 parent directories from where this
    function is called, it might find a cache directory that does not lie directly in the current projects root
    directory. This can be confusing, however, it does not restrict functionality.

    This fact can also be used on purpose by manually creating a __pb_cache__ directory one parent above, that can be
    shared by multiple projects that require historic data.

    Proposed structure:
    parent_dir
    | __pb_cache__
    |
    |--- project_1
    |	|   file.py
    |
    |--- project_2
    |	|   file.py
    |
    |--- project_3
        |   file.py

    Returns:
        Path
    """
    if Path("__pb_cache__").exists():
        return Path("__pb_cache__")

    cache_path = None
    root_path = Path().cwd()

    for _ in range(3):
        cache_path = [root for root, directory, file in os.walk(root_path) if "__pb_cache__" in root]

        # Check if cache was found
        if cache_path:
            cache_path = Path(cache_path[0])
            break

        root_path = root_path.parent

    if not cache_path:
        cache_path = Path().cwd().joinpath("__pb_cache__")

    return cache_path


def _get_file_cachepath(api_client: Union[ApiClient, HistoryApiClient], contract_key: str, delivery_area: str, exchange: str = None) -> str:
    """
    Helper function that constructs most of the path of a cached file.

    Args:
        api_client (ApiClient/HistoryApiClient): PowerBot ApiClient if loading from API else HistoryApiClient
        contract_key (str): Key of dictionary
        delivery_area (str): EIC Area Code for Delivery Area
        exchange (str): exchange of contracts -> needed when loading with SQLExporter

    Returns:
        filepath: str
    """
    environment = api_client.configuration.host.split("/")[2].split(".")[0] if isinstance(api_client, ApiClient) else None
    environment = "staging" if environment == "staging" else "prod"
    market = api_client.configuration.host.split("/")[4] if isinstance(api_client, ApiClient) else api_client.exchange if api_client else exchange
    delivery_date = datetime.strptime(contract_key.split(" ")[0], DATE_YMD)
    year_month = delivery_date.strftime(DATE_YM)
    day_month = delivery_date.strftime(DATE_MD)
    file_name = contract_key.replace(f"{str(contract_key).split(' ')[0]}", "").replace(":", "-")

    return f"{environment}\\{market}_{delivery_area}\\{year_month}\\{day_month}\\raw\\{file_name}"


def _check_contracts(contract, delivery_areas: list[str], products: list[str], allow_udc: bool) -> bool:
    """
    Helper function to determine if contract is of interest and should be added to contract dictionary.

    Args:
        contract: Contract Object
        delivery_areas (list): List of EIC-codes
        products (list): List of products

    Returns:
        bool
    """
    if contract.exchange in SYSTEMS["M7"]:
        if delivery_areas and contract.delivery_areas and not any(
                area in contract.delivery_areas for area in delivery_areas) \
                or delivery_areas and contract.contract_details["deliveryAreas"] and not any(
            area in contract.contract_details["deliveryAreas"] for area in delivery_areas) \
                or delivery_areas and not contract.delivery_areas and not contract.contract_details["deliveryAreas"] \
                or products and contract.product not in products \
                or not products and "10YGB----------A" not in delivery_areas and contract.product == "GB_Hour_Power" \
                or contract.type == "UDC" and not allow_udc:
            return False

    else:
        if delivery_areas and contract.delivery_areas and not any(
                area in contract.delivery_areas for area in delivery_areas) \
                or delivery_areas and not contract.delivery_areas \
                or products and contract.product not in products \
                or contract.type == "UDC" and not allow_udc:
            return False

    return True
