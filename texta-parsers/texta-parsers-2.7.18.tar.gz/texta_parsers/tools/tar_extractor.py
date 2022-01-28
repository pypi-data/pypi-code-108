import subprocess
import os
import logging

def extract_tar_file(tar_filepath, tmp_dir):
    """ Extracts files from .tar file located in tar_filepath to tmp_dir.
    """
    logging.info('Extracting {}...'.format(tar_filepath))
    return subprocess.run(["tar", "-xf", tar_filepath, "-C", tmp_dir])

def check_tar_exists():
    try:
        p = subprocess.run(["tar"], stdout=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False
