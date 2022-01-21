# Copyright (C) 2018 Shasvath Kapadia, Deep Chatterjee
#                    Heather Fong, Surabhi Sachdev
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import io
import json
import sqlite3

from argparse import ArgumentParser
from configparser import ConfigParser
import numpy as np

from astropy.table import Table

from glue.ligolw import ligolw
from glue.ligolw.ligolw import LIGOLWContentHandler
from glue.ligolw import array as ligolw_array
from glue.ligolw import param as ligolw_param
from glue.ligolw import dbtables
from glue.ligolw import utils as ligolw_utils
from glue.ligolw import lsctables
from lalinspiral import thinca
from lal import rate

from .p_astro import SourceType, MarginalizedPosterior


class _RankingStatPDF(object):
    ligo_lw_name_suffix = "gstlal_inspiral_rankingstatpdf"

    @classmethod
    def from_xml(cls, xml, name):
        """
        Find the root of the XML tree containing the
        serialization of this object
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
        return self


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

def _get_ln_f_over_b(ranking_data_bytes,
                     ln_likelihood_ratios,
                     ln_likelihood_ratio_threshold):
    ranking_data_xmldoc, _ = ligolw_utils.load_fileobj(
        io.BytesIO(ranking_data_bytes), contenthandler=_ContentHandler)
    rankingstatpdf = _parse_likelihood_control_doc(ranking_data_xmldoc)
    # affect the zeroing of the PDFs below threshold by hacking the
    # histograms. Do the indexing ourselves to not 0 the bin @ threshold
    noise_lr_lnpdf = rankingstatpdf.noise_lr_lnpdf
    rankingstatpdf.noise_lr_lnpdf.array[
        :noise_lr_lnpdf.bins[0][ln_likelihood_ratio_threshold]] \
        = 0.
    rankingstatpdf.noise_lr_lnpdf.normalize()
    signal_lr_lnpdf = rankingstatpdf.signal_lr_lnpdf
    rankingstatpdf.signal_lr_lnpdf.array[
        :signal_lr_lnpdf.bins[0][ln_likelihood_ratio_threshold]] \
        = 0.
    rankingstatpdf.signal_lr_lnpdf.normalize()
    zero_lag_lr_lnpdf = rankingstatpdf.zero_lag_lr_lnpdf
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
    return ln_f_over_b


def _load_search_results(conn, end_time, mass, ln_likelihood_ratio_threshold):
    """Queries SQLite file for background trigger data.
    The query has an extra check to make sure the event is not
    double counted.
    """
    cur = conn.cursor()

    xmldoc = dbtables.get_xml(conn)
    definer_id = lsctables.CoincDefTable.get_table(xmldoc).get_coinc_def_id(
        thinca.InspiralCoincDef.search,
        thinca.InspiralCoincDef.search_coinc_type,
        create_new=False)
    cur.execute("""
SELECT
        coinc_event.likelihood,
        (
        SELECT sngl_inspiral.Gamma1
        FROM
                sngl_inspiral JOIN coinc_event_map ON (
                        coinc_event_map.table_name == "sngl_inspiral"
                        AND coinc_event_map.event_id == sngl_inspiral.event_id
                )
        WHERE
        coinc_event_map.coinc_event_id == coinc_inspiral.coinc_event_id
        LIMIT 1
        ),
        EXISTS (
    SELECT
*
    FROM
time_slide
    WHERE
time_slide.time_slide_id == coinc_event.time_slide_id
AND time_slide.offset != 0
        )
FROM
        coinc_event JOIN coinc_inspiral ON (
    coinc_inspiral.coinc_event_id == coinc_event.coinc_event_id
        )
