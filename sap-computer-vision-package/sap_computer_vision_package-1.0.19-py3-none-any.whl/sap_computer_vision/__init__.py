"""Detectron2 extension. This package extends detectron2 to support image classification and
feature extraction/image retrieval models."""
import pathlib

SAP_COMPUTER_VISION_DIR = pathlib.Path(__file__).parent
DISCLAIMER = SAP_COMPUTER_VISION_DIR / 'DISCLAIMER'
LICENSE = SAP_COMPUTER_VISION_DIR / 'LICENSE'
VERSION_TXT = SAP_COMPUTER_VISION_DIR / 'VERSION'

from .config import get_cfg, get_config_file, setup_loggers
from .engine import *
from .modelling import *

__version__ = VERSION_TXT.open().read().strip() if VERSION_TXT.exists() else None
__all__ = ["config", "get_cfg", "get_config_file", "setup_loggers", "DISCLAIMER", "LICENSE", "SAP_COMPUTER_VISION_DIR"]
