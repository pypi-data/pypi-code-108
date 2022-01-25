import typing
import numpy as np
import requests
import os
import sys
import platform
from enum import Enum
from trtpy import *

List  = typing.List
Tuple = typing.Tuple

torch    = None
hub_url  = "http://zifuture.com:1556/fs/25.shared"

def lazy_import_torch():
    global torch

    if torch is not None:
        return

    import torch

def onnx_hub(name):
    # arcface_iresnet50 ：人脸识别Arcface
    # mb_retinaface     ：人脸检测Retinaface
    # scrfd_2.5g_bnkps  ：人脸检测SCRFD小模型2.5G Flops
    # fall_bp           ：摔倒分类模型
    # sppe              ：人体关键点检测AlphaPose
    # yolov5m           ：yolov5 m模型，目标检测coco80类
    # yolox_m           ：yolox m模型，目标检测coco80类

    if "HOME" in os.environ:
        root = os.path.join(os.environ["HOME"], ".trtpy")
        if not os.path.exists(root):
            os.mkdir(root)
    else:
        root = "."

    local_file = os.path.join(root, f"{name}.onnx")
    if not os.path.exists(local_file):
        url        = f"{hub_url}/{name}.onnx"
        
        from trtpy import downloader
        print(f"OnnxHub: download from {url}, to {local_file}")
        if not downloader.download_to_file(url, local_file):
            return None

    return local_file


def reference_numpy_tensor(t, tensor):

    if tensor is None:
        return None

    if tensor.size == 0 or tensor.dtype != np.float32:
        raise TypeError("tensor Must float32 numpy.ndarray")

    tensor = np.ascontiguousarray(tensor)
    t.reference_data(tensor.shape, tensor.ctypes.data, tensor.size * 4, 0, 0)


def reference_torch_tensor(t, tensor):

    lazy_import_torch()
    if tensor is None:
        return None

    if tensor.numel() == 0 or tensor.dtype != torch.float32:
        raise TypeError("Must float32 torch tensor")

    tensor = tensor.contiguous()
    if tensor.is_cuda:
        t.reference_data(tensor.shape, 0, 0, tensor.data_ptr(), tensor.numel() * 4)
    else:
        t.reference_data(tensor.shape, tensor.data_ptr(), tensor.numel() * 4, 0, 0)

def reference_tensor(t, tensor):

    if isinstance(tensor, np.ndarray):
        return reference_numpy_tensor(t, tensor)
    else:
        return reference_torch_tensor(t, tensor)


def infer_torch__call__(self : Infer, *args):

    lazy_import_torch()
    templ  = args[0]
    stream = torch.cuda.current_stream().cuda_stream

    for index, x in enumerate(args):
        self.input(index).stream = stream
        reference_tensor(self.input(index), x)

    batch   = templ.size(0)
    device  = templ.device
    outputs = []
    for index in range(self.num_output):
        out_shape = self.output(index).shape
        out_shape[0] = batch

        if templ.is_cuda:
            out_tensor = torch.empty(out_shape, dtype=torch.float32, device=device)
        else:
            out_tensor = torch.empty(out_shape, dtype=torch.float32, device=device, pin_memory=True)
        self.output(index).stream = stream
        reference_tensor(self.output(index), out_tensor)
        outputs.append(out_tensor)

    self.forward(False)

    if not templ.is_cuda:
        for index in range(self.num_output):
            self.output(index).to_cpu()

    for index, x in enumerate(args):
        self.input(index).clean_reference()

    for index in range(self.num_output):
        self.output(index).clean_reference()

    if len(outputs) == 1:
        return outputs[0]

    return tuple(outputs)


def infer_numpy__call__(self : Infer, *args):

    templ = args[0]
    batch = templ.shape[0]
    assert batch <= self.max_batch_size, "Batch must be less max_batch_size"

    for index, x in enumerate(args):
        reference_tensor(self.input(index), x)

    self.forward(False)

    for index, x in enumerate(args):
        self.input(index).clean_reference()

    outputs = []
    for index in range(self.num_output):
        outputs.append(self.output(index).numpy)

    if len(outputs) == 1:
        return outputs[0]

    return tuple(outputs)


