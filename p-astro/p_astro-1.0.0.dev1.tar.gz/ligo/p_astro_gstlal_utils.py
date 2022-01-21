import io
import json

from glue.ligolw.ligolw import LIGOLWContentHandler \
    as GlueLIGOLWContentHandler
from glue.ligolw import array as glue_ligolw_array
from glue.ligolw import param as glue_ligolw_param
from glue.ligolw import utils as glue_ligolw_utils
from glue.ligolw import lsctables as glue_lsctables
from ligo.lw import ligolw
from ligo.lw.ligolw import LIGOLWContentHandler
from ligo.lw import array as ligolw_array
from ligo.lw import param as ligolw_param
from ligo.lw import utils as ligolw_utils
from ligo.lw import lsctables
from ligo.segments import utils as segments_utils
from lal import rate

import itertools
import math
import numpy as np
from scipy import interpolate
from scipy import optimize

def assert_probability(f):
    """
    Adapted from gstlal/stats, gstlal-inspiral-1.6 branch
    """
    def g(*args, **kwargs):
        p = f(*args, **kwargs)
        if isinstance(p, np.ndarray):
            assert ((0. <= p) & (p <= 1.)).all()
        else:
            assert 0. <= p <= 1.
        return p
    return g

@assert_probability
@np.vectorize
def poisson_p_not_0(var):
    """
    Adapted from gstlal/stats, gstlal-inspiral-1.6 branch
    """
    assert var >= 0.
    var = -float(var)

    if var < -0.69314718055994529:
        return 1. - math.exp(var)

    s = [var]
    term = var
    threshold = -1e-20 * var
    for n in itertools.count(2):
        term *= var / n
        s.append(term)
        if abs(term) <= threshold:
            s.reverse()
            s = -sum(s)
            assert s >= 0.
            return s if s else 0.


class _RankingStatPDF(object):
    """
    Adapted from far.py, gstlal-inspiral-1.6 branch
    """
    ligo_lw_name_suffix = "gstlal_inspiral_rankingstatpdf"

    @classmethod
    def from_xml(cls, xml, name):
        """
        Find the root of the XML tree containing the serialization of this
        object
        """
        xml, = [elem for elem in
                xml.getElementsByTagName(ligolw.LIGO_LW.tagName)
                if elem.hasAttribute("Name") and
                elem.Name == "%s:%s" % (name, cls.ligo_lw_name_suffix)]
        # create a uninitialized instance
        self = super().__new__(cls)
        # populate from XML
        self.noise_lr_lnpdf = rate.BinnedLnPDF.from_xml(xml, "noise_lr_lnpdf")
        self.signal_lr_lnpdf = rate.BinnedLnPDF.from_xml(xml,
                                                         "signal_lr_lnpdf")
        self.zero_lag_lr_lnpdf = rate.BinnedLnPDF.from_xml(
            xml, "zero_lag_lr_lnpdf")
        self.segments = ligolw_param.get_pyvalue(xml, u"segments").strip()
        self.segments = \
            segments_utils.from_range_strings(self.segments.split(",")
                                              if self.segments else [], float)

        return self

    def new_with_extinction(self, extinct_zerowise_elems):
        """
        Adapted from far.py, gstlal-inspiral-1.6 branch
        """
        bg = self.noise_lr_lnpdf.array
        x = self.noise_lr_lnpdf.bins[0].centres()
        assert (x == self.zero_lag_lr_lnpdf.bins[0].centres()).all()
        ccdf = bg[::-1].cumsum()[::-1]
        ccdf /= ccdf[0]

        def mk_survival_probability(rate_eff, m):
            return np.exp(-rate_eff * ccdf**m)

        zl = self.zero_lag_lr_lnpdf.copy()
        zl.array[:extinct_zerowise_elems] = 0.
        if not zl.array.any():
            raise ValueError("zero-lag counts are all zero")

        mode, = zl.argmax()
        zlcumsum = zl.array.cumsum()
        assert zlcumsum[-1] > 1000, \
            "Need at least 1000 zero lag events to compute extinction model"
        ten_thousand_events_lr = \
            x[zlcumsum.searchsorted(zlcumsum[-1] - 10000)]
        # Adjust the mode to be at 10,000 events if that LR is higher
        if ten_thousand_events_lr > mode:
            mode = ten_thousand_events_lr
        one_hundred_events_lr = x[zlcumsum.searchsorted(zlcumsum[-1] - 100)]
        mask = (x < mode) | (x > one_hundred_events_lr)
        zl = np.ma.masked_array(zl.array, mask)
        bg = np.ma.masked_array(bg, mask)

        def ssr(params):
            norm, rate_eff, m = params
            if norm <= 0. or rate_eff <= 0. or m <= 0.:
                return np.inf

            model = norm * bg * mk_survival_probability(rate_eff, m)
            model_var = np.where(model > 1., model, 1.)
            square_error = (zl - model)**2. / model_var

            return np.trapz(square_error, x)

        norm, rate_eff, m = optimize.fmin(ssr,
                                          (zl.sum() / bg.sum(), zl.sum(), 5.),
                                          xtol=1e-8, ftol=1e-8, disp=0)

        # compute survival probability model from best fit
        survival_probability = mk_survival_probability(rate_eff, m)

        # apply to background counts and signal counts
        self.noise_lr_lnpdf.array *= survival_probability
        self.noise_lr_lnpdf.normalize()
        self.signal_lr_lnpdf.array *= survival_probability
        self.signal_lr_lnpdf.normalize()

        return self

