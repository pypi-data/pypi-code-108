import base64
import copy
import json
import logging
import os
import pathlib

import pkg_resources
from colorama import Fore, Style
from pkg_resources.extern.packaging.requirements import InvalidRequirement

# list from https://scikit-learn.org/stable/developers/advanced_installation.html
SKLEARN_REQ_MODULE_NAME = {
    'numpy',
    'scipy',
    'joblib',
    'scikit-learn',
    'threadpoolctl',
}

# list from https://www.tensorflow.org/install/pip
# if problematic, lets look to https://www.tensorflow.org/install/source
TENSORFLOW_REQ_MODULE_NAME = {
    'tensorflow',
}


# list from https://pytorch.org/get-started/locally/
PYTORCH_REQ_MODULE_NAME = {
    'torch',
    'torchvision',
    'torchaudio',
}


LOG_COLORS = {
    logging.ERROR: Fore.RED,
    logging.DEBUG: Fore.MAGENTA,
    logging.WARNING: Fore.YELLOW,
    logging.INFO: Fore.GREEN,
}


class ColorFormatter(logging.Formatter):
    def format(self, record, *args, **kwargs):
        new_record = copy.copy(record)
        if new_record.levelno in LOG_COLORS:
            new_record.levelname = "{color_begin}{level}{color_end}".format(
                level=new_record.levelname,
                color_begin=LOG_COLORS[new_record.levelno],
                color_end=Style.RESET_ALL,
            )
        return super(ColorFormatter, self).format(new_record, *args, **kwargs)


def setup_logger(package_name, level):
    baseten_logger = logging.getLogger(package_name)
    baseten_logger.setLevel(level)
    handler = logging.StreamHandler()
    formatter = ColorFormatter(fmt='%(levelname)s %(message)s')
    handler.setFormatter(formatter)
    if baseten_logger.hasHandlers():
        baseten_logger.handlers.clear()
    baseten_logger.addHandler(handler)


def base64_encoded_json_str(obj):
    return base64.b64encode(str.encode(json.dumps(obj))).decode('utf-8')


def zipdir(path, zip_handler):
    for root, dirs, files in os.walk(path):
        relative_root = ''.join(root.split(path))
        for _file in files:
            zip_handler.write(
                os.path.join(root, _file), os.path.join(f'model{relative_root}', _file))


def print_error_response(response):
    print(Fore.YELLOW + f'{response["message"]}')
    print('---------------------------------------------------------------------------')
    print(Fore.GREEN + 'Stack Trace:')
    if 'exception' in response:
        excp = response['exception']
        for excp_st_line in excp['stack_trace']:
            print(Fore.GREEN + '---->' + Fore.WHITE + f'{excp_st_line}')
        print(Fore.RED + f'Exception: {excp["message"]}')


def parse_requirements_file(requirements_file: str) -> dict:
    name_to_req_str = {}
    with pathlib.Path(requirements_file).open() as reqs_file:
        for raw_req in reqs_file.readlines():
            try:
                req = pkg_resources.Requirement.parse(raw_req)
                if req.specifier:
                    name_to_req_str[req.name] = str(req)
                else:
                    name_to_req_str[str(req)] = str(req)
            except InvalidRequirement:
                # there might be pip requirements that do not conform
                raw_req = str(raw_req).strip()
                name_to_req_str[f'custom_{raw_req}'] = raw_req
            except ValueError:
                # can't parse empty lines
                pass

    return name_to_req_str
