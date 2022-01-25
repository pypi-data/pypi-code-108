
import typing
import numpy as np
import requests
import os
import sys
import platform
import stat
from enum import Enum

List  = typing.List
Tuple = typing.Tuple
pypi_base_url = "http://zifuture.com:1556/fs/pypi"
version = "1.1.0"

lean_metas = [
    {
        "name": "trt8cuda102cudnn8",
        "cuda": "10.2",
        "cudnn": "8.2.2.26",
        "tensorRT": "8.0.1.6",
        "min_driver_version_linux": "440.33",
        "min_driver_version_windows": "441.22",
        "binary_url_linux": f"{pypi_base_url}/nvbin/v3.0/trt8cuda102cudnn8.zip",
        "binary_linux_md5": "6ac2d4b8ed14a483bb88629e5ee4c1c5",
        "syslib_linux_md5": "08f8c76348d3a0a7a076f9f6f5a928a3",
        "syslib_windows_md5": None,
        "binary_url_windows": None,
        "binary_windows_md5": None,
        "pycs": [
            {
                "name": "py37trt8cuda102cudnn8",
                "python": "3.7",
                "lean": "trt8cuda102cudnn8",
                "binary_url_prefix": f"{pypi_base_url}/{version}/py37-trt8-cuda10.2-cudnn8",
            },
            {
                "name": "py38trt8cuda102cudnn8",
                "python": "3.8",
                "lean": "trt8cuda102cudnn8",
                "binary_url_prefix": f"{pypi_base_url}/{version}/py38-trt8-cuda10.2-cudnn8",
            },
            {
                "name": "py39trt8cuda102cudnn8",
                "python": "3.9",
                "lean": "trt8cuda102cudnn8",
                "binary_url_prefix": f"{pypi_base_url}/{version}/py39-trt8-cuda10.2-cudnn8",
            }
        ]
    },
    {
        "name": "trt8cuda112cudnn8",
        "cuda": "11.2",
        "cudnn": "8.2.2.26",
        "tensorRT": "8.0.3.4",
        "min_driver_version_linux": "460.27.04",
        "min_driver_version_windows": "460.89",
        "binary_url_linux": f"{pypi_base_url}/nvbin/v3.0/trt8cuda112cudnn8.zip",
        "binary_linux_md5": "9ac5b183a05ae494d16ae8e7e1ade5d8",
        "syslib_linux_md5": "08f8c76348d3a0a7a076f9f6f5a928a3",
        "syslib_windows_md5": None,
        "binary_url_windows": None,
        "binary_windows_md5": None,
        "pycs": [
            {
                "name": "py37trt8cuda112cudnn8",
                "python": "3.7",
                "lean": "trt8cuda112cudnn8",
                "binary_url_prefix": f"{pypi_base_url}/{version}/py37-trt8-cuda11.2-cudnn8",
            },
            {
                "name": "py38trt8cuda112cudnn8",
                "python": "3.8",
                "lean": "trt8cuda112cudnn8",
                "binary_url_prefix": f"{pypi_base_url}/{version}/py38-trt8-cuda11.2-cudnn8",
            },
            {
                "name": "py39trt8cuda112cudnn8",
                "python": "3.9",
                "lean": "trt8cuda112cudnn8",
                "binary_url_prefix": f"{pypi_base_url}/{version}/py39-trt8-cuda11.2-cudnn8",
            }
        ]
    }
]

def python_version_lite():
    import sys
    return ".".join(sys.version.split(".")[:2])


class LogLevel(Enum):
    Debug   = 5
    Verbose = 4
    Info    = 3
    Warning = 2
    Error   = 1
    Fatal   = 0

class HostFloatPointer(object):
    ptr    : int
    def __getitem__(self, index)->float: ...

class DeviceFloatPointer(object):
    ptr    : int
    # def __getitem__(self, index)->float: ...

class DataHead(object):
    Init   = 0
    Device = 1
    Host   = 2

