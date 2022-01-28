class LcBuild:
    """
    Used as output of the LcBuilder.build method to unify the returned variables
    """
    def __init__(self, lc, lc_data, star_info, transits_min_count, cadence, detrend_period, sectors, source, apertures):
        self.lc = lc
        self.lc_data = lc_data
        self.star_info = star_info
        self.transits_min_count = transits_min_count
        self.cadence = cadence
        self.detrend_period = detrend_period
        self.sectors = sectors
        self.tpf_apertures = apertures
        self.tpf_source = source

