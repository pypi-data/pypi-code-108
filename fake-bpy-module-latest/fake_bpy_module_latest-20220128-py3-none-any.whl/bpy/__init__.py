import sys
import typing
import bpy.types

from . import types
from . import app
from . import ops
from . import context
from . import utils
from . import msgbus
from . import props
from . import path

data: 'bpy.types.BlendData' = None
''' Access to Blender's internal data
'''
