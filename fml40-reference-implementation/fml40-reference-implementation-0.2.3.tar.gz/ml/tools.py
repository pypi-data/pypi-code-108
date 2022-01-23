"""This module provides a collection of convenience functions."""

import json
import os
import xml.etree.ElementTree as ET
import sqlite3
import time
import jsonschema
from jsonschema import validate
from ml.app_logger import APP_LOGGER

IDENTITY_PROVIDER_URL = "https://idp.s3i.vswf.dev/"
BUILT_IN = ["from", "str", "dict", "list", "bool", "float", "int", "tuple",
               "def", "return", "for", "if", "class", "try", "except"]

class BColors:
    """colors for the console log"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def make_sub_thing(name, roles, features=[]):
    """
    Creates a dictionary representing this thing in it's current state
    as a subordinate thing. This representation should be used for
    subordinate things in s3i repository entries

    :param name: name of the sub thing
    :type name: str
    :param roles: fml40 roles of the sub thing
    :type roles: str
    :param features: fml40 features of the sub thing
    :type features: list

    :returns: JSON of the sub thing
    :rtype: dict

    """
    sub_thing = {
        "class": "ml40::Thing",
        "name": name,
        "roles": roles,
        "features": features
    }

    return sub_thing


def make_feature_config(class_name, identifier="", name="", subFeatures=""):
    """
    Creates a dictionary representing for its ml/fml40 features

    :param class_name: class name of the fml40 feature
    :type class_name: str
    :param identifier: local id of the fml40 feature
    :type identifier: str
    :param name: name of the fml40 feature
    :type name: str
    :param subFeatures: sub features
    :type subFeatures: dict

    :returns: JSON of the fml40 feature
    :rtype: dict

    """
    config_json = {
        "class": class_name
    }
    if identifier:
        config_json["identifier"] = identifier
    if name:
        config_json["name"] = name
    if subFeatures:
        config_json["subFeatures"] = subFeatures

    return config_json


def make_thing_config(thing_id, name, roles, features=[], config_path=""):
    """
    Creates a configuration file (JSON) for a fml40 thing.

    :param thing_id: identifier of the thing
    :type thing_id: str
    :param name: name of the thing
    :type name: str
    :param roles: fml40 roles of the thing
    :type roles: list
    :param features: fml40 features of the thing
    :type features: list
    :param config_path: path where the configuration file should be located
    :type config_path: str

    :returns: name of the configuration file of the thing
    :rtype: str


    """
    if not config_path:
        config_path = os.path.join("__file__", "configs")

    config_file = {
        "thingId": thing_id,
        "policyId": thing_id,
        "attributes": {
            "class": "ml40::Thing",
            "name": name,
            "roles": roles,
            "features": features,
        }
    }
    file_path = os.path.join(config_path, "{}.json".format(name))
    with open(file_path, 'wb') as file:
        file.write(json.dumps(config_file).encode('utf-8'))
    return "{}.json".format(name)


def load_config(config_filepath):
    """
    Loads a JSON object from a json formatted file found at config_filepath.

    :param config_filepath: Path to json formatted file.
    :type config_filepath: str

    """
    with open(config_filepath) as config_file:
        config = json.load(config_file)
        return config


def find_broker_endpoint(dir_obj, thing_id):
    """
    Finds the S3I-B endpoint of a thing

    :param dir_obj: S³I Directory Object
    :type dir_obj: object
    :param thing_id: identifier of the searched thing

    """
    thing_json = dir_obj.queryThingIDBased(thing_id)
    all_endpoints = thing_json["attributes"].get("allEndpoints", None)
    if all_endpoints:
        for ep in all_endpoints:
            if "s3ib" in ep:
                return ep


def remove_namespace(input_str):
    """
    Removes the specified namespace like ml40 or fml40

    :param input_str: input with namespace
    :type input_str: str
    :returns: output without namespace
    :rtype: str

    """
    return input_str.replace("mml40::", "").replace("fml40::", "").replace("ml40::", "")


def check_var_conflict(var):
    """
    check if the input is built-in variable
    :param var: python var
    :return: modified variable, if the input is a input variable.
    """

    if var in BUILT_IN:
        return "_{}".format(var)
    else:
        return var


class XML:
    def __init__(self, path=None, xml_str=None):
        self.et = ET
        self._namespace = {}

        self._namespace = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'schemaLocation': 'urn:skogforsk:stanford2010 HarvestedProduction_V3p0.xsd',
            '': 'urn:skogforsk:stanford2010'
        }

        for key in self._namespace:
            self.et.register_namespace(key, self._namespace[key])

        if path is not None:
            self.tree = self.et.parse(path)
            self.root = self.tree.getroot()

        if xml_str is not None:
            self.root = self.et.fromstring(xml_str)

    def find_nodes(self, path):
        path_list = path.split('/')
        new_path = ""
        for _path in path_list:
            if ":" not in _path:
                _path = "{" + self._namespace.get('') + "}" + _path
            new_path += _path
            new_path += "/"
        if new_path[-1] == "/":
            new_path = new_path[:-1]
        return self.root.findall(new_path, self._namespace)

    def to_string(self, root):
        return self.et.tostring(root, "unicode", "xml")


class DataBase:
    def __init__(self, db):
        self.__db = db
        self.__table_conf = {}
        self.__conn = None

    @property
    def conn(self):
        return self.__conn

    @property
    def cursor(self):
        return self.__conn.cursor()

    def connect(self):
        self.__conn = sqlite3.connect(self.__db, check_same_thread=False)
        APP_LOGGER.info("Connect to the database {}".format(self.__db))

    def build_table(self, table, configuration):
        conf_schema = {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["var_name", "var_type"],
                "properties": {
                    "var_name": {"type": "string"},
                    "var_type": {"type": "string"}
                }
            }
        }
        try:
            validate(instance=configuration, schema=conf_schema)
        except jsonschema.ValidationError as e:
            APP_LOGGER.error("config json error: {}".format(e))

        exec_str = "ID INTEGER PRIMARY KEY AUTOINCREMENT"

        for i in configuration:
            name = i["var_name"]
            type = i["var_type"]
            exec_str += ", {} {}".format(name, type)

        exec_str = '''CREATE TABLE if not exists {0} ({1});'''.format(table, exec_str)
        cursor = self.__conn.cursor()
        try:
            cursor.execute(exec_str)
            APP_LOGGER.info("Create table {} if not exists".format(table))
        except sqlite3.OperationalError as e:
            APP_LOGGER.warning(e)

        self.__table_conf[table] = configuration

    def disconnect(self):
        self.__conn.close()

    def update(self, table, value_dict):
        for key in value_dict.keys():
            def_var_name = []
            for var in self.__table_conf.get(table, {}):
                def_var_name.append(var["var_name"])
            if key not in def_var_name:
                raise ValueError("{} is not defined variable name".format(key))

        cursor = self.__conn.cursor()
        exec_str = ""

        for i in value_dict.keys():
            exec_str += "{},".format(i)
        """    
        for i in self.__table_conf.get(table):
            exec_str += "{},".format(i["var_name"])
        """
        exec_str = exec_str[:-1]
        exec_str = "INSERT INTO {} ({})".format(table, exec_str)

        value_str = ""

        for i in value_dict.keys():
            if isinstance(value_dict[i], str):
                value_str += "'{}',".format(value_dict[i])
            elif isinstance(value_dict[i], (float, int, bool)):
                value_str += "{},".format(value_dict[i])
        """        
        for i in self.__table_conf.get(table, {}):
            if isinstance(value_dict[i["var_name"]], str):
                value_str += "'{}',".format(value_dict[i["var_name"]])
            elif isinstance(value_dict[i["var_name"]], (float, int, bool)):
                value_str += "{},".format(value_dict[i["var_name"]])
        """
        value_str = value_str[:-1]
        value_str = "VALUES ({})".format(value_str)

        exec_str += value_str
        try:
            cursor.execute(exec_str)
        except sqlite3.OperationalError as e:
            APP_LOGGER.warning(e)
        self.__conn.commit()

    def delete(self, table, id=None):
        if id is None:
            exec_str = "DELETE FROM {};".format(table)
        else:
            exec_str = "DELETE FROM {} where id={}".format(table, id)
        try:
            self.__conn.cursor().execute(exec_str)
        except sqlite3.OperationalError as e:
            APP_LOGGER.warning(e)

        self.__conn.commit()

    def drop(self, table):
        exec_str = "DROP TABLE {}".format(table)
        try:
            self.__conn.cursor().execute(exec_str)
        except sqlite3.OperationalError as e:
            APP_LOGGER.warning(e)
        self.__conn.commit()

    def search(self, table):
        exec_str = "SELECT * FROM {};".format(table)
        cursor = self.__conn.cursor().execute(exec_str)
        for row in cursor:
            print("------------------")
            print("ID = {}".format(row[0]))
            for i in range(len(self.__table_conf.get(table, {}))):
                print("{} = {}".format(self.__table_conf.get(table)[i]["var_name"].upper(), row[i + 1]))
            print("------------------\n\n")

    def execute(self, exec_str):
        try:
            return self.__conn.cursor().execute(exec_str)
        except sqlite3.OperationalError as e:
            APP_LOGGER.warning(e)

