from dataclasses import dataclass
from dataclasses import field
from typing import List

import numpy as np
from astropy.time import Time
from dkist_processing_common.tasks.mixin.quality import QualityMixin

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_quality_fits_access import VispL1QualityFitsAccess
from dkist_processing_visp.visp_base import VispScienceTask


@dataclass
class _QualityData:
    datetimes: List[str] = field(default_factory=list)
    Q_RMS_noise: List[float] = field(default_factory=list)
    U_RMS_noise: List[float] = field(default_factory=list)
    V_RMS_noise: List[float] = field(default_factory=list)
    intensity_values: List[float] = field(default_factory=list)


class VispQualityMetrics(VispScienceTask, QualityMixin):
    def run(self) -> None:
        with self.apm_step("Calculating L1 ViSP quality metrics"):
            if self.correct_for_polarization:
                self.compute_polarimetric_metrics()

    def compute_polarimetric_metrics(self) -> None:
        with self.apm_step("Calculating polarization metrics"):
            all_datetimes = []
            all_Q_RMS_noise = []
            all_U_RMS_noise = []
            all_V_RMS_noise = []
            all_pol_sens_values = []
            for drep in range(1, self.num_dsps_repeats + 1):
                polarization_data = _QualityData()
                for step in range(1, self.num_raster_steps + 1):

                    # grab stokes I data
                    stokesI_frame = next(
                        self.fits_data_read_fits_access(
                            tags=[
                                VispTag.output(),
                                VispTag.frame(),
                                VispTag.raster_step(step),
                                VispTag.dsps_repeat(drep),
                                VispTag.stokes("I"),
                            ],
                            cls=VispL1QualityFitsAccess,
                        )
                    )
                    stokesI_data = stokesI_frame.data
                    polarization_data.datetimes.append(Time(stokesI_frame.time_obs).mjd)
                    polarization_data.intensity_values.append(np.max(stokesI_data))

                    # grab other stokes data and find and store RMS noise
                    for stokes_param, data_list in zip(
                        ("Q", "U", "V"),
                        (
                            polarization_data.Q_RMS_noise,
                            polarization_data.U_RMS_noise,
                            polarization_data.V_RMS_noise,
                        ),
                    ):
                        stokes_frame = next(
                            self.fits_data_read_fits_access(
                                tags=[
                                    VispTag.output(),
                                    VispTag.frame(),
                                    VispTag.raster_step(step),
                                    VispTag.dsps_repeat(drep),
                                    VispTag.stokes(stokes_param),
                                ],
                                cls=VispL1QualityFitsAccess,
                            )
                        )
                        # find Stokes RMS noise
                        data_list.append(np.std(stokes_frame.data / stokesI_data))

                all_datetimes.append(Time(np.mean(polarization_data.datetimes), format="mjd").isot)
                all_Q_RMS_noise.append(np.average(polarization_data.Q_RMS_noise))
                all_U_RMS_noise.append(np.average(polarization_data.U_RMS_noise))
                all_V_RMS_noise.append(np.average(polarization_data.V_RMS_noise))
                # find the polarimetric sensitivity of this drep (smallest intensity signal measured)
                polarimetric_sensitivity = 1 / np.max(polarization_data.intensity_values)
                all_pol_sens_values.append(polarimetric_sensitivity)

        with self.apm_step("Sending lists for storage"):
            for stokes_index, stokes_noise in zip(
                ("Q", "U", "V"), (all_Q_RMS_noise, all_U_RMS_noise, all_V_RMS_noise)
            ):
                self.quality_store_polarimetric_noise(
                    stokes=stokes_index, datetimes=all_datetimes, values=stokes_noise
                )
            self.quality_store_polarimetric_sensitivity(
                datetimes=all_datetimes, values=all_pol_sens_values
            )
