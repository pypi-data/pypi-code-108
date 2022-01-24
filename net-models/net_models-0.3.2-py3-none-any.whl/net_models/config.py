from dataclasses import dataclass
import logging
from net_models.utils.get_logger import get_logger, VERBOSITY_MAP


@dataclass()
class NetModelsConfig:

    FIELDS_LOGGING_LEVEL: int = 4
    INTERFACE_UTILS_LOG_LEVEL: int = 4

CONFIG = NetModelsConfig()

LOGGER_SPEC = {
    "interface_utils": {
        "name": "NetModels-InterfaceUtils",
        "verbosity": CONFIG.INTERFACE_UTILS_LOG_LEVEL,
        "logger": None
    },
    "fields": {
        "name": "NetModels-Fields",
        "verbosity": CONFIG.FIELDS_LOGGING_LEVEL,
        "logger": None
    }
}


def update_loggers():
    global LOGGER_SPEC
    for name, spec in LOGGER_SPEC.items():
        spec["logger"] = get_logger(name=spec["name"], verbosity=spec["verbosity"])
        for handler in spec["logger"].handlers:
            handler.setLevel(VERBOSITY_MAP[spec["verbosity"]])

update_loggers()

LOGGER_INTERFACE_UTILS = LOGGER_SPEC["interface_utils"]["logger"]
LOGGER_FIELDS  = LOGGER_SPEC["fields"]["logger"]



