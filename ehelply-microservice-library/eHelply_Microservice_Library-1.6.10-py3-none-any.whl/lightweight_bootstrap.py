from pathlib import Path
import os, glob
from typing import List
from ehelply_bootstrapper.utils.environment import Environment
from ehelply_bootstrapper.drivers.aws import AWS
import json
# Import the things required to setup the config
from ehelply_bootstrapper.drivers.config import Config
from ehelply_bootstrapper.utils.state import State
from ehelply_logger.Logger import Logger


def lightweight_bootstrap(root_path: Path):
    """
    Prepares vitals

    Useful for CLIs

    Args:
        root_path (Path): Path to the root directory of the microservice

    Returns:

    """
    try:
        Environment(str(root_path.joinpath('env.json')))
    except:
        pass

    configs: List[str] = []

    service_configs_path: Path = root_path.joinpath("config")

    for config in glob.glob(str(service_configs_path.joinpath(Environment.stage()).joinpath('service')) + "/*.yaml"):
        config: Path = Path(config)
        configs.append(str(config.relative_to(service_configs_path.joinpath(Environment.stage()))))

    if State.config is None:
        bootstrap_config_path = service_configs_path.joinpath(Environment.stage())
        Config(config_path=str(bootstrap_config_path), configs=configs).init()

    if State.logger is None:
        State.logger = Logger()

    State.aws = AWS(service_gatekeeper_key=json.loads(os.environ["EHELPLY_GATEKEEPER_KEY"])['secret_key']).init()