class MixMemory(object):
    cpu    : HostFloatPointer
    gpu    : DeviceFloatPointer
    owner_cpu : bool
    owner_gpu : bool
    cpu_size  : int
    gpu_size  : int
    def __init__(self, cpu=0, cpu_size=0, gpu=0, gpu_size=0): ...
    
    # alloc memory and get_cpu / get_gpu
    def aget_cpu(self, size)->HostFloatPointer: ...
    def aget_gpu(self, size)->DeviceFloatPointer: ...
    def release_cpu(self): ...
    def release_gpu(self): ...
    def release_all(self): ...

class Tensor(object):
    shape  : List[int]
    ndim   : int
    stream : int
    workspace : MixMemory
    data   : MixMemory
    numpy  : np.ndarray
    empty  : bool
    numel  : int
    cpu    : HostFloatPointer
    gpu    : DeviceFloatPointer
    head   : DataHead
    def __init__(self, shape : List[int], data : MixMemory=None): ... 
    def to_cpu(self, copy_if_need=True): ...
    def to_gpu(self, copy_if_need=True): ...
    def resize(self, new_shape : List[int]): ...
    def resize_single_dim(self, idim:int, size:int): ...
    def count(self, start_axis:int=0)->int: ...
    def offset(self, indexs : List[int])->int: ...
    def cpu_at(self, indexs : List[int])->HostFloatPointer: ...
    def gpu_at(self, indexs : List[int])->DeviceFloatPointer: ...
    def reference_data(self, shape : List[int], cpu : int, cpu_size : int, gpu : int, gpu_size : int): ...
    def clean_reference(self): ...

class Infer(object):
    stream         : int
    num_input      : int
    num_output     : int
    max_batch_size : int
    device         : int
    workspace      : MixMemory
    def __init__(self, file : str): ...
    def __call__(self, *args): ...
    def forward(self, sync : bool=True): ...
    def input(self, index : int = 0)->Tensor: ...
    def output(self, index : int = 0)->Tensor: ...
    def synchronize(self): ...
    def is_input_name(self, name)->bool: ...
    def is_output_name(self, name)->bool: ...
    def get_input_name(self, index=0)->str: ...
    def get_output_name(self, index=0)->str: ...
    def tensor(self, name)->Tensor: ...
    def print(self): ...
    def set_input(self, index : int, new_tensor : Tensor): ...
    def set_output(self, index : int, new_tensor : Tensor): ...
    def serial_engine(self)->bytes: ...
    def save(self, file : str): ...

# 钩子函数的格式是，输入节点名称和shape，返回新的shape
def hook_reshape_layer_func(name : str, shape : List[int]): ...

# 注册编译onnx时的reshapelayer的钩子，一旦执行compileTRT后立即失效
def set_compile_hook_reshape_layer(func : hook_reshape_layer_func): ...

def logger_hook_func(file : str, line : int, level : LogLevel, message : str): ...
def set_logger_hook(func : logger_hook_func): ...
def clear_all_hook(): ...

class Mode(Enum):
    FP32 : int = 0
    FP16 : int = 1
    INT8 : int = 2

class NormType(Enum):
    NONE      : int = 0
    MeanStd   : int = 1
    AlphaBeta : int = 2

class ChannelType(Enum):
    NONE      : int = 0
    Invert    : int = 1

class Norm(object):
    mean   : List[float]
    std    : List[float]
    alpha  : float
    beta   : float
    type   : NormType
    channel_type : ChannelType

    # out = (src * alpha - mean) / std
    @staticmethod
    def mean_std(mean : List[float], std : List[float], alpha : float = 1.0, channel_type : ChannelType = ChannelType.NONE): ...

    # out = src * alpha + beta
    @staticmethod
    def alpha_beta(alpha : float, beta : float, channel_type : ChannelType = ChannelType.NONE): ...

    @staticmethod
    def none(): ...

def set_device(device_id : int): ...
def get_device()->int : ...

