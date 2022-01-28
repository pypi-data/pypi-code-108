from abc import ABC, abstractmethod


class ObjectInfo(ABC):
    """
    Root class to be extended to characterize the input object to be analysed by Sherlock.
    """
    OBJECT_ID_REGEX = "^(KIC|TIC|EPIC)[-_ ]([0-9]+)$"
    NUMBERS_REGEX = "[0-9]+$"
    MISSION_ID_KEPLER = "KIC"
    MISSION_ID_KEPLER_2 = "EPIC"
    MISSION_ID_TESS = "TIC"
    initial_detrend_period = None
    initial_mask = None
    initial_transit_mask = None
    star_info = None

    def __init__(self, initial_mask=None, initial_transit_mask=None, star_info=None,
                 apertures=None, outliers_sigma=3, high_rms_enabled=True, high_rms_threshold=2.5,
                 high_rms_bin_hours=4, smooth_enabled=False,
                 auto_detrend_enabled=False, auto_detrend_method="cosine", auto_detrend_ratio=0.25,
                 auto_detrend_period=None, prepare_algorithm=None, reduce_simple_oscillations=False,
                 oscillation_snr_threshold=4, oscillation_amplitude_threshold=0.1, oscillation_ws_scale=100,
                 oscillation_min_period=0.002, oscillation_max_period=0.2, binning=1
    ):
        self.initial_mask = initial_mask
        self.initial_transit_mask = initial_transit_mask
        self.star_info = star_info
        self.apertures = apertures
        self.outliers_sigma = outliers_sigma
        self.high_rms_enabled = high_rms_enabled
        self.high_rms_threshold = high_rms_threshold
        self.high_rms_bin_hours = high_rms_bin_hours
        self.smooth_enabled = smooth_enabled
        self.auto_detrend_enabled = auto_detrend_enabled
        self.auto_detrend_method = auto_detrend_method
        self.auto_detrend_ratio = auto_detrend_ratio
        self.auto_detrend_period = auto_detrend_period
        self.prepare_algorithm = prepare_algorithm
        self.reduce_simple_oscillations = reduce_simple_oscillations
        self.oscillation_snr_threshold = oscillation_snr_threshold
        self.oscillation_amplitude_threshold = oscillation_amplitude_threshold
        self.oscillation_ws_scale = oscillation_ws_scale
        self.oscillation_min_period = oscillation_min_period
        self.oscillation_max_period = oscillation_max_period
        self.binning = binning

    @abstractmethod
    def sherlock_id(self):
        """
        Returns the unique name generated for Sherlock processing
        """
        pass

    @abstractmethod
    def mission_id(self):
        """
        Returns the real mission identifier
        """
        pass
