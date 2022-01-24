# constants.py
import logging
from pathlib import Path

log = logging.getLogger(__name__)

DATA_DIR = Path('~').expanduser().resolve().absolute() / 'nessvec-data'
log.info(f'DATA_DIR: {DATA_DIR}')


if not DATA_DIR.is_dir():
    DATA_DIR.mkdir()
