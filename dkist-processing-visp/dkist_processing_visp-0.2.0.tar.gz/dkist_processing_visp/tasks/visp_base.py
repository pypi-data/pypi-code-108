from abc import ABC
from typing import Generator
from typing import Iterable
from typing import Optional
from typing import TypeVar
from typing import Union

import numpy as np
import scipy.ndimage as spnd
from astropy.io import fits
from dkist_processing_common.models.fits_access import FitsAccessBase
from dkist_processing_common.tasks import ScienceTaskL0ToL1Base
from dkist_processing_common.tasks.mixin.input_dataset import InputDatasetMixin
from dkist_processing_math.transform.affine import affine_transform_arrays
from dkist_processing_math.transform.affine import rotate_arrays_about_point

from dkist_processing_visp.models.constants import VispConstants
from dkist_processing_visp.models.parameters import VispParameters
from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess


class VispScienceTask(ScienceTaskL0ToL1Base, InputDatasetMixin, ABC):
    """"""

    F = TypeVar("F", bound=FitsAccessBase)

    def __init__(
        self,
        recipe_run_id: int,
        workflow_name: str,
        workflow_version: str,
    ):
        super().__init__(
            recipe_run_id=recipe_run_id,
            workflow_name=workflow_name,
            workflow_version=workflow_version,
        )
        self.constants = VispConstants(self._constants_db)
        self.parameters = VispParameters(
            self.input_dataset_parameters, wavelength=self.constants.wavelength
        )

    def matching_beam_2_fits_access(self, beam_1_fits_access: VispL0FitsAccess) -> VispL0FitsAccess:
        all_tags = list(self.scratch.tags(beam_1_fits_access.name))
        all_tags.remove(VispTag.beam(1))
        beam_1_match_id = beam_1_fits_access.beam_match_id

        all_matching_beam_2_obj = self.fits_data_read_fits_access(
            tags=all_tags + [VispTag.beam(2)], cls=VispL0FitsAccess
        )
        beam_2_obj: VispL0FitsAccess
        for beam_2_obj in all_matching_beam_2_obj:
            if beam_2_obj.beam_match_id == beam_1_match_id:
                return beam_2_obj

        raise FileNotFoundError(f"Could not find a beam2 match for {beam_1_fits_access.name}")

    def load_intermediate_arrays(
        self,
        beam: Optional[int] = None,
        task: Optional[str] = None,
        modstate: Optional[int] = None,
        exposure_time: Optional[float] = None,
    ) -> Generator[np.ndarray, None, None]:
        """
        Yield a generator that produces ndarrays for the requested tags
        """
        # See write_intermediate_arrays for an explanation of how this works, to add new tags *all* that's needed
        # is to add a kwarg that has the same name as a tag
        passed_args = locals()
        tags = [VispTag.intermediate(), VispTag.frame()]
        for t, v in passed_args.items():
            if t not in ["self"] and v is not None:
                tags.append(getattr(VispTag, t)(v))

        for path, hdu in self.fits_data_read_hdu(tags=tags):
            yield hdu.data

    def load_intermediate_dark_array(
        self, beam: Optional[int] = None, exposure_time: Optional[float] = None
    ) -> np.ndarray:
        return next(
            self.load_intermediate_arrays(beam=beam, task="DARK", exposure_time=exposure_time)
        )

    def load_intermediate_lamp_gain_array(
        self, beam: Optional[int] = None, modstate: Optional[int] = None
    ) -> np.ndarray:
        return next(self.load_intermediate_arrays(beam=beam, task="LAMP_GAIN", modstate=modstate))

    def load_intermediate_solar_gain_array(
        self, beam: Optional[int] = None, modstate: Optional[int] = None
    ) -> np.ndarray:
        return next(self.load_intermediate_arrays(beam=beam, task="SOLAR_GAIN", modstate=modstate))

    def load_intermediate_demodulated_arrays(
        self, beam: Optional[int] = None, modstate: Optional[int] = None
    ) -> Generator[np.ndarray, None, None]:
        return self.load_intermediate_arrays(
            beam=beam, task="DEMODULATED_ARRAYS", modstate=modstate
        )

    def write_intermediate_arrays(
        self,
        arrays: Union[Iterable[np.ndarray], np.ndarray],
        headers: Optional[Union[Iterable[fits.Header], fits.Header]] = None,
        beam: Optional[int] = None,
        modstate: Optional[int] = None,
        dsps_repeat: Optional[int] = None,
        raster_step: Optional[int] = None,
        task: Optional[str] = None,
        exposure_time: Optional[float] = None,
    ) -> None:
        # To add a new tag all you need to do is add a kwarg that has the same name as a tag. That's it!
        ## Construct the tags based on which optional parameters were passed
        passed_args = locals()
        tags = [VispTag.intermediate(), VispTag.frame()]
        for t, v in passed_args.items():
            # Look at all the arguments passed to this function, ignore those that aren't tags
            # and update tags with those that aren't None
            if t not in ["self", "arrays", "headers"] and v is not None:
                tags.append(getattr(VispTag, t)(v))

        arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
        if headers is not None:
            headers = [headers] if isinstance(headers, fits.Header) else headers
        else:
            headers = [None] * len(arrays)

        for array, header in zip(arrays, headers):
            hdul = fits.HDUList([fits.PrimaryHDU(data=array, header=header)])
            self.fits_data_write(hdu_list=hdul, tags=tags)

    def load_intermediate_demod_matrices(self, beam_num: int) -> np.ndarray:
        tags = [
            VispTag.intermediate(),
            VispTag.task("DEMOD_MATRICES"),
            VispTag.beam(beam_num),
        ]
        path, hdu = next(self.fits_data_read_hdu(tags=tags))
        return hdu.data

    def input_fits_access_generator(
        self,
        beam: Optional[int] = None,
        modstate: Optional[int] = None,
        dsps_repeat: Optional[int] = None,
        raster_step: Optional[int] = None,
        task: Optional[str] = None,
        cs_step: Optional[int] = None,
        exposure_time: Optional[float] = None,
    ) -> Generator[F, None, None]:
        passed_args = locals()
        tags = [VispTag.input(), VispTag.frame()]
        for t, v in passed_args.items():
            if t not in ["self"] and v is not None:
                tags.append(getattr(VispTag, t)(v))

        frame_generator = self.fits_data_read_fits_access(tags, cls=VispL0FitsAccess)
        return frame_generator

    def input_dark_array_generator(
        self, beam: Optional[int] = None, exposure_time: Optional[float] = None
    ) -> Generator[np.ndarray, None, None]:
        dark_array_fits_access = self.input_fits_access_generator(
            task="DARK", beam=beam, exposure_time=exposure_time
        )
        return (array.data for array in dark_array_fits_access)

    def input_lamp_gain_array_generator(
        self,
        beam: Optional[int] = None,
        modstate: Optional[int] = None,
        exposure_time: Optional[float] = None,
    ) -> Generator[np.ndarray, None, None]:
        lamp_gain_array_fits_access = self.input_fits_access_generator(
            task="LAMP_GAIN", beam=beam, modstate=modstate, exposure_time=exposure_time
        )
        return (array.data for array in lamp_gain_array_fits_access)

    def input_solar_gain_array_generator(
        self,
        beam: Optional[int] = None,
        modstate: Optional[int] = None,
        exposure_time: Optional[float] = None,
    ) -> Generator[np.ndarray, None, None]:
        solar_gain_array_fits_access = self.input_fits_access_generator(
            task="SOLAR_GAIN", beam=beam, modstate=modstate, exposure_time=exposure_time
        )
        return (array.data for array in solar_gain_array_fits_access)

    def input_observe_fits_access_generator(
        self,
        beam: Optional[int] = None,
        modstate: Optional[int] = None,
        raster_step: Optional[int] = None,
        dsps_repeat: Optional[int] = None,
        exposure_time: Optional[float] = None,
    ) -> Generator[FitsAccessBase, None, None]:
        return self.input_fits_access_generator(
            task="OBSERVE",
            beam=beam,
            modstate=modstate,
            raster_step=raster_step,
            dsps_repeat=dsps_repeat,
            exposure_time=exposure_time,
        )

    def input_polcal_fits_access_generator(
        self,
        beam: Optional[int] = None,
        modstate: Optional[int] = None,
        cs_step: Optional[int] = None,
        exposure_time: Optional[float] = None,
    ) -> Generator[FitsAccessBase, None, None]:
        return self.input_fits_access_generator(
            task="POLCAL",
            beam=beam,
            modstate=modstate,
            cs_step=cs_step,
            exposure_time=exposure_time,
        )

    def intermediate_fits_access_generator(
        self,
        tags: Iterable[str],
    ) -> Generator[F, None, None]:
        tags += [VispTag.intermediate(), VispTag.frame()]
        frame_generator = self.fits_data_read_fits_access(tags, cls=VispL0FitsAccess)
        return frame_generator

    def get_angle(self, beam: int) -> float:
        angle_array = next(self.load_intermediate_arrays(beam=beam, task="GEOMETRIC_ANGLE"))
        return angle_array[0]

    def get_state_offset(self, beam: int, modstate: int) -> np.ndarray:
        offset = next(
            self.load_intermediate_arrays(beam=beam, task="GEOMETRIC_OFFSET", modstate=modstate)
        )
        return offset

    def get_spec_shift(self, beam: int) -> np.ndarray:
        shifts = next(self.load_intermediate_arrays(beam=beam, task="GEOMETRIC_SPEC_SHIFTS"))
        return shifts

    @staticmethod
    def correct_geometry(
        arrays: Union[Iterable[np.ndarray], np.ndarray],
        shift: np.ndarray = np.zeros(2),
        angle: float = 0.0,
    ) -> Generator[np.ndarray, None, None]:
        """A simple function to shift and then rotate data.
        It applies the inverse of the given shift and angle."""
        arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
        for array in arrays:
            array[np.where(array == np.inf)] = np.max(array[np.isfinite(array)])
            array[np.where(array == -np.inf)] = np.min(array[np.isfinite(array)])
            array[np.isnan(array)] = np.nanmedian(array)
            translated = affine_transform_arrays(
                array, translation=-shift, mode="constant", cval=np.nanmedian(array)
            )
            yield next(
                rotate_arrays_about_point(
                    translated, angle=-angle, mode="constant", cval=np.nanmedian(array)
                )
            )

    @staticmethod
    def remove_spec_geometry(
        arrays: Union[Iterable[np.ndarray], np.ndarray], spec_shift: np.ndarray
    ) -> Generator[np.ndarray, None, None]:
        """Remove spectral curvature.

        This is a pretty simple function that simply undoes the computed spectral shifts.

        Parameters
        ----------
        arrays
            2D array(s) containing the data for the un-distorted beam

        spec_shift
            Array with shape (X), where X is the number of pixels in the spatial dimension.
            This dimension gives the spectral shift.

        Returns
        -------
            2D array(s) containing the data of the corrected beam

        """
        arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
        for array in arrays:
            numy = array.shape[1]
            array_output = np.zeros(array.shape)
            for j in range(numy):
                array_output[:, j] = spnd.interpolation.shift(
                    array[:, j], -spec_shift[j], mode="constant", cval=np.nanmedian(array[:, j])
                )
            yield array_output
