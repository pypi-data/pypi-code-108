flatfield_modes = {
    "true": True,
    "1": True,
    "false": False,
    "0": False,
    "forced": "force-load",
    "force-load": "force-load",
    "force-compute": "force-compute",
}

phase_retrieval_methods = {
    "": None,
    "none": None,
    "paganin": "paganin",
    "tie": "paganin",
    "ctf": "CTF",
}

unsharp_methods = {
    "gaussian": "gaussian",
    "log": "log",
    "laplacian": "log",
    "none": None,
    "": None,
}

padding_modes = {
    "edges": "edge",
    "edge": "edge",
    "mirror": "mirror",
    "zeros": "zeros",
    "zero": "zeros",
}

reconstruction_methods = {
    "fbp": "FBP",
    "none": None,
    "": None
}

fbp_filters = {
    "ramlak": "ramlak",
    "ram-lak": "ramlak",
    "none": None,
    "": None,
}

iterative_methods = {
    "tv": "TV",
    "wavelets": "wavelets",
    "l2": "L2",
    "ls": "L2",
    "sirt": "SIRT",
    "em": "EM",
}

optim_algorithms = {
    "chambolle": "chambolle-pock",
    "chambollepock": "chambolle-pock",
    "fista": "fista",
}

files_formats = {
    "h5": "hdf5",
    "hdf5": "hdf5",
    "nexus": "hdf5",
    "nx": "hdf5",
    "npy": "npy",
    "npz": "npz",
    "tif": "tiff",
    "tiff": "tiff",
    "jp2": "jp2",
    "jp2k": "jp2",
    "j2k": "jp2",
    "jpeg2000": "jp2",
    "edf": "edf",
}

distribution_methods = {
    "local": "local",
    "slurm": "slurm",
    "": "local",
    "preview": "preview",
}

log_levels = {
    "0": "error",
    "1": "warning",
    "2": "info",
    "3": "debug",
}

sino_normalizations = {
    "none": None,
    "": None,
    "chebyshev": "chebyshev",
}

cor_methods = {
    "auto": "centered",
    "centered": "centered",
    "global": "global",
    "sliding-window": "sliding-window",
    "sliding window": "sliding-window",
    "growing-window": "growing-window",
    "growing window": "growing-window",
    "sino-coarse-to-fine": "sino-coarse-to-fine",
    "composite-coarse-to-fine": "composite-coarse-to-fine",
}

tilt_methods = {
    "1d-correlation": "1d-correlation",
    "1dcorrelation": "1d-correlation",
    "polarfft": "fft-polar",
    "polar-fft": "fft-polar",
    "fft-polar": "fft-polar",
}

rings_methods = {
    "none": None,
    "": None,
    "munch": "munch",
}

radios_rotation_mode = {
    "none": None,
    "": None,
    "chunk": "chunk",
    "chunks": "chunk",
    "full": "full",
}
