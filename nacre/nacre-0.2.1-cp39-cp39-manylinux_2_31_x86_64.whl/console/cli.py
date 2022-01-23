import importlib
import sys
from typing import Dict, Optional

import fire
import yaml  # type: ignore
from nautilus_trader.trading.config import ImportableStrategyConfig
from nautilus_trader.trading.config import StrategyFactory
from nautilus_trader.trading.strategy import TradingStrategy

from nacre.live.node import TradingNode
from nacre.live.node import TradingNodeConfig


def run():
    fire.Fire(run_live_node)


def run_live_node(config: str, log: Optional[str] = None):
    with open(config, "r") as stream:
        node_cfg = yaml.safe_load(stream)

    if "strategies" not in node_cfg:
        return "strategy not specified"

    # redirect log
    if log is not None:
        sys.stdout = open(log, "w")
        sys.stderr = sys.stdout

    # insert path
    if "paths" in node_cfg:
        for path in node_cfg.pop("paths"):
            sys.path.insert(0, path)

    # initialize strategies
    strategies = [build_strategy(strategy) for strategy in node_cfg.pop("strategies")]

    factories_cfg = node_cfg.pop("factories")
    node = TradingNode(config=TradingNodeConfig(**node_cfg))
    node.trader.add_strategies(strategies)

    # apply factories
    add_client_factories(node, factories_cfg)

    node.build()

    try:
        node.start()
    finally:
        node.dispose()


def import_cls(path: str):
    assert path
    assert ":" in path

    module, cls = path.rsplit(":")
    mod = importlib.import_module(module)
    return getattr(mod, cls)


def add_client_factories(node: TradingNode, config: Dict):
    if "data_clients" in config:
        for venue, path in config["data_clients"].items():
            node.add_data_client_factory(venue, import_cls(path))
    if "exec_clients" in config:
        for venue, path in config["exec_clients"].items():
            node.add_exec_client_factory(venue, import_cls(path))


def build_strategy(config: Dict) -> TradingStrategy:
    stra_config_cls = import_cls(config.pop("config_path"))
    stra_config = stra_config_cls(**config.pop("config"))

    isc = ImportableStrategyConfig(path=config["path"], config=stra_config)
    return StrategyFactory.create(isc)
