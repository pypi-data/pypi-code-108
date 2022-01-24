#
# Default configuration for CLI tools
#

# Default configuration for "bootstrap" command
BootstrapConfig = {
    "bootstrap": {
        "help": "DEPRECATED, this is the default behavior. Bootstrap a configuration file from scratch.",
        "action": "store_const",
        "const": 1,
    },
    "convert": {
        "help": "UNSUPPORTED. This option has no effect and will disappear. Convert a PyHST configuration file to a nabu configuration file.",
        "default": "",
    },
    "output": {
        "help": "Output filename",
        "default": "nabu.conf",
    },
    "nocomments": {
        "help": "Remove the comments in the configuration file (default: False)",
        "action": "store_const",
        "const": 1,
    },
    "level": {
        "help": "Level of options to embed in the configuration file. Can be 'required', 'optional', 'advanced'.",
        "default": "optional",
    },
    "dataset": {
        "help": "Pre-fill the configuration file with the dataset path.",
        "default": "",
    }
}

# Default configuration for "zsplit" command
ZSplitConfig = {
    "input_file": {
        "help": "Input HDF5-Nexus file",
        "mandatory": True,
    },
    "output_directory": {
        "help": "Output directory to write split files.",
        "mandatory": True,
    },
    "loglevel": {
        "help": "Logging level. Can be 'debug', 'info', 'warning', 'error'. Default is 'info'.",
        "default": "info",
    },
    "entry": {
        "help": "HDF5 entry to take in the input file. By default, the first entry is taken.",
        "default": "",
    },
    "n_stages": {
        "help": "Number of expected stages (i.e different 'Z' values). By default it is inferred from the dataset.",
        "default": -1,
        "type": int,
    },
    "use_virtual_dataset": {
        "help": "Whether to use virtual datasets for output file. Not using a virtual dataset duplicates data and thus results in big files ! However virtual datasets currently have performance issues. Default is False",
        "default": 0,
        "type": int,
    },
}

# Default configuration for "histogram" command
HistogramConfig = {
    "h5_file": {
        "help": "HDF5 file(s). It can be one or several paths to HDF5 files. You can specify entry for each file with /path/to/file.h5?entry0000",
        "mandatory": True,
        "nargs": "+",
    },
    "output_file": {
        "help": "Output file (HDF5)",
        "mandatory": True,
    },
    "bins": {
        "help": "Number of bins for histogram if they have to be computed. Default is one million.",
        "default": 1000000,
        "type": int,
    },
    "chunk_size_slices": {
        "help": "If histogram are computed, specify the maximum subvolume size (in number of slices) for computing histogram.",
        "default": 100,
        "type": int,
    },
    "chunk_size_GB": {
        "help": "If histogram are computed, specify the maximum subvolume size (in GibaBytes) for computing histogram.",
        "default": -1,
        "type": float,
    },
    "loglevel": {
        "help": "Logging level. Can be 'debug', 'info', 'warning', 'error'. Default is 'info'.",
        "default": "info",
    },
}


# Default configuration for "reconstruct" command
ReconstructConfig = {
    "input_file": {
        "help": "Nabu input file",
        "default": "",
        "mandatory": True,
    },
    "logfile": {
        "help": "Log file. Default is dataset_prefix_nabu.log",
        "default": "",
    },
    "log_file": {
        "help": "Same as logfile. Deprecated, use --logfile instead.",
        "default": "",
    },
    "slice": {
        "help": "Slice(s) indice(s) to reconstruct, in the format z1-z2. Default (empty) is the whole volume. This overwrites the configuration file start_z and end_z. You can also use --slice first, --slice last, --slice middle, and --slice all",
        "default": "",
    },
    # ~ "compute": {
        # ~ "help": "Computation distribution method. Can be 'local' or 'slurm'",
        # ~ "default": "local",
    # ~ },
    # ~ "nodes": {
        # ~ "help": "Number of computing nodes to use. Ignored if --compute is set to 'local'.",
        # ~ "default": 1,
        # ~ "type": int,
    # ~ },
    "energy": {
        "help": "Beam energy in keV. DEPRECATED, was used to patch missing fields in BCU HDF5 file.",
        "default": -1,
        "type": float,
    },
    "gpu_mem_fraction": {
        "help": "Which fraction of GPU memory to use. Default is 0.9.",
        "default": 0.9,
        "type": float,
    },
    "cpu_mem_fraction": {
        "help": "Which fraction of memory to use. Default is 0.9.",
        "default": 0.9,
        "type": float,
    },
    "max_chunk_size": {
        "help": "Maximum chunk size to use.",
        "default": -1,
        "type": int,
    },
    "use_phase_margin": {
        "help": "DEPRECATED. Use --phase_margin instead. Whether to use a margin when performing phase retrieval. Defautl is True.",
        "default": True,
        "type": bool,
    },
    "phase_margin": {
        "help": "Specify an explicit phase margin to use when performing phase retrieval.",
        "default": -1,
        "type": int,
    },
    "force_use_grouped_pipeline": {
        "help": "Force nabu to use the 'grouped' reconstruction pipeline - slower but should work for all big datasets.",
        "default": 0,
        "type": int,
    },
}

