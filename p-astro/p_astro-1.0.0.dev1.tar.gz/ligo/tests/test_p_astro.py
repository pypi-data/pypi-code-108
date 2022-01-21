from importlib import resources

import numpy as np
import pytest

from .. import p_astro
from . import data


def source_type(label, w_fgmc):
    return p_astro.SourceType(label=label, w_fgmc=w_fgmc)

def counts_instance_func(f_divby_b,prior_type, terr_source_instance,
                         fix_sources_dict,**source_instances):
    return p_astro.MarginalizedPosterior(f_divby_b=f_divby_b,
                                         prior_type=prior_type,
                                         terr_source=terr_source_instance,
                                         fix_sources=fix_sources_dict,
                                         **source_instances)

def compute_pastro(category, idx, counts_instance):
    return counts_instance.pastro(categories=[category], trigger_idx=idx)[0]

@pytest.mark.filterwarnings('ignore::RuntimeWarning')
def test_p_astro_categories():
    with resources.open_binary(data, 'zerolag_svd_bank_nums.txt') as f:
        zerolag_lnls, svd_bank_nums = np.loadtxt(f, unpack=True)
    with resources.open_binary(data, 'f_divby_b.txt') as f:
        fb = np.loadtxt(f, unpack=True)

    # Acquire activation counts for each source category
    with resources.open_binary(data, 'bns_wellfound_hits.txt') as f:
        a_bns = np.genfromtxt(f, names=True)["hit_count"]
    with resources.open_binary(data, 'nsbh_wellfound_hits.txt') as f:
        a_nsbh = np.genfromtxt(f, names=True)["hit_count"]
    with resources.open_binary(data, 'bbh_wellfound_hits.txt') as f:
        a_bbh = np.genfromtxt(f, names=True)["hit_count"]
    with resources.open_binary(data, 'background_hits.txt') as f:
        a_terr = np.genfromtxt(f, names=True)["hit_count"]

    # Normalize activation counts
    a_hat_bns = a_bns/(np.sum(a_bns))
    a_hat_nsbh = a_nsbh/(np.sum(a_nsbh))
    a_hat_bbh = a_bbh/(np.sum(a_bbh))
    a_hat_terr = a_terr/(np.sum(a_terr))

    # Assign one weight per source category to each candidate event
    w_bns = np.array([a_hat_bns[int(svd)] for svd in svd_bank_nums])
    w_nsbh = np.array([a_hat_nsbh[int(svd)] for svd in svd_bank_nums])
    w_bbh = np.array([a_hat_bbh[int(svd)] for svd in svd_bank_nums])
    #w_terr = np.ones(len(w_bns))
    w_terr = np.array([a_hat_terr[int(svd)] for svd in svd_bank_nums])

    N = len(zerolag_lnls) # number of candidate events
    counts_instance = counts_instance_func(
        f_divby_b=fb,
        prior_type="Uniform",
        terr_source_instance=source_type(label="Terr",w_fgmc=w_terr),
        fix_sources_dict={"Terr":N},
        bns_inst=source_type(label="BNS",w_fgmc=w_bns),
        bbh_inst=source_type(label="BBH",w_fgmc=w_bbh),
        nsbh_inst=source_type(label="NSBH",w_fgmc=w_nsbh))

    p_astro_bns = compute_pastro(category="BNS", idx=N-1,
                                 counts_instance=counts_instance)

    p_astro_bbh = compute_pastro(category="BBH", idx=N-1,
                                 counts_instance=counts_instance)

    p_astro_nsbh = compute_pastro(category="NSBH", idx=N-1,
                                 counts_instance=counts_instance)

    assert np.isclose(p_astro_bns, 0.)
    assert np.isclose(p_astro_bbh, 0.446, rtol=1e-03)
    assert np.isclose(p_astro_nsbh, 0.)
