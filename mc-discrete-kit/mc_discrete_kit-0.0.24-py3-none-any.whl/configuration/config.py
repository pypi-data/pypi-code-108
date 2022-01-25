import enum
import glob
import os
import datetime
import logging
from mc_automation_tools import common

_log = logging.getLogger('discrete_kit.configuration.config')

files_names = ['Files', 'Product', 'ShapeMetadata']

files_extension_list = ['.cpg', '.dbf', '.prj', '.shp', '.shx']

METADATA_TYPE = 'RECORD_RASTER'
JSON_NAME = "validation_schema.json"
SCHEMA_FOLDER = 'configuration'

PATH_TO_CHECK = r'/home/dimitry/Downloads/tt/3273(1)/3273/2021-2683-0/Shapes'


class OSName(enum.Enum):
    LINUX = 'Linux'


class ExtensionTypes(enum.Enum):
    """
    Types of environment.
    """
    SHAPE = '.shp'
    TFW = '.tfw'


class EnvironmentTypes(enum.Enum):
    """
    Types of environment.
    """
    QA = 1
    DEV = 2
    PROD = 3


def validate_ext_files_exists(path, ext):
    _log.info("Validating if extension : " + ext + " exists for : " + path)
    if not glob.glob(path + ext):
        _log.error("Missing filename {0}{1}".format(path, ext))
        return False, "{0}{1}".format(path, ext)
        # raise Exception("Missing filename {0}{1}".format(path, ext))
    return True, ""


def get_tiff_basename(path):
    return ''.join(os.path.basename(item) for item in (glob.glob(path + '//t*')))


def convert_time_to_utc(received_time):
    return datetime.datetime.strptime(received_time,
                                      '%d/%m/%Y').strftime('%Y-%d-%mT%H:%M:%S.%f')[:-7] + 'Z'


def generate_datatime_zulu(current=True, time_dict=None):
    """
    generate current time on zulu format
    :param current: if curren=True (as default) will return current time, if False wil generate by time_dict
    :param time_dict: should be as example: {'year':2020, 'month':12, 'day':12, 'hour':12, 'minute':10,'second':10}
    """
    if current:
        res = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
    elif time_dict:
        res = datetime.datetime(time_dict['year'], time_dict['month'], time_dict['day'], time_dict['hour'],
                                time_dict['minute'], time_dict['second']).strftime('%Y-%m-%dT%H:%M:%SZ')
    else:
        _log.error("Should provide current=True param or time dictionary value")
        raise ValueError("Should provide current=True param or time dictionary value")
    return res


def find_folder_in_path(path_to_search, folder_name):
    c = [x[0] for x in os.walk(path_to_search)]
    found_path = ("\n".join(s for s in c if folder_name.lower() in s.lower()))
    return found_path
