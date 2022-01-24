from pkg_resources import get_distribution
__version__ = get_distribution('rialtic-klee-py')

import datetime as _dt
from os.path import join, abspath
import shutil, os, logging, sys, dotenv

from logging import Logger as _Logger
log = _Logger('klee-logs', level=0)

class Structure:
    reference: 'Structure' = None

    def __init__(self, root_dir: str = '.', claim_dir: str = 'test_claims', output_dir: str = 'test_cases'):
        self.root_dir, self.json_enabled = abspath(root_dir), False
        self.claim_dir = join(self.root_dir, claim_dir)
        self.output_dir = join(self.root_dir, output_dir)
        self.dotenv = join(self.root_dir, '.env')

        self.internal = join(self.output_dir, '.klee-internal')
        self.insights = join(self.output_dir, 'INSIGHTS.md')
        self.reports = join(self.output_dir, 'reports')
        self.logs = join(self.output_dir, 'logs')

        self.history = join(self.internal, '_history.json')
        self.binary = join(self.internal, '_cases.klee')

        self.timestamp = int(_dt.datetime.utcnow().timestamp())
        self.search = (self.claim_dir, self.output_dir)

    @property
    def json_cases(self):
        if self.json_enabled:
            return join(self.output_dir, 'json_cases')

    @property
    def json_history(self):
        if self.json_enabled:
            return join(self.output_dir, 'history')

    @staticmethod
    def iter_search():
        if Structure.reference:
            return Structure.reference.search
        return 'test_cases', 'test_claims'

    def register_instance(self):
        Structure.reference = self
        print(f'klee version {__version__.version} initializing...')
        self.init_directories()

        dotenv.load_dotenv(self.dotenv)

        logfile = join(self.logs, f"klee-{self.timestamp}.log")
        Structure.enable_logging(logfile)

    def init_directories(self):
        root = os.path.dirname(__file__)

        os.makedirs(self.internal, exist_ok=True)
        os.makedirs(self.reports, exist_ok=True)
        os.makedirs(self.logs, exist_ok=True)

        def copy_file(full_name, hard_copy=False):
            src = join(root, 'resource', full_name)
            dest = join(self.output_dir, full_name)

            if not os.path.exists(dest) or hard_copy:
                parent = os.path.dirname(dest)
                os.makedirs(parent, exist_ok=True)
                shutil.copy2(src, dest)

        copy_file('.gitignore', hard_copy=True)

    @staticmethod
    def enable_logging(location = ''):
        log_file = logging.FileHandler(filename = location, mode="w")
        log_file.setFormatter(logging.Formatter("%(asctime)s: [%(levelname)s] %(message)s"))
        log.addHandler(log_file)

        std_err = logging.StreamHandler(stream=sys.stderr)
        std_err.setLevel(os.getenv('KLEE_LOG_LEVEL', 'WARNING'))
        std_err.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        log.addHandler(std_err)

        log.info("klee version: %s", __version__)
        log.info("os.cwd: %s", os.getcwd())

# Level	Numeric value
# CRITICAL	50
# ERROR	40
# WARNING	30
# INFO	20
# DEBUG	10
# NOTSET	0
