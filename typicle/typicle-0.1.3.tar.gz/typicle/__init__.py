from pathlib import Path

import yaml


THIS_DIR = Path(__file__).parent

def parse_yaml(path: str):
    with open(path, 'r') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data

def struc_type(type_dict: dict) -> list:
    return list(type_dict.items())

_immutable_struc = lambda x: tuple(struc_type(x))

class Types:
    def __init__(self, config_file: str=str(THIS_DIR / 'types.yml')):
        data = parse_yaml(config_file)
        for key, val in data['TYPE'].items():
            setattr(self, key, val)
        for key, val in data['PHYSICS_TYPE'].items():
            setattr(self, key, val)
        self.__pmu = _immutable_struc(data['PMU_DTYPE'])
        self.__edge = _immutable_struc(data['EDGE_DTYPE'])
        self.__color = _immutable_struc(data['COLOR_DTYPE'])

    @property
    def pmu(self):
        return list(self.__pmu)

    @property
    def edge(self):
        return list(self.__edge)

    @property
    def color(self):
        return list(self.__color)
