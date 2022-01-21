import os
import clr
import colorlog
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 importlib_resources.
    import importlib_resources as pkg_resources

from ruamel.yaml import YAML, yaml_object, add_representer
from . import resources

logger = colorlog.getLogger('PySimultan')

# import SIMULTAN DLLs

clr.AddReference('System.Collections')

# check if environment variable is set:
try:
    dll_path = os.environ['SIMULTAN_SDK_DIR']
    clr.AddReference(os.path.join(dll_path, 'SIMULTAN.Project.dll'))
    clr.AddReference(os.path.join(dll_path, 'ParameterStructure.dll'))
    clr.AddReference(os.path.join(dll_path, 'SIMULTAN.UI.dll'))
    clr.AddReference(os.path.join(dll_path, 'GeometryViewer.dll'))
    clr.AddReference(os.path.join(dll_path, 'GeometryViewer.Data.dll'))
    clr.AddReference(os.path.join(dll_path, 'SIMULTAN.DataExchange.dll'))

except KeyError as e:
    logger.info(f'SIMULTAN Environment variable not set. Loading package DLLs...')
    with pkg_resources.path(resources, 'SIMULTAN.Project.dll') as r_path:
        clr.AddReference(str(r_path))
    with pkg_resources.path(resources, 'ParameterStructure.dll') as r_path:
        clr.AddReference(str(r_path))
    with pkg_resources.path(resources, 'SIMULTAN.UI.dll') as r_path:
        clr.AddReference(str(r_path))
    with pkg_resources.path(resources, 'GeometryViewer.dll') as r_path:
        clr.AddReference(str(r_path))
    with pkg_resources.path(resources, 'GeometryViewer.Data.dll') as r_path:
        clr.AddReference(str(r_path))
    with pkg_resources.path(resources, 'SIMULTAN.DataExchange.dll') as r_path:
        clr.AddReference(str(r_path))


def represent_none(self, _):
    return self.represent_scalar('tag:yaml.org,2002:null', '')


add_representer(type(None), represent_none)
yaml = YAML()
yaml.default_flow_style = None
yaml.preserve_quotes = True
yaml.allow_unicode = True

continue_on_error = True

cs_axis_up = 2  # define which axis is in up/down direction; 0: x-axis; 1: y-axis; 2: z-axis; In SIMULTAN the y-axis is the up/down axis
