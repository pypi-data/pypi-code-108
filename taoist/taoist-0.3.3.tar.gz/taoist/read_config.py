"""read_config.py"""
import sys
import os
from pathlib import Path
from configparser import ConfigParser

def read_config() -> ConfigParser:
    """
    Read the taoist user config file
    """
    
    # Get user home directory path
    home_dir = Path.home()

    # Full config file path
    config_file = os.path.join(home_dir, ".taoist/config.ini")

    # Initialize config data structure
    config = ConfigParser()
 
    # Read config.ini
    if os.path.isfile(config_file):
        config.read(config_file)
    else:
        print("Error: Cannot read API token, please run init function")
        sys.exit(1)
    
    return config
