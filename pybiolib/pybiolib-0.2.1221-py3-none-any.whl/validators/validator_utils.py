from enum import Enum
import re


def validate_hostname_and_return_error_message(hostname):
    if '/' in hostname or '\\' in hostname:
        return 'The hostname can not contain slashes. Please only use the domain'

    if re.findall(r'[\s]', hostname):
        return 'The hostname can not contain whitespace'

    if hostname.split('.')[-1].isdigit():
        return 'The hostname can not be an IP address'

    # Using 'in' to catch subdomains as well i.e. 'account.biolib.com'
    if 'biolib.com' in hostname:
        return 'The biolib.com domain can not be used as a remote host'


stdout_render_types = [
    ('text', 'Text'),
    ('markdown', 'Markdown'),
]


class ChoicesEnum(Enum):
    """
    Class to be inherited from when using enums with the choice option in CharFields
    """
    @classmethod
    def choices(cls):
        return tuple((i.value, i.name) for i in cls)

    @classmethod
    def values(cls):
        return [i.value for i in cls]


class AllowedYAMLEnvironments(ChoicesEnum):
    LOCAL_DOCKER = 'local-docker'
    DOCKERHUB = 'dockerhub'
    BIOLIB_APP = 'biolib'


def normalize(string):
    return string.replace('-', '_').lower()


custom_executors = {
    'python3': {
        'latest': '1.0.0',
        'versions': [
            '1.0.0'
        ],
    },
    'onnx': {
        'latest': '1.0.0',
        'versions': [
            '1.0.0'
        ],
    },
    'r': {
        'latest': '1.0.0',
        'versions': [
            '1.0.0'
        ],
    },
    'rust': {
        'latest': '1.0.0',
        'versions': [
            '1.0.0'
        ],
    },
    'tensorflow': {
        'latest': '1.0.0',
        'versions': [
            '1.0.0'
        ],
    },
    'tflite': {
        'latest': '1.0.0',
        'versions': [
            '1.0.0'
        ],
    },
    'emscripten': {
        'latest': '1.0.0',
        'versions': [
            '1.0.0'
        ],
    }
}

old_to_new_executors_map = {
    'bl-python3': 'python3',
    'bl-onnx': 'onnx',
    'bl-rust': 'rust',
    'bl-r': 'r',
    'bl-tensorflow': 'tensorflow',
    'bl-emscripten': 'emscripten',
    'bl-tflite': 'tflite'
}

