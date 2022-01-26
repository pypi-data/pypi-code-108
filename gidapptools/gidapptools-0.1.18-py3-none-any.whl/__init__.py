"""
WiP
"""

from gidapptools.meta_data.interface import setup_meta_data, get_meta_config, get_meta_info, get_meta_item, get_meta_paths
from gidapptools.gid_logger.logger import setup_main_logger, get_logger, setup_main_logger_with_file_logging, get_main_logger


__version__ = "0.1.18"


from pathlib import Path
THIS_FILE_DIR = Path(__file__).resolve().parent
