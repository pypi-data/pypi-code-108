import colorlog
from .config import *
from .data_model import DataModel
from .simultan_utils import create_component
from .template_tools import Template, TemplateParser
from .geo_default_types import BaseGeometricLayer, BaseGeometricVertex, BaseGeometricEdge, BaseGeometricEdgeLoop, BaseGeometricFace, BaseGeometricVolume

from .ParameterStructure.Components import SimComponent
from .ParameterStructure.Parameters import SimParameter

handler = colorlog.StreamHandler()
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

handler.setFormatter(formatter)

logger = colorlog.getLogger('PySimultan')
logger.addHandler(handler)
