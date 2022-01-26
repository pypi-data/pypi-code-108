import gzip
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Union
from zipfile import ZipFile, BadZipFile

import pandas as pd
import requests
from powerbot_client.exceptions import ApiException

from powerbot_backtesting.exceptions import ChecksumError, NotInCacheError
from powerbot_backtesting.historic_data_processing import process_historic_data
from powerbot_backtesting.models import HistoryApiClient
from powerbot_backtesting.utils import _find_cache
from powerbot_backtesting.utils.constants import *


def get_historic_data(api_key: str,
                      exchange: str,
                      delivery_areas: list[str],
                      day_from: Union[str, datetime],
                      day_to: Union[str, datetime] = None,
                      cache_path: Path = None,
                      extract_files: bool = False,
                      process_data: bool = False,
                      skip_on_error: bool = False,
                      keep_zip_files: bool = False) -> Union[list, dict]:
    """
    Function loads all public data for specified days in the specified delivery area. Output is a zipped directory
    containing all files in JSON format. Optionally, zip file can be extracted automatically and processed to be
    compatible with other functions in the powerbot_backtesting package.

    Args:
        api_key (str): Specific history instance API key
        exchange (str): One of the following: epex, hupx, tge, nordpool, southpool, ibex
        delivery_areas (list): List of EIC Area Codes for Delivery Areas
        day_from (str): Datetime/ String in format YYYY-MM-DD
        day_to (str): Datetime/ String in format YYYY-MM-DD
        cache_path (Path): Optional path for caching files
        extract_files (bool): True if zipped files should be extracted automatically (Warning: immense size increase)
        process_data (bool): True if extracted files should be processed to resemble files loaded via API
        skip_on_error (bool): True if all dates that cannot possibly be loaded (e.g. due to lack of access rights) are
        skipped if the difference between day_from and day_to is at least 2 days
        keep_zip_files (bool): True if zip-files should be kept after download

    Returns:
        list of loaded file paths | dict
    """
    # Validity check
    if not isinstance(day_from, datetime):
        try:
            day_from = datetime.strptime(day_from, DATE_YMD)
        except ValueError:
            raise ValueError("day_from needs to be a date or a string in YYYY-MM-DD format")
    if day_to and not isinstance(day_to, datetime):
        try:
            day_to = datetime.strptime(day_to, DATE_YMD)
        except ValueError:
            raise ValueError("day_to needs to be a date or a string in YYYY-MM-DD format")

    delivery_areas = delivery_areas if isinstance(delivery_areas, list) else [delivery_areas]
    cache_path = _find_cache() if not cache_path else cache_path
    cache_path = Path(cache_path) if not isinstance(cache_path, Path) else cache_path
    headers = {"accept": "application/zip", "X-API-KEY": api_key}
    day_to = day_to if day_to else day_from
    skip_on_error = True if skip_on_error and day_to and day_to - day_from >= timedelta(days=2) else False

    zipfiles = []
    extracted_files = {}
    retry = 0
    reload_faulty = 0

    while day_from <= day_to:
        # While False, days will continue with iteration
        prevent_update = False

        for del_area in delivery_areas:
            host = f"https://history.powerbot-trading.com/history/{exchange}/{del_area}/{day_from.strftime(DATE_YMD)}"

            # Filepath
            filepath = cache_path.joinpath(f"history/{exchange}_{del_area}/{day_from.strftime(DATE_YM)}")

            # File
            filename = f"{day_from.strftime(DATE_MD)}_public_data.zip"
            zipfiles.append(f"{del_area}_{filename.strip('.zip')}")

            # Skip if file exists
            if not filepath.joinpath(filename).exists() and not filepath.joinpath(day_from.strftime(DATE_MD)).exists():
                # Load file
                r = requests.get(host, headers=headers, stream=True)
                m = hashlib.sha256()

                if skip_on_error and r.status_code in [204, 403, 404]:
                    continue
                if r.status_code == 503:
                    raise ApiException(status=503, reason="Service unavailable or API rate limit exceeded")
                if r.status_code == 404:
                    raise ApiException(status=404,
                                       reason=f"Data for '{day_from}' in {del_area} has not been exported yet")
                if r.status_code == 403:
                    raise ApiException(status=403, reason="Currently used API Key does not have access to this data")
                if r.status_code == 204:
                    raise ApiException(status=204, reason=f"There is no data for '{day_from}' in {del_area}")

                # Create filepath only if file is valid
                filepath.mkdir(parents=True, exist_ok=True)

                with open(filepath.joinpath(filename), 'wb') as fd:
                    for chunk in r.iter_content(chunk_size=128):
                        m.update(chunk)
                        fd.write(chunk)

                expected_hash = \
                    json.loads(
                        [i for i in requests.get(host + "/sha256", headers=headers, stream=True).iter_lines()][0])[
                        "sha_256"]

                if not expected_hash == m.hexdigest():
                    if retry < 3:  # Retry 3 times
                        filepath.joinpath(filename).unlink(missing_ok=False)
                        retry += 1
                        prevent_update = True
                        continue
                    if skip_on_error:  # Skip
                        filepath.joinpath(filename).unlink(missing_ok=False)
                    else:
                        filepath.joinpath(filename).unlink(missing_ok=False)
                        raise ChecksumError(
                            "Corrupted file: expected sha256 checksum does not match sha256 of received files. "
                            "Please try again.")

            # Extraction
            if extract_files and not filepath.joinpath(day_from.strftime(DATE_MD)).exists():
                try:
                    with ZipFile(filepath.joinpath(filename), 'r') as _zip:
                        _zip.extractall(filepath.joinpath(day_from.strftime(DATE_MD)))
                    if not keep_zip_files:
                        # Delete Zip
                        filepath.joinpath(filename).unlink()
                    # Reset counter if file is OK
                    reload_faulty = 0

                except BadZipFile:
                    if reload_faulty < 3:
                        print(
                            f"The loaded file for day {day_from} in {del_area} is faulty. Attempting to load it again (Retry {reload_faulty + 1})")

                        # Delete faulty file
                        filepath.joinpath(filename).unlink(missing_ok=True)

                        # Set counter and prevent update
                        reload_faulty += 1
                        prevent_update = True

                    elif skip_on_error:
                        print(
                            f"The loaded file for day {day_from} in {del_area} is still faulty (Retry {reload_faulty}). Skipping file")

                    else:
                        raise TypeError(
                            f"The loaded file for day {day_from} in {del_area} is still faulty (Retry {reload_faulty}). Please delete cache and load again")

            if extract_files and not reload_faulty:
                # Add to dictionary
                extracted_files[f"{del_area}_{filename.strip('.zip')}"] = [str(e) for e in filepath.joinpath(
                    day_from.strftime(DATE_MD)).iterdir() if e.is_file()]

            # Reset counters
            retry = 0
            reload_faulty = 0 if reload_faulty and not prevent_update else reload_faulty

        day_from = day_from + timedelta(days=1) if not prevent_update else day_from

    if not zipfiles:
        return []
    if extract_files:
        if process_data:
            return process_historic_data(extracted_files, exchange, keep_zip_files)
        return extracted_files
    return zipfiles


