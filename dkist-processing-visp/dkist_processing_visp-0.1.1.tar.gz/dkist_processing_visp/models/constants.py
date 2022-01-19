from enum import Enum


class VispBudName(Enum):
    num_raster_steps = "NUM_RASTER_STEPS"
    polarimeter_mode = "POLARIMETER_MODE"
    lamp_exposure_times = "LAMP_EXPOSURE_TIMES"
    solar_exposure_times = "SOLAR_EXPOSURE_TIMES"
    observe_exposure_times = "OBSERVE_EXPOSURE_TIMES"
    polcal_exposure_times = "POLCAL_EXPOSURE_TIMES"
