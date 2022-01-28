import os
import sys
from appdirs import user_config_dir
from yaml import full_load, dump
try:
    from UserDict import DictMixin
except ImportError:
    from collections.abc import MutableMapping as DictMixin
import pkg_resources

from norns.exceptions import ConfigError

class Config(DictMixin):
    """ Configuration class. 

    State will be shared across config objects. 
    """
    # Store shared state, Borg pattern
    __shared_state = {}
    
    def __init__(self, name=None, config_file=None, default=None):
        """ 
        Create a Config object and read a config file.

        Either name or config_file is required.
        
        Parameters
        ----------
        name : str, optional
            name for configuration

        config_file : str, optional
            name of specific configration file
        
        default : str, optional
            default config, relative to package directory
        """

        self.__dict__ = self.__shared_state
        
        self.config_file = None

        # Lookup the config file according to XDG hierarchy
        if name:
            self.config_file = os.path.join(
                    user_config_dir(name), "{}.yaml".format(name)
                )
        elif config_file: # Read specific file
            self.config_file = config_file
        
        if default and (not self.config_file or 
                not os.path.exists(self.config_file)):
            self.config_file = pkg_resources.resource_filename(name, default)
        
        if not self.config_file or not os.path.exists(self.config_file):
            raise ConfigError("please provide name or config_file")
        
        self.config = {}
        self.load(self.config_file)

    def load(self, path):
        """ 
        Load yaml-formatted config file.

        Parameters
        ----------
        path : str
            path to config file
        """
        with open(path) as f:
            self.config = full_load(f)
            if self.config is None:
                sys.stderr.write("Warning: config file is empty!\n")
                self.config = {}

    def save(self):
        """ 
        Save current state of config dictionary.
        """
        with open(self.config_file, "w") as f:
            f.write(dump(self.config, default_flow_style=False))

    def __getitem__(self, key):
        return self.config.__getitem__(key)
       
    def __delitem__(self, key):
        self.config.__delitem__(key)
    
    def __setitem__(self, key, value):
        return self.config.__setitem__(key, value)

    def __len__(self):
        return self.config.__len__()

    def __iter__(self):
        return self.config.__iter__()
    
    def __str__(self):
        return '{' + ', '.join(': '.join([str(key), str(value)]) for key, value in self.items()) + '}'

    def keys(self):
        return self.config.keys()
