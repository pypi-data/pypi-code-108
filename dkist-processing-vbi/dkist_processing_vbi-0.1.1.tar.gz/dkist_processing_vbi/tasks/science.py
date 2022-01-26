import logging

from astropy.io import fits
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import divide_fits_access_by_array
from dkist_processing_math.arithmetic import subtract_array_from_fits_access

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l0_fits_access import VbiL0FitsAccess
from dkist_processing_vbi.tasks.mixin.intermediate_loaders import IntermediateLoaderMixin
from dkist_processing_vbi.vbi_base import VbiScienceTask


class ScienceCalibration(VbiScienceTask, IntermediateLoaderMixin, QualityMixin):
    """
    Class for running full science calibration on a set of Observe images
    """

    def run(self) -> None:
        """
        For each spatial position:
            - Collect dark calibration frame
            - Collect gain calibration frame
            For each dsps repeat number:
                - Collect input frames
                - Subtract dark
                - Divide by gain
                - Write out
        """
        logging.info(
            f"Starting science with {self.num_spatial_steps} steps and {self.num_dsps_repeats} repeats"
        )
        with self.apm_step(
            f"Reducing science frames from {self.num_spatial_steps} steps and {self.num_dsps_repeats} repeats"
        ):
            for exp_time in self.observe_exposure_times:
                for step in range(1, self.num_spatial_steps + 1):
                    logging.info(f"retrieving dark calibration for step {step} and {exp_time = }")
                    dark_calibration_array = self.intermediate_dark_array(
                        spatial_step=step, exposure_time=exp_time
                    )

                    logging.info(f"retrieving gain calibration for step {step}")
                    gain_calibration_array = self.intermediate_gain_array(spatial_step=step)

                    for drep in range(1, self.num_dsps_repeats + 1):
                        apm_str = f"step {step} and repeat number {drep}"
                        logging.info(f"collecting observe frames for {apm_str}")
                        sci_access = self.fits_data_read_fits_access(
                            tags=[
                                VbiTag.input(),
                                VbiTag.frame(),
                                VbiTag.task("OBSERVE"),
                                VbiTag.dsps_repeat(drep),
                                VbiTag.spatial_step(step),
                                VbiTag.exposure_time(exp_time),
                            ],
                            cls=VbiL0FitsAccess,
                        )

                        logging.info(f"subtracting dark from {apm_str}")
                        sci_access = subtract_array_from_fits_access(
                            access_objs=sci_access, array_to_subtract=dark_calibration_array
                        )

                        logging.info(f"dividing gain from {apm_str}")
                        sci_access = divide_fits_access_by_array(
                            access_objs=sci_access, array_to_divide_by=gain_calibration_array
                        )

                        for i, access_obj in enumerate(sci_access):
                            logging.info(f"updating level 1 headers for {apm_str} and exposure {i}")
                            processed_hdu_list = fits.HDUList(
                                [fits.PrimaryHDU(data=access_obj.data, header=access_obj.header)]
                            )

                            logging.info(f"Writing output for {apm_str} and exposure {i}")
                            # It was an intentional decision to not tag with exposure time here
                            self.fits_data_write(
                                processed_hdu_list,
                                tags=[
                                    VbiTag.calibrated(),
                                    VbiTag.frame(),
                                    VbiTag.spatial_step(step),
                                    VbiTag.dsps_repeat(drep),
                                    VbiTag.stokes("I"),
                                ],
                            )

        with self.apm_step("Computing and logging quality metrics"):
            no_of_raw_obs_frames: int = self.count(
                tags=[
                    VbiTag.input(),
                    VbiTag.frame(),
                    VbiTag.task("OBSERVE"),
                ],
            )
            self.quality_store_task_type_counts(
                task_type="observe", total_frames=no_of_raw_obs_frames
            )
