import os
import pathlib

HOME = pathlib.Path.home()
CONFIGS_DIR = pathlib.Path(os.getenv('CONFIGS_DIR', HOME.joinpath('configs')))
TOKEN_PATH = CONFIGS_DIR.joinpath('stat_explore.txt')

# Arguments for logging.basicConfig
LOGGING = dict(
    # Log string format
    # https://docs.python.org/3.8/library/logging.html#logrecord-attributes
    format='%(asctime)s %(filename)s:%(lineno)s %(levelname)s %(message)s',
)
