from .core import (BackendType, Padding, PoolType, LearningType, LayerType,
                   HwVersion, NP, MeshMapper, Layer, Device, HardwareDevice,
                   devices, NSoC_v1, NSoC_v2, Latest, PowerMeter, PowerEvent,
                   Sequence, Pass, soc, __version__)

from .layer import *
from .input_data import InputData
from .fully_connected import FullyConnected
from .convolutional import Convolutional
from .separable_convolutional import SeparableConvolutional
from .input_convolutional import InputConvolutional
from .concat import Concat
from .model import Model
from .statistics import SequenceStatistics, Statistics
from .sparsity import evaluate_sparsity
from .np import *
from .sequence import *
from .virtual_devices import *
from .array_to_cpp import array_to_cpp

Layer.__str__ = layer_str
Layer.__repr__ = layer_repr
Layer.set_variable = set_variable
Layer.get_variable = get_variable
Layer.get_variable_names = get_variable_names
Layer.get_learning_histogram = get_learning_histogram

Sequence.__repr__ = sequence_repr
Pass.__repr__ = pass_repr

NP.Info.__repr__ = np_info_repr
NP.Mesh.__repr__ = np_mesh_repr
NP.Mapping.__repr__ = np_mapping_repr