WHERE
        coinc_event.coinc_def_id == ?
        AND coinc_event.likelihood >= ?
        AND coinc_inspiral.end_time != ?
        AND coinc_inspiral.mass != ?""", (definer_id,
                                          ln_likelihood_ratio_threshold,
                                          end_time,
                                          mass))
    ln_likelihood_ratio, svd_banks, is_background = np.array(cur.fetchall()).T
    background_ln_likelihood_ratios = \
        ln_likelihood_ratio[is_background.astype(bool)]
    zerolag_ln_likelihood_ratios = \
        ln_likelihood_ratio[np.logical_not(is_background.astype(bool))]
    svd_banks = svd_banks[np.logical_not(is_background.astype(bool))].astype(int)

    return background_ln_likelihood_ratios, \
        zerolag_ln_likelihood_ratios, svd_banks


def _get_counts_instance(ln_f_over_b,
                         svd_bank_nums,
                         num_svd_bins,
                         activation_counts_table,
                         lnl_threshold=None,
                         fgmc_data_history=None,
                         prior_type="Uniform"):

    a_hat_bns = np.array(activation_counts_table['bns'], dtype=float)
    a_hat_bns /= np.sum(a_hat_bns)
    a_hat_bbh = np.array(activation_counts_table['bbh'], dtype=float)
    a_hat_bbh /= np.sum(a_hat_bbh)
    a_hat_nsbh = np.array(activation_counts_table['nsbh'], dtype=float)
    a_hat_nsbh /= np.sum(a_hat_nsbh)
    a_hat_mg = np.array(activation_counts_table['mg'], dtype=float)
    a_hat_mg /= np.sum(a_hat_mg)
    

    w_bns = num_svd_bins*np.take(a_hat_bns, svd_bank_nums)
    w_nsbh = num_svd_bins*np.take(a_hat_nsbh, svd_bank_nums)
    w_bbh = num_svd_bins*np.take(a_hat_bbh, svd_bank_nums)
    w_mg = num_svd_bins*np.take(a_hat_mg, svd_bank_nums)

    if fgmc_data_history is not None and lnl_threshold is not None:

        history = np.genfromtxt(fgmc_data_history,names=True)
        idx = history["lnl"] >= lnl_threshold

        w_bns = np.array(list(num_svd_bins*history["w_bns"][idx])+list(w_bns))
        w_nsbh = np.array(list(num_svd_bins*history["w_nsbh"][idx])+list(w_nsbh))
        w_bbh = np.array(list(num_svd_bins*history["w_bbh"][idx])+list(w_bbh))
        w_mg = np.array(list(num_svd_bins*history["w_mg"][idx])+list(w_mg))

        ln_f_over_b = np.array(list(history["ln_f_over_b"][idx]) +
                               list(ln_f_over_b))

    num_f_over_b = len(ln_f_over_b)
    w_terr = np.ones(num_f_over_b)
    fb = np.exp(ln_f_over_b)
    return MarginalizedPosterior(f_divby_b=fb, prior_type=prior_type,
                                 terr_source=SourceType(label="counts_Terrestrial",
                                                        w_fgmc=w_terr),
                                 fix_sources={"counts_Terrestrial": num_f_over_b},
                                 bns_inst=SourceType(label="counts_BNS",
                                                     w_fgmc=w_bns),
                                 bbh_inst=SourceType(label="counts_BBH",
                                                     w_fgmc=w_bbh),
                                 nsbh_inst=SourceType(label="counts_NSBH",
                                                      w_fgmc=w_nsbh),
                                 mg_inst=SourceType(label="counts_MassGap",
                                                      w_fgmc=w_mg),
                                 verbose=False)


def compute_counts_mean():
    parser = ArgumentParser("Compute mean on Poisson count")
    parser.add_argument(
        '-i', '--input', required=True,
        help='Astropy table storing activation counts per source category')
    parser.add_argument(
        '-r', '--ranking-data', required=True,
        help='Ranking stat pdf XML file to be used for f/b')
    parser.add_argument(
        '-c', '--config', required=True,
        help='Config file for extra parameters')
    parser.add_argument(
        '-o', '--output', required=True,
        help='Output file to store mean and covariance values in JSON format')
    parser.add_argument(
        '-s', '--trigger-db', required=True,
        help='Gstlal trigger sqlite database')
    parser.add_argument(
        '-f', '--data-history', default=None,
        help='The FGMC data history as astropy table, possibly from previous runs')
    args = parser.parse_args()
    config = ConfigParser()
    config.read(args.config)
    conn = sqlite3.connect(args.trigger_db)
    activation_counts_table = Table.read(args.input, format="ascii")
    ln_likelihood_ratio_threshold = config.getfloat('p_astro',
                                                    'ln_likelihood_threshold')
    end_time_threshold = config.getfloat('p_astro', 'end_time_threshold')
    mass_threshold = config.getfloat('p_astro', 'mass_threshold')
    num_svd_bins = config.getint('p_astro', 'num_svd_bins')
    prior_type = config.get('p_astro', 'prior_type')
    background_ln_likelihood_ratios, zerolag_ln_likelihood_ratios, \
    svd_banks = _load_search_results(conn,
                                     end_time=end_time_threshold,
                                     mass=mass_threshold,
                                     ln_likelihood_ratio_threshold=
                                     ln_likelihood_ratio_threshold)

    with open(args.ranking_data, 'rb') as f:
        ranking_data_bytes = f.read()
    ln_f_over_b = _get_ln_f_over_b(ranking_data_bytes,
                                   zerolag_ln_likelihood_ratios,
                                   ln_likelihood_ratio_threshold)
    counts_instance = \
        _get_counts_instance(ln_f_over_b=ln_f_over_b,
                            svd_bank_nums=svd_banks,
                            num_svd_bins=num_svd_bins,
                            activation_counts_table=activation_counts_table,
                            lnl_threshold=ln_likelihood_ratio_threshold,
                            fgmc_data_history=args.data_history,
                            prior_type=prior_type)

    mean_values_dict = {}
    for category in ["counts_BNS",
                     "counts_NSBH",
                     "counts_BBH",
                     "counts_MassGap",
                     "counts_Terrestrial"]:

        mean_values_dict[category] = \
            counts_instance.getOneDimMean(category=category)

    with open(args.output, 'w') as f:
        content = mean_values_dict
        json.dump(content, f, default=_default)

def _default(o):
    if isinstance(o, np.int64):
        return int(o)  
    raise TypeError

def histogram_by_bin():
    parser = ArgumentParser(
        description='Executable to histogram triggers by SVD bin number')

    parser.add_argument(
        '-i', '--input',
        help='Astropy table containing  data extracted from injection database')
    parser.add_argument(
        '-o', '--output',
        help='Text file to store activation counts per bin and source category')
    parser.add_argument(
        '-c', '--config', required=True,
        help='Config file with additional parameters')

    args = parser.parse_args()

    config = ConfigParser()
    config.read(args.config)

    cfar_threshold = eval(config.get('p_astro','cfar_threshold'))
    num_svds = config.getint('p_astro','num_svd_bins')

    data = Table.read(args.input,format="ascii")
    cfar = data["cfar"]
    Gamma1 = data["Gamma1"]
    mass1 = np.maximum(data["inj_m1"], data["inj_m2"])
    mass2 = np.minimum(data["inj_m1"], data["inj_m2"])
    # definition of NS: m_2 < 3 m_sun
    # definition of BH: m_2 > 5 m_sun
    # definition of MG: m1 or m2, > 3 and <= 5 
    bns_mask = np.logical_and(mass1 <= 3.0, mass2 <= 3.0)
    nsbh_mask = np.logical_and(mass1 > 3.0, mass2 <= 3.0)
    bbh_mask = np.logical_and(mass1 > 5.0, mass2 > 5.0)
    mg_mask = np.logical_or(np.logical_and(mass1 > 3.0, mass1 <= 5.0),
                            np.logical_and(mass2 > 3.0, mass2 <= 5.0))
    cfar_mask = cfar < cfar_threshold
    # calculate activation counts
    # BNS
    svd_bank_nums_bns = Gamma1[cfar_mask * bns_mask]
    act_counts_bns = np.zeros(num_svds, dtype=int)
    _uniq, _count = np.unique(svd_bank_nums_bns, return_counts=True)
    act_counts_bns[_uniq.astype(int)] = _count
    # NSBH
    svd_bank_nums_nsbh = Gamma1[cfar_mask * nsbh_mask]
    act_counts_nsbh = np.zeros(num_svds, dtype=int)
    _uniq, _count = np.unique(svd_bank_nums_nsbh, return_counts=True)
    act_counts_nsbh[_uniq.astype(int)] = _count
    # BBH
    svd_bank_nums_bbh = Gamma1[cfar_mask * bbh_mask]
    act_counts_bbh = np.zeros(num_svds, dtype=int)
    _uniq, _count = np.unique(svd_bank_nums_bbh, return_counts=True)
    act_counts_bbh[_uniq.astype(int)] = _count
    # MG
    svd_bank_nums_mg = Gamma1[cfar_mask * mg_mask]
    act_counts_mg = np.zeros(num_svds, dtype=int)
    _uniq, _count = np.unique(svd_bank_nums_mg, return_counts=True)
    act_counts_mg[_uniq.astype(int)] = _count
    # write activation counts to astropy table
    dat = np.array([act_counts_bns, act_counts_nsbh, act_counts_bbh, act_counts_mg]).T
    t = Table(data=dat, names=("bns","nsbh","bbh","mg"))
    t.write(args.output, format="ascii")