def infer__call__(self : Infer, *args):
    
    templ = args[0]
    if isinstance(templ, np.ndarray):
        return infer_numpy__call__(self, *args)
    else:
        return infer_torch__call__(self, *args)

def infer_save(self : Infer, file):

    with open(file, "wb") as f:
        f.write(self.serial_engine())

Infer.__call__ = infer__call__
Infer.save     = infer_save

def normalize_numpy(norm : Norm, image):

    if norm.channel_type == ChannelType.Invert:
        image = image[..., ::-1]

    if image != np.float32:
        image = image.astype(np.float32)

    if norm.type == NormType.MeanStd:
        mean = np.array(norm.mean, dtype=np.float32)
        std = np.array(norm.std, dtype=np.float32)
        alpha = norm.alpha
        out = (image * alpha - mean) / std
    elif norm.type == NormType.AlphaBeta:
        out = image * norm.alpha + norm.beta
    else:
        out = image
    return np.expand_dims(out.transpose(2, 0, 1), 0)


def normalize_torch(norm : Norm, image):

    lazy_import_torch()
    if norm.channel_type == ChannelType.Invert:
        image = image[..., [2, 1, 0]]

    if image != torch.float32:
        image = image.float()

    if norm.type == NormType.MeanStd:
        mean = torch.tensor(norm.mean, dtype=torch.float32, device=image.device)
        std = torch.tensor(norm.std, dtype=torch.float32, device=image.device)
        alpha = norm.alpha
        out = (image * alpha - mean) / std
    elif norm.type == NormType.AlphaBeta:
        out = image * norm.alpha + norm.beta
    else:
        out = image
    return out.permute(2, 0, 1).unsqueeze(0)


def normalize(norm : Norm, image):
    if isinstance(image, np.ndarray):
        return normalize_numpy(norm, image)
    else:
        return normalize_torch(norm, image)


class MemoryData(object):

    def __init__(self):
        self.data = None

    def write(self, data):
        if self.data is None:
            self.data = data
        else:
            self.data += data

    def flush(self):
        pass


def compile_onnx_to_file(
    max_batch_size               : int,
    file                         : str,
    saveto                       : str,
    mode                         : Mode        = Mode.FP32,
    inputs_dims                  : np.ndarray  = np.array([], dtype=int),
    device_id                    : int         = 0,
    int8_norm                    : Norm        = Norm.none(),
    int8_preprocess_const_value  : int = 114,
    int8_image_directory         : str = ".",
    int8_entropy_calibrator_file : str = "",
    max_workspace_size           : int = 1 << 30
)->bool:
    return compileTRT(
        max_batch_size               = max_batch_size,
        source                       = ModelSource.from_onnx(file),
        output                       = CompileOutput.to_file(saveto),
        mode                         = mode,
        inputs_dims                  = inputs_dims,
        device_id                    = device_id,
        int8_norm                    = int8_norm,
        int8_preprocess_const_value  = int8_preprocess_const_value,
        int8_image_directory         = int8_image_directory,
        int8_entropy_calibrator_file = int8_entropy_calibrator_file,
        max_workspace_size           = max_workspace_size
    )