GenerateInfoConfig = {
    "hist_file": {
        "help": "HDF5 file containing the histogram, either the reconstruction file or a dedicated histogram file.",
        "default": "",
    },
    "hist_entry": {
        "help": "Histogram HDF5 entry. Defaults to the first available entry.",
        "default": "",
    },
    "output": {
        "help": "Output file name",
        "default": "",
        "mandatory": True,
    },
    "bliss_file": {
        "help": "HDF5 master file produced by BLISS",
        "default": "",
    },
    "bliss_entry": {
        "help": "Entry in the HDF5 master file produced by BLISS. By default, take the first entry.",
        "default": "",
    },
    "info_file": {
        "help": "Path to the .info file, in the case of a EDF dataset",
        "default": "",
    },
    "edf_proj": {
        "help": "Path to a projection, in the case of a EDF dataset",
        "default": "",
    },

}

RotateRadiosConfig = {
    "dataset": {
        "help": "Path to the dataset. Only HDF5 format is supported for now.",
        "default": "",
        "mandatory": True,
    },
    "entry": {
        "help": "HDF5 entry. By default, the first entry is taken.",
        "default": "",
    },
    "angle": {
        "help": "Rotation angle in degrees",
        "default": 0.,
        "mandatory": True,
        "type": float,
    },
    "center": {
        "help": "Rotation center, in the form (x, y) where x (resp. y) is the horizontal (resp. vertical) dimension, i.e along the columns (resp. lines). Default is (Nx/2 - 0.5, Ny/2 - 0.5).",
        "default": "",
    },
    "output": {
        "help": "Path to the output file. Only HDF5 output is supported. In the case of HDF5 input, the output file will have the same structure.",
        "default": "",
        "mandatory": True,
    },
    "loglevel": {
        "help": "Logging level. Can be 'debug', 'info', 'warning', 'error'. Default is 'info'.",
        "default": "info",
    },
    "batchsize": {
        "help": "Size of the batch of images to process. Default is 100",
        "default": 100,
        "type": int,
    },
    "use_cuda": {
        "help": "Whether to use Cuda if available",
        "default": "1",
    },
    "use_multiprocessing": {
        "help": "Whether to use multiprocessing if available",
        "default": "1",
    },
}

DFFConfig = {
    "dataset": {
        "help": "Path to the dataset.",
        "default": "",
        "mandatory": True,
    },
    "entry": {
        "help": "HDF5 entry (for HDF5 datasets). By default, the first entry is taken.",
        "default": "",
    },
    "flatfield": {
        "help": "Whether to perform flat-field normalization. Default is True.",
        "default": "1",
        "type": int,
    },
    "sigma": {
        "default": 0.,
        "help": "Enable high-pass filtering on double flatfield with this value of 'sigma'",
        "type": float,
    },
    "output": {
        "help": "Path to the output file (HDF5).",
        "default": "",
        "mandatory": True,
    },
    "loglevel": {
        "help": "Logging level. Can be 'debug', 'info', 'warning', 'error'. Default is 'info'.",
        "default": "info",
    },
    "chunk_size": {
        "help": "Maximum number of lines to read in each projection in a single pass. Default is 100",
        "default": 100,
        "type": int,
    },
}
