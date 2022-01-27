from scarv import scarv_queries


def get_entropy (p):
    import numpy as np
    return np.nansum(-p * np.log2(p), axis=p.ndim-1)



def calibrate(uncalibrated_predictions, calibration_model, sequence):
    import numpy as np

    epsilon = 1e-9
    flank = sequence.shape[1]//2
    class_scores = np.log(uncalibrated_predictions)

    ref_score = np.nansum(class_scores * sequence[:, flank, :], axis=1)
    ref_score[~np.isfinite(ref_score)] = np.log(epsilon)                    # calibration model doesn't accept -np.inf
    ref_score_calibrated = calibration_model.transform(ref_score)
    ref_prob = np.apply_along_axis(lambda x: x * ref_score_calibrated, 0, sequence[:, flank, :])

    alternate_probs_unnormalised = np.exp(class_scores) * (1 - sequence[:, flank, :])
    normalisation_factor = (1 - ref_score_calibrated) / np.sum(alternate_probs_unnormalised, axis=1)
    normalisation_factor[np.isnan(normalisation_factor)] = 1                # division by zero occurs when all weight is on reference
    alternate_probs = np.apply_along_axis(lambda x: x * normalisation_factor, 0, alternate_probs_unnormalised)

    prediction = ref_prob + alternate_probs
    return prediction



def match_scores_to_ranges(gr, gr_reliable_mgd, obs_reliable_flat, exp_reliable_flat):
    import pyranges as pr
    import pandas as pd
    import numpy as np
    import collections

    gr_reliable_spl = gr_reliable_mgd.tile(1)

    o = pd.Series(data = obs_reliable_flat, name="observed")
    e = pd.Series(data = exp_reliable_flat, name="expected")

    gr_reliable_spl = gr_reliable_spl.insert(o)
    gr_reliable_spl = gr_reliable_spl.insert(e)

    index = pd.Series(range(len(gr)), name="id")
    gr = gr.insert(index) 

    hits = gr.join(gr_reliable_spl, suffix="_spl")
    out = hits.as_df().groupby(['id']).agg({'observed': "sum", 'expected': "sum"})

    countsByIndex = collections.Counter(hits.id)
    out['coverage'] = [countsByIndex[ix] if ix in countsByIndex.keys() else 0 for ix in out.index]    

    return out



def process_variants (variants, allele_counts, insertion=False):
    import pandas as pd
    import numpy as np

    df = variants.as_df()
    df = df.set_index('Start')

    df.alt = pd.Categorical(df.alt, categories=['A','C','X','G','T'])
    df.ref = pd.Categorical(df.ref, categories=['A','C','X','G','T'])

    alternate_alleles = pd.get_dummies(df.alt).mul(df.ac, axis=0)\
                                                   .groupby('Start')\
                                                   .sum()\
                                                   .to_numpy()

    reference_alleles = pd.get_dummies(df.ref).mul(df.an, axis=0)\
                                                   .groupby('Start')\
                                                   .first()\
                                                   .to_numpy()

    reference_alleles -= np.sum(alternate_alleles, axis=1)[:, np.newaxis]
    reference_alleles[reference_alleles < 0] = 0

    increment = 1 if insertion else 0
    allele_counts[2 * np.unique(df.index) + increment] = reference_alleles + alternate_alleles

    return allele_counts



def toPercentile(scores, percentiles):
    import pandas as pd
    import numpy as np

    # extend boundaries in case min/max extends beyond sampled min/max
    percentiles[0] = -np.inf
    percentiles[-1] = np.inf 

    assert len(np.unique(percentiles)) == len(percentiles), "Percentile values are non-unique"

    percentiles = pd.cut(scores, bins=percentiles, labels=np.arange(0.1,100.1,0.1), include_lowest=True)
    return percentiles



def percScoreToCumulativePercCountPlot(percScore, plt=None, x_upper=None, dashed=False):
    cumulativeCounts = getCumulativeCounts(percScore)
    plt = plotCumulativePercCountPlot(cumulativeCounts, plt, x_upper, dashed)

    return plt



def getCumulativeCounts(percentile_values):
    import collections
    import numpy as np

    percentileTally = collections.Counter([int(10*x) for x in percentile_values])
    addMissingPercentiles(percentileTally)

    counts = [count for perc, count in sorted(percentileTally.items())]
    countsCumulative = np.sum(counts) - np.cumsum(counts)

    return countsCumulative



def plotCumulativePercCountPlot(countsCumulative, plt=None, x_lower=None, dashed=False):
    import numpy as np

    percentiles = np.arange(0, 100.1, 0.1)

    if dashed:
        plt.plot(percentiles, countsCumulative, '--', linewidth=3)
    else:
        plt.plot(percentiles, countsCumulative, linewidth=3)

    plt.set_xlabel("Percentile", fontsize=23)
    plt.set_ylabel("Cumulative count", fontsize=23)

    plt.set_ylim(0, 1.1 * countsCumulative[0])

    if x_lower is not None:
        plt.set_xlim(x_lower, 100.1)
        plt.set_ylim(0, 1.1 * max([line.get_ydata()[x_lower * 10 - 1] for line in plt.lines]))

    return plt



def addMissingPercentiles(percentileCountDictionary):
    import numpy as np

    percentileSetComplete = set(np.arange(0, 1001, 1))
    percentilesPresent = set(percentileCountDictionary.keys())
    
    toAdd = percentileSetComplete - percentilesPresent
    for i in list(toAdd):
        percentileCountDictionary[i] = 0

    return None


