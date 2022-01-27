import pkg_resources
from inspy_logger import InspyLogger
from ip_reveal_headless.config.version import VERSION
from ip_reveal_headless.config.arguments import ParsedArgs, load_subcommands as args_load_subcommands
from configparser import ConfigParser
import os
from pathlib import Path

# Set up a constant containing a string representing the name of the progeram.
PROG_NAME = 'IP-Reveal'

muted = None

# Instantiate object.
_args = ParsedArgs(prog=PROG_NAME, description='Easily find and monitor your IP addresses.', ver_obj=VERSION)
args_load_subcommands(_args.parser, _args.aliases)

PARSED_ARGS = _args.parser.parse_args()
CMD_ALIASES = _args.aliases


class Config(object):
    
    def save(self):
        """
        
        Save the current configuration-state to a file.
        
        (Save location: Config.filepath)
        
        Returns:
            filepath (str): The path of the saved config file.

        """
        with open(self.filepath, 'w') as fp:
            self.parser.write(fp)
            return str(fp)
        
    def delete_conf_file(self):
        """
        
        Delete the currently saved config file from Config.filepath.
        
        Returns:
            ( False | filepath ):
                False (bool): There was a problem deleting the file specified by Config.filepath.
                filepath (str): The path where the now deleted config file once was.
                
        """
        try:
            os.remove(self.filepath)
            return str(self.filepath)
        except FileNotFoundError:
            return False
        
        
    def reset(self):
        """
        
        Deletes the config file currently found in local storage and create a new one using the
        command-line arguments (or their defaults) passed at runtime.
        
        Returns:
            filepath (str): The filepath of the config-file created after being deleted.
            
        Raises:
            FileNotFoundError: Raised when the file indicated by Config.filepath is not present.

        """
        if not self.delete_conf_file():
            raise FileNotFoundError()
        else:
            return self.create()
    
    def create(self):
        
        config = {'DEFAULTS' : {}}

        self.parser.read_dict(config)
        
        print(PARSED_ARGS.config_filepath)
        for item in dir(PARSED_ARGS) :
            if not item.startswith('_') :
                if item != 'subcommands' :
                    exec("self.parser.set('DEFAULTS', %s, str(PARSED_ARGS.%s))" % ('item', item))
        
        print(self.parser.has_option('DEFAULTS', 'config_filepath'))
        
        self.save()
        
        return self.filepath
    
    def build_pref_win_specs(self):

        try:
            import PySimpleGUI as psg
        except ModuleNotFoundError:
            return None
        
        layout = []
        
        for opt in self.parser.options('DEFAULTS'):
            if self.parser.get("DEFAULTS", opt) in ['True', 'False']:
                layout.append([psg.CBox(opt, key=f'PREF_INPUT_CBOX_{opt.upper()}')])
            elif self.parser.get("DEFAULTS", opt).isnumeric():
                layout.append([psg.Text(f'{opt.replace("_", " ").capitalize()}:'),
                              psg.InputText(self.parser['DEFAULTS'][opt],
                                            key=f'PREF_INPUT_NUM_{opt}',
                                            enable_events=True)])
            elif self.parser.get("DEFAULTS", opt).isalnum():
                layout.append(
                        (psg.Text(f'{opt.replace("_", " ").capitalize()}'),
                        psg.InputText(
                                self.parser['DEFAULTS'][opt],
                                key=f"PREF_INPUT_{opt}",
                                enable_events=True
                                )
                         ))
                
        return layout
    
    
    def __init__(self, fp):
        """
        
        Initialize IP-Reveal's Config object.
        
        Args:
            fp:
        """
        self.parser = ConfigParser()
        
        self.filepath = fp
        
        if self.filepath.exists():
            self.parser.read(self.filepath)
        else:
            if not self.filepath.parent.exists():
                os.makedirs(self.filepath.parent, exist_ok=False)
            self.create()

        self.pref_window_specs = self.build_pref_win_specs()


def load_config(fp=None):
    """
    
    Load the configuration for IP-Reveal
    
    Returns:
        None

    """
    _args_ = PARSED_ARGS
    
    if fp is None:
        conf_fp = _args_.config_filepath
    else:
        conf_fp = fp
    
    conf_fp = Path(conf_fp).expanduser().resolve()
    
    return Config(conf_fp)

import os

class Paths(object):
    
    def check_paths(self):
        if not self.cache_dir.exists():
            pass
    
    def __init__(self, config_obj, cache_dir=None, config_dir=None):
        """
        
        Initialize the 'Paths' object which contains the location of the paths for various system files.
        
        Args:
            config_obj (configparser.ConfigParser):
                A previously-instantiated configuration object to pull options from and update when
                changes are ordered
            cache_dir:
                A string containing the path of the cache for the program. (Defaults to:
            
            config_dir:
        """
        self.sub_struct = f'Inspyre-Softworks/{PROG_NAME}/'
        self.config_file_name = 'config'
        self.config_file_ext = 'ini'
        self.config_filename = self.config_file_name + '.' + self.config_file_ext
        if config_dir is None:
            config_path = Path(f'~/{self.sub_struct}config/').expanduser()
        else:
            if not config_dir.endswith('/'):
                config_dir = config_dir + '/'
            
            config_path = Path(config_dir).expanduser()
            
        if not config_path.exists():
            os.makedirs(config_path)
            
        self.config_fp = config_path
        
        self.cache_dir = Path(f'~/.cache/{self.sub_struct}/').expanduser()
        
        

CONFIG = load_config()
''' The instantiated config object '''

ARGS = PARSED_ARGS

LOG_DEVICE = InspyLogger(PROG_NAME, PARSED_ARGS.log_level).device
''' An instantiated logging device '''

ROOT_LOG = LOG_DEVICE.start()




#
# class Config(object):
#     DEFAULT_CONF_FILEPATH = Path("~/Inspyre-Softworks/IP-Reveal/config/config.ini").expanduser()
#
#     FLAGFILE_PATH = Path(__file__).resolve().joinpath('flag.ini')
#
#     ARGS = parse()
#
#     ISL = InspyLogger()
#
#     PROG_LOG_NAME = 'IPReveal'
#
#     LOG_NAME = PROG_LOG_NAME + '.config'
#
#     ISL_DEV = ISL.LogDevice(PROG_LOG_NAME, ARGS.log_level)
#
#     PROG_LOG = ISL_DEV.start()
#     PROG_LOG.debug('Root logger started')
#
#     file_path = DEFAULT_CONF_FILEPATH
#
#     if not file_path.exists():
#         flag_file_fp = FLAGFILE_PATH
#         if not flag_file_fp.exists():
#             file_path = None
#             flag_file_fp = None
#         else:
#             pass
#             # TODO:
#             #     - Write code that does someting if the flag-file exists.
#             #         - Load path to actual config from this flag-file
#     else:
#         parser = ConfigParser()
#         parser.read(DEFAULT_CONF_FILEPATH)
#
#     """
#
#     (pathlib.Path)
#
#     If this program creates and stores a  'config.ini' file in any location except for `DEFAULT_CONF_FILEPATH` we
#     will create a simple .ini file at `FLAGFILE_PATH` to let the program know where to look for it's preferences when it
#     starts each time after it being assigned.
#
#     """
