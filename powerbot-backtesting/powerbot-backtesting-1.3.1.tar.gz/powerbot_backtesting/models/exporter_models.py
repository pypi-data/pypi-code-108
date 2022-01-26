import json
import logging
import re
from abc import ABC, abstractmethod
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Union, Optional, TypeVar, Any
from urllib.parse import quote

import pandas as pd
import plotly.graph_objects as go
from dateutil.tz import tzutc
from powerbot_client import Signal, Trade, InternalTrade, OwnOrder, ContractItem
from pydantic import BaseModel, Field, validate_arguments, root_validator, validator
from sqlalchemy import create_engine
from sqlalchemy.exc import NoSuchModuleError, InterfaceError, ProgrammingError, OperationalError, TimeoutError
from sqlalchemy.orm import Session
from tqdm import tqdm

import powerbot_backtesting as pb
from powerbot_backtesting.exceptions import SQLExporterError
from powerbot_backtesting.utils.constants import *
from powerbot_backtesting.utils.helpers_general import _cache_data, _find_cache, _get_file_cachepath

# Implement custom type for validation
pandas_DataFrame = TypeVar('pandas.core.frame.DataFrame')
ApiClient = TypeVar('powerbot_client.api_client.ApiClient')
HistoryApiClient = TypeVar('powerbot_backtesting.models.history_api_models.HistoryApiClient')


