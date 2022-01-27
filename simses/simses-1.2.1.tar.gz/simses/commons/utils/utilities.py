import csv
import datetime
import inspect
import math
import os
import shutil
import sys
import urllib.request
from os.path import basename
from urllib.error import URLError

from simses.commons.error import InfiniteNumberError, NanNumberError, ComplexNumberError


def remove_file(file: str) -> None:
    """
    Removes file

    Parameters
    ----------
    file :
        path to file

    Returns
    -------

    """
    if os.path.isfile(file):
        os.remove(file)


def remove_all_files_from(directory: str) -> None:
    """
    Function to remove all files from a directory

    Parameters
    ----------
    directory : folder path

    Returns
    -------

    """
    try:
        for item in os.listdir(directory):
            file = os.path.join(directory, item)
            remove_file(file)
    except FileNotFoundError:
        # print(directory + ' does not exist')
        pass


def copy_all_files(source: str, target: str):
    """
    Function to copy all files in a new folder

    Parameters
    ----------
    source : path (string) to the source folder
    target : path (string) to the target folder

    Returns
    -------

    """

    for item in os.listdir(source):
        path = os.path.join(source, item)
        if os.path.isfile(path):
            shutil.copy(path, target)


def download_file(url_path: str, file_name: str) -> None:
    """
    Downloading a file from the given url and stores it to file_name

    Raises FileNotFoundError if file at URL is not available

    Parameters
    ----------
    url_path :
        URL to file to download
    file_name :
        path where file should be stored

    Returns
    -------

    """
    try:
        with urllib.request.urlopen(url_path) as response:
            print('Downloading ' + basename(file_name) + ' from ' + url_path + ' ...')
            with open(file_name, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
    except URLError as err:
        raise FileNotFoundError(err, file_name + ' could not be found on server.')


def create_directory_for(path: str, warn: bool = False) -> None:
    """
    Function to create a folder at a specific path

    Parameters
    ----------
    path : str

    Returns
    -------

    """
    if not os.path.exists(path):
        os.makedirs(path)
    elif warn:
        sys.stderr.write('WARNING: ' + path + ' exists already')
        sys.stderr.flush()


def format_float(value: float, decimals: int = 2) -> str:
    """
    Formatting value to string with given decimals

    Parameters
    ----------
    value :
        given value
    decimals :
        round to number of decimals

    Returns
    -------
    str:
        value as string
    """
    return f"{value:.{decimals}f}"


def write_to_file(filename: str, _list: [str], append: bool = False) -> None:
    """
    Writes given list of strings to file

    Parameters
    ----------
    filename :
        path to file
    _list :
        list with values as strings
    append :
        flag to append to file or (over)write file

    Returns
    -------
    None:
        None
    """
    with open(filename, 'a' if append else 'w', newline='') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerow(_list)
    writeFile.close()


def all_non_abstract_subclasses_of(cls, exclude: list=list()) -> list:
    """
    Generates a list of non-abstract subclass from given class

    Parameters
    ----------
    exclude :
        list of classes which should be excluded from result list
    cls :
        given class

    Returns
    -------
    list:
        list with non-abstract subclasses
    """
    res = list()
    subs = set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_non_abstract_subclasses_of(c)])
    for sub in subs:
        if not inspect.isabstract(sub) and sub not in exclude:
            res.append(sub)
    return res


def search_path_for_file_in(directory: str, filename: str) -> str:
    """
    Searching path where file with filename is located within all subdirectories of directory

    Parameters
    ----------
    directory :
        base directory for search
    filename :
        searched filename

    Returns
    -------
    str:
        path where filename is located, if filename was found - empty string otherwise

    """
    path: str = ''
    for item in os.listdir(directory):
        file = os.path.join(directory, item)
        if os.path.isfile(file) and file.endswith(filename):
            if not path:
                path = directory
                break
        if os.path.isdir(file):
            local_dir = search_path_for_file_in(file, filename)
            if not path and local_dir:
                path = local_dir
                break
    return path


def get_path_for(filename: str, max_depth: int = 4) -> str:
    """
    Searching path for filename starting with current working directory and all of its subdirectories. If file was not
    found, it goes up the parent directories of the CWD with a given maxium depth

    Parameters
    ----------
    filename :
        search filename
    max_depth :
        maximum depth of parent directories in which should be searched, default: 3

    Returns
    -------
    str:
        path where filename is located or a FileNotFoundError

    """
    res: str = ''
    depth: int = 0
    path: str = os.path.dirname(os.path.abspath(__file__))
    while not res and depth < max_depth:
        res = search_path_for_file_in(path, filename)
        path = os.path.dirname(path)
        depth += 1
    if not res:
        raise FileNotFoundError(filename + ' could not be found')
    return res + '/'


def convert_path_codec(path: str, encode: str = 'latin-1', decode: str = 'utf-8') -> str:
    """
    Enconding and decoding path with given codecs, e.g. in order to convert German Umlaut

    Parameters
    ----------
    path :
        string which should be converted
    encode :
        enconding codec, defaults: latin-1
    decode :
        decoding codec, defaults: utf-8

    Returns
    -------
    str:
        decoded path

    """
    try:
        if is_codec(path, decode):
            return path
        return path.encode(encode).decode(decode)
    except (UnicodeEncodeError, UnicodeDecodeError) as err:
        sys.stderr.write(err)
        sys.stderr.flush()
        return path


def is_codec(string: str, codec: str = 'utf-8') -> bool:
    """
    Checks if given string is encoded as given codec

    Parameters
    ----------
    string :
        string to check codec
    codec :
        codec which should be checked, default: utf-8

    Returns
    -------
    bool:
        True if string is encoded with codec, False otherwise
    """
    try:
        string.encode(codec).decode(codec)
        return True
    except (UnicodeEncodeError, UnicodeDecodeError):
        return False


def add_month_to(date: datetime.datetime) -> datetime.datetime:
    """
    Generates a new datetime object from given datetime object with a month added.
    If month is last month of year, it returns first month of next year.

    Parameters
    ----------
    date :
        given datetime object

    Returns
    -------
    datetime:
        new datetime object
    """
    if date.month == 12:
        date = date.replace(year=date.year + 1, month=1)
    else:
        date = date.replace(month=date.month + 1)
    return date


def add_year_to(date: datetime.datetime) -> datetime.datetime:
    """
    Generates a new datetime object from given datetime object with a year added.

    Parameters
    ----------
    date :
        given datetime object

    Returns
    -------
    datetime:
        new datetime object
    """
    return date.replace(year=date.year + 1)


def get_year_from(tstmp: float) -> float:
    """
    Calculates year from given timestamp

    Parameters
    ----------
    tstmp :
        given timestamp in epoch time

    Returns
    -------
    float :
        year of given epoch timestamp
    """
    return datetime.datetime.fromtimestamp(tstmp).year


def get_maximum_from(values: list) -> float:
    """
    Gets maximum value from given values

    Parameters
    ----------
    values :
        list of values

    Returns
    -------
    float:
        maximum value from given list
    """
    if values:
        max_value: float = max(values)
    else:
        max_value: float = 0.0
    return max_value


def get_average_from(values: list) -> float:
    """
    Calculates average from given value list

    Parameters
    ----------
    values :
        list of values

    Returns
    -------
    float:
        average from values
    """
    if values:
        average_value: float = sum(values) / len(values)
    else:
        average_value: float = 0.0
    return average_value


def check(value: float) -> None:
    if math.isinf(value):
        raise InfiniteNumberError()
    if math.isnan(value):
        raise NanNumberError()
    if isinstance(value, complex):
        raise ComplexNumberError()