def get_history_key_info(api_key: str) -> dict:
    """
    Returns information for the specified History API Key

    Args:
        api_key (str): History API Key

    Returns:
        dict
    """
    headers = {"accept": "application/json", "X-API-KEY": api_key}
    host = "https://history.powerbot-trading.com/api-key"

    r = requests.get(host, headers=headers, stream=True)

    if r.status_code == 503:
        raise ApiException(status=503, reason="Service unavailable or API rate limit exceeded")
    if r.status_code == 400:
        raise ApiException(status=400, reason="Request could not be processed, please check your API Key")
    return r.json()


def init_historic_client(exchange: str,
                         delivery_area: str) -> HistoryApiClient:
    """
    Initializes historic client containing information to filter for cached historic data. When using a HistoryApiClient
    instead of an ApiClient, all other function will react accordingly and only load data from the local __pb_cache__.

    Args:
        exchange (str): One of the following: epex, hupx, tge, nordpool, southpool, ibex
        delivery_area (str):  EIC Area Code for Delivery Area

    Returns:
        HistoryApiClient
    """
    return HistoryApiClient(exchange=exchange, delivery_area=delivery_area)


def get_historic_contracts(client: HistoryApiClient,
                           time_from: datetime,
                           time_till: datetime,
                           contract_time: str,
                           products: list[str],
                           allow_udc: bool) -> list[dict]:
    """
    Function mimics get_contracts but loads contracts from a cached index file instead of the API. This is necessary when trying to load data that
    is older than the data retention policy for production instances.

    Args:
        client: HistoryApiClient
        time_from (datetime): yyyy-mm-dd hh:mm:ss
        time_till (datetime): yyyy-mm-dd hh:mm:ss
        contract_time (str): all, hourly, half-hourly or quarter-hourly (all includes UDC)
        products (list): List of specific products to return
        allow_udc (bool): True if user-defined contracts (block products) should also be returned on contract_time = all

    Returns:
        list(dict)}: List of Dictionaries
    """
    return get_historic_contract_ids(client=client,
                                     time_from=time_from,
                                     time_till=time_till,
                                     contract_time=contract_time,
                                     products=products,
                                     allow_udc=allow_udc,
                                     return_contract_objects=True)