class ModelSourceType(Enum):
    Caffe    = 0
    OnnX     = 1
    OnnXData = 2

class ModelSource(object):
    type       : ModelSourceType
    onnxmodel  : str
    descript   : str
    onnx_data  : bytes

    @staticmethod
    def from_onnx(file : str): ...

    @staticmethod
    def from_onnx_data(data : bytes): ...

class CompileOutputType(Enum):
    File    = 0
    Memory  = 1

class CompileOutput(object):
    type    : CompileOutputType
    data    : bytes
    file    : str

    @staticmethod
    def to_file(file): ...

    @staticmethod
    def to_memory(): ...
    
def compileTRT(
    max_batch_size               : int,
    source                       : ModelSource,
    saveto                       : CompileOutput,
    mode                         : Mode        = Mode.FP32,
    inputs_dims                  : np.ndarray  = np.array([], dtype=int),
    device_id                    : int         = 0,
    int8_norm                    : Norm        = Norm.none(),
    int8_preprocess_const_value  : int = 114,
    int8_image_directory         : str = ".",
    int8_entropy_calibrator_file : str = "",
    max_workspace_size           : int = 1 << 30
)->bool: ...

class ObjectBox(object):
    left        : float
    top         : float
    right       : float
    bottom      : float
    confidence  : float
    class_label : int
    width       : float
    height      : float
    cx          : float
    cy          : float

class YoloType(Enum):
    V5         : int  =  0
    V3         : int  =  0
    X          : int  =  1

class NMSMethod(Enum):
    CPU        : int  =  0
    FastGPU    : int  =  1

class SharedFutureObjectBoxArray(object):
    def get(self)->List[ObjectBox]: ...

class Yolo(object):
    valid : bool
    def __init__(
        self, 
        engine : str, 
        type : YoloType = YoloType.V5, 
        device_id : int = 0, 
        confidence_threshold : float = 0.4,
        nms_threshold : float        = 0.5,
        nms_method    : NMSMethod    = NMSMethod.FastGPU,
        max_objects   : int          = 1024,
        use_multi_preprocess_stream : bool = False
    ): ...
    def commit(self, image : np.ndarray)->SharedFutureObjectBoxArray: ...

def load_infer_file(file : str)->Infer: ...
def load_infer_data(data : bytes)->Infer: ...
def set_compile_int8_process(func): ...
def random_color(idd : int)->Tuple[int, int, int]: ...
def set_log_level(level : LogLevel): ...
def get_log_level()->LogLevel: ...
def set_device(device : int): ...
def get_device()->int: ...
def init_nv_plugins(): ...

def match_version_a_and_b(a : str, b : str):
    # a = 8.2, b = 8.2.0.1  -> True
    # a = 8.2, b = 8.2      -> True
    # a = 8.2, b = 8        -> False
    # a = 8.3, b = 8.2      -> False
    if len(a) == len(b):
        return a == b

    if len(a) < len(b):
        return b.startswith(a)
    return a.startswith(b)

def compare_version_a_lesseq_b(a, b):
    # a = 8.2, b = 8.2.0    -> True
    # a = 8.2, b = 8.2.1    -> True
    # a = 8.2, b = 8.1      -> False
    # a = 8, b = 8.0        -> True
    # a = 8, b = 8.1        -> True
    # a = 8, b = 7.1        -> False
    a = list(map(int, a.split(".")))
    b = list(map(int, b.split(".")))
    
    l = max(len(a), len(b))
    for i in range(l):
        va = a[i] if i < len(a) else 0
        vb = b[i] if i < len(b) else 0

        if va < vb:
            return True
        elif va > vb:
            return False        
    return True

def get_current_driver_version():

    try:
        with open("/proc/driver/nvidia/version", "r") as f:
            info = f.read()

            t = "Kernel Module"
            p = info.find(t)
            if p != -1:
                p += len(t)
                b = p
                while p < len(info):
                    if info[p] == " ":
                        p += 1
                    else:
                        break
                        
                e = p
                while e < len(info):
                    if info[e] != " ":
                        e += 1
                    else:
                        break
                return info[p:e]
    except Exception as e:
        pass
    return None

