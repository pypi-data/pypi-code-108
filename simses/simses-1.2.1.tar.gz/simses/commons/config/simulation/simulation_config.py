from configparser import ConfigParser
from simses.commons.config.abstract_config import Config
from simses.commons.utils.utilities import get_path_for


class SimulationConfig(Config):
    """
    All simulation configs are inherited from this class
    """

    CONFIG_NAME: str = 'simulation'
    CONFIG_PATH: str = get_path_for(CONFIG_NAME + Config.DEFAULTS)

    def __init__(self, path: str, config: ConfigParser):
        if path is None:
            path = self.CONFIG_PATH
        super().__init__(path, self.CONFIG_NAME, config)


def create_dict_from(properties: [str], delimiter: str = ',') -> dict:
    res: dict = dict()
    for prop in properties:
        items: list = prop.split(delimiter)
        name: str = items.pop(0)
        if name in res.keys():
            raise Exception(name + ' is not unique. Please check your config file.')
        res[name] = items
    return res


def create_list_from(properties: [str], delimiter: str = ',') -> [[str]]:
    res: [[str]] = list()
    for prop in properties:
        res.append(prop.split(delimiter))
    return res


def clean_split(properties: str, delimiter: str = '\n') -> [str]:
    props: [str] = properties.replace(' ', '').replace('\t', '').split(delimiter)
    copy = props[:]
    for prop in copy:
        if not prop:
            props.remove(prop)
    return props
