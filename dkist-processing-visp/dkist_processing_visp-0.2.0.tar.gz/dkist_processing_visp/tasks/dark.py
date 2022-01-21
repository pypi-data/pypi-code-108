import logging

from astropy.io import fits
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.statistics import average_numpy_arrays

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.visp_base import VispScienceTask


class DarkCalibration(VispScienceTask, QualityMixin):
    """
    Task class for calculation of the averaged dark frame for a VISP calibration run
    """

    def run(self):
        """
        For each beam:
            - Gather input dark frames
            - Calculate master dark
            - Write master dark
            - Record quality metrics

        Returns
        -------
        None

        """
        target_exp_times = list(
            set(
                self.constants.lamp_exposure_times
                + self.constants.solar_exposure_times
                + self.constants.observe_exposure_times
                + self.constants.polcal_exposure_times
            )
        )
        logging.info(f"{target_exp_times = }")
        with self.apm_step(
            f"Calculating dark frames for {self.constants.num_beams} beams and {len(target_exp_times)} exp times"
        ):
            for exp_time in target_exp_times:
                for beam in range(1, self.constants.num_beams + 1):
                    logging.info(f"Gathering input dark frames for {exp_time = } and {beam = }")
                    count_tags = [
                        VispTag.input(),
                        VispTag.frame(),
                        VispTag.task("DARK"),
                        VispTag.beam(beam),
                        VispTag.exposure_time(exp_time),
                    ]
                    if self.count(tags=count_tags) == 0:
                        raise ValueError(f"Could not find any darks for {exp_time = }")
                    input_dark_arrays = self.input_dark_array_generator(
                        beam=beam, exposure_time=exp_time
                    )
                    logging.info(f"Calculating dark for {exp_time = } and {beam = }")
                    averaged_dark_array = average_numpy_arrays(input_dark_arrays)
                    logging.info(f"Writing dark for {exp_time = } {beam = }")
                    hdul = fits.HDUList([fits.PrimaryHDU(averaged_dark_array)])
                    self.fits_data_write(
                        hdu_list=hdul,
                        tags=[
                            VispTag.intermediate(),
                            VispTag.task("DARK"),
                            VispTag.frame(),
                            VispTag.beam(beam),
                            VispTag.exposure_time(exp_time),
                        ],
                    )
                    # These lines are here to help debugging and can be removed if really necessary
                    filename = next(
                        self.read(
                            tags=[
                                VispTag.intermediate(),
                                VispTag.frame(),
                                VispTag.beam(beam),
                                VispTag.task("DARK"),
                                VispTag.exposure_time(exp_time),
                            ]
                        )
                    )
                    logging.info(f"Wrote dark for {exp_time = } and {beam = } to {filename}")

        with self.apm_step("Finding number of input dark frames"):
            no_of_raw_dark_frames: int = self.count(
                tags=[
                    VispTag.input(),
                    VispTag.frame(),
                    VispTag.task("DARK"),
                ],
            )

        with self.apm_step("Sending dark frame count for quality metric storage"):
            self.quality_store_task_type_counts(
                task_type="dark", total_frames=no_of_raw_dark_frames
            )
