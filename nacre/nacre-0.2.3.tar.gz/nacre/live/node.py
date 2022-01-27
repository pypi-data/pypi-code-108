# -------------------------------------------------------------------------------------------------
#  Copyright (C) 2015-2021 Nautech Systems Pty Ltd. All rights reserved.
#  https://nautechsystems.io
#
#  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
#  You may not use this file except in compliance with the License.
#  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# -------------------------------------------------------------------------------------------------

import asyncio
import concurrent.futures
import platform
import socket
import sys
import time
from datetime import timedelta
from typing import Any, List, Optional

from nautilus_trader.cache.cache import Cache
from nautilus_trader.common.clock import LiveClock
from nautilus_trader.common.logging import LiveLogger
from nautilus_trader.common.logging import LogColor
from nautilus_trader.common.logging import LoggerAdapter
from nautilus_trader.common.logging import LogLevelParser
from nautilus_trader.common.uuid import UUIDFactory
from nautilus_trader.core.correctness import PyCondition
from nautilus_trader.infrastructure.cache import RedisCacheDatabase
from nautilus_trader.live.data_engine import LiveDataEngine
from nautilus_trader.live.execution_engine import LiveExecutionEngine
from nautilus_trader.live.node import TradingNode as NautilusTradingNode
from nautilus_trader.live.node_builder import TradingNodeBuilder
from nautilus_trader.live.risk_engine import LiveRiskEngine
from nautilus_trader.model.identifiers import TraderId
from nautilus_trader.msgbus.bus import MessageBus
from nautilus_trader.portfolio.portfolio import Portfolio
from nautilus_trader.serialization.msgpack.serializer import MsgPackSerializer
from nautilus_trader.trading.trader import Trader

from nacre.components.exposer import Exposer
from nacre.infrastructure.pubsub import KafkaPubSub
from nacre.live.config import TradingNodeConfig
from nacre.msgbus.msgbus_ext import MessageBusExt
from nacre.msgbus.pubsub import PubSub


