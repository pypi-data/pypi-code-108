#!/usr/bin/env python

"""
computations.py: determine computational needs, chunking method to be used, etc.
"""

from silx.image.tomography import get_next_power


def estimate_required_memory(process_config, chunk_size=None, group_size=None, radios_and_sinos=True, warn_from_GB=None):
    """
    Estimate the memory (RAM) needed for a reconstruction.

    Parameters
    -----------
    process_config: `ProcessConfig` object
        Data structure with the processing configuration
    chunk_size: int, optional
        Size of a "radios chunk", i.e "delta z". A radios chunk is a 3D array of shape (n_angles, chunk_size, n_x)
        If set to None, then chunk_size = n_z
    group_size: int, optional
        Size of a "radios group", i.e "num_angles". A radios group is a 3D array of shape (group_size, n_z, n_x)
        If set to None, then group_size = n_angles
    radios_and_sinos: bool
        Whether radios and sinograms will co-exist in memory (meaning more memory usage)
    warn_from_GB: float, optional
        Amount of memory in GB from where a warning flag will be raised.
        Default is None
        If set to a number, the result will be in the form (estimated_memory_GB, warning)
        where 'warning' is a boolean indicating whether memory allocation/transfer might be problematic.

    Notes
    -----
    It seems that Cuda does not allow allocating and/or transferring more than 16384 MiB (17.18 GB).
    If warn_from_GB is not None, then the result is in the form (estimated_memory_GB, warning)
    where warning is a boolean indicating wheher memory allocation/transfer might be problematic.
    """
    dataset = process_config.dataset_info
    nabu_config = process_config.nabu_config
    processing_steps = process_config.processing_steps
    Nx, Ny = dataset.radio_dims
    if chunk_size is not None:
        Ny = chunk_size
    Na = dataset.n_angles
    if group_size is not None:
        Na = group_size

    total_memory_needed = 0
    memory_warning = False

    # Read data
    # ----------
    binning_z = nabu_config["dataset"]["binning_z"]
    projections_subsampling = nabu_config["dataset"]["projections_subsampling"]
    data_volume_size = Nx * Ny * Na * 4
    data_image_size = Nx * Ny * 4
    total_memory_needed += data_volume_size
    if (warn_from_GB is not None) and data_volume_size/1e9 > warn_from_GB:
        memory_warning = True

    # CCD processing
    # ---------------
    if "flatfield" in processing_steps:
        # Flat-field is done in-place, but still need to load darks/flats
        n_darks = len(dataset.darks)
        n_flats = len(dataset.flats)
        darks_size = n_darks * Nx * Ny * 2  # uint16
        flats_size = n_flats * Nx * Ny * 4  # f32
        total_memory_needed += darks_size + flats_size

    if "ccd_correction" in processing_steps:
        # CCD filter is "batched 2D"
        total_memory_needed += data_image_size

    # Phase retrieval
    # ---------------
    if "phase" in processing_steps:
        # Phase retrieval is done image-wise, so near in-place, but needs to
        # allocate some images, fft plans, and so on
        Nx_p = get_next_power(2 * Nx)
        Ny_p = get_next_power(2 * Ny)
        img_size_real = 2 * 4 * Nx_p * Ny_p
        img_size_cplx = 2 * 8 * ((Nx_p * Ny_p) // 2 + 1)
        total_memory_needed += 2 * img_size_real + 3 * img_size_cplx

    # Sinogram de-ringing
    # -------------------
    if "sino_rings_correction" in processing_steps:
        # Process is done image-wise.
        # Needs one Discrete Wavelets transform and one FFT/IFFT plan for each scale
        total_memory_needed += (Nx * Na * 4) * 5.5  # approx.


    # Reconstruction
    # ---------------
    reconstructed_volume_size = 0
    if "reconstruction" in processing_steps:
        if radios_and_sinos:
            total_memory_needed += data_volume_size  # radios + sinos
        rec_config = process_config.processing_options["reconstruction"]
        if "rotation_axis_position_halftomo" in rec_config:
            # Slice has a different shape in half acquisition.
            rc = rec_config["rotation_axis_position_halftomo"]
            Nx_rec = 2 * rc
            Nx_rec = max(2 * rc, 2 * (Nx - rc))
            Ny_rec = Nx_rec
        else:
            Nx_rec = (rec_config["end_x"] - rec_config["start_x"] + 1)
            Ny_rec = (rec_config["end_y"] - rec_config["start_y"] + 1)
        Nz_rec = (rec_config["end_z"] - rec_config["start_z"] + 1) // binning_z
        if chunk_size:
            Nz_rec = chunk_size // binning_z
        reconstructed_volume_size = Nx_rec * Ny_rec * Nz_rec * 4  # float32
        total_memory_needed += reconstructed_volume_size

    if warn_from_GB is None:
        return total_memory_needed
    else:
        return (total_memory_needed, memory_warning)



def estimate_chunk_size(available_memory_GB, process_config, chunk_step=50, warn_from_GB=None):
    """
    Estimate the maximum chunk size given an avaiable amount of memory.

    Parameters
    -----------
    available_memory_GB: float
        available memory in Giga Bytes (GB - not GiB !).
    process_config: ProcessConfig
        ProcessConfig object
    """
    chunk_size = chunk_step
    radios_and_sinos = False
    if (
        "reconstruction" in process_config.processing_steps
        and process_config.processing_options["reconstruction"]["enable_halftomo"]
    ):
        radios_and_sinos = True

    max_dz = process_config.dataset_info.radio_dims[1]
    chunk_size = chunk_step
    last_good_chunk_size = chunk_size
    while True:
        res = estimate_required_memory(
            process_config,
            chunk_size=chunk_size,
            radios_and_sinos=radios_and_sinos,
            warn_from_GB=warn_from_GB # 2**32 elements - see estimate_required_memory docstring note
        )
        if warn_from_GB is not None:
            (required_mem, mem_warn) = res
        else:
            (required_mem, mem_warn) = res, False
        required_mem_GB = required_mem / 1e9
        if required_mem_GB > available_memory_GB or chunk_size > max_dz or mem_warn:
            break
        last_good_chunk_size = chunk_size
        chunk_size += chunk_step
    return last_good_chunk_size


def estimate_group_size(available_memory_GB, process_config, step=50, warn_from_GB=None):
    """
    Same as estimate_chunk_size, but for radios group
    """

    def _remove_sino_processing_steps(processing_steps):
        sino_steps = ["sino_rings_correction", "reconstruction"]
        removed_sino_steps = {}
        for step in sino_steps:
            if step in processing_steps:
                idx = processing_steps.index(step)
                removed_sino_steps[idx] = processing_steps.pop(idx)
        return removed_sino_steps

    def _restore_sino_processing_steps(processing_steps, removed_sino_steps):
        for idx, val in removed_sino_steps.items():
            processing_steps.insert(idx, val)

    removed_sino_steps = _remove_sino_processing_steps(process_config.processing_steps)

    group_size = step
    n_angles = process_config.dataset_info.n_angles
    last_good_group_size = group_size
    while True:
        res = estimate_required_memory(
            process_config,
            group_size=group_size,
            radios_and_sinos=False,
            warn_from_GB=warn_from_GB # 2**32 elements - see estimate_required_memory docstring note
        )
        if warn_from_GB is not None:
            (required_mem, mem_warn) = res
        else:
            (required_mem, mem_warn) = res, False
        required_mem_GB = required_mem / 1e9
        if required_mem_GB > available_memory_GB or group_size > n_angles or mem_warn:
            break
        last_good_group_size = group_size
        group_size += step
    _restore_sino_processing_steps(process_config.processing_steps, removed_sino_steps)
    return last_good_group_size