class FAPFAR(object):
    """
    Adapted from far.py, gstlal-inspiral-1.6 branch
    """
    def __init__(self, rankingstatpdf, extinct_zerowise_elems):
        # input checks
        if not rankingstatpdf.zero_lag_lr_lnpdf.array.any():
            raise ValueError("RankingStatPDF's zero-lag counts are all zero")

        # save the livetime
        self.livetime = float(abs(rankingstatpdf.segments))

        zl = rankingstatpdf.zero_lag_lr_lnpdf.copy()
        zl.array[:extinct_zerowise_elems] = 0.
        rate_normalization_lr_threshold, = zl.argmax()

        # record trials factor, with safety checks
        counts = rankingstatpdf.zero_lag_lr_lnpdf.count
        assert not np.isnan(counts.array).any(), \
            "zero lag log likelihood ratio counts contain NaNs"
        assert (counts.array >= 0.).all(), \
            "zero lag log likelihood ratio rates contain negative values"
        self.count_above_threshold = \
            counts[rate_normalization_lr_threshold:, ].sum()

        # get noise model ranking stat values and event counts from
        # bins
        noise_lnpdf = rankingstatpdf.noise_lr_lnpdf

        threshold_index = \
            noise_lnpdf.bins[0][rate_normalization_lr_threshold]
        ranks = \
            noise_lnpdf.bins[0].lower()[threshold_index:]
        counts = noise_lnpdf.array[threshold_index:]
        assert not np.isnan(counts).any(), \
            "background log likelihood ratio rates contain NaNs"
        assert (counts >= 0.).all(), \
            "background log likelihood ratio rates contain negative values"

        ccdf = counts[::-1].cumsum()[::-1]
        ccdf /= ccdf[0]
        ccdf = poisson_p_not_0(ccdf)

        # safety checks
        assert not np.isnan(ranks).any(), \
            "log likelihood ratio co-ordinates contain NaNs"
        assert not np.isinf(ranks).any(), \
            "log likelihood ratio co-ordinates are not all finite"
        assert not np.isnan(ccdf).any(), \
            "log likelihood ratio CCDF contains NaNs"
        assert ((0. <= ccdf) & (ccdf <= 1.)).all(), \
            "log likelihood ratio CCDF failed to be normalized"

        # build interpolator.
        self.ccdf_interpolator = interpolate.interp1d(ranks, ccdf)

        self.minrank = ranks[0]
        self.maxrank = ranks[-1]

    @assert_probability
    def ccdf_from_rank(self, rank):
        return self.ccdf_interpolator(np.clip(rank,
                                              self.minrank,
                                              self.maxrank))

    def far_from_rank(self, rank):
        log_tdp = np.log1p(-self.ccdf_from_rank(rank))
        return self.count_above_threshold * -log_tdp / self.livetime

def _parse_likelihood_control_doc(xmldoc):
    name = "gstlal_inspiral_likelihood"
    rankingstatpdf = _RankingStatPDF.from_xml(xmldoc, name)
    if rankingstatpdf is None:
        raise ValueError("document does not contain likelihood ratio data")
    return rankingstatpdf


