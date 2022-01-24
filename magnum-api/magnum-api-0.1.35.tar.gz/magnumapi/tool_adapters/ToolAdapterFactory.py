import inspect
from typing import Type

from magnumapi.tool_adapters.ToolAdapter import ToolAdapter
from magnumapi.tool_adapters.roxie.RoxieToolAdapter import TerminalRoxieToolAdapter, RestRoxieToolAdapter
from magnumapi.tool_adapters.roxie.RoxieToolAdapter import DockerTerminalRoxieToolAdapter
from magnumapi.tool_adapters.ansys.AnsysToolAdapter import TerminalAnsysToolAdapter
from magnumapi.tool_adapters.ansys.AnsysToolAdapter import MapdlAnsysToolAdapter
from magnumapi.tool_adapters.ansys.AnsysToolAdapter import DockerMapdlAnsysToolAdapter
import magnumapi.commons.json_file as json_file


class ToolAdapterFactory:
    """ A ToolAdapterFactory class producing tool adapter objects from a configuration file either as a json or as a
    dictionary

    """

    @classmethod
    def init_with_json(cls, config_file_path: str) -> Type[ToolAdapter]:
        """ Class method initializing a tool adapter from a json file

        :param config_file_path: an absolute path to a config json file
        :return: an initialized ToolAdapter instance
        """
        config_dct = json_file.read(config_file_path)
        return cls.init_with_dict(config_dct)

    @staticmethod
    def init_with_dict(config_dct: dict) -> Type[ToolAdapter]:
        """ Static method initializing a tool adapter from a dictionary

        :param config_dct: a dictionary with a ToolAdapter configuration parameters
        :return: an initialized ToolAdapter instance
        """
        if config_dct.keys() == inspect.signature(TerminalRoxieToolAdapter).parameters.keys():
            return TerminalRoxieToolAdapter(**config_dct)
        elif config_dct.keys() == inspect.signature(RestRoxieToolAdapter).parameters.keys():
            return RestRoxieToolAdapter(**config_dct)
        elif config_dct.keys() == inspect.signature(DockerTerminalRoxieToolAdapter).parameters.keys():
            return DockerTerminalRoxieToolAdapter(**config_dct)
        elif config_dct.keys() == inspect.signature(TerminalAnsysToolAdapter).parameters.keys():
            return TerminalAnsysToolAdapter(**config_dct)
        elif config_dct.keys() == inspect.signature(MapdlAnsysToolAdapter).parameters.keys():
            return MapdlAnsysToolAdapter(**config_dct)
        elif config_dct.keys() == inspect.signature(DockerMapdlAnsysToolAdapter).parameters.keys():
            return DockerMapdlAnsysToolAdapter(**config_dct)
        else:
            raise KeyError('The input config definition keys {} do not match any tool adapter constructor signature!'
                           .format(config_dct.keys()))
