from os.path import join, isfile, basename, dirname
from math import ceil
import gc
from psutil import virtual_memory
from silx.io import get_data
from silx.io.url import DataUrl
from ...utils import remove_items_from_list, restore_items_in_list
from ...resources.logger import LoggerOrPrint
from ...io.writer import merge_hdf5_files, NXProcessWriter
from ...cuda.utils import collect_cuda_gpus
from ...preproc.phase import compute_paganin_margin
from ...misc.histogram import PartialHistogram, add_last_bin, hist_as_2Darray
from .chunked_cuda import CudaChunkedPipeline, CudaChunkedPipelineLimitedMemory
from .grouped import GroupedPipeline, SinoStackPipeline
from .grouped_cuda import CudaGroupedPipeline, CudaSinoStackPipeline
from .computations import estimate_chunk_size, estimate_group_size


def get_gpus_ids(resources_cfg):
    gpus_ids = resources_cfg["gpu_id"]
    if gpus_ids != []:
        return gpus_ids
    # TODO (?) heuristic to pick the best gpus
    return list(range(resources_cfg["gpus"]))


def variable_idxlen_sort(fname):
    return int(fname.split("_")[-1].split(".")[0])


class ChunkedReconstructor:
    """
    A class for doing full-volume reconstructions.
    """

    _pipeline_cls = CudaChunkedPipeline
    _process_name = "reconstruction"

    def __init__(self, process_config, logger=None, extra_options=None, cuda_options=None):
        """
        Initialize a LocalReconstruction object.
        This class is used for managing pipelines

        Parameters
        ----------
        process_config: ProcessConfig object
            Data structure with process configuration
        logger: Logger, optional
            logging object
        extra_options: dict, optional
            Dictionary with advanced options. Please see 'Other parameters' below
        cuda_options: dict, optional
            Dictionary with cuda options passed to `nabu.cuda.processing.CudaProcessing`


        Other parameters
        -----------------
        Advanced options can be passed in the 'extra_options' dictionary. These can be:

           - "gpu_mem_fraction": 0.9,
           - "cpu_mem_fraction": 0.9,
           - "use_phase_margin": True,
           - "max_chunk_size": None,
           - "phase_margin": None,
        """
        self.logger = LoggerOrPrint(logger)
        self.process_config = process_config
        self._set_extra_options(extra_options)
        self._get_reconstruction_range()
        self._get_resources()
        self._compute_max_chunk_size()
        self._compute_phase_margin()
        self._get_pipeline_class()
        self._build_tasks()
        self.pipeline = None
        self.cuda_options = cuda_options


    def _set_extra_options(self, extra_options):
        if extra_options is None:
            extra_options = {}
        advanced_options = {
            "gpu_mem_fraction": 0.9,
            "cpu_mem_fraction": 0.9,
            "use_phase_margin": True,
            "max_chunk_size": None,
            "phase_margin": None,
        }
        advanced_options.update(extra_options)
        self.extra_options = advanced_options
        self.gpu_mem_fraction = self.extra_options["gpu_mem_fraction"]
        self.cpu_mem_fraction = self.extra_options["cpu_mem_fraction"]
        self.use_phase_margin = self.extra_options["use_phase_margin"]
        self._do_histograms = self.process_config.nabu_config["postproc"]["output_histogram"]
        self._histogram_merged = False


    def _get_reconstruction_range(self):
        rec_cfg = self.process_config.nabu_config["reconstruction"]
        self.z_min = rec_cfg["start_z"]
        self.z_max = rec_cfg["end_z"] + 1
        self.delta_z = self.z_max - self.z_min


    def _get_resources(self):
        self.resources = {}
        self._get_gpu()
        self._get_memory()


    def _get_memory(self):
        vm = virtual_memory()
        self.resources["mem_avail_GB"] = vm.available / 1e9


    def _get_gpu(self):
        gpus = get_gpus_ids(self.process_config.nabu_config["resources"])
        if len(gpus) == 0:
            raise ValueError("Need at least one GPU")
        if len(gpus) > 1:
            raise ValueError("This class does not support more than one GPU")
        self.resources["gpu_id"] = self._gpu_id = gpus[0]
        self.resources["gpus"] = collect_cuda_gpus()


    def _compute_max_chunk_size(self):
        gpu_mem = self.resources["gpus"][self._gpu_id]["memory_GB"] * self.gpu_mem_fraction
        cpu_mem = self.resources["mem_avail_GB"] * self.cpu_mem_fraction
        self.gpu_max_chunk_size = estimate_chunk_size(
            gpu_mem,
            self.process_config,
            chunk_step=10,
             warn_from_GB=17 #2**32 elements - see estimate_required_memory docstring note
        )
        self.cpu_max_chunk_size = estimate_chunk_size(
            cpu_mem,
            self.process_config,
            chunk_step=10
        )
        user_max_chunk_size = self.extra_options["max_chunk_size"]
        if user_max_chunk_size is not None:
            self.gpu_max_chunk_size = min(self.gpu_max_chunk_size, user_max_chunk_size)
            self.cpu_max_chunk_size = min(self.cpu_max_chunk_size, user_max_chunk_size)


    def _compute_phase_margin(self):
        unsharp_margin = self._compute_unsharp_margin()
        if "phase" not in self.process_config.processing_steps:
            self._phase_margin = unsharp_margin
            self._margin_v = self._phase_margin[0]
            return
        radio_shape = self.process_config.dataset_info.radio_dims[::-1]
        opts = self.process_config.processing_options["phase"]
        user_phase_margin = self.extra_options["phase_margin"]
        if user_phase_margin is not None and user_phase_margin > 0:
            margin_v, margin_h = user_phase_margin, user_phase_margin
            self.logger.info("Using user-defined phase margin: %d" % user_phase_margin)
        else:
            margin_v, margin_h = compute_paganin_margin(
                radio_shape,
                distance=opts["distance_m"],
                energy=opts["energy_kev"],
                delta_beta=opts["delta_beta"],
                pixel_size=opts["pixel_size_m"],
                padding=opts["padding_type"]
            )
        margin_v = max(margin_v, unsharp_margin[0])
        self._phase_margin = (margin_v, margin_h)
        self._margin_v = self._phase_margin[0]
        self.logger.info("Estimated phase margin: %d pixels" % self._margin_v)


    def _compute_unsharp_margin(self):
        if "unsharp_mask" not in self.process_config.processing_steps:
            return (0, 0)
        opts = self.process_config.processing_options["unsharp_mask"]
        sigma = opts["unsharp_sigma"]
        # nabu uses cutoff = 4
        cutoff = 4
        gaussian_kernel_size = int(ceil(2 * cutoff * sigma + 1))
        self.logger.debug("Unsharp mask margin: %d pixels" % gaussian_kernel_size)
        return (gaussian_kernel_size, gaussian_kernel_size)


    def _get_pipeline_class(self):
        self._limited_mem = False
        # Actually less in some cases (margin_far_up + margin_far_down instead of 2*margin_v).
        # But we want to use only one class for all stages.
        chunk_size_for_one_slice = 1 + 2 * self._margin_v
        chunk_is_too_small = False
        if chunk_size_for_one_slice > self.gpu_max_chunk_size:
            msg = str(
                "Phase margin is %d, so we need to process at least %d detector rows. However, the available memory enables to process only %d rows at once"
                % (self._margin_v, chunk_size_for_one_slice, self.gpu_max_chunk_size)
            )
            chunk_is_too_small = True
        if self._margin_v > self.gpu_max_chunk_size//3:
            n_slices = max(1, self.gpu_max_chunk_size - (2 * self._margin_v))
            n_stages = ceil(self.delta_z / n_slices)
            if n_stages > 1:
                # In this case, using CudaFlatField + margin would lead to many stages
                msg = str(
                    "Phase margin (%d) is too big for chunk size (%d)"
                    % (self._margin_v, self.gpu_max_chunk_size)
                )
                chunk_is_too_small = True
        if chunk_is_too_small:
            self.logger.warning(msg)
            if self.use_phase_margin:
                self._pipeline_cls = CudaChunkedPipelineLimitedMemory
                self.logger.warning("Using %s" % self._pipeline_cls.__name__)
                self._limited_mem = True
            else:
                self._phase_margin = (0, 0)
                self._margin_v = self._phase_margin[0]
                self._pipeline_cls = CudaChunkedPipeline
                self.logger.warning("Using %s without margin" % self._pipeline_cls.__name__)


    def _build_tasks(self):
        self._compute_volume_chunks()


    def _compute_volume_chunks(self):
        n_z = self.process_config.dataset_info._radio_dims_notbinned[1]
        margin_v = self._margin_v
        self._margin_far_up = min(margin_v, self.z_min)
        self._margin_far_down = min(margin_v, n_z - self.z_max)
        # | margin_up |     n_slices    |  margin_down |
        # |-----------|-----------------|--------------|
        # |----------------------------------------------------|
        #                    delta_z
        if self._limited_mem:
            n_slices = self.cpu_max_chunk_size
        else:
            n_slices = self.gpu_max_chunk_size - (2 * margin_v)
        tasks = []
        if self.gpu_max_chunk_size >= self.delta_z and self.z_min == 0 and self.z_max == n_z:
            # In this case we can do everything in a single stage, without margin
            n_slices = self.delta_z
            tasks.append({
                "sub_region": (self.z_min, self.z_max),
                "phase_margin": None,
            })
        elif n_slices >= self.delta_z:
            # In this case we can do everything in a single stage
            n_slices = self.delta_z
            (margin_up, margin_down) = (self._margin_far_up, self._margin_far_down)
            tasks.append({
                "sub_region": (self.z_min - margin_up, self.z_max + margin_down),
                "phase_margin": ((margin_up, margin_down), (0, 0))
            })
        else:
            # In this case there are at least two stages
            n_stages = ceil(self.delta_z / n_slices)
            tasks = []
            curr_z_min = self.z_min
            curr_z_max = self.z_min + n_slices
            for i in range(n_stages):
                margin_up = min(margin_v, curr_z_min)
                margin_down = min(margin_v, max(n_z - curr_z_max, 0))
                if curr_z_max + margin_down >= self.z_max:
                    curr_z_max -= (curr_z_max - (self.z_max + 0))
                    margin_down = min(margin_v, max(n_z - 1 - curr_z_max, 0))
                tasks.append({
                    "sub_region": (curr_z_min - margin_up, curr_z_max + margin_down),
                    "phase_margin": ((margin_up, margin_down), (0, 0))
                })
                if curr_z_max == self.z_max:
                    # No need for further tasks
                    break
                curr_z_min += n_slices
                curr_z_max += n_slices
        self.tasks = tasks
        self.n_slices = n_slices


    def _print_tasks(self):
        for task in self.tasks:
            margin_up, margin_down = task["phase_margin"][0]
            s_u, s_d = task["sub_region"]
            print(
                "Top Margin: [%04d, %04d[  |  Slices: [%04d, %04d[  |  Bottom Margin: [%04d, %04d["
                % (
                    s_u, s_u + margin_up,
                    s_u + margin_up, s_d - margin_down,
                    s_d - margin_down, s_d
                )
            )


    def _instantiate_pipeline(self, task):
        self.logger.debug("Creating a new pipeline object")
        args = [self.process_config, task["sub_region"]]
        kwargs = {}
        if self._pipeline_cls.backend == "cuda":
            kwargs["cuda_options"] = self.cuda_options
        if self._limited_mem:
            # Adapt chunk size so that [margin_up, chunk_size, margin_down]
            # is equal to delta_z.
            chunk_size = self.gpu_max_chunk_size
            dz = self._get_delta_z(task)
            margin_v_tot = sum(task["phase_margin"][0])
            args.append(chunk_size)
        pipeline = self._pipeline_cls(
            *args,
            logger=self.logger,
            phase_margin=task["phase_margin"],
            **kwargs
        )
        self.pipeline = pipeline


    def _instantiate_pipeline_if_necessary(self, current_task, other_task):
        """
        Instantiate a pipeline only if current_task has a different "delta z" than other_task
        """
        if self.pipeline is None:
            self._instantiate_pipeline(current_task)
            return
        dz_cur = self._get_delta_z(current_task)
        dz_other = self._get_delta_z(other_task)
        if dz_cur != dz_other:
            self.logger.debug("Destroying pipeline instance and releasing memory")
            self._destroy_pipeline()
            self._instantiate_pipeline(current_task)


    def _destroy_pipeline(self):
        self.pipeline = None
        # Not elegant, but for now the only way to release Cuda memory
        gc.collect()

    @staticmethod
    def _get_delta_z(task):
        # will have to be modified if sub_region accounts for x-subregion
        return task["sub_region"][1] - task["sub_region"][0]


    def _get_task_key(self):
        """
        Get the 'key' (number) associated to the current task/pipeline
        """
        return self.pipeline.sub_region[-2:]


    def _give_progress_info(self, task):
        self.logger.info("Processing sub-volume %s" % (str(task["sub_region"])))


    def _process_task(self, task):
        self.pipeline.process_chunk(sub_region=task["sub_region"])


    def reconstruct(self):
        tasks = self.tasks
        self.results = {}
        self._histograms = {}
        self._data_dumps = {}
        prev_task = tasks[0]
        for task in tasks:
            self._give_progress_info(task)
            self._instantiate_pipeline_if_necessary(task, prev_task)
            self._process_task(task)
            task_key = self._get_task_key()
            self.results[task_key] = self.pipeline.writer.fname
            if self.pipeline.histogram_writer is not None: # self._do_histograms
                self._histograms[task_key] = self.pipeline.histogram_writer.fname
            if len(self.pipeline._data_dump) > 0:
                self._data_dumps[task_key] = {}
                for step_name, writer in self.pipeline._data_dump.items():
                    self._data_dumps[task_key][step_name] = writer.fname
            prev_task = task


    def get_relative_files(self, files=None):
        out_cfg = self.process_config.nabu_config["output"]
        if files is None:
            files = list(self.results.values())
        try:
            files.sort(key=variable_idxlen_sort)
        except:
            self.logger.error(
                "Lexical ordering failed, falling back to default sort - it will fail for more than 10k projections"
            )
            files.sort()
        local_files = [
            join(out_cfg["file_prefix"], basename(fname))
            for fname in files
        ]
        return local_files


    def merge_hdf5_reconstructions(self, output_file=None, prefix=None, files=None, process_name=None, axis=0, merge_histograms=True, output_dir=None):
        """
        Merge existing hdf5 files by creating a HDF5 virtual dataset.

        Parameters
        ----------
        output_file: str, optional
            Output file name. If not given, the file prefix in section "output"
            of nabu config will be taken.
        """
        out_cfg = self.process_config.nabu_config["output"]
        out_dir = output_dir or out_cfg["location"]
        prefix = prefix or ""
        # Prevent issue when out_dir is empty, which happens only if dataset/location is a relative path.
        # TODO this should be prevented earlier
        if out_dir is None or len(out_dir.strip()) == 0:
            out_dir = dirname(dirname(self.results[list(self.results.keys())[0]]))
        #
        if output_file is None:
            output_file = join(out_dir, prefix + out_cfg["file_prefix"]) + ".hdf5"
        if isfile(output_file):
            msg = str("File %s already exists" % output_file)
            if out_cfg["overwrite_results"]:
                msg += ". Overwriting as requested in configuration file"
                self.logger.warning(msg)
            else:
                msg += ". Set overwrite_results to True in [output] to overwrite existing files."
                self.logger.fatal(msg)
                raise ValueError(msg)

        local_files = files
        if local_files is None:
            local_files = self.get_relative_files()
        if local_files == []:
            self.logger.error("No files to merge")
            return
        entry = getattr(self.process_config.dataset_info.dataset_scanner, "entry", "entry")
        process_name = process_name or self._process_name
        h5_path = join(entry, *[process_name, "results", "data"])
        #
        self.logger.info("Merging %ss to %s" % (process_name, output_file))
        merge_hdf5_files(
            local_files, h5_path, output_file, process_name,
            output_entry=entry,
            output_filemode="a",
            processing_index=0,
            config={
                self._process_name + "_stages": {
                    str(k): v for k, v in zip(self.results.keys(), local_files)
                },
                "nabu_config": self.process_config.nabu_config,
                "processing_options": self.process_config.processing_options,
            },
            base_dir=out_dir,
            axis=axis,
            overwrite=out_cfg["overwrite_results"]
        )
        if merge_histograms:
            self.merge_histograms(output_file=output_file)
        return output_file

    merge_hdf5_files = merge_hdf5_reconstructions

    def merge_histograms(self, output_file=None, force_merge=False):
        """
        Merge the partial histograms
        """
        if not(self._do_histograms):
            return
        if self._histogram_merged and not(force_merge):
            return
        self.logger.info("Merging histograms")

        masterfile_entry = getattr(self.process_config.dataset_info.dataset_scanner, "entry", "entry")
        masterfile_process_name = "histogram" # TODO don't hardcode process name
        output_entry = masterfile_entry

        out_cfg = self.process_config.nabu_config["output"]
        if output_file is None:
            output_file = join(
                dirname(list(self._histograms.values())[0]),
                out_cfg["file_prefix"] + "_histogram"
            ) + ".hdf5"
        local_files = self.get_relative_files(files=list(self._histograms.values()))
        #
        h5_path = join(masterfile_entry, *[masterfile_process_name, "results", "data"])
        #

        try:
            files = sorted(self._histograms.values(), key=variable_idxlen_sort)
        except:
            self.logger.error(
                "Lexical ordering of histogram failed, falling back to default sort - it will fail for more than 10k projections"
            )
            files = sorted(self._histograms.values())
        data_urls = []
        for fname in files:
            url = DataUrl(
                file_path=fname, data_path=h5_path, data_slice=None, scheme="silx"
            )
            data_urls.append(url)
        histograms = []
        for data_url in data_urls:
            h2D = get_data(data_url)
            histograms.append(
                (h2D[0], add_last_bin(h2D[1]))
            )
        histograms_merger = PartialHistogram( # TODO configurable
            method="fixed_bins_number", num_bins=histograms[0][0].size
        )
        merged_hist = histograms_merger.merge_histograms(histograms)

        #volume_shape = (self.delta_z, ) + self.process_config.dataset_info.radio_dims[::-1]
        rec_options = self.process_config.processing_options["reconstruction"]
        volume_shape = (
            rec_options["end_z"] - rec_options["start_z"] + 1,
            rec_options["end_y"] - rec_options["start_y"] + 1,
            rec_options["end_x"] - rec_options["start_x"] + 1,
        )
        writer = NXProcessWriter(
            output_file, entry=output_entry, filemode="a", overwrite=True
        )
        writer.write(
            hist_as_2Darray(merged_hist),
            "histogram", # TODO don't hard-code
            processing_index=1,
            config={
                "files": local_files,
                "bins": self.process_config.nabu_config["postproc"]["histogram_bins"],
                "volume_shape": volume_shape,
            }
        )
        self._histogram_merged = True


    def merge_data_dumps(self, axis=1):
        # Collect in a dict where keys are step names (instead of task keys)
        dumps = {}
        for task_key, data_dumps in self._data_dumps.items():
            for step_name, fname in data_dumps.items():
                fname = join(basename(dirname(fname)), basename(fname))
                if step_name not in dumps:
                    dumps[step_name] = [fname]
                else:
                    dumps[step_name].append(fname)
        # Merge HDF5 files
        for step_name, files in dumps.items():
            dump_file = self.process_config.get_save_steps_file(step_name=step_name)
            self.merge_hdf5_files(
                output_file=dump_file,
                output_dir=dirname(dump_file),
                files=files, process_name=step_name, axis=axis, merge_histograms=False
            )