class BaseExporter(BaseModel, ABC):
    """
    Base class to all of PowerBot's exporter classes.
    """

    @abstractmethod
    def get_contracts(self, **kwargs) -> list:
        """Acquire contracts from source as defined by specific exporter class."""

    @abstractmethod
    def get_contract_ids(self, **kwargs) -> dict[str, list[str]]:
        """Acquire contract ids from source as defined by specific exporter class."""

    @abstractmethod
    def get_public_trades(self, **kwargs) -> dict[str, pd.DataFrame]:
        """Acquire public trades from source as defined by specific exporter class."""

    @abstractmethod
    def get_contract_history(self, **kwargs) -> dict[str, pd.DataFrame]:
        """Acquire contract history from source as defined by specific exporter class."""

    @validate_arguments
    def get_ohlc_data(self,
                      trade_data: dict[str, pandas_DataFrame],
                      timesteps: int,
                      time_unit: str,
                      delivery_area: str = None,
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
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if data should be cached
            gzip_files (bool): True if cached files should be gzipped
            one_file (bool): True if data should be cached in a single JSON file

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        if not hasattr(self, 'delivery_area') and not delivery_area:
            raise ValueError("Delivery area has to be given")

        return pb.get_ohlc_data(trade_data=trade_data,
                                timesteps=timesteps,
                                time_unit=time_unit,
                                delivery_area=self.delivery_area if hasattr(self, 'delivery_area') and not delivery_area else delivery_area,
                                api_client=self.client if hasattr(self, 'client') else None,
                                use_cached_data=use_cached_data,
                                caching=caching,
                                gzip_files=gzip_files,
                                one_file=one_file)

    @validate_arguments
    def get_orderbooks(self,
                       contract_hist_data: dict[str, pandas_DataFrame],
                       delivery_area: str = None,
                       timesteps: int = 15,
                       time_unit: str = "minutes",
                       shortest_interval: bool = False,
                       timestamp: list[datetime] = None,
                       from_timestamp: bool = False,
                       use_cached_data: bool = True,
                       caching: bool = True,
                       as_json: bool = False,
                       concurrent: bool = False) -> dict[str, pd.DataFrame]:

        """
        Converts contract history data into order books in the specified timesteps. If no API client is passed, the function
        will automatically assume that the data is production data.

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
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if single order books should be cached as JSON
            as_json (bool): True if complete order book should be cached as JSON
            concurrent (bool): True if processing should be multithreaded -> possible performance gain on big datasets and good CPU

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        if not hasattr(self, 'delivery_area') and not delivery_area:
            raise ValueError("Delivery area has to be given")

        return pb.get_orderbooks(contract_hist_data=contract_hist_data,
                                 delivery_area=self.delivery_area if hasattr(self, 'delivery_area') and not delivery_area else delivery_area,
                                 timesteps=timesteps,
                                 time_unit=time_unit,
                                 shortest_interval=shortest_interval,
                                 timestamp=timestamp,
                                 from_timestamp=from_timestamp,
                                 api_client=self.client if hasattr(self, 'client') else None,
                                 use_cached_data=use_cached_data,
                                 caching=caching,
                                 as_json=as_json,
                                 concurrent=concurrent)

    @staticmethod
    @validate_arguments
    def get_orders(contract_hist_data: dict[str, pandas_DataFrame],
                   append_all: bool = False) -> dict[str, pandas_DataFrame]:
        """
        Extracts all order data from contract history as is, without performing any quality control. If necessary, orders for all contracts can be
        appended to a single dataframe.

        Args:
            contract_hist_data (dict): Dictionary of Dataframes containing Contract History Data
            append_all (bool): True if one dataframe containing all orders should be returned

        Returns:
            dict{key: pd.DataFrame}: Dictionary of DataFrames
        """
        return pb.get_orders(contract_hist_data=contract_hist_data,
                             append_all=append_all)

    @staticmethod
    @validate_arguments
    def vwap_by_depth(objects: dict[str, pandas_DataFrame],
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
        return pb.vwap_by_depth(objects=objects,
                                desired_depth=desired_depth,
                                min_depth=min_depth)

    @staticmethod
    @validate_arguments
    def vwap_by_timeperiod(objects: pandas_DataFrame,
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
            60T-60T-0T  <--> VWAP of the previous trading hour.
            60T-15T-0T  <--> VWAP of the last quarter-hour of the previous trading hour.
            60T-30T-15T <--> VWAP of third quarter-hour of the previous trading hour.
            15T-60T-0T  <--> VWAP of last hour calculated from last quarter hour.
            0T-60T-30T  <--> VWAP of first half of the last hour calculated from current timestamp.

        Args:
            objects (pd.DataFrame): Collection of trades/ orders
            timestamp (str): Current timestamp
            time_spec (str): String of time specification as explained above

        Returns:
            float
        """
        return pb.vwap_by_timeperiod(objects=objects,
                                     timestamp=timestamp,
                                     time_spec=time_spec)

    @staticmethod
    @validate_arguments
    def calc_rolling_vwap(trades: dict[str, pandas_DataFrame],
                          rolling_interval: int = 1,
                          rolling_time_unit: str = "hour") -> dict[str, pandas_DataFrame]:
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
        if rolling_time_unit not in ["hour", "minute", "second"]:
            raise ValueError("rolling_time_unit needs to be one of the following: hour, minute, second")

        return pb.calc_rolling_vwap(trades=trades,
                                    rolling_interval=rolling_interval,
                                    rolling_time_unit=rolling_time_unit)

    @staticmethod
    @validate_arguments
    def calc_orderbook_vwap(orderbook: dict[str, pandas_DataFrame], depth: Union[int, float] = 0) -> tuple[pandas_DataFrame, pandas_DataFrame]:
        """
        Function to calculate value-weighted average prices for a single order book for bids and asks respectively.

        Args:
            orderbook (dict): Single order book
            depth (int/float): Depth in MW to calculate average price for

        Returns:
            tuple(vwap_asks, vwap_bids)
        """
        return pb.calc_orderbook_vwap(orderbook=orderbook, depth=depth)

    @staticmethod
    @validate_arguments
    def plot_ohlc(ohlc_data: dict[str, pandas_DataFrame],
                  ohlc_key: Union[int, str] = 0) -> Union[go.Figure, None]:
        """
        Creates a plotly plot of all ohlc data to be displayed by browser or Dash server. Set ohlc_key to change
        displayed dataframe.

        Args:
            ohlc_data (dict{key: DataFrame}): OHLC Data
            ohlc_key (int/ str): Dictionary key

        Returns:
            Plotly plot
        """
        return pb.plot_ohlc(ohlc_data=ohlc_data,
                            ohlc_key=ohlc_key)

    @staticmethod
    @validate_arguments
    def ohlc_table(ohlc_data: dict[str, pandas_DataFrame],
                   ohlc_key: int = 0) -> pd.DataFrame:
        """
        Creates a custom DataFrame to be displayed by Dash server.

        Args:
            ohlc_data (dict[key: DataFrame]): OHLC Data
            ohlc_key (int): Dictionary key

        Returns:
            DataFrame
        """
        return pb.ohlc_table(ohlc_data=ohlc_data,
                             ohlc_key=ohlc_key)

    @staticmethod
    @validate_arguments
    def plot_orderbook(orderbooks: dict[str, dict[str, pandas_DataFrame]],
                       orderbook_key: Union[int, str] = 0,
                       timestamp: Union[int, str] = -1) -> Union[go.Figure, None]:
        """
        Creates a plotly plot of a single order book to be displayed by browser or Dash server. Use order book_key
        to specify an order book and timestamp to specify the timeframe to display.

        Args:
            orderbooks (dict{key: DataFrame}): Order books
            orderbook_key (int): Dictionary key
            timestamp (int): Order book Key

        Returns:
            Plotly plot
        """
        return pb.plot_orderbook(orderbooks=orderbooks,
                                 orderbook_key=orderbook_key,
                                 timestamp=timestamp)

    @staticmethod
    @validate_arguments
    def plot_volume_history(trade_data: dict[str, pandas_DataFrame],
                            trade_key: Union[int, str] = 0) -> Union[go.Figure, None]:
        """
        Creates a plotly plot of the trade volume for a single contract to be displayed by browser or Dash server.

        Args:
            trade_data (dict{key: DataFrame}):  Trade Data
            trade_key (int/str): Dictionary key

        Returns:
            Plotly plot
        """
        return pb.plot_volume_history(trade_data=trade_data,
                                      trade_key=trade_key)


class ApiExporter(BaseExporter):
    """
    Exporter class for interaction with the PowerBot API.

    This class can/ should be used when:
        - the requested data is recent enough to still be stored in the PowerBot instance (see data retention policy)
        - the requested data is fairly small in size (multiple hours, not multiple day -> extensive loading time &
          constant strain on the API rate limit)
        - the requested data is already stored in the local __pb_cache__ and has been loaded via API.

    ATTENTION: if you try to load data from your cache and the original data is already purged from your instance,
    you are no longer able to create an index of contract IDs to load the local data with. Should this occur, please
    load the data in question via the HistoryExporter.
    """
    api_key: str = Field(description="A Standard API Key",
                         example="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXX")
    host: str = Field(description="URL of the PowerBot instance to connect to",
                      example="https://backup.powerbot-trading.com/{COMPANY NAME}/{EXCHANGE}/v2/api")

    client: ApiClient = Field(description="Placeholder value, do not overwrite", default_factory=type(None))

    def __init__(self, **data: Any):
        super().__init__(**data)

        # Init client
        self.client = pb.init_client(api_key=self.api_key, host=self.host)

    @root_validator
    def check_credentials(cls, values):
        api_key, host = values.get('api_key'), values.get('host')

        pattern_key = "\w{8}-\w{4}-\w{4}-\w{4}-\w{12}"
        pattern_host = "https://\w{4,7}.powerbot-trading.com(:443)?/\w+/\w+/v\d{1}/api"

        assert re.match(pattern_key, api_key) and re.match(pattern_host, host), "Your credentials do not conform to the necessary formats"

        return values

    @validate_arguments
    def get_contracts(self,
                      time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss", default_factory=type(None)),
                      time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss", default_factory=type(None)),
                      contract_ids: list[str] = None,
                      contract_time: str = "all",
                      products: list[str] = None,
                      allow_udc: bool = False,
                      delivery_areas: list[str] = None) -> list[ContractItem]:
        """
        Loads all contracts for specified timeframe. Alternatively, a list of contract IDs can be passed instead of a timeframe.

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            contract_ids (list[str]): Optionally, a list of specific contract IDs can be passed to return contract objects
            contract_time (str): all, hourly, half-hourly or quarter-hourly (all includes UDC)
            products (list): Optional list of specific products to return
            allow_udc (bool): True if user-defined contracts (block products) should also be returned on contract_time = all
            delivery_areas (list): List of EIC-codes

        Returns:
            list[ContractItem]: List containing Contracts
        """
        return pb.get_contracts(api_client=self.client,
                                time_from=time_from,
                                time_till=time_till,
                                contract_ids=contract_ids,
                                contract_time=contract_time,
                                products=products,
                                allow_udc=allow_udc,
                                delivery_areas=delivery_areas)

    @validate_arguments
    def get_contract_ids(self,
                         time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss", default_factory=type(None)),
                         time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss", default_factory=type(None)),
                         contract_ids: list[str] = None,
                         contract_time: str = "all",
                         products: list[str] = None,
                         allow_udc: bool = False,
                         delivery_areas: list[str] = None) -> dict[str, list[str]]:
        """
        Loads all contract IDs for specified timeframe. Alternatively, a list of contract IDs can be passed instead of a timeframe, returning a
        dictionary of contract IDs compatible with all other functions of the Backtesting package.

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            contract_ids (list[str]): Optionally, a list of specific contract IDs can be passed to return contract objects
            contract_time (str): all, hourly, half-hourly or quarter-hourly (all includes UDC)
            products (list): Optional list of specific products to return
            allow_udc (bool): True if user-defined contracts (block products) should also be returned on contract_time = all
            delivery_areas (list): List of EIC-codes

        Returns:
            dict{key: (list[str])}: Dictionary of Contract IDs
        """
        return pb.get_contract_ids(api_client=self.client,
                                   time_from=time_from,
                                   time_till=time_till,
                                   contract_ids=contract_ids,
                                   contract_time=contract_time,
                                   products=products,
                                   allow_udc=allow_udc,
                                   delivery_areas=delivery_areas)

    @validate_arguments
    def get_public_trades(self,
                          contract_ids: dict[str, list[str]],
                          delivery_area: str,
                          contract_time: str,
                          iteration_delay: float = 0.4,
                          serialize_data: bool = True,
                          add_vwap: bool = False,
                          use_cached_data: bool = True,
                          caching: bool = True,
                          gzip_files: bool = True,
                          as_csv: bool = False) -> dict[str, pd.DataFrame]:
        """
        Load trade data for given contract IDs. If add_vwap is True, VWAP will be calculated for each trade, incorporating
        all previous trades.

        Args:
            contract_ids (dict): Dictionary of Contract IDs
            delivery_area (str): EIC Area Code for Delivery Area (not needed when loading from historic cache)
            contract_time (str): all, hourly, half-hourly or quarter-hourly
            iteration_delay (float): Optional delay between iterations to prevent hitting API rate limits
            serialize_data (bool): If False, request is received without serialization. Recommended for large data collections
            add_vwap (bool): If True, additional VWAP parameters will be added to each dataframe
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if data should be cached
            gzip_files (bool): True if cached files should be gzipped
            as_csv (bool): if True, will save files as CSV, additionally to JSON

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        return pb.get_public_trades(api_client=self.client,
                                    contract_ids=contract_ids,
                                    contract_time=contract_time,
                                    delivery_area=delivery_area,
                                    iteration_delay=iteration_delay,
                                    serialize_data=serialize_data,
                                    add_vwap=add_vwap,
                                    use_cached_data=use_cached_data,
                                    caching=caching,
                                    gzip_files=gzip_files,
                                    as_csv=as_csv)

    @validate_arguments
    def get_public_trades_by_days(self,
                                  previous_days: int,
                                  delivery_area: str,
                                  time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss", default_factory=type(None)),
                                  contract_time: str = None,
                                  contract_id: str = None) -> dict[str, pd.DataFrame]:
        """
        Gets the contract ID specified by a timeframe or directly by ID and load all trade data for this contract and all
        contracts in the same timeframe for X previous days.

        Args:
            time_from (datetime): YYYY-MM-DD hh:mm:ss
            previous_days (int): Amount of previous days to load data for
            delivery_area (str): EIC Area Code for Delivery Area
            contract_time (str): hourly, half-hourly or quarter-hourly
            contract_id (str): specific contract ID

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        return pb.get_public_trades_by_days(api_client=self.client,
                                            previous_days=previous_days,
                                            delivery_area=delivery_area,
                                            time_from=time_from,
                                            contract_time=contract_time,
                                            contract_id=contract_id)

    @validate_arguments
    def get_contract_history(self,
                             contract_ids: dict[str, list[str]],
                             delivery_area: str,
                             iteration_delay: float = 0.4,
                             serialize_data: bool = True,
                             use_cached_data: bool = True,
                             caching: bool = True,
                             gzip_files: bool = True,
                             as_csv: bool = False) -> dict[str, pd.DataFrame]:
        """
        Load contract history for given contract IDs.

        Args:
            contract_ids (dict): Dictionary of Contract IDs
            delivery_area (str): EIC Area Code for Delivery Area (not needed when loading from historic cache)
            iteration_delay (float): Optional delay between iterations to prevent hitting API rate limits
            serialize_data (bool): If False, request is received without serialization. Recommended for large data collections
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if data should be cached
            gzip_files (bool): True if cached files should be gzipped
            as_csv (bool): if True, will save files as CSV, additionally to JSON

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        return pb.get_contract_history(api_client=self.client,
                                       contract_ids=contract_ids,
                                       delivery_area=delivery_area,
                                       iteration_delay=iteration_delay,
                                       serialize_data=serialize_data,
                                       use_cached_data=use_cached_data,
                                       caching=caching,
                                       gzip_files=gzip_files,
                                       as_csv=as_csv)

    @validate_arguments
    def get_signals(self,
                    time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                    time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                    delivery_area: str = None,
                    portfolio_id: list[str] = None) -> list[Signal]:
        """
        Function gathers all Signals received by the API in the specified time period and gathers them in a list.

        Args:
            time_from (datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
            time_till (datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
            delivery_area (str): EIC Area Code for Delivery Area
            portfolio_id (str): List of all portfolios that signals should be loaded from

        Returns:
            list[Signal]
        """
        return pb.get_signals(api_client=self.client,
                              time_from=time_from,
                              time_till=time_till,
                              delivery_area=delivery_area,
                              portfolio_id=portfolio_id)

    @validate_arguments
    def get_own_trades(self,
                       time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                       time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                       delivery_area: str = None,
                       portfolio_id: list[str] = None) -> list[Trade]:
        """
        Function to collect all Own Trades for the defined time period, either specific to portfolio and/or delivery area
        or all portfolios and delivery areas used API key has access to.

        Args:
            time_from (datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
            time_till (datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
            delivery_area (str): EIC Area Code for Delivery Area
            portfolio_id (list[str]): List of specific portfolio IDs to load trades from. If left out, will load from all IDs.

        Returns:
            list[Trade]
        """
        return pb.get_own_trades(api_client=self.client,
                                 time_from=time_from,
                                 time_till=time_till,
                                 delivery_area=delivery_area,
                                 portfolio_id=portfolio_id)

    @validate_arguments
    def get_internal_trades(self,
                            time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                            time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                            delivery_area: str = None,
                            portfolio_id: list[str] = None) -> list[InternalTrade]:
        """
        Function to collect all Internal Trades for the defined time period, either specific to portfolio and/or delivery
        area or all portfolios and delivery areas used API key has access to.

        Args:
            time_from (datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
            time_till (datetime): YYYY-MM-DD or YYYY-MM-DD hh:mm:ss
            delivery_area (str): EIC Area Code for Delivery Area
            portfolio_id (list[str]): List of specific portfolio IDs to load trades from. If left out, will load from all IDs.

        Returns:
            list[InternalTrade]
        """
        return pb.get_internal_trades(api_client=self.client,
                                      time_from=time_from,
                                      time_till=time_till,
                                      delivery_area=delivery_area,
                                      portfolio_id=portfolio_id)

    @validate_arguments
    def get_own_orders(self,
                       delivery_area: str = None,
                       portfolio_id: list[str] = None,
                       contract_ids: Union[list[str], dict[str, list[str]]] = None,
                       active_only: bool = False) -> list[OwnOrder]:
        """
        Function to collect all available Own Orders, either specific to portfolio and/or delivery area or all portfolios
        and delivery areas used API key has access to.

        Args:
            delivery_area (str): EIC Area Code for Delivery Area
            portfolio_id (list[str]): List of specific portfolio IDs to load trades from. If left out, will load from all IDs.
            contract_ids (list/dict): Collection of contract IDs to specifically load own orders for
            active_only (bool):  True if only active orders should be loaded. If False, loads also hibernate and inactive.

        Returns:
            list[OwnOrder]
        """
        return pb.get_own_orders(api_client=self.client,
                                 delivery_area=delivery_area,
                                 portfolio_id=portfolio_id,
                                 contract_ids=contract_ids,
                                 active_only=active_only)

    @validate_arguments
    def calc_trade_vwap(self,
                        contract_time: str,
                        delivery_area: str,
                        trade_data: dict[str, pandas_DataFrame] = None,
                        time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss", default_factory=type(None)),
                        previous_days: int = 10,
                        contract_id: str = None,
                        index: str = "ID3") -> pd.DataFrame:
        """
        Function gets trades for a certain contract for X previous days in the same delivery period and calculates their
        VWAP for ID3 or ID1 or all. Generates a new list of trades for these contracts.
        Can take either a time period or a specific contract ID to load data for.

        If previous days is 0, only the trades for the original time period/ contract will be loaded.

        Can also be called directly from get_public_trades with parameter 'add_vwap' to add VWAP to loaded trades.

        Args:
            contract_time (str): hourly, half-hourly or quarter-hourly
            delivery_area (str): Area Code for Delivery Area
            trade_data (dict[str, pd.DataFrame]: Dictionary of Dataframes containing Contract Trade Data
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            previous_days (int): Amount of previous days to load data
            contract_id (str): ID of specific Contract
            index (str): all, ID3, ID1

        Returns:
            DataFrame: Trade Data with added calculated fields
        """
        return pb.calc_trade_vwap(api_client=self.client,
                                  contract_time=contract_time,
                                  delivery_area=delivery_area,
                                  trade_data=trade_data,
                                  time_from=time_from,
                                  previous_days=previous_days,
                                  contract_id=contract_id,
                                  index=index)


class HistoryExporter(BaseExporter):
    """
    Exporter class for interaction with the PowerBot History API and the subsequently created local __pb_cache__.

    This class can/ should be used when:
        - the requested data is older than at least 2-3 days and has already been made available via History API
        - the requested data is already stored in the local __pb_cache__ and has been loaded via History API.

    ATTENTION: loading historic data from the History API will create a json file containing all contract information
    for the respective day. If this file should be deleted, the HistoryExporter can no longer create an index of
    contract IDs and therefore not load anything from the local cache.
    """
    exchange: str = Field(description="The exchange data should be loaded for")
    delivery_area: str = Field(description="EIC-code of the delivery area data should be loaded for")

    client: HistoryApiClient = Field(description="Placeholder value, do not overwrite", default_factory=type(None))

    def __init__(self, **data: Any):
        super().__init__(**data)

        # Init client
        self.client = pb.init_historic_client(self.exchange, self.delivery_area)

    @root_validator
    def check_credentials(cls, values):
        exchange, delivery_area = values.get('exchange'), values.get('delivery_area')

        assert exchange in EXCHANGES, "Exchange is not in allowed exchanges"
        assert delivery_area in EIC_CODES[exchange], "Delivery area is not in allowed delivery areas for this exchange"

        return values

    @validate_arguments
    def get_historic_data(self,
                          api_key: str,
                          day_from: Union[str, datetime],
                          day_to: Union[str, datetime] = None,
                          delivery_areas: list[str] = None,
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
            day_from (str): Datetime/ String in format YYYY-MM-DD
            day_to (str): Datetime/ String in format YYYY-MM-DD
            delivery_areas (list): List of EIC Area Codes for Delivery Areas
            cache_path (Path): Optional path for caching files
            extract_files (bool): True if zipped files should be extracted automatically (Warning: immense size increase)
            process_data (bool): True if extracted files should be processed to resemble files loaded via API
            skip_on_error (bool): True if all dates that cannot possibly be loaded (e.g. due to lack of access rights) are
            skipped if the difference between day_from and day_to is at least 2 days
            keep_zip_files (bool): True if zip-files should be kept after download

        Returns:
            list of loaded file paths | dict
        """
        return pb.get_historic_data(api_key=api_key,
                                    exchange=self.client.exchange,
                                    delivery_areas=delivery_areas if delivery_areas else [self.client.delivery_area],
                                    day_from=day_from,
                                    day_to=day_to,
                                    cache_path=cache_path,
                                    extract_files=extract_files,
                                    process_data=process_data,
                                    skip_on_error=skip_on_error,
                                    keep_zip_files=keep_zip_files)

    @validate_arguments
    def get_contracts(self,
                      time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                      time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                      contract_time: Optional[str] = "all",
                      products: Optional[list[str]] = None,
                      allow_udc: Optional[bool] = False) -> list[dict]:
        """
        Loads all contract IDs for specified timeframe from the local cache. The cached data has to have been loaded via get_historic_data, as
        this function utilizes the contract file as an index.

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            contract_time (str): all, hourly, half-hourly or quarter-hourly (all includes UDC)
            products (list): Optional list of specific products to return
            allow_udc (bool): True if user-defined contracts (block products) should also be returned on contract_time = all

        Returns:
            list[dict]: List of Contract Dictionaries
        """
        return pb.get_historic_contract_ids(client=self.client,
                                            time_from=time_from,
                                            time_till=time_till,
                                            contract_time=contract_time,
                                            products=products if products else [],
                                            allow_udc=allow_udc,
                                            return_contract_objects=True)

    @validate_arguments
    def get_contract_ids(self,
                         time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                         time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                         contract_time: Optional[str] = "all",
                         products: Optional[list[str]] = None,
                         allow_udc: Optional[bool] = False) -> dict[str, list[str]]:
        """
        Loads all contract IDs for specified timeframe from the local cache. The cached data has to have been loaded via get_historic_data, as this
        function utilizes the contract file as an index.

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            contract_time (str): all, hourly, half-hourly or quarter-hourly (all includes UDC)
            products (list): Optional list of specific products to return
            allow_udc (bool): True if user-defined contracts (block products) should also be returned on contract_time = all

        Returns:
            dict{key: (list[str])}: Dictionary of Contract IDs
        """
        return pb.get_historic_contract_ids(client=self.client,
                                            time_from=time_from,
                                            time_till=time_till,
                                            contract_time=contract_time,
                                            products=products if products else [],
                                            allow_udc=allow_udc)

    @validate_arguments
    def get_public_trades(self,
                          contract_ids: dict[str, list[str]],
                          contract_time: str,
                          add_vwap: bool = False,
                          as_csv: bool = False) -> dict[str, pd.DataFrame]:
        """
        Load trade data for given contract IDs from local cache. If add_vwap is True, VWAP will be calculated for each
        trade, incorporating all previous trades.

        Args:
            contract_ids (dict): Dictionary of Contract IDs
            contract_time (str): all, hourly, half-hourly or quarter-hourly
            add_vwap (bool): If True, additional VWAP parameters will be added to each dataframe
            as_csv (bool): if True, will save files as CSV, additionally to JSON

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        return pb.get_public_trades(api_client=self.client,
                                    contract_ids=contract_ids,
                                    contract_time=contract_time,
                                    add_vwap=add_vwap,
                                    caching=True if as_csv else False,
                                    as_csv=as_csv)

    @validate_arguments
    def get_contract_history(self,
                             contract_ids: dict[str, list[str]],
                             as_csv: bool = False) -> dict[str, pd.DataFrame]:
        """
        Load contract history for given contract IDs from the local cache.

        Args:
            contract_ids (dict): Dictionary of Contract IDs
            as_csv (bool): if True, will save files as CSV, additionally to JSON

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        return pb.get_contract_history(api_client=self.client,
                                       contract_ids=contract_ids,
                                       as_csv=as_csv)


class SQLExporter(BaseExporter):
    """
    Exporter class for interaction with a SQL database containing PowerBot data.

    This class can/ should be used when:
        - a database containing the structure as defined per PowerBot SQLImporter exists and contains data.

    Instructions for passing arguments to exporter functions:
        - String
            If keyword argument is a string, it will be simply compared with '='. Optionally, a mathematical/ SQL
            operator (LIKE, BETWEEN x AND y, <, <=, >, >=, <>) can be passed within the string. This operator will be used instead of '='.

            Example:
                best_bid='> 0.00' -> best_bid > 0.00
                as_of="> 2020-09-20 00:00:00" -> as_of > '2020-09-20 00:00:00'
                exec_time='BETWEEN 2021-09-10 AND 2021-09-11' -> exec_time BETWEEN '2021-09-10' AND '2021-09-11'

        - Tuple
            If keyword argument is a tuple, it will be checked, if parameter is one of the elements of the tuple.

            Example:
                exchange=("Epex","NordPool") -> exchange IN ('Epex','NordPool')

        - List
            If keyword argument is a list, each element will be checked if it is in the parameter.

            Example:
                portfolio_ids=["TP1","TP2"] -> (portfolio_id LIKE '%TP1%' OR portfolio_id LIKE '%TP2%')

        - Dictionary
            If keyword argument is a dictionary, all values will be extracted and put into a tuple. Afterwards, the
            behaviour is the same as with tuples.

            Example:
                exchange={1:"Epex",2:"NordPool"} -> exchange IN ("Epex","NordPool")

        - Datetime
            If keyword argument is a datetime, parameter will be searched for the exact time of the datetime argument.
            This will in most cases not provide a satisfying result, therefore it is recommended to pass a datetime as
            a string with an operator in front.

            Example:
                as_of=datetime.datetime(2020, 9, 30, 10, 0, 0) -> as_of = '2020-09-30 10:00:00'
    """
    db_type: str = Field(description="Database type")
    user: str = Field(description="Database user")
    password: str = Field(description="Database password")
    host: str = Field(description="Database host address")
    database: str = Field(description="Database name")
    port: int = Field(description="Database port")

    logger: None = Field(description="Placeholder value, do not overwrite", default_factory=type(None))
    engine: None = Field(description="Placeholder value, do not overwrite", default_factory=type(None))

    SQL_ERRORS = (
        InterfaceError,
        OperationalError,
        ProgrammingError,
        TimeoutError,
    )

    def __init__(self, **data: Any):
        super().__init__(**data)

        # Logging Setup
        logging.basicConfig(format="PowerBot_SQL_Exporter %(asctime)s %(levelname)-8s %(message)s",
                            level=logging.INFO)
        self.logger = logging.getLogger()

        # Initialize Connection
        self.engine = self.__create_sql_engine()

    @validator("user", "password")
    def validate_user_and_password(cls, value):
        value = quote(value)

        return value

    @validator("db_type")
    def validate_db_type(cls, value):
        allowed_db_types = ['mysql', 'mariadb', 'postgresql', 'oracle', 'mssql', 'amazon_redshift', 'apache_drill',
                            'apache_druid', 'apache_hive', 'apache_solr', 'cockroachdb', 'cratedb', 'exasolution',
                            'firebird', 'ibm_db2', 'monetdb', 'snowflake', 'teradata_vantage']

        assert value in allowed_db_types, f"Database {value} is not in allowed database"

        return value

    def __install_packages(self):
        """
        Tests if required packages for chosen SQL database type are available and installs them if necessary.
        """
        db_packages = {"mysql": ["mysql-connector-python"],
                       "mariadb": ["PyMySQL"],
                       "postgresql": ["psycopg2"],
                       "oracle": ["cx-Oracle"],
                       "mssql": ["pyodbc"],
                       "amazon_redshift": ["sqlalchemy-redshift", "psycopg2"],
                       "apache_drill": ["sqlalchemy-drill"],
                       "apache_druid": ["pydruid"],
                       "apache_hive": ["PyHive"],
                       "apache_solr": ["sqlalchemy-solr"],
                       "cockroachdb": ["sqlalchemy-cockroachdb", "psycopg2"],
                       "cratedb": ["crate-python"],
                       "exasolution": ["sqlalchemy_exasol", "pyodbc"],
                       "firebird": ["sqlalchemy-firebird"],
                       "ibm_db2": ["ibm_db_sa"],
                       "monetdb": ["sqlalchemy_monetdb"],
                       "snowflake": ["snowflake-sqlalchemy"],
                       "teradata_vantage": ["teradatasqlalchemy"]}

        self.logger.info("Now installing the following necessary package(s):\n"
                         f"{db_packages[self.db_type]}")

        import subprocess
        import sys
        for pkg in db_packages[self.db_type]:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

        return self.__create_sql_engine()

    def __create_sql_engine(self):
        """
        Initializes connection to SQL database
        """
        db_types = {"mysql": "mysql+mysqlconnector",
                    "mariadb": "mariadb+pymysql",
                    "postgresql": "postgresql+psycopg2",
                    "oracle": "oracle+cx_oracle",
                    "mssql": "mssql+pyodbc",
                    "amazon_redshift": "redshift+psycopg2",
                    "apache_drill": "drill+sadrill",
                    "apache_druid": "druid",
                    "apache_hive": "hive",
                    "apache_solr": "solr",
                    "cockroachdb": "cockroachdb",
                    "cratedb": "crate",
                    "exasolution": "exa+pyodbc",
                    "firebird": "firebird",
                    "ibm_db2": "db2+ibm_db",
                    "monetdb": "monetdb",
                    "snowflake": "snowflake",
                    "teradata_vantage": "teradatasql"}

        if self.port:
            try:
                engine = create_engine(
                    f'{db_types[self.db_type]}://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}')
            except:
                pass
        try:
            engine = create_engine(
                f'{db_types[self.db_type]}://{self.user}:{self.password}@{self.host}/{self.database}')

            # Test connection
            engine.connect()

        except (NoSuchModuleError, ModuleNotFoundError):
            self.logger.info("You currently do not have all the necessary packages installed to access a database of"
                             f" type {self.db_type}.")
            return self.__install_packages()

        except ProgrammingError:
            self.logger.error("Could not establish connection to database. Please recheck your credentials!")

        except InterfaceError:
            self.logger.error("Database is not available at the moment!")

        except Exception as e:
            raise SQLExporterError(f"Could not establish connection to database. Reason: \n{e}")

        self.logger.info(f"Connection to database '{self.database}' with user '{self.user}' established")
        self.logger.info("Connection ready to export data")

        return engine

    @contextmanager
    def __get_session(self):
        """
        Context manager to handle sessions connecting to the database.
        """
        try:
            session = Session(bind=self.engine)
        except self.SQL_ERRORS:
            session = Session(bind=self.__create_sql_engine())
        try:
            yield session
        finally:
            session.close()

    @validate_arguments
    def get_contracts(self,
                      as_dataframe: bool = True,
                      **kwargs) -> pd.DataFrame:
        """
        Exports contracts from SQL database. To use different mathematical/SQL operators, pass keyworded arguments
        as strings and include the desired operator followed by a space (e.g. revisions='<> 0').

        Following operators can be passed:
        LIKE, <, <=, >, >=, <>

        Following parameters can be passed as optional keyworded arguments:
        exchange, contract_id, product, type, undrlng_contracts, name, delivery_start, delivery_end, delivery_areas,
        predefined, duration, delivery_units

        Args:
            as_dataframe (bool): If False -> returns list
            **kwargs: any additional fields of SQL table

        Returns:
            list/ DataFrame: SQL query
        """
        allowed_kwargs = ["name", "delivery_areas", "delivery_start", "delivery_end", "delivery_areas", "type",
                          "predefined", "duration", "delivery_units", "contract_id", "exchange", "product",
                          "undrlng_contracts"]

        sql_params = self.__handle_sql_args(kwargs, allowed_kwargs)

        with self.__get_session() as session:
            result = session.execute(f"SELECT * FROM contracts{sql_params}").fetchall()

        if as_dataframe:
            output = pd.DataFrame(result)
            output = output.rename(
                columns={0: 'exchange', 1: 'contract_id', 2: 'product', 3: 'type', 4: 'undrlng_contracts',
                         5: 'name', 6: 'delivery_start', 7: 'delivery_end', 8: 'delivery_areas',
                         9: 'predefined', 10: 'duration', 11: 'delivery_units', 12: 'details'})
            return output

        return result

    @validate_arguments
    def get_contract_ids(self,
                         time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                         time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                         delivery_area: str = Field(description="EIC-code of delivery area"),
                         contract_time: str = "all",
                         exchange: str = "epex",
                         as_list: bool = False) -> dict[str, list[str]]:
        """
            Returns dictionary of contract IDs in a format compatible with backtesting pipeline.

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            delivery_area (str): EIC-Code
            contract_time (str): all, hourly, half-hourly or quarter-hourly
            exchange (str): Name of exchange in lowercase
            as_list (bool): True if output should be list of contract IDs

        Returns:
            dict{key: (list[str])}: Dictionary of Contract IDs
        """
        del_units = {"hourly": 1, "half-hourly": 0.5, "quarter-hourly": 0.25}

        if (del_units := del_units.get(contract_time)):
            sql_addition = f" AND delivery_units = {del_units}"
        else:
            sql_addition = ""

        if not isinstance(time_from, datetime) or not isinstance(time_till, datetime):
            raise SQLExporterError("Please use datetime format for time_from & time_till!")

        with self.__get_session() as session:
            result = session.execute(f"SELECT delivery_start, delivery_end, contract_id FROM contracts "
                                     f"WHERE delivery_start >= '{time_from}' "
                                     f"AND delivery_end <= '{time_till}' "
                                     f"AND delivery_areas LIKE '%{delivery_area}%' "
                                     f"AND product IN {PRODUCTS[contract_time]} "
                                     f"AND exchange = '{exchange}'" + sql_addition).fetchall()
            if not result:
                result = session.execute(f"SELECT delivery_start, delivery_end, contract_id FROM contracts "
                                         f"WHERE delivery_start >= '{time_from}' "
                                         f"AND delivery_end <= '{time_till}' "
                                         f"AND product IN {PRODUCTS[contract_time]} "
                                         f"AND exchange = '{exchange}'" + sql_addition).fetchall()

        if not as_list:
            contract_ids = {f"{i[0].strftime(DATE_YMD_TIME_HM)} - {i[1].strftime(TIME_HM)}": [] for i in result}
            for i in result:
                contract_ids[f"{i[0].strftime(DATE_YMD_TIME_HM)} - {i[1].strftime(TIME_HM)}"].append(i[2])

            # Quality Check
            if not all(i for i in contract_ids.values()):
                raise SQLExporterError("There is no contract data for the specified timeframe!")
        else:
            contract_ids = [i for i in result]

        self.logger.info("Successfully exported contract ids")
        return contract_ids

    @validate_arguments
    def get_public_trades(self,
                          as_dataframe: bool = True,
                          delivery_area: list[str] = None,
                          exchange: str = "epex",
                          use_cached_data: bool = True,
                          caching: bool = False,
                          gzip_files: bool = True,
                          as_csv: bool = False,
                          **kwargs) -> Union[pd.DataFrame, dict[str, pd.DataFrame]]:
        """
        Exports trades from SQL database. To use different mathematical/SQL operators, pass keyworded arguments
        as strings and include the desired operator followed by a space (e.g. price='<> 0.00').

        Following operators can be passed:
        LIKE, <, <=, >, >=, <>

        Following parameters can be passed as optional keyworded arguments (kwargs):
        price, quantity, prc_x_qty, exchange, contract_id, trade_id, exec_time, api_timestamp, self_trade

        Args:
            as_dataframe (bool): If False -> returns list
            delivery_area (list): List of EIC Area Codes for Delivery Areas
            exchange (str): Exchange of requested data
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if data should be cached
            gzip_files (bool): True if cached files should be gzipped
            as_csv (bool): if True, will save files as CSV, additionally to JSON
            **kwargs: any additional fields of SQL table

        Returns:
            list/ DataFrame: SQL query
        """
        if as_dataframe and len(delivery_area) > 1:
            raise ValueError("Please only give one delivery area when loading data as dataframes")

        trades = {}

        if use_cached_data and as_dataframe and (contract_ids := kwargs.get("contract_id")):
            missing_contracts = {}

            # Find __cache__ directory
            cache_path = _find_cache()

            for key, value in tqdm(contract_ids.items(), desc="Loading Cached Trades", unit="time periods", leave=False):
                filepath = _get_file_cachepath(None, key, delivery_area[0], exchange)
                tmp_df = None

                for i in [".json.gz", ".json"]:
                    if cache_path.joinpath(f"{filepath}_trades{i}").exists():
                        tmp_df = pd.read_json(cache_path.joinpath(f"{filepath}_trades{i}"), dtype=False)

                if isinstance(tmp_df, pd.DataFrame):
                    tmp_df['api_timestamp'] = pd.to_datetime(tmp_df['api_timestamp'])
                    tmp_df['exec_time'] = pd.to_datetime(tmp_df['exec_time'])
                    tmp_df = tmp_df.astype({"price": "float64", "trade_id": "str", "contract_id": "str"})
                    for i in ["price", "quantity"]:
                        tmp_df[i] = round(tmp_df[i], 2)

                    # Filter out any contract IDs that are not in value
                    trades[key] = tmp_df.loc[tmp_df.contract_id.isin(value)]

                else:
                    # Save Missing Contract IDs
                    missing_contracts[key] = value

            kwargs["contract_id"] = missing_contracts if missing_contracts else contract_ids

        if (contract_ids := kwargs.get("contract_id")) is None or isinstance(contract_ids, dict) and len(contract_ids) > 0:
            allowed_kwargs = ["price", "quantity", "prc_x_qty", "exchange", "contract_id", "trade_id", "exec_time",
                              "api_timestamp", "self_trade"]

            sql_params = self.__handle_sql_args(kwargs, allowed_kwargs)

            if delivery_area:
                for i in delivery_area:
                    sql_params += f" {'AND' if 'WHERE' in sql_params else 'WHERE'} (buy_delivery_area = '{i}' OR sell_delivery_area = '{i}')"

            with self.__get_session() as session:
                if not (result := session.execute(f"SELECT * FROM public_trades{sql_params}").fetchall()):
                    raise SQLExporterError("There is no trade data for the specified timeframe!")
        else:
            result = None

        if as_dataframe:
            if result:
                output = pd.DataFrame(result)
                if not output.empty:
                    output = output.rename(columns={0: 'exchange', 1: 'contract_id', 2: 'trade_id', 3: 'api_timestamp',
                                                    4: 'exec_time', 5: 'buy_delivery_area', 6: 'sell_delivery_area',
                                                    7: 'price', 8: 'quantity', 9: 'prc_x_qty', 10: "currency",
                                                    11: 'self_trade'})

                    output['api_timestamp'] = pd.to_datetime(output['api_timestamp'], utc=True)
                    output['exec_time'] = pd.to_datetime(output['exec_time'], utc=True)
                    trades |= self.__convert_dataframe("trades", output)

            # Caching
            if caching:
                _cache_data("trades", trades, delivery_area[0], api_client=None, gzip_files=gzip_files, as_csv=as_csv, exchange=exchange)

            self.logger.info("Successfully exported trades")
            return trades

        self.logger.info("Successfully exported trades")

        return result

    @validate_arguments
    def get_contract_history(self,
                             as_dataframe: bool = True,
                             delivery_area: list[str] = None,
                             exchange: str = "epex",
                             use_cached_data: bool = True,
                             caching: bool = False,
                             gzip_files: bool = True,
                             as_csv: bool = False,
                             **kwargs) -> Union[pd.DataFrame, dict[str, pd.DataFrame]]:
        """
        Exports contract revisions from SQL database. To use different mathematical/SQL operators, pass keyworded arguments
        as strings and include the desired operator followed by a space (e.g. best_bid='<> 0.00').

        Following operators can be passed:
        LIKE, <, <=, >, >=, <>

        Following parameters can be passed as optional keyworded arguments:
        exchange, contract_id, exchange, delivery_area, revision_no, as_of, best_bid, best_bid_qty, best_ask,
        best_ask_qty, vwap, high, low, last_price, last_qty, last_trade_time, volume, delta

        Args:
            as_dataframe (bool): If False -> returns list
            delivery_area (list): List of EIC Area Codes for Delivery Areas
            exchange (str): Exchange of requested data
            use_cached_data (bool): If True, function tries to load data from cache wherever possible
            caching (bool): True if data should be cached
            gzip_files (bool): True if cached files should be gzipped
            as_csv (bool): if True, will save files as CSV, additionally to JSON
            **kwargs: any additional fields of SQL table

        Returns:
            list/ DataFrame: SQL query
        """
        orders = {}
        missing_contracts = {}

        if as_dataframe and len(delivery_area) > 1:
            raise ValueError("Please only give one delivery area when loading data as dataframes")

        if use_cached_data and as_dataframe and (contract_ids := kwargs.get("contract_id")):
            # Find __cache__ directory
            cache_path = _find_cache()
            for key, value in contract_ids.items():
                filepath = _get_file_cachepath(None, key, delivery_area[0], exchange)
                tmp_df = None

                for i in [".json.gz", ".json"]:
                    if cache_path.joinpath(f"{filepath}_ordhist{i}").exists():
                        tmp_df = pd.read_json(cache_path.joinpath(f"{filepath}_ordhist{i}"), dtype=False,
                                              convert_dates=False)

                if isinstance(tmp_df, pd.DataFrame):
                    tmp_df['as_of'] = pd.to_datetime(tmp_df['as_of'])

                    cols = {"internal_trades": "object", "contract_id": "str", "auction_price": "float64"}
                    cols = {k: v for k, v in cols.items() if k in tmp_df.columns}
                    tmp_df = tmp_df.astype(cols, errors='ignore')
                    for i in ["best_bid_price", "best_bid_quantity", "best_ask_price", "best_ask_quantity", "last_price",
                              "last_quantity", "total_quantity", "high", "low", "vwap"]:
                        try:
                            tmp_df[i] = round(tmp_df[i], 2)
                        except (TypeError, KeyError):
                            pass

                    if "orders" in tmp_df.columns:
                        order_list = tmp_df.orders.tolist()
                        for order_type in ["bid", "ask"]:
                            for i in order_list:
                                if order_type in i and i[order_type]:
                                    for x in i[order_type]:
                                        for param in ["quantity", "price"]:
                                            x[param] = round(x[param], 2)
                                        try:
                                            x["order_entry_time"] = datetime.strptime(x["order_entry_time"],
                                                                                      "%Y-%m-%dT%H:%M:%S.%fZ").replace(
                                                tzinfo=tzutc())
                                        except ValueError:
                                            x["order_entry_time"] = datetime.strptime(x["order_entry_time"],
                                                                                      "%Y-%m-%dT%H:%M:%SZ").replace(
                                                microsecond=0, tzinfo=tzutc())
                        tmp_df["orders"] = order_list

                    # Filter out any contract IDs that are not in value
                    orders[key] = tmp_df.loc[tmp_df.contract_id.isin(value)]
                else:
                    # Save Missing Contract IDs
                    missing_contracts[key] = value

            kwargs["contract_id"] = missing_contracts

        if (contract_ids := kwargs.get("contract_id")) is None or isinstance(contract_ids, dict) and len(contract_ids) > 0:
            allowed_kwargs = ["exchange", "contract_id", "delivery_area", "revision_no", "as_of", "best_bid",
                              "best_bid_qty", "best_ask", "best_ask_qty", "vwap", "high", "low", "last_price",
                              "last_qty", "last_trade_time", "volume", "delta"]

            sql_params = self.__handle_sql_args(kwargs, allowed_kwargs)

            if delivery_area and not as_dataframe and len(delivery_area) > 1:
                sql_params += f" AND delivery_area IN {tuple(delivery_area)}"
            else:
                sql_params += f" AND delivery_area = '{delivery_area[0]}'"

            with self.__get_session() as session:
                if not (result := session.execute(f"SELECT * FROM contract_revisions{sql_params}").fetchall()):
                    raise SQLExporterError("There is no order data for the specified timeframe!")
        else:
            result = None

        if as_dataframe:
            if result:
                output = pd.DataFrame(result)
                if not output.empty:
                    output = output.rename(columns={0: 'exchange', 1: 'contract_id', 2: 'delivery_area', 3: 'revision_no',
                                                    4: 'as_of', 5: 'best_bid', 6: 'best_bid_qty', 7: 'best_ask',
                                                    8: 'best_ask_qty', 9: 'vwap', 10: 'high', 11: 'low', 12: 'last_price',
                                                    13: 'last_qty', 14: "last_trade_time", 15: 'volume', 16: 'delta',
                                                    17: 'bids', 18: 'asks'})
                orders |= self.__convert_dataframe("orders", output)

            # Caching
            if caching:
                _cache_data("ordhist", orders, delivery_area[0], api_client=None, gzip_files=gzip_files, as_csv=as_csv, exchange=exchange)

            self.logger.info("Successfully exported contract history")
            return orders

        self.logger.info("Successfully exported contract history")

        return result

    @validate_arguments
    def get_own_trades(self,
                       delivery_area: list[str] = None,
                       as_dataframe: bool = True,
                       as_objects: bool = False,
                       **kwargs) -> Union[pd.DataFrame, list[Trade]]:
        """
        Exports Own Trades from SQL database. To use different mathematical/SQL operators, pass keyworded arguments
        as strings and include the desired operator followed by a space (e.g. position_short='<> 0.00').

        Following operators can be passed:
        LIKE, <, <=, >, >=, <>

        Following parameters can be passed as optional keyworded arguments (kwargs):
        exchange, contract_id, contract_name, prod, delivery_start, delivery_end, trade_id, api_timestamp, exec_time,
        buy, sell, price, quantity, state, buy_delivery_area, sell_delivery_area, buy_order_id, buy_clOrderId, buy_txt,
        buy_user_code, buy_member_id, buy_aggressor_indicator, buy_portfolio_id, sell_order_id, sell_clOrderId,
        sell_txt, sell_user_code, sell_member_id, sell_aggressor_indicator, sell_portfolio_id, self_trade, pre_arranged,
        pre_arrange_type

        Args:
            delivery_area (tuple[str]): Multiple delivery areas inside a tuple. Single del. area can be passed as a string
            as_dataframe (bool): True if output should be DataFrame
            as_objects (bool): True if output should be list of OwnTrades
            **kwargs: any additional fields of SQL table

        Returns:
            list: SQL query
        """

        allowed_kwargs = ["exchange", "contract_id", "contract_name", "prod", "delivery_start", "delivery_end",
                          "trade_id",
                          "api_timestamp", "exec_time", "buy", "sell", "price", "quantity", "state",
                          "buy_delivery_area",
                          "sell_delivery_area", "buy_order_id", "buy_clOrderId", "buy_txt", "buy_user_code",
                          "buy_member_id",
                          "buy_aggressor_indicator", "buy_portfolio_id", "sell_order_id", "sell_clOrderId", "sell_txt",
                          "sell_user_code", "sell_member_id", "sell_aggressor_indicator", "sell_portfolio_id",
                          "self_trade",
                          "pre_arranged", "pre_arrange_type"]

        sql_params = self.__handle_sql_args(kwargs, allowed_kwargs)

        if delivery_area:
            for i in delivery_area:
                sql_params += f" AND (buy_delivery_area = '{i}' OR sell_delivery_area = '{i}')"

        with self.__get_session() as session:
            result = session.execute(f"SELECT * FROM own_trades{sql_params}").fetchall()

        self.logger.info("Successfully exported own trades")

        # Convert data back to Trade objects
        if result and as_objects:
            own_trades = [Trade(exchange=i[0],
                                contract_id=i[1],
                                contract_name=i[2],
                                prod=i[3],
                                delivery_start=i[4],
                                delivery_end=i[5],
                                trade_id=i[6],
                                api_timestamp=i[7],
                                exec_time=i[8],
                                buy=i[9],
                                sell=i[10],
                                price=i[11],
                                quantity=i[12],
                                delivery_area=i[13],
                                state=i[14],
                                buy_delivery_area=i[15],
                                sell_delivery_area=i[16],
                                buy_order_id=i[17],
                                buy_cl_order_id=i[18],
                                buy_txt=i[19],
                                buy_user_code=i[20],
                                buy_member_id=i[21],
                                buy_aggressor_indicator=i[22],
                                buy_portfolio_id=i[23],
                                sell_order_id=i[24],
                                sell_cl_order_id=i[25],
                                sell_txt=i[26],
                                sell_user_code=i[27],
                                sell_member_id=i[28],
                                sell_aggressor_indicator=i[29],
                                sell_portfolio_id=i[30],
                                self_trade=i[31],
                                pre_arranged=i[32],
                                pre_arrange_type=i[33])
                          for i in result]
            return own_trades

        if as_dataframe:
            return pd.DataFrame(result)

        return result

    @validate_arguments
    def get_internal_trades(self,
                            delivery_area: tuple[str] = None,
                            as_dataframe: bool = True,
                            as_objects: bool = False,
                            **kwargs) -> Union[pd.DataFrame, list[InternalTrade]]:
        """
        Exports Internal Trades from SQL database. To use different mathematical/SQL operators, pass keyworded arguments
        as strings and include the desired operator followed by a space (e.g. position_short='<> 0.00').

        Following operators can be passed:
        LIKE, <, <=, >, >=, <>

        Following parameters can be passed as optional keyworded arguments (kwargs):
        exchange, contract_id, contract_name, prod, delivery_start, delivery_end, internal_trade_id, api_timestamp,
        exec_time, price, quantity, state, buy_delivery_area, sell_delivery_area, buy_order_id, buy_clOrderId, buy_txt,
        buy_aggressor_indicator, buy_portfolio_id, sell_order_id, sell_clOrderId, sell_txt, sell_aggressor_indicator,
        sell_portfolio_id

        Args:
            delivery_area (tuple[str]): Multiple delivery areas inside a tuple. Single del. area can be passed as a string
            as_dataframe (bool): True if output should be DataFrame
            as_objects (bool): True if output should be list of InternalTrades
            **kwargs: any additional fields of SQL table

        Returns:
            list: SQL query
        """
        allowed_kwargs = ["exchange", "contract_id", "contract_name", "prod", "delivery_start", "delivery_end",
                          "internal_trade_id", "api_timestamp", "exec_time", "price", "quantity", "state",
                          "buy_delivery_area", "sell_delivery_area", "buy_order_id", "buy_clOrderId", "buy_txt",
                          "buy_aggressor_indicator", "buy_portfolio_id", "sell_order_id", "sell_clOrderId", "sell_txt",
                          "sell_aggressor_indicator", "sell_portfolio_id"]

        sql_params = self.__handle_sql_args(kwargs, allowed_kwargs)

        if delivery_area:
            for i in delivery_area:
                sql_params += f" AND (buy_delivery_area = '{i}' OR sell_delivery_area = '{i}')"

        with self.__get_session() as session:
            result = session.execute(f"SELECT * FROM internal_trades{sql_params}").fetchall()

        self.logger.info("Successfully exported internal trades")

        # Convert data back to InternalTrade objects
        if result and as_objects:
            internal_trades = [InternalTrade(exchange=i[0],
                                             contract_id=i[1],
                                             contract_name=i[2],
                                             prod=i[3],
                                             delivery_start=i[4],
                                             delivery_end=i[5],
                                             internal_trade_id=i[6],
                                             api_timestamp=i[7],
                                             exec_time=i[8],
                                             price=i[9],
                                             quantity=i[10],
                                             buy_delivery_area=i[11],
                                             sell_delivery_area=i[12],
                                             buy_order_id=i[13],
                                             buy_cl_order_id=i[14],
                                             buy_txt=i[15],
                                             buy_aggressor_indicator=i[16],
                                             buy_portfolio_id=i[17],
                                             sell_order_id=i[18],
                                             sell_cl_order_id=i[19],
                                             sell_txt=i[20],
                                             sell_aggressor_indicator=i[21],
                                             sell_portfolio_id=i[22])
                               for i in result]
            return internal_trades

        if as_dataframe:
            return pd.DataFrame(result)

        return result

    @validate_arguments
    def get_signals(self,
                    time_from: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                    time_till: datetime = Field(description="Datetime in format yyyy-mm-dd hh:mm:ss"),
                    as_dataframe: bool = True,
                    as_objects: bool = False,
                    **kwargs) -> Union[pd.DataFrame, list[Signal]]:
        """
        Exports signals from SQL database. To use different mathematical/SQL operators, pass keyworded arguments
        as strings and include the desired operator followed by a space (e.g. position_short='<> 0.00').

        Following operators can be passed:
        LIKE, <, <=, >, >=, <>

        Following parameters can be passed as optional keyworded arguments:
        id, source, received_at, revision, delivery_areas, portfolio_ids, tenant_id, position_short,
        position_long, value

        Args:
            time_from (datetime): yyyy-mm-dd hh:mm:ss
            time_till (datetime): yyyy-mm-dd hh:mm:ss
            as_dataframe (bool): True if output should be DataFrame
            as_objects (bool): True if output should be list of Signals
            **kwargs: any additional fields of SQL table

        Returns:
            list: SQL query
        """
        allowed_kwargs = ["id", "source", "received_at", "revision", "delivery_areas", "portfolio_ids", "tenant_id",
                          "position_short", "position_long", "value"]

        sql_params = self.__handle_sql_args(kwargs, allowed_kwargs)
        sql_op = "AND" if sql_params else "WHERE"

        with self.__get_session() as session:
            result = session.execute(f"SELECT * FROM signals{sql_params} "
                                     f"{sql_op} delivery_start >= '{time_from}' "
                                     f"AND delivery_end <= '{time_till}'").fetchall()

        self.logger.info("Successfully exported signals")

        # Convert data back to InternalTrade objects
        if result and as_objects:
            signals = [Signal(id=i[0],
                              source=i[1],
                              received_at=i[2],
                              revision=i[3],
                              delivery_start=i[4],
                              delivery_end=i[5],
                              portfolio_ids=i[6],
                              tenant_id=i[7],
                              position_short=i[8],
                              position_long=i[9],
                              value=i[10])
                       for i in result]

            return signals

        if as_dataframe:
            return pd.DataFrame(result)

        return result

    @validate_arguments
    def send_raw_sql(self,
                     sql_statement: str):
        """
        Function allows for raw SQL queries to be sent to the database.

        Args:
            sql_statement (str): SQL query

        Returns:

        """
        self.engine

        with self.__get_session() as session:
            try:
                result = session.execute(sql_statement).fetchall()
            except self.SQL_ERRORS as e:
                return self.logger.error(e)
        return result

    @staticmethod
    def __handle_sql_args(kwargs,
                          allowed_kwargs: list[str]) -> str:
        """
        Handles incoming arguments by adjusting them to be compatible with SQL.

        Args:
            kwargs: **kwargs of export functions
            allowed_kwargs (list[str]): list of allowed kwargs

        Returns:
            str: SQL request
        """
        if not all(arg for arg in kwargs.values()):
            raise SQLExporterError("Some of your input values are invalid or empty!")
        sql_params = ""
        operators = ["LIKE", "BETWEEN", "<", "<=", ">", ">=", "<>"]

        for keyword, argument in kwargs.items():
            op = "="
            sql_statement = "WHERE" if sql_params == "" else "AND"

            if keyword not in allowed_kwargs:
                raise SQLExporterError(f"{keyword} not in allowed keywords. Allowed keywords: {allowed_kwargs}")
            else:
                if isinstance(argument, str):
                    # Check For SQL Commands Or Mathematical Operators
                    if any(x in argument for x in operators):
                        if len(argument.split(" ")) > 2:
                            op = argument.split(" ")[0]
                            argument = argument.replace(f"{op} ", "")
                        else:
                            op, argument = argument.split(" ")
                        if op == "LIKE":
                            argument = f"%{argument}%"
                        if op == "BETWEEN":
                            if " AND " not in argument:
                                raise SQLExporterError(f"Your input for {keyword} does not conform to the guidelines. Please revise")
                            a1, a2 = argument.split(" AND ")
                            argument = f"'{a1}' AND '{a2}'"
                        try:
                            datetime.strptime(argument, DATE_YMD_TIME_HMS)
                        except:
                            pass
                elif isinstance(argument, tuple):
                    if len(argument) == 1:
                        argument = argument[0]
                    else:
                        op = "IN"
                elif isinstance(argument, list):
                    for nr, element in enumerate(argument):
                        if not nr:
                            if element == argument[-1]:
                                sql_params += f" {sql_statement} ({keyword} LIKE '%{element}%')"
                            else:
                                sql_params += f" {sql_statement} ({keyword} LIKE '%{element}%'"
                        elif element == argument[-1]:
                            sql_params += f" OR {keyword} LIKE '%{element}%')"
                        else:
                            sql_params += f" OR {keyword} LIKE '%{element}%'"
                    continue
                elif isinstance(argument, dict):
                    op = "IN"
                    temp_list = [i for x in argument.values() for i in x]
                    argument = tuple(temp_list)
                    if len(argument) == 1:
                        argument = str(argument[0])
                        op = "="
                try:
                    if keyword == "contract_id" and isinstance(argument, str):
                        raise Exception

                    if not isinstance(argument, tuple) and keyword != "contract_id":
                        argument = float(argument)
                    sql_params += f" {sql_statement} {keyword} {op} {argument}"
                except:
                    if isinstance(argument, str) and len(argument.split(" AND ")) > 1:
                        sql_params += f" {sql_statement} {keyword} {op} {argument}"
                    else:
                        sql_params += f" {sql_statement} {keyword} {op} '{argument}'"

        return sql_params

    def __convert_dataframe(self,
                            df_type: str,
                            dataframe: pandas_DataFrame) -> dict[str, pd.DataFrame]:
        """
        Function to convert dataframe to required format to be processed by backtesting data pipeline.

        Args:
            df_type (str): orders/trades/orderbooks
            dataframe (DataFrame): DataFrame containing exported Data

        Returns:
            dict{key: DataFrame}: Dictionary of DataFrames
        """
        output = {}

        contract_ids = dataframe.contract_id.unique().tolist()
        contracts = self.get_contracts(contract_id=contract_ids)

        if df_type == "trades":
            dataframe = dataframe.astype({'price': 'float', 'quantity': 'float'})

        elif df_type == "orders":
            dataframe["bids"] = [json.loads(i) if i else None for i in dataframe.bids.tolist()]
            dataframe["asks"] = [json.loads(i) if i else None for i in dataframe.asks.tolist()]

        for row_nr, row_id in enumerate(contracts.contract_id):
            key = f"{contracts.iloc[row_nr].delivery_start.strftime(DATE_YMD_TIME_HM)} - " \
                  f"{contracts.iloc[row_nr].delivery_end.strftime(TIME_HM)}"

            if key not in [*output]:
                output[key] = dataframe[dataframe["contract_id"] == row_id]
            else:
                output[key].append(dataframe[dataframe["contract_id"] == row_id])

        return output