@ligolw_array.use_in
@ligolw_param.use_in
@lsctables.use_in
class _ContentHandler(LIGOLWContentHandler):
    pass


@glue_ligolw_array.use_in
@glue_ligolw_param.use_in
@glue_lsctables.use_in
class _GlueContentHandler(GlueLIGOLWContentHandler):
    pass

def _get_ln_f_over_b(ranking_data_bytes,
                     ln_likelihood_ratios,
                     livetime,
                     extinct_zerowise_elems):

    ranking_data_xmldoc = ligolw_utils.load_fileobj(
        io.BytesIO(ranking_data_bytes), contenthandler=_ContentHandler)
    rankingstatpdf = _parse_likelihood_control_doc(ranking_data_xmldoc)
    # affect the zeroing of the PDFs below threshold by hacking the
    # histograms. Do the indexing ourselves to not 0 the bin @ threshold
    noise_lr_lnpdf = rankingstatpdf.noise_lr_lnpdf
    signal_lr_lnpdf = rankingstatpdf.signal_lr_lnpdf
    zero_lag_lr_lnpdf = rankingstatpdf.zero_lag_lr_lnpdf
    ssorted = zero_lag_lr_lnpdf.array.cumsum()[-1] - 10000
    idx = zero_lag_lr_lnpdf.array.cumsum().searchsorted(ssorted)

    ln_likelihood_ratio_threshold = \
        zero_lag_lr_lnpdf.bins[0].lower()[idx]

    # Compute FAR for threshold, and estimate
    # terrestrial count consistent with threshold
    fapfar = \
        FAPFAR(rankingstatpdf.new_with_extinction(extinct_zerowise_elems),
               extinct_zerowise_elems)
    far_threshold = fapfar.far_from_rank(ln_likelihood_ratio_threshold)
    lam_0 = far_threshold*livetime

    rankingstatpdf.noise_lr_lnpdf.array[
        :noise_lr_lnpdf.bins[0][ln_likelihood_ratio_threshold]] \
        = 0.
    rankingstatpdf.noise_lr_lnpdf.normalize()

    rankingstatpdf.signal_lr_lnpdf.array[
        :signal_lr_lnpdf.bins[0][ln_likelihood_ratio_threshold]] \
        = 0.
    rankingstatpdf.signal_lr_lnpdf.normalize()

    rankingstatpdf.zero_lag_lr_lnpdf.array[
        :zero_lag_lr_lnpdf.bins[0][ln_likelihood_ratio_threshold]] \
        = 0.
    rankingstatpdf.zero_lag_lr_lnpdf.normalize()

    f = rankingstatpdf.signal_lr_lnpdf
    b = rankingstatpdf.noise_lr_lnpdf
    ln_f_over_b = \
        np.array([f[ln_lr, ] - b[ln_lr, ] for ln_lr in ln_likelihood_ratios])
    if np.isnan(ln_f_over_b).any():
        raise ValueError("NaN encountered in ranking statistic PDF ratios")
    if np.isinf(np.exp(ln_f_over_b)).any():
        raise ValueError(
            "infinity encountered in ranking statistic PDF ratios")
    return ln_f_over_b, lam_0

def _get_event_ln_likelihood_ratio_svd_endtime_mass(coinc_bytes):
    coinc_xmldoc, _ = glue_ligolw_utils.load_fileobj(
        io.BytesIO(coinc_bytes), contenthandler=_GlueContentHandler)
    coinc_event, = glue_lsctables.CoincTable.get_table(coinc_xmldoc)
    coinc_inspiral, = glue_lsctables.CoincInspiralTable.get_table(coinc_xmldoc)
    sngl_inspiral = glue_lsctables.SnglInspiralTable.get_table(coinc_xmldoc)

    assert all([sngl_inspiral[i].Gamma0 == sngl_inspiral[i+1].Gamma0
                for i in range(len(sngl_inspiral)-1)]), \
        "svd bank different between ifos!"
    return (coinc_event.likelihood,
            sngl_inspiral[0].mass1,
            sngl_inspiral[0].mass2,
            sngl_inspiral[0].spin1z,
            sngl_inspiral[0].spin2z,
            coinc_inspiral.snr,
            coinc_inspiral.combined_far)
