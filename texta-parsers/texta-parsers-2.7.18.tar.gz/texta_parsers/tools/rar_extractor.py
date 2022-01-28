import subprocess
import os
import logging

def extract_rar_file(rar_filepath, tmp_dir):
    """ Extracts files from .rar file located in rar_filepath to tmp_dir.
    """
    logging.info('Extracting {}...'.format(rar_filepath))
    return subprocess.run(["rar", "x", rar_filepath, tmp_dir])

def check_rar_exists():
    try:
        p = subprocess.run(["rar"], stdout=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False
