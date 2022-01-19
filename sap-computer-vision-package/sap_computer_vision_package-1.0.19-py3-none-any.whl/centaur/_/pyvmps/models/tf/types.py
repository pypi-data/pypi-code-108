import tensorflow as tf
from typing import Callable, List, Dict, Tuple
from centaur._.pyvmps.models.tf.constants import SigTensorInfo

Base64Str = str
IndivSigData = Dict[str, Dict]
RawPayload = Tuple[Dict, List]
RowPreprocessFunc = Callable[[List], List]
ColPreprocessFunc = Callable[[Dict], Dict]
InputTensorsMap = Dict[tf.Tensor, List]
ExtractDataFunc = Callable[[Dict], InputTensorsMap]
RowExtractDataPrepFunc = Callable[[List], ExtractDataFunc]
ColExtractDataPrepFunc = Callable[[Dict], ExtractDataFunc]
HandleResFunc = Callable[[Dict], Dict]
InferenceFunc = Callable[[Dict], Dict]
InferenceRes = Dict

# TF2 specific types
Tf2ExtractDataFunc = Callable[[SigTensorInfo], Dict]
Tf2RowExtractDataPrepFunc = Callable[[List], Tf2ExtractDataFunc]
Tf2ColExtractDataPrepFunc = Callable[[Dict], Tf2ExtractDataFunc]


FormatLoadedFunc = Callable[[InferenceFunc, RawPayload, IndivSigData], InferenceRes]
