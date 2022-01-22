from typing import List

import numpy as np

from sonusai.metrics import averages


def generate_snr_summary(mstat: np.ndarray, smetrics: np.ndarray, snrfloat: List[float], tasnridx: List[int]) -> str:
    # Generate summary for each SNR
    # mstat:    config params like target snr, levels, etc. [NNF, NTF, NSNR, NAUG, 23]
    # smetrics: metric data summed by SNR, must be shape [NSNR, num_classes, 12]
    # snrfloat: snr values for each NSNR dim in mstat & metsnr
    # tasnridx: index into snrfloat sorted (i.e. for highest to lowest snr)
    #
    # mstat fields:
    # [mi, tsnr, ssnrmean, ssnrmax, ssnrpk80, tgain, metrics[tridx,12], TN, FN, FP, TP, rmse[tridx]
    # metsnr fields: ACC, TPR, PPV, TNR, FPR, HITFA, F1, MCC, NT, PT, TP, FP]

    assert mstat.ndim == 5, 'mstat must be 5-dimensional.'

    NNF, NTF, NSNR, NAUG, _ = mstat.shape
    NMIX = NNF * NTF * NSNR * NAUG
    num_classes = smetrics.shape[1]

    result = '--- NN Performance over {} mixtures per Global SNR ---\n'.format(NMIX / NSNR)
    result += '| SNR |  PPV% |  TPR% |  F1%  |  FPR% |  ACC% | SgSNRavg | SgSNR80p |\n'
    for si in range(NSNR):
        snri = tasnridx[si]
        tmpif = np.isfinite(mstat[:, :, snri, :, 2])
        mssnravg = np.mean(mstat[:, :, snri, :, 2][tmpif])  # mean segmsnr, unweighted avg, ignoring nans
        tmpif = np.isfinite(mstat[:, :, snri, :, 4])
        segsnr80pc = np.mean(mstat[:, :, snri, :, 4][tmpif])  # segmsnr80pc, unweighted avg, ignoring nans
        metavg = averages(smetrics[snri, :, :])  # multiclass uses class averages
        # metavg fields: [PPV, TPR, F1, FPR, ACC, TPSUM]
        result += '| {:+3.0f} | {:5.1f} | {:5.1f} | {:5.1f} | {:5.1f} | {:5.1f} |   {:+3.0f}    |   {:+3.0f}    |\n'.format(
            max(min(round(mstat[0, 0, snri, 0, 1]), 99), -99),  # target snr, should be same all mixtures
            metavg[0, 0] * 100,  # PPV macro avg
            metavg[0, 1] * 100,  # TPR macro avg
            metavg[0, 2] * 100,  # F1 macro avg
            metavg[1, 3] * 100,  # FPR micro avg
            metavg[1, 4] * 100,  # ACC micro-avg = F1 micro-avg = PPV micro-avg = TPR micro-avg
            max(min(round(mssnravg), 99), -99),  # mean segsnr avg over mixtures
            max(min(round(segsnr80pc), 99), -99))  # segsnr 80th percentile avg over mixutres

    if num_classes > 1:
        result += 'PPV,TPR,F1 are macro-avg, FPR, ACC are micro-avg over {:>6} classes.\n'.format(num_classes)

    return result
