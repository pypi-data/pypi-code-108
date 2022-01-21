import logging
from typing import Generator
from typing import Iterable

import numpy as np
from astropy.io import fits
from astropy.time import Time
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_processing_pac import generic
from dkist_processing_pac.TelescopeModel import TelescopeModel

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.tasks.visp_base import VispScienceTask


class ScienceCalibration(VispScienceTask, QualityMixin):
    def run(self):
        """
        Science Polarization Calibration Task:
            Iterate over beams
                Reduce cal sequence steps for each beam

        Returns
        -------

        """

        telescope_db = generic.get_default_telescope_db()

        # Process the science frames
        # TODO: Major cleanup of this loop needed; the many of the calibration steps aren't dependent on the variables
        #  at the core of the loop
        with self.apm_step("Initial reductions"):
            for exp_time in self.constants.observe_exposure_times:
                for beam in range(1, self.constants.num_beams + 1):
                    if self.constants.correct_for_polarization:
                        logging.info(f"Load demodulation matrices for beam {beam}")
                        demod_matrices = self.load_intermediate_demod_matrices(beam_num=beam)
                    try:
                        dark_array = self.load_intermediate_dark_array(
                            beam=beam, exposure_time=exp_time
                        )
                    except StopIteration:
                        raise ValueError(f"No matching dark found for {exp_time = } s")

                    for dsps_repeat in range(1, self.constants.num_dsps_repeats + 1):
                        for raster_step in range(1, self.constants.num_raster_steps + 1):
                            logging.info(
                                f"Processing observe frames from {beam=}, {dsps_repeat=}, and {raster_step=}"
                            )
                            # Initialize array_stack and headers
                            if self.constants.correct_for_polarization:
                                # Create the 3D stack of corrected modulated arrays
                                array_stack = np.zeros(
                                    (
                                        dark_array.shape[0],
                                        dark_array.shape[1],
                                        self.constants.num_modstates,
                                    )
                                )
                                header_stack = []
                            else:
                                array_stack = None
                                header_stack = None
                            for modstate in range(1, self.constants.num_modstates + 1):
                                # Correct the arrays
                                (corrected_arrays, corrected_headers,) = self.correct_frames(
                                    beam,
                                    modstate,
                                    raster_step,
                                    dsps_repeat,
                                    exp_time,
                                    dark_array,
                                )
                                if self.constants.correct_for_polarization:
                                    # Add this result to the 3D stack
                                    array_stack[:, :, modstate - 1] = next(corrected_arrays)
                                    header_stack.append(next(corrected_headers))

                            if self.constants.correct_for_polarization:
                                intermediate_arrays = self.polarization_correction(
                                    array_stack, demod_matrices
                                )
                                intermediate_headers = header_stack[len(header_stack) // 2]
                            else:
                                intermediate_headers = next(corrected_headers)
                                intermediate_arrays = next(corrected_arrays)

                            self.write_intermediate_arrays(
                                intermediate_arrays,
                                intermediate_headers,
                                beam,
                                dsps_repeat,
                                raster_step,
                                task="INTERMEDIATE_ARRAYS",
                            )

        # Now combine the beams
        with self.apm_step("Combining beams"):
            logging.info("Combining beams")
            averaged_beams = self.average_beams()
        if self.constants.correct_for_polarization:
            with self.apm_step("Correcting telescope polarization"):
                final_fits_access = self.telescope_polarization_correction(
                    averaged_beams, telescope_db
                )
        else:
            final_fits_access = averaged_beams

        # Save the final output files
        with self.apm_step("Writing calibrated arrays"):
            logging.info("Writing calibrated arrays")
            for final_object in final_fits_access:
                if self.constants.correct_for_polarization:  # Write all 4 stokes params
                    for i, stokes_param in enumerate(self.constants.stokes_params):
                        final_data = self._re_dummy_data(final_object.data[:, :, i])
                        hdul = fits.HDUList(
                            [fits.PrimaryHDU(header=final_object.header, data=final_data)]
                        )
                        output_tags = [
                            VispTag.calibrated(),
                            VispTag.frame(),
                            VispTag.stokes(stokes_param),
                            VispTag.raster_step(final_object.raster_scan_step),
                            VispTag.dsps_repeat(final_object.current_dsps_repeat),
                        ]

                        self.fits_data_write(
                            hdu_list=hdul,
                            tags=output_tags,
                        )
                        # Just for debugging
                        filename = next(self.read(tags=output_tags))
                        logging.info(
                            f"Wrote calibrated Science for {stokes_param}, {final_object.raster_scan_step=}, and {final_object.current_dsps_repeat=} to {filename}"
                        )
                else:  # Only write stokes I
                    final_data = self._re_dummy_data(final_object.data)
                    hdul = fits.HDUList(
                        [fits.PrimaryHDU(header=final_object.header, data=final_data)]
                    )
                    output_tags = [
                        VispTag.calibrated(),
                        VispTag.frame(),
                        VispTag.stokes("I"),
                        VispTag.raster_step(final_object.raster_scan_step),
                        VispTag.dsps_repeat(final_object.current_dsps_repeat),
                    ]
                    self.fits_data_write(hdu_list=hdul, tags=output_tags)
                    filename = next(self.read(tags=output_tags))
                    logging.info(
                        f"Wrote calibrated intensity-only Science for raster scan step {final_object.raster_scan_step} and current dsps {final_object.current_dsps_repeat} to {filename}"
                    )
        with self.apm_step("Finding number of input science frames."):
            no_of_raw_science_frames: int = self.count(
                tags=[
                    VispTag.input(),
                    VispTag.frame(),
                    VispTag.task("OBSERVE"),
                ],
            )

        with self.apm_step("Sending science frame count for quality metric storage"):
            self.quality_store_task_type_counts(
                task_type="OBSERVE", total_frames=no_of_raw_science_frames
            )

    def correct_frames(
        self,
        beam: int,
        modstate: int,
        raster_step: int,
        dsps_repeat: int,
        exp_time: float,
        dark_array: np.ndarray,
    ):

        """

        Parameters
        ----------
        beam
            The beam number for this single step
        modstate
            The modulator state for this single step.
        dark_array
            The dark array to be used during dark correction

        Returns
        -------
            Corrected array(s), header(s)
        """

        with self.apm_step("Get geometric objects for this beam and modstate"):
            angle = self.get_angle(beam=beam)
            state_offset = self.get_state_offset(beam=beam, modstate=modstate)
            spec_shift = self.get_spec_shift(beam=beam)
        with self.apm_step(
            "Get observe object(s) for this beam, raster_step, DSPS repeat and modstate"
        ):
            # Get the headers and arrays as iterables
            observe_headers = (
                obj.header
                for obj in self.input_observe_fits_access_generator(
                    beam=beam,
                    modstate=modstate,
                    raster_step=raster_step,
                    dsps_repeat=dsps_repeat,
                    exposure_time=exp_time,
                )
            )
            observe_arrays = (
                obj.data
                for obj in self.input_observe_fits_access_generator(
                    beam=beam,
                    modstate=modstate,
                    raster_step=raster_step,
                    dsps_repeat=dsps_repeat,
                    exposure_time=exp_time,
                )
            )

        if self.constants.correct_for_polarization:
            # Average the arrays (this works for a single array as well)
            observe_arrays = average_numpy_arrays(observe_arrays)
        with self.apm_step("Dark correct the array(s)"):
            dark_corrected_arrays = next(subtract_array_from_arrays(observe_arrays, dark_array))
        with self.apm_step("Solar gain correct the array(s)"):
            solar_gain_array = self.load_intermediate_solar_gain_array(beam=beam, modstate=modstate)
            gain_corrected_arrays = next(
                divide_arrays_by_array(dark_corrected_arrays, solar_gain_array)
            )
        with self.apm_step("Geo correct the array(s)"):
            geo_corrected_arrays = next(
                self.correct_geometry(gain_corrected_arrays, state_offset, angle)
            )
        with self.apm_step("Perform spectral correction"):
            spectral_corrected_arrays = self.remove_spec_geometry(geo_corrected_arrays, spec_shift)
        return spectral_corrected_arrays, observe_headers

    @staticmethod
    def polarization_correction(array_stack: np.ndarray, demod_matrices: np.ndarray) -> np.ndarray:
        # Arthur's awesome way to matrix multiply each (x, y) stack by the demod matrix
        # to yield an array that us (nx, ny, 4) with the planes being IQUV
        demodulated_array = np.sum(demod_matrices * array_stack[:, :, None, :], axis=3)
        return demodulated_array

    def telescope_polarization_correction(
        self,
        inst_demod_objects: Iterable[VispL0FitsAccess],
        telescope_db: str,
    ) -> Generator[VispL0FitsAccess, None, None]:
        for obj in inst_demod_objects:
            wavelength = obj.wavelength
            # obstime = Time(obj.date_begin, format="iso")
            obstime = Time(obj.time_obs)
            tm = TelescopeModel(obj.azimuth, obj.elevation, obj.table_angle)
            tm.load_from_database(telescope_db, obstime.mjd, wavelength)
            mueller_matrix = tm.generate_inverse_telescope_model(M12=True, include_parallactic=True)
            obj.data = self.polarization_correction(obj.data, mueller_matrix)
            yield obj

    def average_beams(self) -> Generator[VispL0FitsAccess, None, None]:
        # Get matching arrays for beam 1 and beam 2
        # average them
        # yield a single result array
        corrected_fits_access_beam1 = self.intermediate_fits_access_generator(
            tags=[
                VispTag.task("INTERMEDIATE_ARRAYS"),
                VispTag.beam(1),
            ]
        )
        for beam1_fits_access in corrected_fits_access_beam1:
            beam2_fits_access = self.matching_beam_2_fits_access(beam1_fits_access)
            header = beam1_fits_access.header
            avg_array = average_numpy_arrays([beam1_fits_access.data, beam2_fits_access.data])
            hdu = fits.PrimaryHDU(header=header, data=avg_array)
            yield VispL0FitsAccess(hdu=hdu, name=None)

    def _re_dummy_data(self, data: np.ndarray):
        """
        Add the dummy dimension that we have been secretly squeezing out during processing

        The dummy dimension is required because its corresponding WCS axis contains important information
        """
        logging.debug(f"Adding dummy WCS dimension to array with shape {data.shape}")
        return data[None, :, :]
