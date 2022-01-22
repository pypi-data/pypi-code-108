import re
import shutil
import sys
from os import mkdir
from os.path import isfile, realpath, exists, dirname
from pathlib import Path
from shutil import copyfile

import munch
import oyaml as yaml
from cloudmesh.common.FlatDict import FlatDict
from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.util import backup_name
from cloudmesh.common.util import path_expand
from cloudmesh.common.variables import Variables
from cloudmesh.configuration.Config import Config

"""
This clas is similar to Config, but does not contain a shared state for the location where to find it.
It also does not mask secrets.
cat was removed
"""


# see also https://github.com/cloudmesh/client/blob/main/cloudmesh_client/cloud/register.py


class Configuration(object):

    def __init__(self, path='~/.cloudmesh/cloudmesh.yaml'):
        """
        Initialize the Config class.

        :param config_path: A local file path to cloudmesh yaml config
            with a root element `cloudmesh`.
            Default: `~/.cloudmesh/cloudmesh.yaml`
        """

        self.path = path

        self.load(path=self.path)

    def set_debug_defaults(self):
        for name in ["trace", "debug"]:
            if name not in self.variable_database:
                self.variable_database[name] = str(False)

    def default(self):
        return dotdict(self.data["cloudmesh"]["default"])

    def load(self, path=None):
        """
        loads a configuration file
        :param path:
        :type path:
        :return:
        :rtype:
        """

        # VERBOSE("Load config")
        self.filename = Path(path_expand(path))

        self.config_folder = dirname(self.path)

        self.create(path=path)

        with open(self.path, "r") as stream:
            content = stream.read()
            # content = path_expand(content)
            content = self.spec_replace(content)
            self.data = yaml.load(content, Loader=yaml.SafeLoader)

        # print (self.data["cloudmesh"].keys())

        # self.data is loaded as nested OrderedDict, can not use set or get
        # methods directly

        if self.data is None:
            raise EnvironmentError(
                "Failed to load configuration file cloudmesh.yaml, "
                "please check the path and file locally")

        #
        # populate default variables
        #

        self.variable_database = Variables(filename="~/.cloudmesh/variable.dat")

        self.set_debug_defaults()

        default = self.default()

        for name in self.default():
            if name not in self.variable_database:
                self.variable_database[name] = default[name]

        if "cloud" in default:
            self.cloud = default["cloud"]
        else:
            self.cloud = None

    def create(self, path=None):
        """
        creates the cloudmesh.yaml file in the specified location. The
        default is

            ~/.cloudmesh/cloudmesh.yaml

        If the file does not exist, it is initialized with a default. You still
        need to edit the file.

        :param path:  The yaml file to create
        :type path: string
        """
        self.path = Path(path_expand(path))

        self.config_folder = dirname(self.path)

        if not exists(self.config_folder):
            mkdir(self.config_folder)

        if not isfile(self.path):
            source = Path(dirname(realpath(__file__)) + "/etc/cloudmesh.yaml")

            copyfile(source.resolve(), self.path)

            # read defaults
            self.__init__()

            defaults = self["cloudmesh.default"]

            # pprint(defaults)

            d = Variables()
            if defaults is not None:
                print("# Set default from yaml file:")

            for key in defaults:
                value = defaults[key]
                print("set {key}={value}".format(**locals()))
                d[key] = defaults[key]

    def save(self, path=None, backup=True):
        """
        #
        # not tested
        #
        saves th dic into the file. It also creates a backup if set to true The
        backup filename  appends a .bak.NO where number is a number that is not
        yet used in the backup directory.

        :param path:
        :type path:
        :return:
        :rtype:
        """
        path = path_expand(path or self.location.config())
        if backup:
            destination = backup_name(path)
            shutil.copyfile(path, destination)
        yaml_file = self.data.copy()
        with open(self.path, "w") as stream:
            yaml.safe_dump(yaml_file, stream, default_flow_style=False)

    def spec_replace(self, spec):

        # TODO: BUG: possible bug redundant char \{ in escape
        #            may be relevant for python 2 may behave differnet in
        #            differnt python versions, has to be checked. a unit test
        #            should be created to just check the \{ issue
        #
        variables = re.findall(r"\{\w.+\}", spec)

        for i in range(0, len(variables)):
            data = yaml.load(spec, Loader=yaml.SafeLoader)

            m = munch.DefaultMunch.fromDict(data)

            for variable in variables:
                text = variable
                variable = variable[1:-1]
                try:
                    value = eval("m.{variable}".format(**locals()))
                    if "{" not in value:
                        spec = spec.replace(text, value)
                except:
                    value = variable
        return spec

    def dict(self):
        return self.data

    def __str__(self):
        return self.cat_dict(self.data)

    def get(self, key, default=None):
        """
        A helper function for reading values from the config without
        a chain of `get()` calls.

        Usage:
            mongo_conn = conf.get('db.mongo.MONGO_CONNECTION_STRING')
            default_db = conf.get('default.db')
            az_credentials = conf.get('data.service.azure.credentials')

        :param default:
        :param key: A string representing the value's path in the config.
        """
        try:
            return self.__getitem__(key)
        except KeyError:
            if default is None:
                path = self.path
                Console.warning(
                    "The key '{key}' could not be found in the yaml file '{path}'".format(
                        **locals()))
                # sys.exit(1)
                raise KeyError(key)
            return default
        except Exception as e:
            print(e)
            sys.exit(1)

    def __setitem__(self, key, value):
        self.set(key, value)

    def set(self, key, value):
        """
        A helper function for setting the default cloud in the config without
        a chain of `set()` calls.

        Usage:
            mongo_conn = conf.set('db.mongo.MONGO_CONNECTION_STRING',
                         "https://localhost:3232")

        :param key: A string representing the value's path in the config.
        :param value: value to be set.
        """

        if value.lower() in ['true', 'false']:
            value = value.lower() == 'true'
        try:
            if "." in key:
                keys = key.split(".")
                #
                # create parents
                #
                parents = keys[:-1]
                location = self.data
                for parent in parents:
                    if parent not in location:
                        location[parent] = {}
                    location = location[parent]
                #
                # create entry
                #
                location[keys[len(keys) - 1]] = value
            else:
                self.data[key] = value

        except KeyError:
            path = self.path
            Console.error(
                "The key '{key}' could not be found in the yaml file '{path}'".format(
                    **locals()))
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

        yaml_file = self.data.copy()
        with open(self.path, "w") as stream:
            yaml.safe_dump(yaml_file, stream, default_flow_style=False)

    def __getitem__(self, item):
        """
        gets an item form the dict. The key is . separated
        use it as follows get("a.b.c")
        :param item:
        :type item:
        :return:
        """
        try:
            if "." in item:
                keys = item.split(".")
            else:
                return self.data[item]
            element = self.data[keys[0]]
            for key in keys[1:]:
                element = element[key]
        except KeyError:
            path = self.path
            Console.warning(
                "The key '{item}' could not be found in the yaml file '{path}'".format(
                    **locals()))
            raise KeyError(item)
            # sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)
        # if element.lower() in ['true', 'false']:
        #    element = element.lower() == 'true'
        return element

    def __delitem__(self, item):
        """
        #
        # BUG THIS DOES NOT WORK
        #
        gets an item form the dict. The key is . separated
        use it as follows get("a.b.c")
        :param item:
        :type item:
        :return:
        """
        try:
            if "." in item:
                keys = item.split(".")
            else:
                return self.data[item]
            element = self.data
            print(keys)
            for key in keys:
                element = element[key]
            del element
        except KeyError:
            path = self.path
            Console.error(
                "The key '{item}' could not be found in the yaml file '{path}'".format(
                    **locals()))
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)

    def search(self, key, value=None):
        """
        search("cloudmesh.cloud.*.cm.active", True)
        :param key:
        :param value:
        :return:
        """
        flat = FlatDict(self.data, sep=".")
        result = flat.search(key, value)
        return result

    def edit(self, attribute):
        """
        edits the dict specified by the attribute and fills out all TBD values.
        :param attribute:
        :type attribute: string
        :return:
        """

        Console.ok("Filling out: {attribute}".format(attribute=attribute))

        try:
            config = Config()
            values = config[attribute]

            print("Editing the values for {attribute}"
                  .format(attribute=attribute))

            print("Current Values:")

            print(yaml.dump(values, indent=2))

            for key in values:
                if values[key] == "TBD":
                    result = input("Please enter new value for {key}: "
                                   .format(**locals()))
                    values[key] = result

            config.save()
        except Exception as e:
            print(e)
            Console.error(f"could not find the attribute '{attribute}' in the yaml file.")

    """
    @staticmethod
    def cat_dict(d,
                 mask_secrets=True,
                 attributes=None,
                 color=None):
        kluge = yaml.dump(d,
                          default_flow_style=False, indent=2)
        content = kluge.splitlines()

        return Config.cat_lines(content, mask_secrets=mask_secrets)
    """

    def cat_dict(self, d):
        kluge = yaml.dump(d,
                          default_flow_style=False, indent=2)
        content = kluge.splitlines()

        return self.cat_lines(content)

    def cat_lines(self, content):
        lines = '\n'.join(content)
        return lines

    def cat(self):

        _path = path_expand(self.path)
        with open(_path) as f:
            content = f.read().splitlines()
        return self.cat_lines(content)
