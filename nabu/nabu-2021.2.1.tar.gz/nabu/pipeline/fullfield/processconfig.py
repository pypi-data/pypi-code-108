import os
import posixpath
import numpy as np
from silx.io import get_data
from ...utils import copy_dict_items, compare_dicts
from ...io.utils import hdf5_entry_exists, get_h5_value
from ...io.reader import import_h5_to_dict
from ...resources.utils import extract_parameters, get_values_from_file
from ...resources.nxflatfield import update_dataset_info_flats_darks
from ..estimators import COREstimator, SinoCOREstimator, CompositeCOREstimator
from ..processconfig import ProcessConfigBase
from .nabu_config import nabu_config, renamed_keys
from .dataset_validator import FullFieldDatasetValidator


class ProcessConfig(ProcessConfigBase):
    default_nabu_config = nabu_config
    config_renamed_keys = renamed_keys

    def _update_dataset_info_with_user_config(self):
        """
        Update the 'dataset_info' (DatasetAnalyzer class instance) data structure with options from user configuration.
        """
        self.logger.debug("Updating dataset information with user configuration")
        if self.dataset_info.kind == "hdf5":
            update_dataset_info_flats_darks(
                self.dataset_info,
                processes_file=self.nabu_config["preproc"]["processes_file"],
                output_dir=self.nabu_config["output"]["location"],
                flatfield_mode=self.nabu_config["preproc"]["flatfield"],
            )
        self._get_rotation_axis_position()
        self._update_rotation_angles()
        self._get_translation_file("reconstruction", "translation_movements_file", "translations")
        self._get_translation_file("phase", "ctf_translations_file", "ctf_translations")


    def _get_translation_file(self, config_section, config_key, dataset_info_attr):
        transl_file = self.nabu_config[config_section][config_key]
        if transl_file in (None, ''):
            return
        translations = None
        if transl_file is not None and "://" not in transl_file:
            try:
                translations = get_values_from_file(
                    transl_file, shape=(self.dataset_info.n_angles, 2)
                ).astype(np.float32)
            except ValueError:
                print("Something wrong with translation_movements_file %s" % transl_file)
                raise
        else:
            try:
                translations = get_data(transl_file)
            except:
                print("Something wrong with translation_movements_file %s" % transl_file)
                raise
        setattr(self.dataset_info, dataset_info_attr, translations)

    def _get_rotation_axis_position(self):
        super()._get_rotation_axis_position()
        rec_params = self.nabu_config["reconstruction"]
        axis_correction_file = rec_params["axis_correction_file"]
        axis_correction = None
        if axis_correction_file is not None:
            try:
                axis_correction = get_values_from_file(
                    axis_correction_file, n_values=self.dataset_info.n_angles
                ).astype(np.float32)
            except ValueError:
                print("Something wrong with axis correction file %s" % axis_correction_file)
                raise
        self.dataset_info.axis_correction = axis_correction


    def _update_rotation_angles(self):
        rec_params = self.nabu_config["reconstruction"]
        n_angles = self.dataset_info.n_angles
        angles_file = rec_params["angles_file"]
        if angles_file is not None:
            try:
                angles = get_values_from_file(angles_file, n_values=n_angles)
                angles = np.deg2rad(angles)
            except ValueError:
                self.logger.fatal("Something wrong with angle file %s" % angles_file)
                raise
            self.dataset_info.rotation_angles = angles
        elif self.dataset_info.rotation_angles is None:
            angles_range_txt = "[0, 180[ degrees"
            if rec_params["enable_halftomo"]:
                angles_range_txt = "[0, 360] degrees"
                angles = np.linspace(0, 2*np.pi, n_angles, True)
            else:
                angles = np.linspace(0, np.pi, n_angles, False)
            self.logger.warning(
                "No information was found on rotation angles. Using default %s (half tomo is %s)"
                % (angles_range_txt, {0: "OFF", 1: "ON"}[int(self.do_halftomo)])
            )
            self.dataset_info.rotation_angles = angles
        angles = self.dataset_info.rotation_angles
        angles += np.deg2rad(rec_params["angle_offset"])
        self.dataset_info.reconstruction_angles = angles


    def _get_cor(self):
        cor = self.nabu_config["reconstruction"]["rotation_axis_position"]
        if isinstance(cor, str): # auto-CoR
            cor_slice = self.nabu_config["reconstruction"]["cor_slice"]
            if cor_slice is not None or cor == "sino-coarse-to-fine":
                subsampling = extract_parameters(
                    self.nabu_config["reconstruction"]["cor_options"]
                ).get("subsampling", 10)
                self.corfinder = SinoCOREstimator(
                    self.dataset_info,
                    cor_slice or 0,
                    subsampling=subsampling,
                    do_flatfield=bool(self.nabu_config["preproc"]["flatfield"]),
                    cor_options=self.nabu_config["reconstruction"]["cor_options"],
                    logger=self.logger
                )
            elif cor == "composite-coarse-to-fine":
                self.corfinder = CompositeCOREstimator(
                    self.dataset_info,
                    cor_options=self.nabu_config["reconstruction"]["cor_options"],
                    logger=self.logger
                )
            else:
                self.corfinder = COREstimator(
                    self.dataset_info,
                    halftomo=self.nabu_config["reconstruction"]["enable_halftomo"],
                    do_flatfield=bool(self.nabu_config["preproc"]["flatfield"]),
                    cor_options=self.nabu_config["reconstruction"]["cor_options"],
                    logger=self.logger
                )
            cor = self.corfinder.find_cor(method=cor)
            self.logger.info("Estimated center of rotation: %.3f" % cor)
        self.dataset_info.axis_position = cor


    @property
    def do_halftomo(self):
        """
        Return True if the current dataset is to be reconstructed using 'half-acquisition' setting.
        """
        enable_halftomo = self.nabu_config["reconstruction"]["enable_halftomo"]
        is_halftomo_dataset = self.dataset_info.is_halftomo
        if enable_halftomo == "auto":
            if is_halftomo_dataset is None:
                raise ValueError("enable_halftomo was set to 'auto', but information on field of view was not found. Please set either 0 or 1 for enable_halftomo")
            return is_halftomo_dataset
        return enable_halftomo


    def _coupled_validation(self):
        self.logger.debug("Doing coupled validation")
        self._dataset_validator = FullFieldDatasetValidator(self.nabu_config, self.dataset_info)


    # TODO update behavior and remove this function once GroupedPipeline cuda backend is implemented
    def get_radios_rotation_mode(self):
        """
        Determine whether projections are to be rotated, and if so, when they are to be rotated.

        Returns
        -------
        method: str or None
            Rotation method: one of the values of `nabu.resources.params.radios_rotation_mode`
        """
        user_rotate_projections = self.nabu_config["preproc"]["rotate_projections"]
        tilt = self.dataset_info.detector_tilt
        phase_method = self.nabu_config["phase"]["method"]
        do_ctf = phase_method == "CTF"
        do_pag = phase_method == "paganin"
        do_unsharp = self.nabu_config["phase"]["unsharp_method"] is not None and self.nabu_config["phase"]["unsharp_coeff"] > 0
        if user_rotate_projections is None and tilt is None:
            return None
        if do_ctf:
            return "full"
        # TODO "chunked" rotation is done only when using a "processing margin"
        # For now the processing margin is enabled only if phase or unsharp is enabled.
        # We can either
        #   - Enable processing margin if rotating projections is needed (more complicated to implement)
        #   - Always do "full" rotation (simpler to implement, at the expense of performances)
        if do_pag or do_unsharp:
            return "chunk"
        else:
            return "full"


    def _build_processing_steps(self):
        nabu_config = self.nabu_config
        dataset_info = self.dataset_info
        binning = (nabu_config["dataset"]["binning"], nabu_config["dataset"]["binning_z"])
        tasks = []
        options = {}

        #
        # Dataset / Get data
        #
        # First thing to do is to get the data (radios or sinograms)
        # For now data is assumed to be on disk (see issue #66).
        tasks.append("read_chunk")
        options["read_chunk"] = {
            "files": dataset_info.projections,
            "sub_region": None,
            "binning": binning,
            "dataset_subsampling": nabu_config["dataset"]["projections_subsampling"]
        }
        #
        # Flat-field
        #
        if nabu_config["preproc"]["flatfield"]:
            tasks.append("flatfield")
            options["flatfield"] = {
                #  ChunkReader handles binning/subsampling by itself,
                # but FlatField needs "real" indices (after binning/subsampling)
                "projs_indices": dataset_info._projs_indices_subsampled,
                "binning": binning,
                "do_flat_distortion": nabu_config["preproc"]["flat_distortion_correction_enabled"],
                "flat_distortion_params": extract_parameters(nabu_config["preproc"]["flat_distortion_params"]),
            }
        #
        # Spikes filter
        #
        if nabu_config["preproc"]["ccd_filter_enabled"]:
            tasks.append("ccd_correction")
            options["ccd_correction"] = {
                "type": "median_clip", # only one available for now
                "median_clip_thresh": nabu_config["preproc"]["ccd_filter_threshold"],
            }
        #
        # Double flat field
        #
        if nabu_config["preproc"]["double_flatfield_enabled"]:
            tasks.append("double_flatfield")
            options["double_flatfield"] = {
                "sigma": nabu_config["preproc"]["dff_sigma"],
                "processes_file": nabu_config["preproc"]["processes_file"],
            }
        #
        # Radios rotation (do it here if possible)
        #
        if self.get_radios_rotation_mode() == "chunk":
            tasks.append("rotate_projections")
            options["rotate_projections"] = {
                "angle": nabu_config["preproc"]["rotate_projections"] or dataset_info.detector_tilt,
                "center": nabu_config["preproc"]["rotate_projections_center"],
                "mode": "chunk",
            }
        #
        #
        # Phase retrieval
        #
        if nabu_config["phase"]["method"] is not None:
            tasks.append("phase")
            options["phase"] = copy_dict_items(
                nabu_config["phase"], ["method", "delta_beta", "margin", "padding_type"]
            )
            options["phase"].update({
                "energy_kev": dataset_info.energy,
                "distance_cm": dataset_info.distance * 1e2,
                "distance_m": dataset_info.distance,
                "pixel_size_microns": dataset_info.pixel_size,
                "pixel_size_m": dataset_info.pixel_size * 1e-6,
            })
            if binning != (1, 1):
                options["phase"]["delta_beta"] /= (binning[0] * binning[1])
            if options["phase"]["method"] == "CTF":
                self._get_ctf_parameters(options["phase"])
        #
        # Unsharp
        #
        if nabu_config["phase"]["unsharp_method"] is not None and nabu_config["phase"]["unsharp_coeff"] > 0:
            tasks.append("unsharp_mask")
            options["unsharp_mask"] = copy_dict_items(
                nabu_config["phase"], ["unsharp_coeff", "unsharp_sigma", "unsharp_method"]
            )
        #
        # -logarithm
        #
        if nabu_config["preproc"]["take_logarithm"]:
            tasks.append("take_log")
            options["take_log"] = copy_dict_items(nabu_config["preproc"], ["log_min_clip", "log_max_clip"])
        #
        # Radios rotation (do it here if mode=="full")
        #
        if self.get_radios_rotation_mode() == "full":
            tasks.append("rotate_projections")
            options["rotate_projections"] = {
                "angle": nabu_config["preproc"]["rotate_projections"] or dataset_info.detector_tilt,
                "center": nabu_config["preproc"]["rotate_projections_center"],
                "mode": "full",
            }
        #
        # Translation movements
        #
        translations = dataset_info.translations
        if translations is not None:
            tasks.append("radios_movements")
            options["radios_movements"] = {
                "translation_movements": dataset_info.translations
            }
        #
        # Sinogram normalization (before half-tomo)
        #
        if nabu_config["preproc"]["sino_normalization"] is not None:
            tasks.append("sino_normalization")
            options["sino_normalization"] = {
                "method": nabu_config["preproc"]["sino_normalization"]
            }
        #
        # Sinogram-based rings artefacts removal
        #
        if nabu_config["preproc"]["sino_rings_correction"]:
            tasks.append("sino_rings_correction")
            options["sino_rings_correction"] = {
                "user_options": nabu_config["preproc"]["sino_rings_options"],
            }
        #
        # Reconstruction
        #
        if nabu_config["reconstruction"]["method"] is not None:
            tasks.append("build_sino")
            options["build_sino"] = copy_dict_items(
                nabu_config["reconstruction"],
                ["rotation_axis_position", "start_x", "end_x", "start_y", "end_y", "start_z", "end_z"]
            )
            options["build_sino"]["axis_correction"] = dataset_info.axis_correction
            tasks.append("reconstruction")
            # Iterative is not supported through configuration file for now.
            options["reconstruction"] = copy_dict_items(
                nabu_config["reconstruction"],
                [
                    "method", "rotation_axis_position", "fbp_filter_type",
                    "padding_type", "start_x", "end_x", "start_y", "end_y", "start_z", "end_z",
                    "centered_axis", "clip_outer_circle"
                ]
            )
            rec_options = options["reconstruction"]
            rec_options["rotation_axis_position"] = dataset_info.axis_position
            rec_options["enable_halftomo"] = self.do_halftomo
            options["build_sino"]["rotation_axis_position"] = dataset_info.axis_position
            options["build_sino"]["enable_halftomo"] = self.do_halftomo
            rec_options["axis_correction"] = dataset_info.axis_correction
            rec_options["angles"] = dataset_info.reconstruction_angles
            rec_options["radio_dims_y_x"] = dataset_info.radio_dims[::-1]
            rec_options["pixel_size_cm"] = dataset_info.pixel_size * 1e-4 # pix size is in microns
            if self.do_halftomo:
                rec_options["angles"] = rec_options["angles"][:(rec_options["angles"].size + 1)//2]
                cor_i = int(round(rec_options["rotation_axis_position"]))
                # New keys
                rec_options["rotation_axis_position_halftomo"] = (2*cor_i-1)/2.
            # New key
            rec_options["cor_estimated_auto"] = isinstance(nabu_config["reconstruction"]["rotation_axis_position"], str)
        #
        # Histogram
        #
        if nabu_config["postproc"]["output_histogram"]:
            tasks.append("histogram")
            options["histogram"] = copy_dict_items(
                nabu_config["postproc"], ["histogram_bins"]
            )
        #
        # Save
        #
        if nabu_config["output"]["location"] is not None:
            tasks.append("save")
            options["save"] = copy_dict_items(
                nabu_config["output"], list(nabu_config["output"].keys())
            )
            options["save"]["overwrite"] = nabu_config["output"]["overwrite_results"]

        self.processing_steps = tasks
        self.processing_options = options
        if set(self.processing_steps) != set(self.processing_options.keys()):
            raise ValueError("Something wrong with process_config: options do not correspond to steps")
        # Add check
        if set(self.processing_steps) != set(self.processing_options.keys()):
            raise ValueError("Something wrong when building processing steps")
        #
        self._configure_save_steps()
        self._configure_resume()


    def _get_ctf_parameters(self, phase_options):
        dataset_info = self.dataset_info
        user_phase_options = self.nabu_config["phase"]

        ctf_geom = extract_parameters(user_phase_options["ctf_geometry"])
        ctf_advanced_params = extract_parameters(user_phase_options["ctf_advanced_params"])

        # z1_vh
        z1_v = ctf_geom["z1_v"]
        z1_h = ctf_geom["z1_h"]
        z1_vh = None
        if z1_h is None and z1_v is None:
            # parallel beam
            z1_vh = None
        elif (z1_v is None) ^ (z1_h is None):
            # only one is provided: source-sample distance
            z1_vh = z1_v or z1_h
        if z1_h is not None and z1_v is not None:
            # distance of the vertically focused source (horizontal line) and the horizontaly focused source (vertical line)
            # for KB mirrors
            z1_vh = (z1_v, z1_h)
        # pix_size_det
        pix_size_det = ctf_geom["detec_pixel_size"] or dataset_info.pixel_size * 1e-6
        # wavelength
        wavelength = 1.23984199e-9 / dataset_info.energy

        phase_options["ctf_geo_pars"] = {
            "z1_vh": z1_vh,
            "z2": phase_options["distance_m"],
            "pix_size_det": pix_size_det,
            "wavelength": wavelength,
            "magnification": bool(ctf_geom["magnification"]),
            "length_scale": ctf_advanced_params["length_scale"]
        }
        phase_options["ctf_lim1"] = ctf_advanced_params["lim1"]
        phase_options["ctf_lim2"] = ctf_advanced_params["lim2"]
        phase_options["ctf_normalize_by_mean"] = ctf_advanced_params["normalize_by_mean"]


    def _configure_save_steps(self):
        self._dump_sinogram = False
        steps_to_save = self.nabu_config["pipeline"]["save_steps"]
        if steps_to_save in (None, ""):
            self.steps_to_save = []
            return
        steps_to_save = [s.strip() for s in steps_to_save.split(",")]
        for step in self.processing_steps:
            step = step.strip()
            if step in steps_to_save:
                self.processing_options[step]["save"] = True
                self.processing_options[step]["save_steps_file"] = self.get_save_steps_file(step_name=step)
        # "sinogram" is a special keyword, not explicitly in the processing steps
        if "sinogram" in steps_to_save:
            self._dump_sinogram = True
            self._dump_sinogram_file = self.get_save_steps_file(step_name="sinogram")
        self.steps_to_save = steps_to_save


    def _get_dump_file_and_h5_path(self):
        resume_from = self.resume_from_step
        process_file = self.get_save_steps_file(step_name=resume_from)
        if not os.path.isfile(process_file):
            self.logger.error(
                "Cannot resume processing from step '%s': no such file %s" % (resume_from, process_file)
            )
            return None, None
        h5_entry = self.dataset_info.hdf5_entry or "entry"
        process_h5_path = posixpath.join(
            h5_entry,
            resume_from,
            "results/data"
        )
        if not hdf5_entry_exists(process_file, process_h5_path):
            self.logger.error(
                "Could not find data in %s in file %s" % (process_h5_path, process_file)
            )
            process_h5_path = None
        return process_file, process_h5_path


    def _configure_resume(self):
        resume_from = self.nabu_config["pipeline"]["resume_from_step"]
        if resume_from in (None, ""):
            self.resume_from_step = None
            return
        resume_from = resume_from.strip(" ,;")
        self.resume_from_step = resume_from

        processing_steps = self.processing_steps
        # special case: resume from sinogram
        if resume_from == "sinogram":
            if "build_sino" not in processing_steps:
                msg = "Cannot resume processing from step 'sinogram': reconstruction is disabled with this configuration"
                self.logger.fatal(msg)
                raise ValueError(msg)
            idx = processing_steps.index("build_sino") # disable up to 'build_sino', not included
        #
        elif resume_from in processing_steps:
            idx = processing_steps.index(resume_from) + 1 # disable up to resume_from, included
        else:
            msg = "Cannot resume processing from step '%s': no such step in the current configuration" % resume_from
            self.logger.error(msg)
            self.resume_from_step = None
            return

        # Get corresponding file and h5 path
        process_file, process_h5_path = self._get_dump_file_and_h5_path()
        if process_file is None or process_h5_path is None:
            self.resume_from_step = None
            return
        dump_info = self._check_dump_file(process_file, raise_on_error=False)
        if dump_info is None:
            self.logger.error(
                "Cannot resume from step %s: cannot use file %s" % (resume_from, process_file)
            )
            self.resume_from_step = None
            return
        dump_start_z, dump_end_z = dump_info

        # Disable steps
        steps_to_disable = processing_steps[1:idx]
        self.logger.debug("Disabling steps %s" % str(steps_to_disable))
        for step_name in steps_to_disable:
            processing_steps.remove(step_name)
            self.processing_options.pop(step_name)

        # Update configuration
        self.logger.info(
            "Processing will be resumed from step '%s' using file %s"
            % (resume_from, process_file)
        )
        self._old_read_chunk = self.processing_options["read_chunk"]
        self.processing_options["read_chunk"] = {
            "process_file": process_file,
            "process_h5_path": process_h5_path,
            "step_name": resume_from,
            "dump_start_z": dump_start_z,
            "dump_end_z": dump_end_z
        }
        # Dont dump a step if we resume from this step
        if resume_from in self.steps_to_save:
            self.logger.warning(
                "Processing is resumed from step '%s'. This step won't be dumped to a file" % resume_from
            )
            self.steps_to_save.remove(resume_from)
            if resume_from == "sinogram":
                self._dump_sinogram = False
            else:
                self.processing_options[resume_from].pop("save")


    def _check_dump_file(self, process_file, raise_on_error=False):
        """
        Return (start_z, end_z) on success
        Return None on failure
        """
        # Ensure data in the file correspond to what is currently asked
        if self.resume_from_step is None:
            return None

        # Check dataset shape/start_z/end_z
        rec_cfg_h5_path = posixpath.join(
            self.dataset_info.hdf5_entry or "entry",
            self.resume_from_step,
            "configuration/nabu_config/reconstruction"
        )
        dump_start_z = get_h5_value(process_file, posixpath.join(rec_cfg_h5_path, "start_z"))
        dump_end_z = get_h5_value(process_file, posixpath.join(rec_cfg_h5_path, "end_z"))
        start_z, end_z = self.nabu_config["reconstruction"]["start_z"], self.nabu_config["reconstruction"]["end_z"]
        if not (dump_start_z <= start_z and end_z <= dump_end_z):
            msg = "File %s was built with start_z=%d, end_z=%d but current configuration asks for start_z=%d, end_z=%d" % (process_file, dump_start_z, dump_end_z, start_z, end_z)
            if not raise_on_error:
                self.logger.error(msg)
                return None
            self.logger.fatal(msg)
            raise ValueError(msg)

        # Check parameters other than reconstruction
        filedump_nabu_config = import_h5_to_dict(
            process_file,
            posixpath.join(
                self.dataset_info.hdf5_entry or "entry",
                self.resume_from_step,
                "configuration/nabu_config"
            )
        )
        sections_to_ignore = ["reconstruction", "output", "pipeline"]
        for section in sections_to_ignore:
            filedump_nabu_config[section] = self.nabu_config[section]
        # special case of the "save_steps process"
        # filedump_nabu_config["pipeline"]["save_steps"] = self.nabu_config["pipeline"]["save_steps"]

        diff = compare_dicts(filedump_nabu_config, self.nabu_config)
        if diff is not None:
            msg = "Nabu configuration in file %s differ from the current one: %s" % (process_file, diff)
            if not raise_on_error:
                self.logger.error(msg)
                return None
            self.logger.fatal(msg)
            raise ValueError(msg)
        #

        return (dump_start_z, dump_end_z)


    def get_save_steps_file(self, step_name=None):
        if self.nabu_config["pipeline"]["steps_file"] not in (None, ""):
            return self.nabu_config["pipeline"]["steps_file"]
        nabu_save_options = self.nabu_config["output"]
        output_dir = nabu_save_options["location"]
        file_prefix = step_name + "_" + nabu_save_options["file_prefix"]
        fname = os.path.join(output_dir, file_prefix) + ".hdf5"
        return fname