class TradingNode(NautilusTradingNode):
    def __init__(self, config: Optional[TradingNodeConfig] = None):  # noqa: C901
        """
        Initialize a new instance of the TradingNode class.
        Parameters
        ----------
        config : TradingNodeConfig, optional
            The configuration for the instance.
        Raises
        ------
        TypeError
            If `config` is not of type `TradingNodeConfig`.
        """
        if config is None:
            config = TradingNodeConfig()
        PyCondition.not_none(config, "config")
        PyCondition.type(config, TradingNodeConfig, "config")

        # Configuration
        self._config = config

        # Setup loop
        self._loop = asyncio.get_event_loop()
        self._executor = concurrent.futures.ThreadPoolExecutor()
        self._loop.set_default_executor(self._executor)
        self._loop.set_debug(config.loop_debug)

        # Components
        self._clock = LiveClock(loop=self._loop)
        self._uuid_factory = UUIDFactory()
        self.created_time = self._clock.utc_now()
        self._is_running = False

        # Identifiers
        self.trader_id = TraderId(config.trader_id)
        self.machine_id = socket.gethostname()
        self.instance_id = self._uuid_factory.generate()

        # Setup logging
        self._logger = LiveLogger(
            loop=self._loop,
            clock=self._clock,
            trader_id=self.trader_id,
            machine_id=self.machine_id,
            instance_id=self.instance_id,
            level_stdout=LogLevelParser.from_str_py(config.log_level.upper()),
        )

        self._log = LoggerAdapter(
            component_name=type(self).__name__,
            logger=self._logger,
        )

        self._log_header()
        self._log.info("Building...")

        if platform.system() != "Windows":
            # Windows does not support signal handling
            # https://stackoverflow.com/questions/45987985/asyncio-loops-add-signal-handler-in-windows
            self._setup_loop()

        ########################################################################
        # Build platform
        ########################################################################
        if config.cache_database is None or config.cache_database.type == "in-memory":
            cache_db = None
        elif config.cache_database.type == "redis":
            cache_db = RedisCacheDatabase(
                trader_id=self.trader_id,
                logger=self._logger,
                serializer=MsgPackSerializer(timestamps_as_str=True),
                config=config.cache_database,
            )
        else:  # pragma: no cover (design-time error)
            raise ValueError(
                "The cache_db_type in the configuration is unrecognized, "
                "can one of {{'in-memory', 'redis'}}.",
            )

        self._cache = Cache(
            database=cache_db,
            logger=self._logger,
            config=config.cache,
        )

        ########################################################################
        # Add pubsub
        ########################################################################
        pubsub = None  # type: Optional[PubSub]
        if config.pubsub is None:
            pass
        elif config.pubsub.type == "kafka":
            pubsub = KafkaPubSub(
                loop=self._loop,
                trader_id=self.trader_id,
                logger=self._logger,
                config=config.pubsub,
            )
        else:  # pragma: no cover (design-time error)
            raise ValueError(
                "The pubsub_type in the configuration is unrecognized, "
                "can one of {{'kafka', '...'}}.",
            )

        if pubsub is None:
            self._msgbus = MessageBus(
                trader_id=self.trader_id,
                clock=self._clock,
                logger=self._logger,
            )
        else:
            self._msgbus = MessageBusExt(
                trader_id=self.trader_id,
                clock=self._clock,
                logger=self._logger,
                pubsub=pubsub,
            )

        self._pubsub = pubsub

        ########################################################################
        # Add exposer
        ########################################################################
        exposer = None
        if config.exposer:
            exposer = Exposer(
                loop=self._loop,
                msgbus=self._msgbus,
                cache=self._cache,
                clock=self._clock,
                logger=self._logger,
                config=config.exposer,
            )

        self._exposer = exposer

        ########################################################################
        # Added
        ########################################################################

        self.portfolio = Portfolio(
            msgbus=self._msgbus,
            cache=self._cache,
            clock=self._clock,
            logger=self._logger,
        )

        self._data_engine = LiveDataEngine(
            loop=self._loop,
            msgbus=self._msgbus,
            cache=self._cache,
            clock=self._clock,
            logger=self._logger,
            config=config.data_engine,
        )

        self._exec_engine = LiveExecutionEngine(
            loop=self._loop,
            msgbus=self._msgbus,
            cache=self._cache,
            clock=self._clock,
            logger=self._logger,
            config=config.exec_engine,
        )
        self._exec_engine.load_cache()

        self._risk_engine = LiveRiskEngine(
            loop=self._loop,
            portfolio=self.portfolio,
            msgbus=self._msgbus,
            cache=self._cache,
            clock=self._clock,
            logger=self._logger,
            config=config.risk_engine,
        )

        self.trader = Trader(
            trader_id=self.trader_id,
            msgbus=self._msgbus,
            cache=self._cache,
            portfolio=self.portfolio,
            data_engine=self._data_engine,
            risk_engine=self._risk_engine,
            exec_engine=self._exec_engine,
            clock=self._clock,
            logger=self._logger,
        )

        if config.load_strategy_state:
            self.trader.load()

        # Setup persistence (requires trader)
        self.persistence_writers: List[Any] = []
        if config.persistence:
            self._setup_persistence(config=config.persistence)

        self._builder = TradingNodeBuilder(
            loop=self._loop,
            data_engine=self._data_engine,
            exec_engine=self._exec_engine,
            msgbus=self._msgbus,
            cache=self._cache,
            clock=self._clock,
            logger=self._logger,
            log=self._log,
        )

        self._log.info("INITIALIZED.")
        self.time_to_initialize = self._clock.delta(self.created_time)
        self._log.info(f"Initialized in {int(self.time_to_initialize.total_seconds() * 1000)}ms.")

        self._is_built = False

    def dispose(self) -> None:
        """
        Dispose of the trading node.

        Gracefully shuts down the executor and event loop.

        """
        try:
            timeout = self._clock.utc_now() + timedelta(seconds=self._config.timeout_disconnection)
            while self._is_running:
                time.sleep(0.1)
                if self._clock.utc_now() >= timeout:
                    warnings = (
                        f"Timed out ({self._config.timeout_disconnection}s) waiting for node to stop."
                        f"\nStatus"
                        f"\n------"
                        f"\nDataEngine.check_disconnected() == {self._data_engine.check_disconnected()}"
                        f"\nExecEngine.check_disconnected() == {self._exec_engine.check_disconnected()}"
                    )
                    if self._pubsub:
                        warnings += (
                            f"\nPubsub.check_disconnected() == {self._pubsub.check_disconnected()}"
                        )
                    self._log.warning(warnings)
                    break

            self._log.info("DISPOSING...")

            self._log.debug(f"{self._data_engine.get_run_queue_task()}")
            self._log.debug(f"{self._exec_engine.get_run_queue_task()}")
            self._log.debug(f"{self._risk_engine.get_run_queue_task()}")
            if self._pubsub is not None:
                self._log.debug(f"{self._pubsub.get_run_queue_task()}")

            self.trader.dispose()
            self._data_engine.dispose()
            self._exec_engine.dispose()
            self._risk_engine.dispose()
            if self._pubsub:
                self._pubsub.dispose()

            self._log.info("Shutting down executor...")
            if sys.version_info >= (3, 9):
                # cancel_futures added in Python 3.9
                self._executor.shutdown(wait=True, cancel_futures=True)
            else:
                self._executor.shutdown(wait=True)

            self._log.info("Stopping event loop...")
            self._cancel_all_tasks()
            self._loop.stop()
        except RuntimeError as ex:
            self._log.exception(ex)
        finally:
            if self._loop.is_running():
                self._log.warning("Cannot close a running event loop.")
            else:
                self._log.info("Closing event loop...")
                self._loop.close()

            # Check and log if event loop is running
            if self._loop.is_running():
                self._log.warning(f"loop.is_running={self._loop.is_running()}")
            else:
                self._log.info(f"loop.is_running={self._loop.is_running()}")

            # Check and log if event loop is closed
            if not self._loop.is_closed():
                self._log.warning(f"loop.is_closed={self._loop.is_closed()}")
            else:
                self._log.info(f"loop.is_closed={self._loop.is_closed()}")

            self._log.info("DISPOSED.")

    async def _run(self) -> None:  # noqa: C901
        try:
            self._log.info("STARTING...")
            self._is_running = True

            # Start system
            self._logger.start()
            if self._pubsub:
                self._pubsub.start()
            if self._exposer:
                self._exposer.start()
            self._data_engine.start()
            self._exec_engine.start()
            self._risk_engine.start()

            # Connect all clients
            self._data_engine.connect()
            self._exec_engine.connect()

            # Await engine connection and initialization
            self._log.info(
                f"Waiting for engines to connect and initialize "
                f"({self._config.timeout_connection}s timeout)...",
                color=LogColor.BLUE,
            )
            if not await self._await_engines_connected():
                warnings = (
                    f"Timed out ({self._config.timeout_connection}s) waiting for engines to connect and initialize."
                    f"\nStatus"
                    f"\n------"
                    f"\nDataEngine.check_connected() == {self._data_engine.check_connected()}"
                    f"\nExecEngine.check_connected() == {self._exec_engine.check_connected()}"
                )
                if self._pubsub:
                    warnings += f"\nPubsub.check_connected() == {self._pubsub.check_connected()}"
                self._log.warning(warnings)
                return
            self._log.info("Engines connected.", color=LogColor.GREEN)

            # if self._exposer is not None:
            #     self._exposer.start()

            # Await execution state reconciliation
            self._log.info(
                f"Waiting for execution state to reconcile "
                f"({self._config.timeout_reconciliation}s timeout)...",
                color=LogColor.BLUE,
            )
            if not await self._exec_engine.reconcile_state(
                timeout_secs=self._config.timeout_reconciliation,
            ):
                self._log.warning(
                    f"Timed out ({self._config.timeout_reconciliation}s) waiting for "
                    f"execution state to reconcile."
                )
                return
            self._log.info("State reconciled.", color=LogColor.GREEN)

            # Initialize portfolio
            self.portfolio.initialize_orders()
            self.portfolio.initialize_positions()

            # Await portfolio initialization
            self._log.info(
                "Waiting for portfolio to initialize "
                f"({self._config.timeout_portfolio}s timeout)...",
                color=LogColor.BLUE,
            )
            if not await self._await_portfolio_initialized():
                self._log.warning(
                    f"Timed out ({self._config.timeout_portfolio}s) waiting for portfolio to initialize."
                    f"\nStatus"
                    f"\n------"
                    f"\nPortfolio.initialized == {self.portfolio.initialized}"
                )
                return
            self._log.info("Portfolio initialized.", color=LogColor.GREEN)

            # Start trader and strategies
            self.trader.start()

            if self._loop.is_running():
                self._log.info("RUNNING.")
            else:
                self._log.warning("Event loop is not running.")

            # Continue to run while engines are running...
            await self._data_engine.get_run_queue_task()
            await self._exec_engine.get_run_queue_task()
            await self._risk_engine.get_run_queue_task()
            if self._pubsub:
                await self._pubsub.get_run_queue_task()
        except asyncio.CancelledError as ex:
            self._log.error(str(ex))

    async def _stop(self) -> None:  # noqa: C901
        self._is_stopping = True
        self._log.info("STOPPING...")

        if self.trader.is_running:
            self.trader.stop()
            self._log.info(
                f"Awaiting residual state ({self._config.check_residuals_delay}s delay)...",
                color=LogColor.BLUE,
            )
            await asyncio.sleep(self._config.check_residuals_delay)
            self.trader.check_residuals()

        if self._config.save_strategy_state:
            self.trader.save()

        # Disconnect all clients
        self._data_engine.disconnect()
        self._exec_engine.disconnect()

        if self._pubsub:
            self._pubsub.stop()
        if self._exposer:
            self._exposer.stop()

        if self._data_engine.is_running:
            self._data_engine.stop()
        if self._exec_engine.is_running:
            self._exec_engine.stop()
        if self._risk_engine.is_running:
            self._risk_engine.stop()

        self._log.info(
            f"Waiting for engines to disconnect "
            f"({self._config.timeout_disconnection}s timeout)...",
            color=LogColor.BLUE,
        )
        if not await self._await_engines_disconnected():
            errors = (
                f"Timed out ({self._config.timeout_disconnection}s) waiting for engines to disconnect."
                f"\nStatus"
                f"\n------"
                f"\nDataEngine.check_disconnected() == {self._data_engine.check_disconnected()}"
                f"\nExecEngine.check_disconnected() == {self._exec_engine.check_disconnected()}"
            )
            if self._pubsub:
                errors += f"Pubsub.check_disconnected() == {self._pubsub.check_disconnected()}"
            self._log.error(errors)

        # Clean up remaining timers
        timer_names = self._clock.timer_names()
        self._clock.cancel_timers()

        for name in timer_names:
            self._log.info(f"Cancelled Timer(name={name}).")

        # Clean up persistence
        for writer in self.persistence_writers:
            writer.close()

        self._log.info("STOPPED.")
        self._logger.stop()
        self._is_running = False

    async def _await_engines_connected(self) -> bool:
        # - The data engine clients will be set connected when all
        # instruments are received and updated with the data engine.
        # - The execution engine clients will be set connected when all
        # accounts are updated and the current order and position status is
        # reconciled.
        # Thus any delay here will be due to blocking network I/O.
        seconds = self._config.timeout_connection
        timeout: timedelta = self._clock.utc_now() + timedelta(seconds=seconds)
        while True:
            await asyncio.sleep(0)
            if self._clock.utc_now() >= timeout:
                return False
            if not self._data_engine.check_connected():
                continue
            if not self._exec_engine.check_connected():
                continue
            if self._pubsub and not self._pubsub.check_connected():
                continue
            break

        return True  # Engines connected

    async def _await_engines_disconnected(self) -> bool:
        seconds = self._config.timeout_disconnection
        timeout: timedelta = self._clock.utc_now() + timedelta(seconds=seconds)
        while True:
            await asyncio.sleep(0)
            if self._clock.utc_now() >= timeout:
                return False
            if not self._data_engine.check_disconnected():
                continue
            if not self._exec_engine.check_disconnected():
                continue
            if self._pubsub and not self._pubsub.check_disconnected():
                continue
            break

        return True  # Engines disconnected
