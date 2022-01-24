import posixpath
from os import path
from math import ceil
from shutil import copy
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
import numpy as np
from tomoscan.io import HDF5File
from tomoscan.esrf.hdf5scan import HDF5TomoScan
from ..io.utils import get_first_hdf5_entry
from ..misc.rotation import Rotation
from ..resources.logger import Logger, LoggerOrPrint
from ..pipeline.config_validators import optional_tuple_of_floats_validator, boolean_validator
from ..misc.rotation_cuda import CudaRotation, __has_pycuda__
from .utils import parse_params_values
from .cli_configs import RotateRadiosConfig


class HDF5ImagesStackRotation:
    def __init__(self, input_file, output_file, angle, center=None, entry=None, logger=None, batch_size=100, use_cuda=True, use_multiprocessing=True):
        self.logger = LoggerOrPrint(logger)
        self.use_cuda = use_cuda & __has_pycuda__
        self.batch_size = batch_size
        self.use_multiprocessing = use_multiprocessing
        self._browse_dataset(input_file, entry)
        self._get_rotation(angle, center)
        self._init_output_dataset(output_file)

    def _browse_dataset(self, input_file, entry):
        self.input_file = input_file
        if entry is None or entry == "":
            entry = get_first_hdf5_entry(input_file)
        self.entry = entry
        self.dataset_info = HDF5TomoScan(input_file, entry=entry)

    def _get_rotation(self, angle, center):
        if self.use_cuda:
            self.logger.info("Using Cuda rotation")
            rot_cls = CudaRotation
        else:
            self.logger.info("Using skimage rotation")
            rot_cls = Rotation
            if self.use_multiprocessing:
                self.thread_pool = ThreadPool(processes=cpu_count() - 2)
                self.logger.info("Using multiprocessing with %d cores" % self.thread_pool._processes)

        self.rotation = rot_cls(
            (self.dataset_info.dim_2, self.dataset_info.dim_1),
            angle,
            center=center,
            mode="edge"
        )

    def _init_output_dataset(self, output_file):
        self.output_file = output_file
        copy(self.input_file, output_file)

        first_proj_url = self.dataset_info.projections[list(self.dataset_info.projections.keys())[0]]
        self.data_path = first_proj_url.data_path()
        dirname, basename = posixpath.split(self.data_path)
        self._data_path_dirname = dirname
        self._data_path_basename = basename

    def _rotate_stack_cuda(self, images, output):
        self.rotation.cuda_processing._allocate_array("tmp_images_stack", images.shape)
        self.rotation.cuda_processing._allocate_array("tmp_images_stack_rot", images.shape)
        d_in = self.rotation.cuda_processing.tmp_images_stack
        d_out = self.rotation.cuda_processing.tmp_images_stack_rot
        n_imgs = images.shape[0]
        d_in[:n_imgs].set(images)
        for j in range(n_imgs):
            self.rotation.rotate(d_in[j], output=d_out[j])
        d_out[:n_imgs].get(ary=output[:n_imgs])

    def _rotate_stack(self, images, output):
        if self.use_cuda:
            self._rotate_stack_cuda(images, output)
        elif self.use_multiprocessing:
            out_tmp = self.thread_pool.map(self.rotation.rotate, images)
            print(out_tmp[0])
            output[:] = np.array(out_tmp, dtype="f") # list -> np array... consumes twice as much memory
        else:
            for j in range(images.shape[0]):
                output[j] = self.rotation.rotate(images[j])

    def rotate_images(self, suffix="_rot"):
        data_path = self.data_path
        fid = HDF5File(self.input_file, "r")
        fid_out = HDF5File(self.output_file, "a")

        try:
            data_ptr = fid[data_path]
            n_images = data_ptr.shape[0]
            data_out_ptr = fid_out[data_path]

            # Delete virtual dataset in output file, create "data_rot" dataset
            del fid_out[data_path]
            fid_out[self._data_path_dirname].create_dataset(
                self._data_path_basename + suffix, shape=data_ptr.shape, dtype=data_ptr.dtype
            )
            data_out_ptr = fid_out[data_path + suffix]

            # read by group of images to hide latency
            group_size = self.batch_size
            images_rot = np.zeros((group_size, data_ptr.shape[1], data_ptr.shape[2]), dtype="f")
            n_groups = ceil(n_images / group_size)
            for i in range(n_groups):
                self.logger.info("Processing radios group %d/%d" % (i+1, n_groups))
                i_min = i * group_size
                i_max = min((i + 1) * group_size, n_images)
                images = data_ptr[i_min:i_max, :, :].astype("f")
                self._rotate_stack(images, images_rot)
                data_out_ptr[i_min:i_max, :, :] = images_rot[:i_max-i_min, :, :].astype(data_ptr.dtype)
        finally:
            fid_out[self._data_path_dirname].move(posixpath.basename(data_path) + suffix, self._data_path_basename)
            fid_out[data_path].attrs["interpretation"] = "image"
            fid.close()
            fid_out.close()




def rotate_cli():
    args = parse_params_values(
        RotateRadiosConfig,
        parser_description="A command-line utility for performing a rotation on all the radios of a dataset."
    )
    logger = Logger(
        "nabu_rotate", level=args["loglevel"], logfile="nabu_rotate.log"
    )

    dataset_path = args["dataset"]
    h5_entry = args["entry"]
    output_file = args["output"]
    center = optional_tuple_of_floats_validator("", "", args["center"])
    use_cuda = boolean_validator("", "", args["use_cuda"])
    use_multiprocessing = boolean_validator("", "", args["use_multiprocessing"])

    if path.exists(output_file):
        logger.fatal("Output file %s already exists, not overwriting it" % output_file)
        exit(1)

    h5rot = HDF5ImagesStackRotation(
        dataset_path, output_file, args["angle"], center=center, entry=h5_entry, logger=logger,
        batch_size=args["batchsize"], use_cuda=use_cuda, use_multiprocessing=use_multiprocessing
    )
    h5rot.rotate_images()


if __name__ == "__main__":
    rotate_cli()
