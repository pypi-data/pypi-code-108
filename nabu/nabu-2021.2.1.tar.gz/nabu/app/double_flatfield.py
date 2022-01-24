import numpy as np
from ..preproc.double_flatfield import DoubleFlatField
from ..preproc.flatfield import FlatFieldDataUrls
from ..io.reader import ChunkReader
from ..io.writer import NXProcessWriter
from ..resources.dataset_analyzer import analyze_dataset
from ..resources.logger import Logger, LoggerOrPrint
from .cli_configs import DFFConfig
from .utils import parse_params_values

class DoubleFlatFieldChunks:

    def __init__(self, dataset_path, output_file, chunk_size=100, sigma=None, do_flatfield=True, h5_entry=None, logger=None):
        self.logger = LoggerOrPrint(logger)
        self.dataset_info = analyze_dataset(
            dataset_path, extra_options={"hdf5_entry": h5_entry}, logger=logger
        )
        self.do_flatfield = bool(do_flatfield)
        self.output_file = output_file
        self.sigma = sigma if sigma is not None and abs(sigma) > 1e-5 else None
        self._init_reader(chunk_size)
        self._init_flatfield((None, None, 0, self.chunk_size))
        self._init_dff()


    def _init_reader(self, chunk_size, start_idx=0):
        self.chunk_size = min(chunk_size, self.dataset_info.radio_dims[-1])
        self.reader = ChunkReader(
            self.dataset_info.projections,
            sub_region=(None, None, start_idx, start_idx + self.chunk_size),
            convert_float=True,
        )
        self.projections = self.reader.files_data


    def _init_flatfield(self, subregion):
        if not self.do_flatfield:
            return
        self.flatfield = FlatFieldDataUrls(
            (self.dataset_info.n_angles, self.chunk_size, self.dataset_info.radio_dims[0]),
            self.dataset_info.flats,
            self.dataset_info.darks,
            sorted(self.dataset_info.projections.keys()),
            sub_region=subregion
        )


    def _apply_flatfield(self):
        if self.do_flatfield:
            self.flatfield.normalize_radios(self.projections)


    def _set_reader_subregion(self, subregion):
        self.reader._set_subregion(subregion)
        self.reader._init_reader()
        self.reader._loaded = False


    def _init_dff(self):
        self.double_flatfield = DoubleFlatField(
            self.projections.shape,
            input_is_mlog=False,
            output_is_mlog=False,
            average_is_on_log=self.sigma is not None,
            sigma_filter=self.sigma
        )


    def _get_config(self):
        conf = {
            "dataset": self.dataset_info.location,
            "entry": self.dataset_info.hdf5_entry or None,
            "dff_sigma": self.sigma,
            "do_flatfield": self.do_flatfield,
        }
        return conf


    def compute_double_flatfield(self):
        """
        Compute the double flatfield for the current dataset.
        """
        n_z = self.dataset_info.radio_dims[-1]
        chunk_size = self.chunk_size
        n_steps = n_z // chunk_size
        extra_step = bool(n_z % chunk_size)
        res = np.zeros(self.dataset_info.radio_dims[::-1])
        for i in range(n_steps):
            self.logger.debug("Computing DFF batch %d/%d" % (i+1, n_steps + int(extra_step)))
            subregion = (None, None, i*chunk_size, (i+1)*chunk_size)
            self._set_reader_subregion(subregion)
            self._init_flatfield(subregion)
            self.reader.load_files()
            self._apply_flatfield()
            dff = self.double_flatfield.compute_double_flatfield(self.projections, recompute=True)
            res[subregion[-2]:subregion[-1]] = dff[:]
        # Need to initialize objects with a different shape
        if extra_step:
            curr_idx = (i+1)*self.chunk_size
            self.logger.debug("Computing DFF batch %d/%d" % (i+2, n_steps + int(extra_step)))
            self._init_reader(n_z - curr_idx, start_idx=curr_idx)
            self._init_flatfield(self.reader.sub_region)
            self._init_dff()
            self.reader.load_files()
            self._apply_flatfield()
            dff = self.double_flatfield.compute_double_flatfield(self.projections, recompute=True)
            res[curr_idx:] = dff[:]
        return res


    def write_double_flatfield(self, arr):
        """
        Write the double flatfield image to a file
        """
        writer = NXProcessWriter(
            self.output_file,
            entry=self.dataset_info.hdf5_entry or "entry",
            filemode="a",
            overwrite=True,
        )
        writer.write(
            arr,
            "double_flatfield",
            config=self._get_config()
        )
        self.logger.info("Wrote %s" % writer.fname)


def dff_cli():
    args = parse_params_values(
        DFFConfig,
        parser_description="A command-line utility for computing the double flatfield of a dataset."
    )
    logger = Logger(
        "nabu_double_flatfield", level=args["loglevel"], logfile="nabu_double_flatfield.log"
    )

    output_file = args["output"]

    dff = DoubleFlatFieldChunks(
        args["dataset"],
        output_file,
        chunk_size=args["chunk_size"],
        sigma=args["sigma"],
        do_flatfield=bool(args["flatfield"]),
        h5_entry=args["entry"] or None,
        logger=logger
    )
    dff_image = dff.compute_double_flatfield()
    dff.write_double_flatfield(dff_image)


if __name__ == "__main__":
    dff_cli()
