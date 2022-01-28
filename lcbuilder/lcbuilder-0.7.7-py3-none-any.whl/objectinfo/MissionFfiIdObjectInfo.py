from lcbuilder.objectinfo.ObjectInfo import ObjectInfo


class MissionFfiIdObjectInfo(ObjectInfo):
    """
    Implementation of ObjectInfo to be used to characterize long-cadence objects.
    """
    def __init__(self, mission_id, sectors, author=None, cadence=None, initial_mask=None, initial_transit_mask=None,
                 star_info=None, apertures=None, eleanor_corr_flux="pca_flux",
                 outliers_sigma=3, high_rms_enabled=True, high_rms_threshold=2.5,
                 high_rms_bin_hours=4, smooth_enabled=False,
                 auto_detrend_enabled=False, auto_detrend_method="cosine", auto_detrend_ratio=0.25,
                 auto_detrend_period=None, prepare_algorithm=None, reduce_simple_oscillations=False,
                 oscillation_snr_threshold=4, oscillation_amplitude_threshold=0.1, oscillation_ws_scale=60,
                 oscillation_min_period=0.002, oscillation_max_period=0.2, binning=1):
        """
        @param mission_id: the mission identifier. TIC ##### for TESS, KIC ##### for Kepler and EPIC ##### for K2.
        @param sectors: an array of integers specifying which sectors will be analysed for the object
        @param initial_mask: an array of time ranges provided to mask them into the initial object light curve.
        @param star_info: input star information
        @param apertures: the aperture pixels [col, row] per sector as a dictionary.
        from the initial light curve before processing.
        @param eleanor_corr_flux the corrected flux name to be used from ELEANOR
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
        super().__init__(initial_mask, initial_transit_mask, star_info, apertures,
                         outliers_sigma, high_rms_enabled, high_rms_threshold, high_rms_bin_hours, smooth_enabled,
                         auto_detrend_enabled, auto_detrend_method, auto_detrend_ratio, auto_detrend_period,
                         prepare_algorithm, reduce_simple_oscillations, oscillation_snr_threshold,
                         oscillation_amplitude_threshold, oscillation_ws_scale, oscillation_min_period,
                         oscillation_max_period, binning)
        self.id = mission_id
        self.sectors = sectors
        self.cadence = cadence
        self.author = author
        self.eleanor_corr_flux = eleanor_corr_flux

    def sherlock_id(self):
        return self.id.replace(" ", "") + "_FFI_" + str(self.sectors)

    def mission_id(self):
        return self.id


