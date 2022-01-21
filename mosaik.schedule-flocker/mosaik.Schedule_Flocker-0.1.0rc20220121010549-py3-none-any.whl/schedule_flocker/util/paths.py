from os.path import abspath
from pathlib import Path

ROOT_PATH = Path(abspath(__file__)).parent.parent.parent.parent
DATA_PATH: Path = ROOT_PATH / 'data'
RESULTS_PATH: Path = DATA_PATH / 'results'

LOG_FILE_PATH = str(ROOT_PATH / 'logs' / 'app.log')