def compile_onnxdata_to_memory(
    max_batch_size               : int,
    data                         : bytes,
    mode                         : Mode        = Mode.FP32,
    inputs_dims                  : np.ndarray  = np.array([], dtype=int),
    device_id                    : int         = 0,
    int8_norm                    : Norm        = Norm.none(),
    int8_preprocess_const_value  : int = 114,
    int8_image_directory         : str = ".",
    int8_entropy_calibrator_file : str = "",
    max_workspace_size           : int = 1 << 30
)->bytes:
    mem     = CompileOutput.to_memory()
    success = compileTRT(
        max_batch_size               = max_batch_size,
        source                       = ModelSource.from_onnx_data(data),
        output                       = mem,
        mode                         = mode,
        inputs_dims                  = inputs_dims,
        device_id                    = device_id,
        int8_norm                    = int8_norm,
        int8_preprocess_const_value  = int8_preprocess_const_value,
        int8_image_directory         = int8_image_directory,
        int8_entropy_calibrator_file = int8_entropy_calibrator_file,
        max_workspace_size           = max_workspace_size
    )

    if not success:
        return None

    return mem.data


def from_torch(torch_model, input, 
    max_batch_size               : int         = None,
    mode                         : Mode        = Mode.FP32,
    inputs_dims                  : np.ndarray  = np.array([], dtype=int),
    device_id                    : int         = 0,
    input_names                  : List[str]   = None,
    output_names                 : List[str]   = None,
    dynamic                      : bool        = True,
    opset                        : int         = 11,
    onnx_save_file               : str         = None,
    engine_save_file             : str         = None,
    int8_norm                    : Norm        = Norm.none(),
    int8_preprocess_const_value  : int = 114,
    int8_image_directory         : str = ".",
    int8_entropy_calibrator_file : str = "",
    max_workspace_size           : int = 1 << 30
)->Infer:

    lazy_import_torch()
    if isinstance(input, torch.Tensor):
        input = (input,)

    assert isinstance(input, tuple) or isinstance(input, list), "Input must tuple or list"
    input = tuple(input)
    torch_model.eval()

    if max_batch_size is None:
        max_batch_size = input[0].size(0)

    if input_names is None:
        input_names = []
        for i in range(len(input)):
            input_names.append(f"input.{i}")

    if output_names is None:
        output_names = []
        with torch.no_grad():
            dummys_output = torch_model(*input)

        def count_output(output):
            if isinstance(output, torch.Tensor):
                return 1

            if isinstance(output, tuple) or isinstance(output, list):
                count = 0
                for item in output:
                    count += count_output(item)
                return count
            return 0

        num_output = count_output(dummys_output)
        for i in range(num_output):
            output_names.append(f"output.{i}")
    
    dynamic_batch = {}
    for name in input_names + output_names:
        dynamic_batch[name] = {0: "batch"}

    onnx_data  = MemoryData()
    torch.onnx.export(torch_model, 
        input, 
        onnx_data, 
        opset_version=opset, 
        enable_onnx_checker=False, 
        input_names=input_names, 
        output_names=output_names,
        dynamic_axes=dynamic_batch if dynamic else None
    )

    if onnx_save_file is not None:
        with open(onnx_save_file, "wb") as f:
            f.write(onnx_data.data)

    model_data = compile_onnxdata_to_memory(
        max_batch_size = max_batch_size, 
        data           = onnx_data.data, 
        mode           = mode, 
        inputs_dims    = inputs_dims,
        device_id      = device_id,
        int8_norm      = int8_norm,
        int8_preprocess_const_value  = int8_preprocess_const_value,
        int8_image_directory         = int8_image_directory,
        int8_entropy_calibrator_file = int8_entropy_calibrator_file,
        max_workspace_size           = max_workspace_size
    )

    if engine_save_file is not None:
        with open(engine_save_file, "wb") as f:
            f.write(model_data)

    trt_model    = load_infer_data(model_data)
    torch_stream = torch.cuda.current_stream().cuda_stream
    
    if torch_stream != 0:
        trt_model.stream = torch_stream
        
    return trt_model

def upbound(value, align=32):
    return (value + align - 1) // align * align

def load(file_or_data)->Infer:

    if isinstance(file_or_data, str):
        return load_infer_file(file_or_data)
    else:
        return load_infer_data(file_or_data)

YOLOV5_NORM    = Norm.alpha_beta(1 / 255.0, 0.0, ChannelType.Invert)