def get_historic_contract_ids(client: HistoryApiClient,
                              time_from: datetime,
                              time_till: datetime,
                              contract_time: str,
                              products: list[str],
                              allow_udc: bool,
                              return_contract_objects: bool = False) -> Union[dict[str, list[str]], list[dict]]:
    """
    Function mimics get_contract_ids but loads contract IDs from a cached index file instead of the API. This is necessary when trying to load data
    that is older than the data retention policy for production instances.

    Args:
        client: HistoryApiClient
        time_from (datetime): yyyy-mm-dd hh:mm:ss
        time_till (datetime): yyyy-mm-dd hh:mm:ss
        contract_time (str): all, hourly, half-hourly or quarter-hourly (all includes UDC)
        products (list): List of specific products to return
        allow_udc (bool): True if user-defined contracts (block products) should also be returned on contract_time = all
        return_contract_objects: if True will return contract objects instead

    Returns:
        dict{key: (list[str])}: Dictionary of Contract IDs or List of Dictionaries
        OR: list[ContractItem]: Contract Object
    """
    # Setup
    timeframes = {"all": 15, "hourly": 60, "half-hourly": 30, "quarter-hourly": 15}
    ct = timeframes[contract_time]
    products = PRODUCTS[contract_time] if not products else products
    contracts = defaultdict(list) if not return_contract_objects else []
    time_range = []

    # Split time up if range covers multiple days
    while time_from.date() < time_till.date():
        time_range.append((time_from, time_from.replace(hour=0, minute=0, second=0) + timedelta(days=1)))
        time_from = time_from.replace(hour=0, minute=0, second=0) + timedelta(days=1)
    else:
        if not time_from == time_till:
            time_range.append((time_from, time_till))

    # Find __cache__ directory
    cache_path = _find_cache()

    for tr in time_range:
        # Extract date information
        year_month = tr[0].strftime(DATE_YM)
        day_month = tr[0].strftime(DATE_MD)

        # Construct path to index file
        file_path = cache_path.joinpath(f"prod\{client.exchange}_{client.delivery_area}\{year_month}\{day_month}\\raw")
        if not file_path.exists():
            raise NotInCacheError("The requested data is currently not cached")
        index = next((i for i in file_path.iterdir() if i.is_file() and "contract" in i.name))

        if not index:
            raise NotInCacheError("Cannot find correct index file in local cache")
        index = pd.read_json(gzip.open(index))

        # Transform
        index['delivery_start'] = pd.to_datetime(index['delivery_start'])
        index['delivery_end'] = pd.to_datetime(index['delivery_end'])
        index = index.astype({"contract_id": "str", "delivery_areas": "str"})

        # Construct list of contract times
        contract_times = [tr[0]]
        [contract_times.append(contract_times[-1] + timedelta(minutes=ct)) for _ in
         range(1, ((tr[1] - tr[0]) / (ct * 60)).seconds)]
        contract_times = [str(i.replace(tzinfo=timezone.utc)) for i in contract_times]

        # Filter dataframe down
        index = index.loc[(index._product.isin(PRODUCTS[contract_time])) & (index._product.isin(products)) & (
            index.delivery_areas.str.contains(client.delivery_area))]
        index = index.loc[index.delivery_start.isin(contract_times)]

        # Block product filter
        if not contract_time == "all" or not allow_udc:
            if client.exchange not in SYSTEMS["NordPool"]:
                index = index.loc[index.undrlng_contracts.isna()]
            else:
                index = index.loc[index.productType != "CUSTOM_BLOCK"]

        if not return_contract_objects:
            [contracts[
                f'{datetime.strftime(v.delivery_start, DATE_YMD_TIME_HM)} - {datetime.strftime(v.delivery_end, TIME_HM if v.delivery_start.date() == v.delivery_end.date() else DATE_YMD_TIME_HM)}'].append(
                v.contract_id) for k, v in index.iterrows()]
        else:
            contracts += (index.to_dict(orient="records"))

    return dict(contracts) if not return_contract_objects else contracts
