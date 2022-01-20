# Copyright Exafunction, Inc.

_module_repository_clear_allowed = False
from exa.common_pb.common_pb2 import DataType
from exa.common_pb.common_pb2 import ModuleContextInfo
from exa.common_pb.common_pb2 import ModuleInfo
from exa.common_pb.common_pb2 import ValueMetadata
from exa.py_module_repository.module_repository import glob
from exa.py_module_repository.module_repository import ModuleRepository

# Enable partial distribution without actual client
try:
    from exa.py_client.module import Module
    from exa.py_client.session import ModuleContextSpec
    from exa.py_client.session import PlacementGroupSpec
    from exa.py_client.session import Session
    from exa.py_module.base_module import BaseModule
    from exa.py_module.base_module import export
    from exa.py_module.base_module_context import BaseModuleContext
    from exa.py_module.base_module_context import wrap_call
    from exa.py_module.method_context import MethodContext
    from exa.py_value.value import Value
    from exa.py_value.value import ValueCompressionType
except ImportError as e:
    import os

    if os.environ.get("EXA_DEBUG_IMPORT", False):
        print("Failed to import Exafunction modules")
        raise e

# Enable extra module distribution without dependencies
try:
    from exa.ffmpeg_pb.ffmpeg_pb2 import DecoderParameters
    from exa.ffmpeg_pb.ffmpeg_pb2 import DecoderType
    from exa.ffmpeg_pb.ffmpeg_pb2 import EncoderParameters
    from exa.ffmpeg_pb.ffmpeg_pb2 import EncoderType
    from exa.py_ffmpeg.ffmpeg import VideoDecoder
    from exa.py_ffmpeg.ffmpeg import VideoEncoder
except ImportError as e:
    import os

    if os.environ.get("EXA_DEBUG_IMPORT_EXTRAS", False):
        print("Failed to import Exafunction extras modules")
        raise e
