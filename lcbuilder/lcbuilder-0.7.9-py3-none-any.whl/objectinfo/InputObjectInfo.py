import os
from lcbuilder.objectinfo.ObjectInfo import ObjectInfo


class InputObjectInfo(ObjectInfo):
    """
    Implementation of ObjectInfo to be used to characterize objects which are to be loaded from a csv file.
    """
    def __init__(self, input_file, initial_mask=None, initial_transit_mask=None,
                 star_info=None, outliers_sigma=3, high_rms_enabled=True, high_rms_threshold=2.5,
                 high_rms_bin_hours=4, smooth_enabled=False,
                 auto_detrend_enabled=False, auto_detrend_method="cosine", auto_detrend_ratio=0.25,
                 auto_detrend_period=None, prepare_algorithm=None, reduce_simple_oscillations=False,
                 oscillation_snr_threshold=4, oscillation_amplitude_threshold=0.1, oscillation_ws_scale=60,
                 oscillation_min_period=0.002, oscillation_max_period=0.2, object_info=1):
        """
        @param input_file: the file to be used for loading the light curve
        @param initial_mask: an array of time ranges provided to mask them into the initial object light curve.
        @param star_info: input star information
        @param apertures: the aperture pixels [col, row] per sector as a dictionary.
        @param outliers_sigma: sigma used to cut upper outliers.
        @param high_rms_enabled: whether RMS masking is enabled
        @param high_rms_threshold: RMS masking threshold
        @param high_rms_bin_hours: RMS masking binning
        @param smooth_enabled: whether short-window smooth is enabled
        @param auto_detrend_enabled: whether automatic high-amplitude periodicities detrending is enabled
        @param auto_detrend_method: biweight or cosine
        @param auto_detrend_ratio: the ratio to be used as window size in relationship to the strongest found period
        @param auto_detrend_period: the fixed detrend period (disables auto_detrend)
        @param prepare_algorithm: custom curve preparation logic
        @param reduce_simple_oscillations: whether to reduce dirac shaped oscillations
        @param oscillation_snr_threshold: oscillations snr threshold to be removed
        @param oscillation_amplitude_threshold: oscillations amplitude threshold over std
        @param oscillation_ws_scale: oscillation window size chunks
        @param oscillation_min_period: minimum period to be computed in the oscillations periodogram
        @param oscillation_max_period: maximum period to be computed in the oscillations periodogram
        @param binning: the number of cadences to be binned together
        """
        super().__init__(initial_mask, initial_transit_mask, star_info, None,
                         outliers_sigma, high_rms_enabled, high_rms_threshold, high_rms_bin_hours, smooth_enabled,
                         auto_detrend_enabled, auto_detrend_method, auto_detrend_ratio, auto_detrend_period,
                         prepare_algorithm, reduce_simple_oscillations, oscillation_snr_threshold,
                         oscillation_amplitude_threshold, oscillation_ws_scale, oscillation_min_period,
                         oscillation_max_period, object_info)
        self.input_file = input_file

    def sherlock_id(self):
        return "INP_" + os.path.splitext(self.input_file)[0].replace("/", "_")

    def mission_id(self):
        return None
