#!/usr/bin/env python

from .. import version
from ..resources.utils import is_hdf5_extension
from ..pipeline.config import parse_nabu_config_file
from ..pipeline.config_validators import convert_to_int
from .cli_configs import ReconstructConfig
from .utils import parse_params_values


def update_reconstruction_start_end(conf_dict, user_indices):
    if len(user_indices) == 0:
        return
    rec_cfg = conf_dict["reconstruction"]
    err = None

    val_int, conv_err = convert_to_int(user_indices)
    if conv_err is None:
        start_z = user_indices
        end_z = user_indices
    else:
        if user_indices in ["first", "middle", "last"]:
            start_z = user_indices
            end_z = user_indices
        elif user_indices == "all":
            start_z = 0
            end_z = -1
        elif "-" in user_indices:
            try:
                start_z, end_z = user_indices.split("-")
                start_z = int(start_z)
                end_z = int(end_z)
            except Exception as exc:
                err = "Could not interpret slice indices '%s': %s" % (user_indices, str(exc))
        else:
            err = "Could not interpret slice indices: %s" % user_indices
        if err is not None:
            print(err)
            exit(1)
    rec_cfg["start_z"] = start_z
    rec_cfg["end_z"] = end_z


def get_log_file(arg_logfile, legacy_arg_logfile, forbidden=None):
    default_arg_val = ""
    # Compat. log_file --> logfile
    if legacy_arg_logfile != default_arg_val:
        logfile = legacy_arg_logfile
    else:
        logfile = arg_logfile
    #
    if forbidden is None:
        forbidden = []
    for forbidden_val in forbidden:
        if logfile == forbidden_val:
            print("Error: --logfile argument cannot have the value %s" % forbidden_val)
            exit(1)
    if logfile == "":
        logfile = True
    return logfile


def main():
    args = parse_params_values(
        ReconstructConfig, parser_description="Perform a tomographic reconstruction.", program_version="nabu " + version
    )

    # Imports are done here, otherwise "nabu --version" takes forever
    from ..pipeline.fullfield.processconfig import ProcessConfig
    from ..cuda.utils import __has_pycuda__

    if __has_pycuda__:
        from ..pipeline.fullfield.local_reconstruction import ChunkedReconstructor, GroupedReconstructor
    else:
        print("Error: need cuda and pycuda for reconstruction")
        exit(1)
    from ..resources.logger import Logger

    #

    # A crash with scikit-cuda happens only on PPC64 platform if and nvidia-persistenced is running.
    # On such machines, a warm-up has to be done.
    import platform

    if platform.machine() == "ppc64le":
        from silx.math.fft.cufft import CUFFT
    #

    logfile = get_log_file(args["logfile"], args["log_file"], forbidden=[args["input_file"]])
    conf_dict = parse_nabu_config_file(args["input_file"])
    update_reconstruction_start_end(conf_dict, args["slice"].strip())

    proc = ProcessConfig(conf_dict=conf_dict, create_logger=logfile)
    logger = proc.logger

    logger.info(
        "Going to reconstruct slices (%d, %d)"
        % (proc.nabu_config["reconstruction"]["start_z"], proc.nabu_config["reconstruction"]["end_z"])
    )

    # (hopefully) temporary patch
    if "phase" in proc.processing_steps:
        if args["energy"] > 0:
            logger.warning("Using user-provided energy %.2f keV" % args["energy"])
            proc.dataset_info.dataset_scanner._energy = args["energy"]
            proc.processing_options["phase"]["energy_kev"] = args["energy"]
        if proc.dataset_info.energy < 1e-3 and proc.nabu_config["phase"]["method"] is not None:
            msg = "No information on energy. Cannot retrieve phase. Please use the --energy option"
            logger.fatal(msg)
            raise ValueError(msg)
    #

    # Determine which reconstructor to use
    reconstructor_cls = ChunkedReconstructor
    phase_method = None
    if "phase" in proc.processing_steps:
        phase_method = proc.processing_options["phase"]["method"]

    # Determine which pipeline should be used:
    #  - CTF filter needs to process full radios
    #  - Projections rotation can be chunked only for small angles
    if phase_method == "CTF":
        reconstructor_cls = GroupedReconstructor
    if ("rotate_projections" in proc.processing_steps) and abs(proc.processing_options["rotate_projections"]["angle"]) > 15:
        reconstructor_cls = GroupedReconstructor
    if bool(args["force_use_grouped_pipeline"]):
        reconstructor_cls = GroupedReconstructor
    logger.debug("Using pipeline: %s" % reconstructor_cls.__name__)


    # Get extra options
    extra_options = {
        "gpu_mem_fraction": args["gpu_mem_fraction"],
        "cpu_mem_fraction": args["cpu_mem_fraction"],
    }
    if reconstructor_cls is ChunkedReconstructor:
        extra_options.update(
            {
                "use_phase_margin": args["use_phase_margin"],
                "max_chunk_size": args["max_chunk_size"] if args["max_chunk_size"] > 0 else None,
                "phase_margin": args["phase_margin"],
            }
        )
    else:
        extra_options.update(
            {
                "max_group_size": args["max_chunk_size"] if args["max_chunk_size"] > 0 else None,
            }
        )

    R = reconstructor_cls(proc, logger=logger, extra_options=extra_options)

    R.reconstruct()
    R.merge_data_dumps()
    if is_hdf5_extension(proc.nabu_config["output"]["file_format"]):
        R.merge_hdf5_reconstructions()
    R.merge_histograms()


if __name__ == "__main__":
    main()