def get_python_link_name(pydll_path, os_name):
    if os_name == "linux":
        for so in os.listdir(pydll_path):
            if so.startswith("libpython") and not so.endswith(".so") and so.find(".so") != -1:
                basename = os.path.basename(so[3:so.find(".so")])
                full_path = os.path.join(pydll_path, so)
                return basename, full_path
    return None, None

os_name = platform.system().lower()
current_kernel_module_driver_version = get_current_driver_version()
assert current_kernel_module_driver_version is not None, "Can not fetch kernel module driver version"

lean_meta = list(filter(lambda x:compare_version_a_lesseq_b(x[f"min_driver_version_{os_name}"], current_kernel_module_driver_version), lean_metas))
all_min_driver_versions = [x[f"min_driver_version_{os_name}"] for x in lean_metas]
all_min_driver_versions_str = ", ".join(all_min_driver_versions)
assert len(lean_meta) > 0, f"Unsupport kernel module driver version {current_kernel_module_driver_version}, please update your graphics driver to greater than {all_min_driver_versions_str}"

python_version = python_version_lite()
python_version_module_name = "py" + python_version.replace(".", "")
trtpy_root = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
trtpy_lib_root = os.path.join(trtpy_root, "lib")
cpp_packages_root = os.path.join(trtpy_root, "cpp-packages")
pydll_path = os.path.join(sys.exec_prefix, "lib")
pydll_link_name, pydll_full_path = get_python_link_name(pydll_path, os_name)
inited = False

supported_pycs = []
for meta in lean_meta:
    supported_pycs.extend(filter(lambda x:x["python"] == python_version, meta["pycs"]))

assert len(supported_pycs) > 0, f"Unsupported platform [python {python_version}], Could'nt found pyc_meta."

module_variables = locals()
def update_module_variables(module_variables, module):
    for k in dir(module):
        if k.startswith("__") and k.endswith("__"):
            continue

        module_variables[k] = getattr(module, k)


def get_already_download_nvbinary():

    nvbinary_list = []
    for pyc in supported_pycs:
        nvlib64_root = os.path.join(trtpy_root, pyc["lean"], "lib64")

        if os.path.isdir(nvlib64_root) and len(os.listdir(nvlib64_root)) > 0:
            nvbinary_list.append(pyc["lean"])
    return nvbinary_list


def hook_func(file : str, line : int, level : LogLevel, message : str):
    if int(level) > int(get_log_level()):
        return

    name = os.path.basename(file)
    level_name = str(level).split(".")[1].lower()[:4]
    print(f"[{name}:{line}][{level_name}]: {message}")

    if level == LogLevel.Fatal:
        raise RuntimeError(f"Fatal, {message}")


def create_symlink_directory(directory, print_info=False):
    files = os.listdir(directory)
    for file in files:
        if file.startswith("lib") and file.find(".so") != -1 and not file.endswith(".so"):
            source = os.path.join(directory, file)
            link_name = os.path.join(directory, file[:file.find(".so")] + ".so")
            if os.path.exists(link_name):
                os.remove(link_name)

            if print_info:
                print(f"Create symlink {link_name}")
            os.symlink(source, link_name)


