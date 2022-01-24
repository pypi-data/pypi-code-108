from enum import Enum


class ModelFormat(Enum):
    NON_SPECIFIED = 0
    UNKNOWN = 1

    PT_NN_MODULE = 11
    TF_KERAS_MODEL = 12
    KERAS_MODEL = 13
    TF_SESSION = 14

    H5 = 21
    SAVED_MODEL = 22
    PB = 23
    ZIPPED_SAVED_MODEL = 24
    TFLITE = 25

    PTH = 31
    ONNX = 32
    TORCH_TRACED = 33

    CKPT = 26

    TRT_PLAN = 41

    GRAPHDEF = 51

    RELAYIR = 61

    MLIR = 71


TF_MODEL_FORMATS = [ModelFormat.TF_KERAS_MODEL,
                    ModelFormat.KERAS_MODEL,
                    ModelFormat.H5,
                    ModelFormat.SAVED_MODEL,
                    ModelFormat.PB]


class ModelDataType(Enum):
    NON_SPECIFIED = 0
    FP32 = 1
    FP16 = 2

    BF16 = 11

    INT8 = 21