# COMPAT.
LocalReconstruction = ChunkedReconstructor
#

# TODO this class inherits from ChunkedReconstructor, but its principle is different.
# Many methods from ChunkedReconstructor are reused.
# Create a base class ?
class GroupedReconstructor(ChunkedReconstructor):

    _pipeline_cls_radios = CudaGroupedPipeline
    _pipeline_cls_sinos = CudaSinoStackPipeline
    _reconstruction_states = ["radios", "sinos"]

    def __init__(self, process_config, logger=None, extra_options=None, cuda_options=None):
        self.logger = LoggerOrPrint(logger)
        self.process_config = process_config
        self._set_extra_options(extra_options)
        self._get_reconstruction_range()
        self._get_subregion()
        self._get_resources()
        self._compute_max_group_size() # radios pipeline
        self._compute_max_chunk_size() # sinos pipeline
        self._build_tasks()
        self.pipeline = None
        self.set_reconstruction_state("radios")
        self.cuda_options = cuda_options


    def _set_extra_options(self, extra_options):
        if extra_options is None:
            extra_options = {}
        advanced_options = {
            "gpu_mem_fraction": 0.9,
            "cpu_mem_fraction": 0.9,
            "max_group_size": None,
            "max_chunk_size": None,
        }
        advanced_options.update(extra_options)
        self.extra_options = advanced_options
        self.gpu_mem_fraction = self.extra_options["gpu_mem_fraction"]
        self.cpu_mem_fraction = self.extra_options["cpu_mem_fraction"]
        self._histogram_merged = False


    def _get_subregion(self):
        # For GroupedPipeline, sub-region is always the same
        x_min, x_max = None, None

        # TODO the following is not working for half tomography, as end_x is "twice" bigger.
        # So X-subregion is not supported until the "config file ingestion refactoring"
        # if "reconstruction" in self.process_config.processing_steps:
            # rec_cfg = self.process_config.processing_options["reconstruction"]
            # x_min, x_max = rec_cfg["start_x"], rec_cfg["end_x"] + 1
        self.sub_region = (x_min, x_max, self.z_min, self.z_max)

    def _compute_max_group_size(self):
        """
        Compute the maximum number of radios that can be processed in memory
        """
        gpu_mem = self.resources["gpus"][self._gpu_id]["memory_GB"] * self.gpu_mem_fraction
        cpu_mem = self.resources["mem_avail_GB"] * self.cpu_mem_fraction
        self.gpu_max_group_size = estimate_group_size(
            gpu_mem,
            self.process_config,
            step=10,
            warn_from_GB=17 #2**32 elements - see estimate_required_memory docstring note
        )
        self.cpu_max_group_size = estimate_group_size(
            cpu_mem,
            self.process_config,
            step=10,
        )
        user_max_group_size = self.extra_options["max_group_size"]
        if user_max_group_size is not None:
            self.gpu_max_group_size = min(self.gpu_max_group_size, user_max_group_size)
            self.cpu_max_group_size = min(self.cpu_max_group_size, user_max_group_size)

        self.max_group_size = self.gpu_max_group_size

    def _compute_max_chunk_size(self):
        processing_steps = self.process_config.processing_steps
        processing_steps, removed_steps = remove_items_from_list(
            processing_steps,
            ["flatfield", "ccd_correction", "phase"]
        )
        LocalReconstruction._compute_max_chunk_size(self)
        restore_items_in_list(processing_steps, removed_steps)


    def _build_tasks(self):
        self._build_radios_processing_tasks()
        self._build_sinos_processing_tasks()

    def _build_radios_processing_tasks(self):
        n_a = len(self.process_config.dataset_info.projections)
        group_size = self.max_group_size
        tasks = []
        if group_size >= n_a:
            # In this case we can do everything in a single stage
            # (but then we would have been better of with a LocalReconstruction)
            tasks.append({
                "images_group": (0, n_a),
            })
        else:
            # In this case there are at least two stages
            n_stages = ceil(n_a / group_size)
            tasks = []
            curr_a_min = 0
            curr_a_max = group_size
            for i in range(n_stages):
                curr_a_max = min(n_a, curr_a_max)
                tasks.append({
                    "images_group": (curr_a_min, curr_a_max)
                })
                if curr_a_max == n_a:
                    # No need for further tasks
                    break
                curr_a_min += group_size
                curr_a_max += group_size
        self.radios_tasks = tasks


    def _build_sinos_processing_tasks(self):
        n_z = self.delta_z
        chunk_size = self.gpu_max_chunk_size
        tasks = []
        if chunk_size >= n_z:
            # In this case we can do everything in a single stage
            # (but then we would have been better of with a LocalReconstruction)
            tasks.append({
                "stack": (0, n_z),
            })
        else:
            # In this case there are at least two stages
            n_stages = ceil(n_z / chunk_size)
            tasks = []
            curr_a_min = 0
            curr_a_max = chunk_size
            for i in range(n_stages):
                curr_a_max = min(n_z, curr_a_max)
                tasks.append({
                    "stack": (curr_a_min, curr_a_max)
                })
                if curr_a_max == n_z:
                    # No need for further tasks
                    break
                curr_a_min += chunk_size
                curr_a_max += chunk_size
        self.sinos_tasks = tasks


    def set_reconstruction_state(self, state):
        """
        Set the reconstruction state of the current class, depending on which stage of processing
        we want to accomplish.

        Parameters
        ----------
        state: str
            Reconstruction state. Can be 'radios' or 'sinos'
        """
        if state == "radios":
            self._process_name = "sinogram"
            self._do_histograms = False
            self.tasks = self.radios_tasks
        elif state == "sinos":
            self._process_name = "reconstruction"
            self._do_histograms = self.process_config.nabu_config["postproc"]["output_histogram"]
            self.tasks = self.sinos_tasks
        else:
            raise ValueError("state can only be in %s" % str(self._reconstruction_states))
        self._reconstruction_state = state


    def _print_tasks(self):
        if self._reconstruction_state == "radios":
            desc = "Images"
            key = "images_group"
        else:
            desc = "Sinogram stack"
            key = "stack"
        for task in self.tasks:
            i_u, i_d = task[key]
            print(
                "%s: [%04d, %04d[" % desc
                % (i_u, i_d)
            )

    @staticmethod
    def _get_group_size(task):
        group = task["images_group"]
        return group[1] - group[0]

    @staticmethod
    def _get_stack_size(task):
        stack = task["stack"]
        return stack[1] - stack[0]


    def _instantiate_pipeline_radios(self, task):
        args = [self.process_config, task["images_group"]]
        kwargs = {}
        if self._pipeline_cls_radios.backend == "cuda":
            kwargs["cuda_options"] = self.cuda_options
        pipeline = self._pipeline_cls_radios(
            *args,
            sub_region=self.sub_region,
            logger=self.logger,
            **kwargs
        )
        self.pipeline = pipeline


    def _instantiate_pipeline_sinos(self, task):
        args = [self.process_config, task["stack"]]
        kwargs = {}
        if self._pipeline_cls_sinos.backend == "cuda":
            kwargs["cuda_options"] = self.cuda_options
        pipeline = self._pipeline_cls_sinos(
            *args,
            self._projections,
            logger=self.logger,
            **kwargs
        )
        self.pipeline = pipeline


    def _instantiate_pipeline(self, task):
        self.logger.debug("Creating a new pipeline object")
        if self._reconstruction_state == "radios":
            self._instantiate_pipeline_radios(task)
        else:
            self._instantiate_pipeline_sinos(task)


    def _instantiate_pipeline_if_necessary(self, current_task, other_task):
        """
        Instantiate a pipeline only if current_task has a different "group_size" than other_task
        """
        if self.pipeline is None:
            self._instantiate_pipeline(current_task)
            return
        if self._reconstruction_state == "radios":
            group_size_cur = self._get_group_size(current_task)
            group_size_other = self._get_group_size(other_task)
            recreate_pipeline = group_size_cur != group_size_other
        else:
            stack_size_cur = self._get_stack_size(current_task)
            stack_size_other = self._get_stack_size(other_task)
            recreate_pipeline = stack_size_cur != stack_size_other
        if recreate_pipeline:
            self.logger.debug("Destroying pipeline instance and releasing memory")
            self._destroy_pipeline()
            self._instantiate_pipeline(current_task)


    def _get_task_key(self):
        """
        Get the 'key' (number) associated to the current task/pipeline
        """
        if self._reconstruction_state == "radios":
            return self.pipeline.images_group
        else:
            return self.pipeline.stack


    def _give_progress_info(self, task):
        if self._reconstruction_state == "radios":
            self.logger.info("Processing images group %s" % (str(task["images_group"])))
        else:
            self.logger.info("Processing sinograms stack %s" % (str(task["stack"])))


    def _process_task(self, task):
        if self._reconstruction_state == "radios":
            self.pipeline.process_group(images_group=task["images_group"])
        else:
            self.pipeline.process_stack(stack=task["stack"])


    def reconstruct(self, projections=None):
        """
        Perform a volume reconstruction with the current configuration.
        """
        if self.process_config.resume_from_step is not None and self.process_config.resume_from_step == "sinogram":
            projections = self.process_config.processing_options["read_chunk"]["process_file"]
            self.logger.info("Resuming from sinograms in %s" % projections)
        if projections is None:
            self.set_reconstruction_state("radios")
            # TODO this is clumsy - see comment above the class definition
            LocalReconstruction.reconstruct(self)
            #
            self._projections = self.merge_hdf5_reconstructions(prefix="sinogram_", merge_histograms=False)
            self.merge_data_dumps(axis=0)
            self._destroy_pipeline()
        else:
            self._projections = projections
        self.set_reconstruction_state("sinos")
        LocalReconstruction.reconstruct(self)
