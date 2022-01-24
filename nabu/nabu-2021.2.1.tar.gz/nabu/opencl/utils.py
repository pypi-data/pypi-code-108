from numpy import prod
try:
    import pyopencl as cl
    __has_pyopencl__ = True
    __pyopencl_error_msg__ = None
except ImportError as err:
    __has_pyopencl__ = False
    __pyopencl_error_msg__ = str(err)
from ..resources.gpu import GPUDescription


def usable_opencl_devices():
    """
    Test the available OpenCL platforms/devices.

    Returns
    --------
    platforms: dict
        Dictionary where the key is the platform name, and the value is a list
        of `silx.opencl.common.Device` object.
    """
    platforms = {}
    for platform in cl.get_platforms():
        platforms[platform.name] = platform.get_devices()
    return platforms


def detect_opencl_gpus():
    """
    Get the available OpenCL-compatible GPUs.

    Returns
    --------
    gpus: dict
        Nested dictionary where the keys are OpenCL platform names,
        values are dictionary of GPU IDs and `silx.opencl.common.Device` object.
    error_msg: str
        In the case where there is an error, the message is returned in this item.
        Otherwise, it is a None object.
    """
    gpus = {}
    error_msg = None
    if not(__has_pyopencl__):
        return {}, __pyopencl_error_msg__
    try:
        platforms = usable_opencl_devices()
    except Exception as exc:
        error_msg = str(exc)
    if error_msg is not None:
        return {}, error_msg
    for platform_name, devices in platforms.items():
        for d_id, device in enumerate(devices):
            if device.type == cl.device_type.GPU:# and bool(device.available):
                if platform_name not in gpus:
                    gpus[platform_name] = {}
                gpus[platform_name][d_id] = device
    return gpus, None


def collect_opencl_gpus():
    """
    Return a dictionary of platforms and brief description of each OpenCL-compatible
    GPU with a few fields
    """
    gpus, error_msg = detect_opencl_gpus()
    if error_msg is not None:
        return None
    opencl_gpus = {}
    for platform, gpus in gpus.items():
        for gpu_id, gpu in gpus.items():
            if platform not in opencl_gpus:
                opencl_gpus[platform] = {}
            opencl_gpus[platform][gpu_id] = GPUDescription(gpu, device_id=gpu_id).get_dict()
            opencl_gpus[platform][gpu_id]["platform"] = platform
    return opencl_gpus


def collect_opencl_cpus():
    """
    Return a dictionary of platforms and brief description of each OpenCL-compatible
    CPU with a few fields
    """
    opencl_cpus = {}
    platforms = usable_opencl_devices()
    for platform, devices in platforms.items():
        if "cuda" in platform.lower():
            continue
        opencl_cpus[platform] = {}
        for device_id, device in enumerate(devices): # device_id might be inaccurate
            if device.type != cl.device_type.CPU:
                continue
            opencl_cpus[platform][device_id] = GPUDescription(device).get_dict()
            opencl_cpus[platform][device_id]["platform"] = platform
    return opencl_cpus



def create_opencl_context(platform_id, device_id, cleanup_at_exit=True):
    """
    Create an OpenCL context.
    """
    platforms = cl.get_platforms()
    platform = platforms[platform_id]
    devices = platform.get_devices()
    ctx = cl.Context(devices=[devices[device_id]])
    return ctx


def replace_array_memory(arr, new_shape):
    """
    Replace the underlying buffer data of a  `pyopencl.array.Array`.
    This function is dangerous !
    It should merely be used to clear memory, the array should not be used afterwise.
    """
    arr.data.release()
    arr.base_data = cl.Buffer(
        arr.context,
        cl.mem_flags.READ_WRITE,
        prod(new_shape) * arr.dtype.itemsize
    )
    arr.shape = new_shape
    # strides seems to be updated by pyopencl
    return arr



def pick_opencl_cpu_platform(opencl_cpus):
    """
    Pick the best OpenCL implementation for the opencl cpu.
    This function assume that there is only one opencl-enabled CPU on the
    current machine, but there might be several OpenCL implementations/vendors.


    Parameters
    ----------
    opencl_cpus: dict
        Dictionary with the available opencl-enabled CPUs.
        Usually obtained with collect_opencl_cpus().

    Returns
    -------
    cpu: dict
        A dictionary describing the CPU.
    """
    if len(opencl_cpus) == 0:
        raise ValueError("No CPU to pick")
    name2device = {}
    for platform, devices in opencl_cpus.items():
        for device_id, device_desc in devices.items():
            name2device.setdefault(device_desc["name"], [])
            name2device[device_desc["name"]].append(platform)
    if len(name2device) > 1:
        raise ValueError(
            "Expected at most one CPU but got %d: %s"
            % (len(name2device), list(name2device.keys()))
        )
    cpu_name = list(name2device.keys())[0]
    platforms = name2device[cpu_name]
    # Several platforms for the same CPU
    res = opencl_cpus[platforms[0]]
    if len(platforms) > 1:
        if "intel" in cpu_name.lower():
            for platform in platforms:
                if "intel" in platform.lower():
                    res = opencl_cpus[platform]
    #
    return res[list(res.keys())[0]]