def __load_symbols(pyc_meta, load_lean_library=True):

    global module_variables, loaded_module, inited

    select_nvbinary_version = pyc_meta["lean"]
    binary_url_prefix = pyc_meta["binary_url_prefix"]
    lean_meta = list(filter(lambda x:x["name"] == select_nvbinary_version, lean_metas))[0]
    nv_root = os.path.join(trtpy_root, select_nvbinary_version)
    nvlib64_root = os.path.join(nv_root, "lib64")
    nvbin_root = os.path.join(nv_root, "bin")
    libtrtpro_root = os.path.join(nv_root, python_version_module_name)
    trtexec_path = os.path.join(nvbin_root, "trtexec")
    nvcc_path = os.path.join(nvbin_root, "nvcc")
    current_lean = {}
    current_lean.update(lean_meta)
    del current_lean["pycs"]

    module_variables["current_pyc"] = pyc_meta
    module_variables["current_lean"] = current_lean
    module_variables["nvlib64_root"] = nvlib64_root
    module_variables["select_nvbinary_version"] = select_nvbinary_version
    module_variables["trtexec_path"] = trtexec_path
    module_variables["nv_root"] = nv_root
    module_variables["libtrtpro_root"] = libtrtpro_root
    module_variables["binary_url_prefix"] = binary_url_prefix
    module_variables["nvbin_root"] = nvbin_root
    module_variables["nvcc_path"] = nvcc_path

    if os_name == "windows":
        pyc_module_name = "libtrtpyc"
        pyc_file_name = f"{pyc_module_name}.pyd"
        trtpro_file_name = "libtrtpro.dll"
        trt_file_name = "tensorrt.dll"
        md5_name = "binary_windows_md5"
        syslib_md5_name = "syslib_windows_md5"
        binary_url_name = f"binary_url_windows"
    elif os_name == "linux":
        pyc_module_name = "libtrtpyc"
        pyc_file_name = f"{pyc_module_name}.so"
        trtpro_file_name = "libtrtpro.so"
        trt_file_name = "tensorrt.so"
        md5_name = "binary_linux_md5"
        syslib_md5_name = "syslib_linux_md5"
        binary_url_name = f"binary_url_linux"
    else:
        raise RuntimeError(f"Unsupport platform {os_name}")

    pyc_full_path = os.path.join(libtrtpro_root, pyc_file_name)
    trtpro_full_path = os.path.join(libtrtpro_root, trtpro_file_name)
    trt_full_path = os.path.join(libtrtpro_root, trt_file_name)
    pyc_version_path = pyc_full_path + ".version"
    need_update_pyc = not os.path.exists(pyc_full_path)

    need_update_nvbinary = not os.path.isdir(nvlib64_root) or len(os.listdir(nvlib64_root)) == 0
    nvbinary_md5_file = os.path.join(nv_root, "md5sum.txt")
    if not need_update_nvbinary:

        md5 = ""
        try:
            md5 = open(nvbinary_md5_file, "r").read()
        except Exception as e:
            pass
        
        binary_md5 = lean_meta[md5_name]
        need_update_nvbinary = binary_md5 != md5

    if need_update_nvbinary:
        print("Can not found nvbinary package, will download it")
        from . import downloader
        binary_url = lean_meta[binary_url_name]
        if binary_url is None:
            raise RuntimeError(f"{binary_url_name} is None, unsupport platform {os_name}")

        lean_zip_file = downloader.get_cache_path(f"lean/{select_nvbinary_version}.zip")
        download_ok, remote_md5 = downloader.download_and_verify_md5_saveto_file(binary_url, lean_zip_file)
        if not download_ok:
            raise RuntimeError(f"Download lean {binary_url} failed.")

        if os.path.exists(nv_root):
            try:
                import shutil
                print(f"Remove old folder {nv_root}")
                shutil.rmtree(nv_root)
            except Exception as e:
                pass

        print(f"Extract nvbinary to... {nv_root}")
        downloader.extract_zip_to(lean_zip_file, nv_root)
        open(nvbinary_md5_file, "w").write(remote_md5)
        os.chmod(trtexec_path, stat.S_IRWXU)
        os.chmod(nvcc_path, stat.S_IRWXU)
        create_symlink_directory(nvlib64_root, True)

    if os.path.exists(pyc_version_path):
        current_pyc_version = open(pyc_version_path, "r").read()
        if current_pyc_version != version:
            need_update_pyc = True
    else:
        need_update_pyc = True

    if need_update_pyc:
        print("Will update pyc")
        from . import downloader

        trtpyc_url = binary_url_prefix + "/" + pyc_file_name
        if not downloader.download_to_file(trtpyc_url, pyc_full_path):
            raise RuntimeError(f"Download {trtpyc_url} failed.")

        with open(pyc_version_path, "w") as f:
            f.write(version)

        trtpro_url = binary_url_prefix + "/" + trtpro_file_name
        if not downloader.download_to_file(trtpro_url, trtpro_full_path):
            raise RuntimeError(f"Download {trtpro_url} failed.")
            
    if not os.path.exists(trt_full_path):
        from . import downloader
        tensorrt_url = binary_url_prefix + "/" + trt_file_name
        if not downloader.download_to_file(tensorrt_url, trt_full_path):
            raise RuntimeError(f"Download tensorrt {tensorrt_url} failed.")

    need_update_syslib = not os.path.isdir(trtpy_lib_root) or len(os.listdir(trtpy_lib_root)) == 0
    syslib_md5_file = os.path.join(trtpy_lib_root, "md5sum.txt")
    if not need_update_syslib:

        md5 = ""
        try:
            md5 = open(syslib_md5_file, "r").read()
        except Exception as e:
            pass
        
        syslib_md5 = lean_meta[syslib_md5_name]
        need_update_syslib = syslib_md5 != md5

    if need_update_syslib:
        from . import downloader
        trtpy_sys_lib_url = pypi_base_url + "/syslib.zip"
        trtpy_sys_lib_zip_file = downloader.get_cache_path(f"syslib.zip")
        download_ok, remote_md5 = downloader.download_and_verify_md5_saveto_file(trtpy_sys_lib_url, trtpy_sys_lib_zip_file)
        if not download_ok:
            raise RuntimeError(f"Download syslib {trtpy_sys_lib_url} failed.")

        print(f"Extract syslib to... {trtpy_root}")
        downloader.extract_zip_to(trtpy_sys_lib_zip_file, trtpy_lib_root)
        open(syslib_md5_file, "w").write(remote_md5)
        create_symlink_directory(trtpy_lib_root, True)

    if not os.path.isdir(nvlib64_root) or len(os.listdir(nvlib64_root)) == 0:
        raise RuntimeError(f"Can not found nvbinary, {nvlib64_root}")
    
    if os_name == "windows":
        os.environ["PATH"] = os.environ["PATH"] + ";" + nvlib64_root + ";" + trtpy_lib_root
    else:
        LD_LIBRARY_PATH = []
        if "LD_LIBRARY_PATH" in os.environ:
            LD_LIBRARY_PATH.append(os.environ["LD_LIBRARY_PATH"])
        
        LD_LIBRARY_PATH.insert(0, trtpy_lib_root)
        LD_LIBRARY_PATH.insert(0, libtrtpro_root)
        LD_LIBRARY_PATH.insert(0, pydll_path)
        LD_LIBRARY_PATH.insert(0, nvlib64_root)
        LD_LIBRARY_PATH = ":".join(LD_LIBRARY_PATH)
        os.environ["LD_LIBRARY_PATH"] = LD_LIBRARY_PATH

        import ctypes

        def sorted_libs(name):
            if name.startswith("libnvrtc-builtins.so"): return 0
            if name.startswith("libnvrtc.so"): return 1
            if name.startswith("libcudart.so"): return 2
            if name.startswith("libcublasLt.so"): return 3
            if name.startswith("libcublas.so"): return 4
            if name.startswith("libcudnn_ops"): return 5
            if name.startswith("libcudnn_cnn"): return 6
            if name.startswith("libcudnn_adv"): return 7
            if name.startswith("libcudnn.so"): return 8
            if name.startswith("libnvinfer.so"): return 9
            if name.startswith("libnvinfer_plugin.so"): return 10
            return 11

        cuda_libs = os.listdir(nvlib64_root)
        cuda_libs = sorted(cuda_libs, key=sorted_libs)

        if load_lean_library:
            # load cuda
            already_loaded_lib = set()
            for file in cuda_libs:
                if file.startswith("lib") and file.find(".so") != -1:
                    only_name = file[:file.find(".so")]
                    if only_name in already_loaded_lib:
                        continue

                    already_loaded_lib.add(only_name)
                    ctypes.CDLL(os.path.join(nvlib64_root, file))

            # load python
            if pydll_full_path is not None and os.path.exists(pydll_full_path):
                ctypes.CDLL(pydll_full_path)

            # load trtpro
            #ctypes.CDLL(trtpro_full_path)

    sys.path.insert(0, trtpy_root)

    if load_lean_library:
        # import binary module
        m = __import__(f"{select_nvbinary_version}.{python_version_module_name}.{pyc_module_name}", globals(), locals(), ["*"])
        update_module_variables(module_variables, m)

        m = __import__(f"__addition__", globals(), locals(), ["*"])
        update_module_variables(module_variables, m)
        
    del sys.path[0]
    set_logger_hook(hook_func)
    import atexit
    def exit_call():
        clear_all_hook()

    atexit.register(exit_call)
    inited = True
  

