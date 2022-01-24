import json
import os
import pathlib

from discolib.discogen.config import Config
from discolib.discogen.clang import ClangGenerator

LANGUAGE_C = 'c'
CODEGEN_PATH = pathlib.Path(__file__).parent.parent / 'codegen'

class ConfigParser:
    
    filename = 'disco.json'
    _config_path = pathlib.Path(os.getcwd()) / filename

    def __init__(self):
        if not os.path.exists(self._config_path):
            raise RuntimeError(f'{self.filename} config file missing from cwd.')
        with open(self._config_path) as cfg_file:
            self._config_dict = json.load(cfg_file)
        self.config = Config(self._config_dict)

def _gen_c():
    parser = ConfigParser()
    generator = ClangGenerator(parser.config)
    generator.write_attributes()

LANGUAGE_MAP = {
    LANGUAGE_C : _gen_c
}
