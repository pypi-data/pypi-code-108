import importlib
import os
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


def run_live_node(config: str, log_path: Optional[str] = None, credential_path: str = "~/.nsrc"):
    with open(config, "r") as stream:
        node_cfg = yaml.safe_load(stream)

    if "strategies" not in node_cfg:
        return "strategy not specified"

    # redirect log
    if log_path is None and "log_path" in node_cfg:
        log_path = node_cfg.pop("log_path")
    if log_path is not None:
        sys.stdout = open(log_path, "w")
        sys.stderr = sys.stdout

    # insert path
    paths = node_cfg.pop("paths", None)
    if paths and isinstance(paths, list):
        for path in paths:
            sys.path.insert(0, path)

    # load api key/sec from default credential path
    node_cfg["exec_clients"] = _load_credentials(node_cfg, credential_path)

    # initialize strategies
    strategies = [_build_strategy(strategy) for strategy in node_cfg.pop("strategies")]

    factories_cfg = node_cfg.pop("factories")
    node = TradingNode(config=TradingNodeConfig(**node_cfg))
    node.trader.add_strategies(strategies)

    # apply factories
    _add_client_factories(node, factories_cfg)

    node.build()

    try:
        node.start()
    finally:
        node.dispose()


def _import_cls(path: str):
    assert path
    assert ":" in path

    module, cls = path.rsplit(":")
    mod = importlib.import_module(module)
    return getattr(mod, cls)


def _add_client_factories(node: TradingNode, config: Dict):
    if "data_clients" in config:
        for venue, path in config["data_clients"].items():
            node.add_data_client_factory(venue, _import_cls(path))
    if "exec_clients" in config:
        for venue, path in config["exec_clients"].items():
            node.add_exec_client_factory(venue, _import_cls(path))


def _build_strategy(config: Dict) -> TradingStrategy:
    stra_config_cls = _import_cls(config.pop("config_path"))
    stra_config = stra_config_cls(**config.pop("config"))

    isc = ImportableStrategyConfig(path=config["path"], config=stra_config)
    return StrategyFactory.create(isc)


def _load_credentials(node_cfg: Dict, credential_path: str) -> Dict:
    # Load sec from "~/.nsrc" or somewhere else
    # Update exec_clients dict
    exec_clients = node_cfg.pop("exec_clients", {})
    exec_client_ids = node_cfg.pop("exec_client_ids", None)
    if not exec_client_ids:
        return exec_clients

    with open(os.path.expanduser(credential_path)) as yamlfile:
        account_credentials = yaml.safe_load(yamlfile)["account_credentials"]
        for id, settings in exec_client_ids.items():
            main_venue, _, account_id = id.partition("-")
            creds = account_credentials.get(id, {})
            for account_type in ("SPOT", "FUTURE"):
                client_id = f"{main_venue}_{account_type}-{account_id}"
                override_settings = {"defaultType": account_type.lower(), **creds, **settings}
                if client_id in exec_clients:
                    for key, val in override_settings.items():
                        if key not in exec_clients[client_id]:
                            exec_clients[client_id][key] = val
                else:
                    exec_clients[client_id] = override_settings

    return exec_clients
