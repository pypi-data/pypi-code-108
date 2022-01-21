"""run_init.py"""
import os
import argparse
from pathlib import Path
from configparser import ConfigParser

def run_init(args: argparse.ArgumentParser) -> None:
    """
    Initialize Todoist account with API token
    """

    # Get user home directory path
    home_dir = Path.home()

    # Path to taoist config directory
    taoist_dir = os.path.join(home_dir, ".taoist")

    # Full config file path
    config_file = os.path.join(taoist_dir, "config.ini")
    
     # Initialize config data structure
    config = ConfigParser()

    # Read existing config file or make directory
    if os.path.isdir(taoist_dir):
        if os.path.isfile(config_file):
            config.read(config_file)
    else:
        os.mkdir(taoist_dir)
    
    # Get token if not specified on command line
    if args.token:
        config['Default'] = {'token': args.token}
    else:
        token = input('Enter Your Todoist API Token: ')
        config['Default'] = {'token': token}
    
    # Write new config file
    with open(config_file, 'w') as config_out:
        config.write(config_out)
    
    # Make config file private to user
    os.chmod(config_file, 0o600)
