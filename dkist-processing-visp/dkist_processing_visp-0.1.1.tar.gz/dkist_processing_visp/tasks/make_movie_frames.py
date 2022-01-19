import logging

import numpy as np
from astropy.io import fits

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.visp_base import VispScienceTask
from dkist_processing_visp.visp_l1_fits_access import VispL1FitsAccess


class MakeVispMovieFrames(VispScienceTask):
    """
    For each stokes state:
        For each dsps repeat:
          - Integrate each step in the scan over wavelength into a single column of pixels
          - Build a movie frame by lining the columns up side by side
          - Write full wavelength integrated frame as a "MOVIE_FRAME"
    """

    def run(self):
        is_polarized = False
        stokes_states = ["I", "Q", "U", "V"]
        # Loop over the number of raster scans
        for dsps_repeat in range(1, self.num_dsps_repeats + 1):
            with self.apm_step(f"Making movie frame for raster scan {dsps_repeat}"):
                instrument_set = set()
                wavelength_set = set()
                time_obs = []
                # Loop over the stokes states to add them to the frame array
                for stokes_state in stokes_states:
                    stokes_paths = list(
                        self.read(
                            tags=[VispTag.frame(), VispTag.output(), VispTag.stokes(stokes_state)]
                        )
                    )
                    if len(stokes_paths) > 0:
                        # Loop over the raster steps in a single scan
                        for raster_step in range(1, self.num_raster_steps + 1):
                            calibrated_frame: VispL1FitsAccess = next(
                                self.fits_data_read_fits_access(
                                    tags=[
                                        VispTag.frame(),
                                        VispTag.output(),
                                        VispTag.stokes(stokes_state),
                                        VispTag.dsps_repeat(dsps_repeat),
                                        VispTag.raster_step(raster_step),
                                    ],
                                    cls=VispL1FitsAccess,
                                )
                            )
                            data = calibrated_frame.data
                            if self.num_raster_steps == 1:
                                logging.info(
                                    "Only a single raster step found. Making a spectral movie."
                                )
                                stokes_frame_data = data
                            else:
                                wavelength_integrated_data = np.sum(data, axis=-1)
                                if raster_step == 1:
                                    stokes_frame_data = wavelength_integrated_data[:, None]
                                else:
                                    stokes_frame_data = np.concatenate(
                                        (stokes_frame_data, wavelength_integrated_data[:, None]),
                                        axis=1,
                                    )
                            # Grab the relevant header info from the frame
                            instrument_set.add(calibrated_frame.instrument)
                            wavelength_set.add(calibrated_frame.wavelength)
                            time_obs.append(calibrated_frame.time_obs)

                        # Encode the data as a specific stokes state
                        if stokes_state == "I":
                            stokes_i_data = stokes_frame_data
                        if stokes_state == "Q":
                            is_polarized = True
                            stokes_q_data = stokes_frame_data
                        if stokes_state == "U":
                            is_polarized = True
                            stokes_u_data = stokes_frame_data
                        if stokes_state == "V":
                            is_polarized = True
                            stokes_v_data = stokes_frame_data

                # Use the most recently read header as the base header because we need to be able to read it
                # with VispL1FitsAccess. We'll update the values we actually care about below.
                header = fits.Header(calibrated_frame.header)

                # Make sure only one instrument value was found
                if len(instrument_set) != 1:
                    raise ValueError(
                        f"There should only be one instrument value in the headers. "
                        f"Found {len(instrument_set)}: {instrument_set=}"
                    )
                header["INSTRUME"] = instrument_set.pop()
                # The timestamp of a movie frame will be the time of raster scan start
                header["DATE-BEG"] = time_obs[0]
                # Make sure only one wavelength value was found
                if len(wavelength_set) != 1:
                    raise ValueError(
                        f"There should only be one wavelength value in the headers. "
                        f"Found {len(wavelength_set)}: {wavelength_set=}"
                    )
                header["LINEWAV"] = wavelength_set.pop()
                # Write the movie frame file to disk and tag it
                if is_polarized:
                    movie_frame_data = np.concatenate(
                        (
                            np.concatenate((stokes_i_data, stokes_q_data), axis=1),
                            np.concatenate((stokes_u_data, stokes_v_data), axis=1),
                        ),
                        axis=0,
                    )
                else:
                    movie_frame_data = stokes_i_data

                self.fits_data_write(
                    hdu_list=fits.HDUList(
                        [fits.PrimaryHDU(header=header, data=np.asarray(movie_frame_data))]
                    ),
                    tags=[
                        VispTag.dsps_repeat(dsps_repeat),
                        VispTag.movie_frame(),
                    ],
                )
