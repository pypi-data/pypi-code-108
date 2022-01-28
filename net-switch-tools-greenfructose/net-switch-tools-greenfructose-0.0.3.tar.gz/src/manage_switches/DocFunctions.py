import os
import inspect
import csv
from pprint import pprint


def retrieve_name(var) -> str:
    """
    Gets name of variable passed to a function.
    :param var: Variable whos name is needed.
    :return: String of original variable name.
    """
    callers_local_vars = inspect.currentframe().f_back.f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var][0]


def write_result_csv(source: list[dict], method: str, prepend: str = None) -> None:
    """
    Writes a list of dictionaries to a CSV file in CWD. Name
    of file is generated from name of list variable. Requires
    'retrieve_name' function.
    :param source: List of dictionaries with same field names.
    :param method: Method of writing ('w', 'w+', 'a', 'a+').
    :param prepend: String to prepend to filename, optional.
    :return: None
    """
    if prepend is None:
        filename = f'{retrieve_name(source)}.csv'
    else:
        filename = f'{prepend}-{retrieve_name(source)}.csv'
    file_exists = os.path.exists(filename)
    fieldnames = list(source[0].keys())
    with open(filename, method) as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\n', delimiter=',')
        if not file_exists:
            writer.writeheader()
        for data in source:
            writer.writerow(data)
            pprint(f"Writing Row: {data}")


def reformat_mac(mac: str) -> str:
    """
    Reformat MAC address to all lowercase with
     dashes separating octets e.g. 1a-2a-a3-b5-e4-2a
    :param mac: MAC address to format
    :return: reformatted MAC as string
    """
    mac = mac.replace('-', '').replace(':', '')
    mac = '-'.join(mac[i:i + 2] for i in range(0, 12, 2)).lower()
    return mac
