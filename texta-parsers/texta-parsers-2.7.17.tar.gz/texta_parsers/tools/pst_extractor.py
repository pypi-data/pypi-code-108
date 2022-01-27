import subprocess
import os
import logging

def _extract_pst_file(pst_filepath, tmp_dir):
    """ Extracts emails and attachments from .pst file located in pst_filepath
        to separate files located in outdir.
    """
    logging.info('Converting {}...'.format(pst_filepath))
    return subprocess.run(["readpst", pst_filepath, "-o", tmp_dir])

def _get_mbox_files(tmp_dir):
    """ Returns a list of full paths to mbox files.
    """
    result = []
    for dirpath, _, filenames in os.walk(tmp_dir):
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext == ".mbox":
                result.append(os.path.join(dirpath, filename))
    return result

def extract_pst_file(pst_file, tmp_dir):
    """ Extracts emails and attachments from given .pst file
        to separate files (and subdirectories) located in outdir.

        Returns full path from base directory to extracted mbox files.
    """
    _extract_pst_file(pst_file, tmp_dir)

    return _get_mbox_files(tmp_dir)


def check_readpst_exists():
    try:
        p = subprocess.run(["readpst"], stdout=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False
