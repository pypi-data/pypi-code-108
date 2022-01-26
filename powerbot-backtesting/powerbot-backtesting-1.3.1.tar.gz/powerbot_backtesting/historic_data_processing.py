import os
import shutil
from datetime import timedelta, datetime as dt
from pathlib import Path
from typing import Union

import pandas as pd
from tqdm import tqdm

from powerbot_backtesting.utils import _cache_data, _find_cache, _historic_data_transformation, _historic_contract_transformation
from powerbot_backtesting.utils.constants import *


def process_historic_data(extracted_files: Union[list[str], dict[str, list[str]]],
                          exchange: str,
                          keep_zip_files: bool = False):
    """
    Function processes list of files extracted from a zip-file downloaded via History API to be compatible with the
    rest of the powerbot_backtesting package. Once files have been processed, they are cached in the same manner as
    data loaded via PowerBot API, allowing functions like get_contract_history and get_public_trades to load them from
    the cache.

    Args:
        extracted_files (list(str), dict[str, list[str]]): List of files extracted with get_historic_data
        (-> return value of get_historic_data)
        exchange (str): One of the following: epex, hupx, tge, nordpool, southpool, ibex
        keep_zip_files (bool): True if zip-files should be kept after download
    """
    # Setup
    prod_path = _find_cache().joinpath("prod")
    prod_files = []

    for filename, unzipped_files in extracted_files.items():
        # We cannot delete this -> we need the index
        contract_file = [i for i in unzipped_files if "contracts.json" in i][0]
        contract_file = unzipped_files.pop(unzipped_files.index(contract_file))

        delivery_area = filename.split("_")[0]

        # Contract file transformation & caching -> serves as index file
        index = _historic_contract_transformation(contract_file, exchange)

        # Group contracts after delivery period
        index['delivery_start'] = pd.to_datetime(index['delivery_start'])
        index['delivery_end'] = pd.to_datetime(index['delivery_end'])

        index.sort_values(by=["delivery_start"], inplace=True)

        contract_times = {}
        start = index.delivery_start.iloc[0]
        end = index.delivery_start.iloc[-1]

        while start <= end:
            for timestep in [15, 30, 60]:
                ids = index.loc[(index.delivery_start == start) & (
                        index.delivery_end == (start + timedelta(minutes=timestep)))].contract_id.tolist()
                if ids:
                    contract_times[
                        f"{start.strftime(DATE_YMD_TIME_HM)} - {(start + timedelta(minutes=timestep)).strftime(TIME_HM)}"] = ids
            start += timedelta(minutes=15)

        transformed_trade_files, transformed_order_files = {}, {}

        # Add any contract with duration upwards of 1 hour
        udcs = index.loc[index.delivery_end - index.delivery_start > timedelta(hours=1)]

        for r, v in udcs.iterrows():
            if v.delivery_start.date() == v.delivery_end.date():
                contract_times[
                    f'{dt.strftime(v.delivery_start, DATE_YMD_TIME_HM)} - {dt.strftime(v.delivery_end, TIME_HM if v.delivery_start.date() == v.delivery_end.date() else DATE_YMD_TIME_HM)}'] = [
                    v.contract_id]

        # For each timestep
        for time, ids in tqdm(contract_times.items(), desc="Historic File Transformation", unit="files", leave=False):
            files = {"trades": [i for i in unzipped_files if any(str(x) in i for x in ids) and "Trades" in i],
                     "orders": [i for i in unzipped_files if any(str(x) in i for x in ids) and "Orders" in i]}

            for k, v in files.items():
                if v:
                    if k == "trades":
                        transformed_trade_files[time] = _historic_data_transformation(v, exchange, k)
                    else:
                        transformed_order_files[time] = _historic_data_transformation(v, exchange, k)

        # Cache the result
        _cache_data("contracts", {f"{index.delivery_start.iloc[0].date()}": index}, delivery_area, exchange)
        _cache_data("trades", transformed_trade_files, delivery_area, exchange)
        _cache_data("ordhist", transformed_order_files, delivery_area, exchange)

        # Save paths of all transformed files
        prod_files += [str(e) for e in
                       prod_path.joinpath(f"{exchange}_{delivery_area}\{end.strftime('%Y-%m')}\{end.strftime('%m-%d')}\\raw").iterdir() if
                       e.is_file()]

        # Cleanup
        for file in unzipped_files:
            Path(file).unlink(missing_ok=True)
        Path(contract_file).unlink(missing_ok=True)
        shutil.rmtree(Path('\\'.join(unzipped_files[0].split("\\")[:-1])), ignore_errors=True)

    # Delete history directory if it's empty (no files)
    history_path = _find_cache().joinpath("history")
    history_files = [file for root, directory, file in os.walk(history_path)]

    if not all(i for i in history_files) and not keep_zip_files:
        shutil.rmtree(history_path)

    return prod_files