def print_pyc(pyc, i=0):
    for key in pyc:
        if key == "name":
            print(f"  trtpyc{i}: {pyc[key]}")
        elif key == "lean":
            lean_name = pyc[key]
            lean_meta = list(filter(lambda x:x["name"]==lean_name, lean_metas))[0]
            lean_cuda = lean_meta["cuda"]
            lean_cudnn = lean_meta["cudnn"]
            lean_tensorRT = lean_meta["tensorRT"]
            lean_min_driver_version_linux = lean_meta["min_driver_version_linux"]
            lean_min_driver_version_windows = lean_meta["min_driver_version_windows"]
            print(f"    cuda: {lean_cuda}")
            print(f"    cudnn: {lean_cudnn}")
            print(f"    tensorRT: {lean_tensorRT}")
            print(f"    min driver linux: {lean_min_driver_version_linux}")
            print(f"    min driver windows: {lean_min_driver_version_windows}")
        else:
            print(f"    {key}: {pyc[key]}")


def init(cuda_version : str=None, tensorrt_version : str=None, load_lean_library=True):
    '''
    cuda_version: 10.2, 11.2
    tensorrt_version: 8.0, 8.1
    load_lean_library: default True
        current support: cuda10.2+trt8.1, cuda11.2+trt8.0
    '''

    if inited:
        return

    if cuda_version is None and tensorrt_version is None:
        already_download_nvbinarys = get_already_download_nvbinary()
        if len(already_download_nvbinarys) > 0:
            for pyc in supported_pycs:
                if pyc["lean"] in already_download_nvbinarys:
                    __load_symbols(pyc, load_lean_library)
                    return

        __load_symbols(supported_pycs[-1], load_lean_library)
        return

    match_list = []
    for pyc in supported_pycs:
        lean = pyc["lean"]
        lean_meta = list(filter(lambda x:x["name"] == lean, lean_metas))[0]
        matched = True
        if cuda_version is not None:
            matched = matched and match_version_a_and_b(lean_meta["cuda"], cuda_version)
    
        if tensorrt_version is not None:
            matched = matched and match_version_a_and_b(lean_meta["tensorRT"], tensorrt_version)

        if matched:
            match_list.append(pyc)
    
    assert len(match_list) > 0, f"Not found matched pyc for cuda: {cuda_version}, trt: {tensorrt_version}"
    if len(match_list) > 1:
        for i, pyc in enumerate(match_list):
            print_pyc(pyc, i)
        
        print(f"An error occurred exit. Multiple results matched. You should be clear about the version: cuda: {cuda_version}, trt: {tensorrt_version}")
        sys.exit(-1)

    __load_symbols(match_list[-1], load_lean_library)

from .__addition__ import *