import logging
from typing import Generator

import numpy as np
import peakutils as pku
import scipy.ndimage as spnd
import skimage.registration as skir
from dkist_processing_common.tasks.mixin.quality import QualityMixin
from dkist_processing_math.arithmetic import divide_arrays_by_array
from dkist_processing_math.arithmetic import subtract_array_from_arrays
from dkist_processing_math.feature import find_px_angles
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_processing_math.transform import do_hough
from dkist_processing_math.transform import make_binary
from scipy.optimize import minimize

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.visp_base import VispScienceTask


class GeometricCalibration(VispScienceTask, QualityMixin):
    """
    Task for computing the spectral geometry. Geometry is represented by three quantities:

      - Angle[2] - The angle between slit hairlines and pixel axes for each beam

      - State_offset[2, M, 2] - The [x, y] shift between each modstate in each beam and a fiducial modstate

      - Spectral_shift[2, y] - The shift in the spectral dimension for each beam for every spatial position needed to
                               "straighten" the spectra so a single wavelength is at the same pixel for all slit positions.
    """

    def run(self) -> None:

        # This lives outside the run() loops and has its own internal loops because the angle calculation
        # only happens for a single modstate
        with self.apm_step("Do basic corrections"):
            self.do_basic_corrections()

        with self.apm_step(
            f"Generating geometric calibrations for {self.constants.num_beams} beams"
        ):
            for beam in range(1, self.constants.num_beams + 1):
                logging.info(f"Compute and write angle for {beam=}")
                angle = self.compute_beam_angle(beam=beam)
                self.write_angle(angle=angle, beam=beam)

                for modstate in range(1, self.constants.num_modstates + 1):
                    logging.info(f"Removing angle from {beam=} and {modstate=}")
                    angle_corr_array = self.remove_beam_angle(
                        angle=angle, beam=beam, modstate=modstate
                    )
                    logging.info(f"Computing state offset for {beam=} and {modstate=}")
                    state_offset = self.compute_modstate_offset(
                        array=angle_corr_array, beam=beam, modstate=modstate
                    )
                    self.write_state_offset(offset=state_offset, beam=beam, modstate=modstate)
                    self.remove_state_offset(
                        array=angle_corr_array, offset=state_offset, beam=beam, modstate=modstate
                    )
                logging.info(f"Computing and writing spectral shifts for {beam=}")
                spec_shifts = self.compute_spectral_shifts(beam=beam)
                self.write_spectral_shifts(shifts=spec_shifts, beam=beam)

        with self.apm_step("Finding number of input geometric frames."):
            no_of_raw_geo_frames: int = self.count(
                tags=[
                    VispTag.input(),
                    VispTag.frame(),
                    VispTag.task("SOLAR_GAIN"),
                ],
            )

        with self.apm_step("Sending geometric frame count for quality metric storage"):
            self.quality_store_task_type_counts(
                task_type="GEOMETRIC", total_frames=no_of_raw_geo_frames
            )

    def pre_run(self) -> None:
        super().pre_run()
        self._fiducial_array = None

    def basic_corrected_data(self, beam: int, modstate: int) -> np.ndarray:
        """ The dark/lamp corrected data array for a single beam and modstate """
        array_generator = self.load_intermediate_arrays(
            beam=beam, task="GC_BASIC", modstate=modstate
        )
        return next(array_generator)

    @property
    def fiducial_array(self) -> np.ndarray:
        """ The target array used for determining state offsets """
        if self._fiducial_array is None:
            raise ValueError("Fiducial array has not been set. This should never happen.")
        return self._fiducial_array

    @fiducial_array.setter
    def fiducial_array(self, array: np.ndarray) -> None:
        self._fiducial_array = array

    def offset_corrected_array_generator(self, beam: int) -> Generator[np.ndarray, None, None]:
        """All modstates for a single beam that have had their state offset applied.

        This is a generator because the arrays will be immediately averaged
        """
        array_generator = self.load_intermediate_arrays(beam=beam, task="GC_OFFSET")
        return array_generator

    def do_basic_corrections(self):
        """ Apply dark and lamp corrections to all data that will be used for Geometric Calibration """
        for exp_time in self.constants.solar_exposure_times:
            for beam in range(1, self.constants.num_beams + 1):
                logging.info(f"Starting basic reductions for {exp_time = } and {beam = }")
                try:
                    dark_array = self.load_intermediate_dark_array(
                        beam=beam, exposure_time=exp_time
                    )
                except StopIteration:
                    raise ValueError(f"No matching dark found for {exp_time = } s")

                for modstate in range(1, self.constants.num_modstates + 1):
                    input_solar_arrays = self.input_solar_gain_array_generator(
                        beam=beam,
                        modstate=modstate,
                        exposure_time=exp_time,
                    )
                    avg_solar_array = average_numpy_arrays(input_solar_arrays)

                    lamp_array = self.load_intermediate_lamp_gain_array(
                        beam=beam, modstate=modstate
                    )
                    dark_corrected_solar_array = subtract_array_from_arrays(
                        arrays=avg_solar_array, array_to_subtract=dark_array
                    )

                    # Technically speaking the lamp correction is unnecessary and we might actually find that it negatively
                    # affects the Geometric Calibration. No big deal if it is taken out.
                    lamp_corrected_solar_array = next(
                        divide_arrays_by_array(
                            arrays=dark_corrected_solar_array, array_to_divide_by=lamp_array
                        )
                    )

                    logging.info(f"Writing dark/lamp corrected data for {beam=}, {modstate=}")
                    self.write_intermediate_arrays(
                        arrays=lamp_corrected_solar_array,
                        beam=beam,
                        modstate=modstate,
                        task="GC_BASIC",
                    )

    def compute_beam_angle(self, beam: int) -> float:
        """Find the angle between the slit hairlines and the pixel axes for a single beam

        Generally, the algorithm is:

         1. Convert the spectra to a binary image that separates the lower-signal hairlines
         2. Use a Hough Transform to identify these hairlines
         3. Fit a peak to the Hough array to find the most prominant angle
        """
        logging.info(f"Finding angle using modstate 1 from beam {beam}")
        beam_array = self.basic_corrected_data(beam=beam, modstate=1)

        numotsu = self.parameters.geo_num_otsu
        numtheta = self.parameters.geo_num_theta
        theta_min = self.parameters.geo_theta_min
        theta_max = self.parameters.geo_theta_max

        binary = make_binary(beam_array, numotsu=numotsu)
        H, t, r = do_hough(binary, theta_min=theta_min, theta_max=theta_max, numtheta=numtheta)
        peak_theta = float(find_px_angles(H, t)[0])

        logging.info(f"Beam angle for {beam=}: {np.rad2deg(peak_theta):0.3f} deg")
        return peak_theta

    def remove_beam_angle(self, angle: float, beam: int, modstate: int) -> np.ndarray:
        """ Rotate a single modstate and beam's data by the beam angle """
        logging.info(f"Removing beam angle from {beam=}, {modstate=}")
        # TODO: Figure out why the type of basic_corrected_data was >f8 prior to conversion
        beam_mod_array = self.basic_corrected_data(beam=beam, modstate=modstate).astype(np.float64)
        corrected_array = next(self.correct_geometry(beam_mod_array, angle=angle))
        return corrected_array

    def compute_modstate_offset(self, array: np.ndarray, beam: int, modstate: int) -> np.ndarray:
        """A higher-level helper function to compute the (x, y) offset between modstates

        Exists so the fiducial array can be set from the first beam and modstate
        """
        if beam == 1 and modstate == 1:
            self.fiducial_array = array
            return np.zeros(2)

        shift = self.compute_single_state_offset(
            fiducial_array=self.fiducial_array,
            array=array,
            upsample_factor=self.parameters.geo_upsample_factor,
        )
        logging.info(f"Offset for {beam=} and {modstate=} is {np.array2string(shift, precision=3)}")

        return shift

    def remove_state_offset(
        self, array: np.ndarray, offset: np.ndarray, beam: int, modstate: int
    ) -> None:
        """ Shift an array by some offset (to make it in line with the fiducial array) """
        corrected_array = next(self.correct_geometry(array, shift=offset))
        self.write_intermediate_arrays(
            arrays=corrected_array, modstate=modstate, beam=beam, task="GC_OFFSET"
        )

    def compute_spectral_shifts(self, beam: int) -> np.ndarray:
        """Compute the spectral "curvature"

        I.e., the spectral shift at each slit position needed to have wavelength be constant across a single spatial
        pixel. Generally, the algorithm is:

         1. Identify the fiducial spectrum as the center of the slit
         2. For each slit position, make an initial guess of the shift via correlation
         3. Take the initial guesses and use them in a chisq minimizer to refine the shifts
         4. Interpolate over those shifts identified as too large
         5. Remove the mean shift so the total shift amount is minimized
        """
        max_shift = self.parameters.geo_max_shift
        poly_fit_order = self.parameters.geo_poly_fit_order

        logging.info(f"Computing spectral shifts for beam {beam}")
        beam_generator = self.offset_corrected_array_generator(beam=beam)
        avg_beam_array = average_numpy_arrays(beam_generator)
        num_spec = avg_beam_array.shape[1]

        ref_spec = avg_beam_array[:, num_spec // 2]
        beam_shifts = np.empty(num_spec) * np.nan
        for j in range(num_spec):
            target_spec = avg_beam_array[:, j]

            ## Correlate the target and reference beams to get an initial guess
            corr = np.correlate(
                target_spec - np.nanmean(target_spec),
                ref_spec - np.nanmean(ref_spec),
                mode="same",
            )
            # This min_dist ensures we only find a single peak in each correlation signal
            pidx = pku.indexes(corr, min_dist=corr.size)
            initial_guess = 1 * (pidx - corr.size // 2)

            # These edge-cases are very rare, but do happen sometimes
            if initial_guess.size == 0:
                logging.info(
                    f"Spatial position {j} in {beam=} doesn't have a correlation peak. Initial guess set to 0"
                )
                initial_guess = 0.0

            elif initial_guess.size > 1:
                logging.info(
                    f"Spatial position {j} in {beam=} has more than one correlation peak ({initial_guess}). Initial guess set to mean ({np.nanmean(initial_guess)})"
                )
                initial_guess = np.nanmean(initial_guess)

            ## Then refine shift with a chisq minimization
            shift = minimize(
                self.shift_chisq,
                np.array([float(initial_guess)]),
                args=(ref_spec, target_spec),
                method="nelder-mead",
            ).x[0]
            if np.abs(shift) > max_shift:
                # Didn't find a good peak, probably because of a hairline
                logging.info(
                    f"shift in {beam=} at spatial pixel {j} out of range ({shift} > {max_shift})"
                )
                continue

            beam_shifts[j] = shift

        ## Subtract the average so we shift my a minimal amount
        beam_shifts -= np.nanmean(beam_shifts)

        ## Finally, interpolate out-of-range shifts
        nan_idx = np.isnan(beam_shifts)
        logging.info(
            f"Interpolating {np.sum(nan_idx)} ({np.sum(nan_idx) / num_spec * 100:0.2f} %) out-of-range pixels"
        )
        poly = np.poly1d(
            np.polyfit(np.arange(num_spec)[~nan_idx], beam_shifts[~nan_idx], poly_fit_order)
        )
        nan_x = np.arange(num_spec)[nan_idx]
        beam_shifts[nan_idx] = poly(nan_x)

        return beam_shifts

    @staticmethod
    def compute_single_state_offset(
        fiducial_array: np.ndarray, array: np.ndarray, upsample_factor: float = 1000.0
    ) -> np.ndarray:
        """Find the (x, y) shift between the current beam and the reference beam.

        The shift is found by fitting the peak of the correlation of the two beams

        Parameters
        ----------
        fiducial_array
            Reference beam from mod state 1 data

        array
            Beam data from current mod state

        Returns
        -------
        numpy.ndarray
            The (x, y) shift between the reference beam and the current beam at hand
        """
        # Pixel precision is 1/upsample factor
        shift = skir.phase_cross_correlation(
            fiducial_array, array, return_error=False, upsample_factor=upsample_factor
        )

        # Multiply by -1 so that the output is the shift needed to move from "perfect" to the current state.
        #  In other words, applying a shift equal to the negative of the output of this function will undo the measured
        #  shift.
        return -shift

    @staticmethod
    def shift_chisq(par: np.ndarray, ref_spec: np.ndarray, spec: np.ndarray) -> float:
        """
        Goodness of fit calculation for a simple shift. Uses simple chisq as goodness of fit.
        Less robust than SolarCalibration's `reshift`, but waaaay faster
        """
        shift = par[0]
        shifted_spec = spnd.shift(spec, -shift, mode="constant", cval=np.nan)
        chisq = np.nansum((ref_spec - shifted_spec) ** 2 / ref_spec)
        return chisq

    def write_angle(self, angle: float, beam: int) -> None:
        """ Write the angle component of the geometric calibration for a single beam """
        array = np.array([angle])
        self.write_intermediate_arrays(arrays=array, beam=beam, task="GEOMETRIC_ANGLE")

    def write_state_offset(self, offset: np.ndarray, beam: int, modstate: int) -> None:
        """ Write the state offset component of the geometric calibration for a single modstate and beam """
        self.write_intermediate_arrays(
            arrays=offset, beam=beam, modstate=modstate, task="GEOMETRIC_OFFSET"
        )

    def write_spectral_shifts(self, shifts: np.ndarray, beam: int) -> None:
        """ Write the spectral shift component of the geometric calibration for a single beam """
        self.write_intermediate_arrays(arrays=shifts, beam=beam, task="GEOMETRIC_SPEC_SHIFTS")
