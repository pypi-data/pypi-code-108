from typing import List, Dict, Any
from skl2onnx.common.data_types import FloatTensorType, StringTensorType,DoubleTensorType, Int64TensorType,Int32TensorType,BooleanTensorType
import numpy as np
from enum import Enum
from copy import deepcopy
import json

class InputType(Enum):

    def __new__(cls, value, numpy_type, onnx_type ):
        t = object.__new__(cls)
        t._value_ = value
        t._numpy_type = numpy_type
        t._onnx_type = onnx_type
        return t

    
    integer = (1, np.dtype("int32"), Int32TensorType([None, 1]))
    # double = (2, np.dtype("float64"), DoubleTensorType([None, 1])) # onnx doesnt support DoubleTensorType yet
    long = (3, np.dtype("int64"), Int64TensorType([None, 1]))
    float = (4, np.dtype("float32"), FloatTensorType([None, 1]))
    string = (5, np.dtype("str"), StringTensorType([None, 1]))
    boolean = (6, np.dtype("bool"), BooleanTensorType([None, 1]))

    def __repr__(self):
        return self.name

    def to_numpy(self) -> np.dtype:
        return self._numpy_type

    def to_onnx(self):
        return self._onnx_type
    
    
class Input(object):
    def __init__(self, name, input_type):
        self.name = name
        try:
            self.input_type = InputType[input_type] if isinstance(input_type, str) else input_type
        except KeyError:
            raise Exception("Unsupported type '{0}', expected inputs: {1}".format(input_type, [i.name for i in InputType]))
        if not isinstance(self.input_type, InputType):
            raise TypeError("Expected InputType")
        

    def to_dict(self):
        return {"name": self.name, "type": self.input_type.name}


class Image(object):
    def __init__(self, width:int, height:int, channel=3):
        self.type = "IMAGE"
        self.width = width
        self.height = height
        self.channel = channel
        
    def to_list(self):
        return [{"width": self.width,  "height": self.height, "channel": self.channel}]

    
class InputList(object):
    def __init__(self, inputs: List[Input]):
        self.type = "INPUT_LIST"
        if not (
            all(map(lambda x: isinstance(x, Input), inputs))
        ):
            raise Exception(
                "List should include Input"
            )

        self.inputs = inputs
    
    def convert_onnx(self):
        result = list(map(lambda x: (x.name,x.input_type.to_onnx()), self.inputs))

        result = []
        selector = None
        for input in self.inputs:
            if selector != input.input_type:
                selector = input.input_type
                onnx_input_name = f"{input.input_type.name}_{len(result)}"
                onnx_type = deepcopy(input.input_type.to_onnx())
                result.append((onnx_input_name, onnx_type ))
            else:
                result[-1][1].shape[1] += 1

        return result

    def to_json(self) -> str:
        return json.dumps([x.to_dict() for x in self.inputs])

    def to_list(self) -> List[Dict[str, Any]]:
        return [x.to_dict() for x in self.inputs]

       