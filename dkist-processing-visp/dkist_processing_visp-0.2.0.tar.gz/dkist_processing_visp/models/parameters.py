import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import numpy as np
from dkist_processing_common.models.parameters import ParameterBase
from dkist_processing_common.tasks.mixin.input_dataset import InputDatasetParameterValue


class VispParameters(ParameterBase):
    def __init__(
        self,
        input_dataset_parameters: Dict[str, List[InputDatasetParameterValue]],
        wavelength: Optional[float] = None,
    ):
        super().__init__(input_dataset_parameters)
        self._wavelength = wavelength

    @property
    def beam_border(self):
        return self._find_most_recent_past_value("visp_beam_border")

    @property
    def geo_num_otsu(self):
        return self._find_most_recent_past_value("visp_geo_num_otsu")

    @property
    def geo_num_theta(self):
        return self._find_most_recent_past_value("visp_geo_num_theta")

    @property
    def geo_theta_min(self):
        return self._find_most_recent_past_value("visp_geo_theta_min")

    @property
    def geo_theta_max(self):
        return self._find_most_recent_past_value("visp_geo_theta_max")

    @property
    def geo_upsample_factor(self):
        return self._find_most_recent_past_value("visp_geo_upsample_factor")

    @property
    def geo_max_shift(self):
        return self._find_most_recent_past_value("visp_geo_max_shift")

    @property
    def geo_poly_fit_order(self):
        return self._find_most_recent_past_value("visp_geo_poly_fit_order")

    @property
    def solar_spectral_avg_window(self):
        return self._find_most_recent_past_value("visp_solar_spectral_avg_window")

    @property
    def solar_hairline_fraction(self):
        return self._find_most_recent_past_value("visp_solar_hairline_fraction")

    @property
    def solar_zone_prominence(self):
        return self._find_parameter_closest_wavelength("visp_solar_zone_prominence")

    @property
    def solar_zone_width(self):
        return self._find_parameter_closest_wavelength("visp_solar_zone_width")

    @property
    def solar_zone_bg_order(self):
        return self._find_parameter_closest_wavelength("visp_solar_zone_bg_order")

    @property
    def solar_zone_normalization_percentile(self):
        return self._find_parameter_closest_wavelength("visp_solar_zone_normalization_percentile")

    @property
    def solar_zone_rel_height(self):
        return self._find_most_recent_past_value("visp_solar_zone_rel_height")

    @property
    def max_cs_step_time_sec(self):
        return self._find_most_recent_past_value("visp_max_cs_step_time_sec")

    def _find_parameter_closest_wavelength(self, parameter_name: str) -> Any:
        """
        Find the database value for a parameter that is closest to the requested wavelength.

        NOTE: If the requested wavelength is exactly between two database values, the value from the smaller wavelength
        will be returned
        """
        if self._wavelength is None:
            raise ValueError(
                f"Cannot get wavelength dependent parameter {parameter_name} without wavelength"
            )

        parameter_dict = self._find_most_recent_past_value(parameter_name)
        wavelengths = np.array(parameter_dict["wavelength"])
        values = parameter_dict["values"]
        idx = np.argmin(np.abs(wavelengths - self._wavelength))
        chosen_wave = wavelengths[idx]
        chosen_value = values[idx]
        logging.debug(
            f"Choosing {parameter_name} = {chosen_value} from {chosen_wave = } (requested {self._wavelength}"
        )
        return chosen_value
