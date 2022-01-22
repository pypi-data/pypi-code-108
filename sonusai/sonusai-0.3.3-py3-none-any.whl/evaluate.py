"""evaluate

usage: evaluate [-hv] (-f FEATURE) [-n PRED] [-b BTHR] [-p PLOTNUM]

options:
   -h, --help
   -v, --verbose                    Be verbose.
   -f FEATURE, --feature FEATURE    Feature .h5 data file.
   -n PRED, --pred PRED             Optional predict .h5 data file.
   -b BTHR, --bthr BTHR             Optional binary detection threshold, 0 = argmax(). [default: 0].
   -p PLOTNUM, --plotnum PLOTNUM    Optional plot mixture results (-1 is plot all, 0 is plot none) [default: 0].

The evaluate command measures performance of neural-network models from frame-by-frame truth and prediction data.
It supports data mixtures of target and noise files at various SNR levels as created by sonusai genft function.

"""
from datetime import datetime
from os import mkdir
from os.path import basename
from os.path import splitext
from pathlib import Path
from typing import Union

import numpy as np
from docopt import docopt
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from sonusai import create_file_handler
from sonusai import initial_log_messages
from sonusai import logger
from sonusai import update_console_handler
from sonusai import version
from sonusai.metrics import averages
from sonusai.metrics import calculate_metrics
from sonusai.metrics import format_confusion_matrix
from sonusai.metrics import generate_snr_summary
from sonusai.metrics import generate_summary
from sonusai.metrics import one_hot
from sonusai.utils import read_feature_data
from sonusai.utils import read_predict_data
from sonusai.utils import trim_docstring


def evaluate(feature: dict,
             output_dir: str,
             predict: Union[None, np.ndarray] = None,
             binary_detection_threshold: float = 0.0,
             plot_number: int = 0,
             verbose: bool = False):
    """ Comments go here
    """

    update_console_handler(verbose)
    initial_log_messages('evaluate')

    # Scale to float range, only support 16-bit audio
    data_scale = 2 ** 15
    # Only support 16 kHz sample rates
    sample_rate = 16000

    # Summarize the mixture data
    # Number of mixtures
    num_mixtures = len(feature['mixture_database'])

    if plot_number < 0:
        # If plot_number is negative, plot all
        plot_number = [*range(num_mixtures)]
    elif plot_number == 0:
        # If plot_number is zero, plot none
        plot_number = []
    else:
        # plot_number needs to be a list (for looping later)
        plot_number = [plot_number]

    # Number of feature frames
    feature_frames = feature['feature'].shape[0]

    # Number of samples per feature
    samples_per_feature = int(feature['feature_samples'])

    # Total mixture audio samples
    mixture_samples = feature_frames * samples_per_feature

    # Number of transform frames
    transform_frames = feature['segsnr'].shape[0]

    # Number of samples per transform frame
    samples_per_transform = int(mixture_samples / transform_frames)

    # Number of classes
    num_classes = feature['truth'].shape[1]

    # Summarize mixture data by noise file, target file, SNR via array mstat:
    # size NNFxNTFxNSNRxNAUGx20
    #  #noise-files, #SNR, #target-files, #augmentations, #param fields.
    # We track all other augmentations in a dimension that auto-increments, so we can support any combinations.
    # param fields:
    #          mi,tsnr,...
    noise_files = feature['noise_files']
    num_noise_files = len(noise_files)
    target_files = feature['target_files']
    num_target_files = len(target_files)

    # Determine number of SNR cases
    # Create dictionary of SNRs
    # Each key is an SNR and its value is a list of target augmentation indices containing that SNR
    snrs = {}
    for index, augmentation in enumerate(feature['target_augmentations']):
        key = str(augmentation['snr'])
        if key not in snrs:
            snrs[key] = []
        snrs[key].append(index)
    snrs = sorted(snrs, reverse=True)

    num_snrs = len(snrs)  # Number of SNR cases
    # Detect special noise-only cases, specified by SNR < -96 where genft sets target gain = 0
    np_snrs = []
    for i, x in enumerate(snrs):
        if float(x) < -96:
            np_snrs.append(i)
    # Index of noise performance SNR (should only be 1 of them)
    if len(np_snrs) > 1:
        logger.debug('Error: more than one noise performance SNR < -96 dB detected, proceeding with first one.')
        np_snrs = [np_snrs[0]]

    num_augmentation_types = num_mixtures / (num_noise_files * num_target_files * num_snrs)
    if num_augmentation_types % 1:  # Number of augmentation types should always be integer
        logger.warning('Number of augmentations is fractional.')
    num_augmentation_types = int(np.ceil(num_augmentation_types))

    logger.info('Detected {} augmentation types beyond noise, target, and SNR.'.format(num_augmentation_types))

    if feature['config']['truth_mode'] == 'mutex':
        logger.debug('Detected truth mutex mode')
        truth_is_mutex = True
    else:
        truth_is_mutex = False

    logger.info(
        'Analyzing performance for {} mixtures, {} noise files, {} target files, and {} SNR levels.'.format(
            num_mixtures, num_noise_files,
            num_target_files,
            num_snrs))

    if binary_detection_threshold == 0:
        binary_detection_threshold = 0.5
        cmode = 0
        logger.debug('Using default argmax() for detection (binary binary_detection_threshold = {:4.2f})'.format(
            binary_detection_threshold))
    else:
        cmode = binary_detection_threshold
        logger.debug('Using custom detection threshold of {:4.2f}'.format(binary_detection_threshold))

    # Mixture stats
    mstat = np.zeros(shape=(num_noise_files, num_target_files, num_snrs, num_augmentation_types, 23), dtype=np.single)
    # Multiclass stats
    mcmall = np.zeros(shape=(num_noise_files, num_target_files, num_snrs, num_augmentation_types, num_classes, 2, 2),
                      dtype=np.single)
    if num_classes > 1:
        cmall = np.zeros(
            shape=(num_noise_files, num_target_files, num_snrs, num_augmentation_types, num_classes, num_classes),
            dtype=np.single)
    else:
        cmall = np.zeros(shape=(num_noise_files, num_target_files, num_snrs, num_augmentation_types, 2, 2),
                         dtype=np.single)

    # Keep indices in fields [gsnr,HITFA,FPR,TPR,segsnravg,mxst.segsnrpkmed,mxst.NF]
    fnameidx = np.zeros(shape=(num_noise_files, num_target_files, num_snrs, num_augmentation_types, 5), dtype=np.int16)

    # Initial augmentation type
    augi = 0
    nno = []

    miwidth = len(str(num_mixtures - 1))
    tfwidth = max(len(ele) for ele in [Path(x).stem for x in target_files])
    nfwidth = max(len(ele) for ele in [Path(x).stem for x in noise_files])

    if len(plot_number) > 0:
        pdf = PdfPages('{}/evaluate.pdf'.format(output_dir))

    for mi in range(num_mixtures):
        ni = int(feature['mixture_database'][mi]['noise_file_index'])
        ti = int(feature['mixture_database'][mi]['target_file_index'])

        # Get mixture config parameters target gain (and target SNR above)
        taugi = int(feature['mixture_database'][mi]['target_augmentation_index'])
        tsnr = str(feature['target_augmentations'][taugi]['snr'])

        if 'gain' in feature['target_augmentations'][taugi].keys():
            tgain = float(feature['target_augmentations'][taugi]['gain'])
        else:
            tgain = 1

        snri = snrs.index(tsnr)

        # record the truth index, provided by genft per mixture.
        tridx = int(feature['mixture_database'][mi]['truth_index']) - 1
        # store index into filename lists in case we want full filenames
        fnameidx[ni, ti, snri, augi, :] = [ni, ti, tridx, snri, augi]

        # For each mixture, get index endpoint (mix,noise,target sample,...)
        if mi == num_mixtures - 1:
            mxend = mixture_samples
            fend = feature_frames
            ifend = transform_frames
        else:
            mxend = feature['mixture_database'][mi + 1]['i_sample_offset']
            # out frames are possibly decimated/stride-combined
            fend = feature['mixture_database'][mi + 1]['o_frame_offset']
            # in frames are transform
            ifend = feature['mixture_database'][mi + 1]['i_frame_offset']

        # Select subset of waveforms, if present
        mxbegin = feature['mixture_database'][mi]['i_sample_offset']
        if 'mixture' in feature.keys():
            mx = feature['mixture'][mxbegin:mxend] / data_scale
        else:
            mx = []

        if 'noise' in feature.keys():
            nt = feature['noise'][mxbegin:mxend] / data_scale
            # noise level in dB
            n_level = 20 * np.log10(np.sqrt(np.mean(np.square(nt))) + np.finfo(float).eps)
            # noise max in dB
            nmax_level = 20 * np.log10(np.max(np.abs(nt)) + np.finfo(float).eps)
        else:
            nt = []
            n_level = float('nan')
            nmax_level = float('nan')

        if 'target' in feature.keys():
            tt = feature['target'][mxbegin:mxend] / data_scale
            # target level in dB
            t_level = 20 * np.log10(np.sqrt(np.mean(np.square(tt))) + np.finfo(float).eps)
            # target max in dB
            tmax_level = 20 * np.log10(np.max(np.abs(tt)) + np.finfo(float).eps)
        else:
            tt = []
            t_level = float('nan')
            tmax_level = float('nan')

        mxsnr = t_level - n_level

        # Segmental SNR and target stats
        segsnr = feature['segsnr'][feature['mixture_database'][mi]['i_frame_offset']:ifend]

        # Replace float('Inf') with weighted filter of 16 past samples, then median filter
        segsnr = segsnr_filter(segsnr)

        # segmental SNR mean = mxsnr and tsnr
        ssnrmean = 10 * np.log10(np.mean(segsnr + 1e-10))
        # seg SNR max
        ssnrmax = 10 * np.log10(max(segsnr + 1e-10))
        # seg SNR 80% percentile
        ssnrpk80 = 10 * np.log10(np.percentile(segsnr + 1e-10, 80, interpolation='midpoint'))

        # Truth and neural-net prediction data, feature_frames x num_classes
        truth = feature['truth'][feature['mixture_database'][mi]['o_frame_offset']:fend, :]

        if len(predict) > 0:
            nno = predict[feature['mixture_database'][mi]['o_frame_offset']:fend]
            # don't do this, expect genft to do the right thing w/truth, must be mutex
            # special case for false alarm analysis, set truth to zeros
            # if float(tsnr) < -96:
            #     truth = np.zeros(truth.shape)

            # ACC TPR PPV TNR FPR HITFA F1 MCC NT PT for each class, nclass x 10
            # cm is [TN FP; FN TP]
            (mcm, metrics, cm, cmn, rmse) = one_hot(truth, nno, cmode)
            # mcm2, metrics2, cm2, cmn2, rmse2 = classmetrics(truth, nno, cmode)

            # Save all stats, metrics and TN FP FN TP, but only includes for tridx class.
            mstat[ni, ti, snri, augi, :] = [mi, tsnr, ssnrmean, ssnrmax, ssnrpk80, tgain, *metrics[tridx, :],
                                            mcm[tridx, 0, 0], mcm[tridx, 0, 1], mcm[tridx, 1, 0], mcm[tridx, 1, 1],
                                            rmse[tridx]]
            # metricsall[ni, ti, snri, augi, :, :] = metrics
            mcmall[ni, ti, snri, augi, :, :, :] = mcm
            cmall[ni, ti, snri, augi, :, :] = cm
            # cmnall[ni, ti, snri, augi, :, :] = cmn

            # Increment augmentation type
            augi += 1
            if augi >= num_augmentation_types:
                augi = 0

        if mi + 1 in plot_number:
            tname = Path(target_files[ti]).stem
            nname = Path(noise_files[ni]).stem
            logger.debug(
                '{:{iwidth}}: Mix spec: SNR: {:4.1f}, target gain: {:+4.1f}, file: {:>{twidth}}, {:>{nwidth}}'.format(
                    mi, float(tsnr), tgain, tname, nname, iwidth=miwidth, twidth=tfwidth, nwidth=nfwidth))
            logger.debug(
                '{:{iwidth}}: Measured: SNR: {:4.1f}, target level: {:4.1f}, SegSNR mean, max, peak80%: {:4.1f}, {:4.1f}, {:4.1f}'.format(
                    mi, mxsnr, t_level, ssnrmean, ssnrmax, ssnrpk80, iwidth=miwidth))

            # Expand number of frames to number of samples (for plotting together with waveforms)
            segsnrex = np.reshape(np.tile(10 * np.log10(segsnr + np.finfo(float).eps), [samples_per_transform, 1]),
                                  len(segsnr) * samples_per_transform,
                                  order='F')
            feat = feature['feature'][feature['mixture_database'][mi]['o_frame_offset']:fend, :, :]

            # Truth extension to #samples in this mixture, i.e. MixSubSamples x num_classes
            truthex = np.zeros((len(segsnr) * samples_per_transform, num_classes))
            for ntri in range(num_classes):
                truthex[:, ntri] = np.reshape(np.tile(truth[:, ntri], [samples_per_feature, 1]),
                                              len(segsnr) * samples_per_transform, order='F')

            # vector of indices where truth is present
            truth_active = []
            for i, x in enumerate(np.any(truth, axis=0)):
                if x:
                    truth_active.append(i)

            if truth_is_mutex:
                # remove mutex (end), but not when class is always active
                if len(truth_active) > 1:
                    truth_active = np.delete(truth_active, -1)

            if len(truth_active) != 0:
                logger.debug(
                    '{:{iwidth}}: Truth present in {} of {} classes. First active category index: {}'.format(mi, len(
                        truth_active), num_classes, truth_active[0], iwidth=miwidth))
            else:
                logger.debug('{:{iwidth}}: Truth not present in {} classes.'.format(mi, num_classes, iwidth=miwidth))

            fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

            secu = np.arange(len(segsnr) * samples_per_transform, dtype=np.single) / sample_rate
            plots = []
            ymin = [0]

            if 'mixture' in feature.keys():
                mix_plot, = ax1.plot(secu, mx, 'r', label='Mix')
                plots.append(mix_plot)
                ymin.append(min(mx))
            if 'target' in feature.keys():
                target_plot, = ax1.plot(secu, tt, 'b', label='Target')
                plots.append(target_plot)
                ymin.append(min(tt))

            ax1.set_ylim([min(ymin), 1.05])

            if len(truth_active) > 0:
                if len(truth_active) == 1:
                    truthn_plot, = ax1.plot(secu, truthex[:, truth_active[0]], 'g-',
                                            label='NN Truth{}'.format(truth_active[0]))
                    plots.append(truthn_plot)
                    if truth_is_mutex:
                        trutho_plot, = ax1.plot(secu, truthex[:, -1], 'm-.',
                                                label='NN Truth{} (Other)'.format(num_classes))
                        plots.append(trutho_plot)
                else:
                    trutha_plot, = ax1.plot(secu, truthex, 'g-', label='NN Truth All')
                    plots.append(trutha_plot)

            if len(nno) != 0:
                nnoex = np.reshape(np.tile(nno, [samples_per_feature, 1]), len(segsnr) * samples_per_transform)
                nno_plot, = ax1.plot(secu, nnoex, 'k', label='NN Predict All')
                plots.append(nno_plot)

            ax1.legend(handles=plots, bbox_to_anchor=(1.05, 1.0), loc='upper left')

            ax2.plot(secu, segsnrex)
            ax2.set_ylim([-51, max(min(max(segsnrex), 100), -10)])
            ax2.title.set_text(
                'SegSNR mean={:4.1f} dB, max={:4.1f} dB, Peak80%={:4.1f} dB'.format(ssnrmean, ssnrmax, ssnrpk80))

            if feat.shape[1] < 5:
                tmp = np.reshape(feat, (feat.shape[0], feat.shape[1] * feat.shape[2]))
                titlestr = 'All {} features of size {}x{}'.format(feat.shape[0], feat.shape[2], feat.shape[1])
            else:
                if len(truth_active) != 0:
                    fti = np.nonzero(truth[:, truth_active[0]])[0][0]
                else:
                    fti = 0
                tmp = np.squeeze(feat[fti, :, :])
                titlestr = 'Example feature, frame {} of size {}x{}'.format(fti, feat.shape[2], feat.shape[1])
            ax3.imshow(np.transpose(tmp), aspect='auto')
            ax3.invert_yaxis()
            ax3.title.set_text(titlestr)

            fig.suptitle('{} of {}'.format(mi + 1, num_mixtures))
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

    if len(plot_number) > 0:
        pdf.close()

    if len(predict) > 0:
        save_eval_report(output_dir, noise_files, target_files, snrs, fnameidx, feature, predict,
                         binary_detection_threshold,
                         np_snrs, truth_is_mutex,
                         mstat, mcmall, cmall)


def median_filter(x: np.ndarray, n: int) -> np.ndarray:
    assert x.ndim == 1, 'Input must be one-dimensional.'

    n2 = (n - 1) // 2
    if n % 2 == 0:
        n2 += 1

    pad_x = np.zeros(len(x) + n, dtype=x.dtype)
    pad_x[n2:n2 + len(x)] = x

    y = np.zeros((len(x), n), dtype=x.dtype)
    for k in range(len(x)):
        y[k, :] = pad_x[k:k + n]

    return np.median(y, axis=1)


def segsnr_filter(segsnr: np.ndarray) -> np.ndarray:
    assert segsnr.ndim == 1, 'Input must be one-dimensional.'

    inf_indices = [i for i, val in enumerate(segsnr) if np.isinf(val)]

    if inf_indices:
        scale = np.arange(16) + 1
        for inf_index in inf_indices:
            # avoid underflow at beginning
            if inf_index > 15:
                i = range(inf_index - 1, inf_index - 17, -1)
                segsnr[inf_index] = np.sum(np.multiply(segsnr[i], scale)) / 136
            else:
                i = range(inf_index + 1)
                segsnr[inf_index] = np.median(segsnr[i])
        segsnr = median_filter(segsnr, 32)
    return segsnr


def save_eval_report(output_dir, noise_files, target_files, snrs, fnameidx, dfname, nnname,
                     binary_detection_threshold, np_snrs,
                     truth_is_mutex,
                     mstat, mcmall, cmall, nfacrit=0.05):
    outname = 'evaluate'
    num_noise_files = len(noise_files)
    num_target_files = len(target_files)
    num_snrs = len(snrs)
    num_augmentation_types = mstat.shape[3]
    NCLASS = mcmall.shape[4]  # mcm will = 1 for binary (always be correct)
    NMIX = num_noise_files * num_target_files * num_snrs * num_augmentation_types
    logger.info(
        'Printing reports in {} for {} mixtures, {} noise files, {} target files, {} SNRs, {} augmentations'.format(
            output_dir, NMIX, num_noise_files, num_target_files, num_snrs, num_augmentation_types))

    # Target all SNR list index, ordered from highest to lowest SNR
    tasnridx = np.flip(np.argsort(mstat[0, 0, :, 0, 1]))
    # Detect special case SNR
    if len(np_snrs) == 0:
        np_snrs = len(snrs) - 1
        logger.warning('Did not find low SNR (<-96 dB) case, FA analysis uses lowest SNR of {:3.0f}\n'.format(
            float(snrs[np_snrs])))
    else:
        np_snrs = np_snrs[0]  # In case a list is returned, use 0, TBD list support

    FPSNR = float(snrs[np_snrs])
    # Create list of non-special case SNRs, for some metrics
    if FPSNR < -96:
        sridx = np.arange(0, num_snrs)
        sridx = np.delete(sridx, np_snrs)  # Remove special case SNR
        srsnrlist = list(map(snrs.__getitem__, sridx))  # new list wo fpsnr case
    else:
        FPSNR = 99  # Mark as unused with value 99
        sridx = tasnridx
        srsnrlist = snrs

    snrfloat = np.zeros((num_snrs, 1))
    for i, x in enumerate(snrs):
        snrfloat[i] = float(x)

    if NCLASS == 1:
        bmode = True
    else:
        bmode = False  # TBD might need to detect NCLASS == 2 and truth_is_mutex

    # Total metrics over all data
    metsa, mcmsa, cmsumsa = calculate_metrics(cmall, bmode)  # metric summary all
    metsa_avg = averages(metsa)  # 3 rows: [PPV, TPR, F1, FPR, ACC, TPSUM]
    metsa_avgwo = averages(metsa[0:-1, :])

    # Total metrics over all non-special case SNR
    metsn, mcmsn, cmsumsn = calculate_metrics(cmall[:, :, sridx, :, :, :], bmode)
    metsn_avg = averages(metsn)  # 3x6
    metsn_avgwo = averages(metsn[0:-1, :])  # without other (last) class

    # Metric summary by noise and snr per class: 
    # fields: [ACC, TPR, PPV, TNR, FPR, HITFA, F1, MCC, NT, PT, TP, FP]
    metsnr = np.zeros((num_snrs, NCLASS, 12))  # per SNR: nsnr x class x 12
    metsnr_avg = np.zeros((num_snrs, 3, 6))  # per SNR avg over classes: nsnr x 3 x 6
    metsnr_avgwo = np.zeros((num_snrs, 3, 6))  # without other class
    metnsnr = np.zeros((num_noise_files, num_snrs, NCLASS, 12))  # Per Noise & SNR: nnf x nsnr x nclass x 12
    metnsnr_avg = np.zeros((num_noise_files, num_snrs, 3, 6))
    metnsnr_avgwo = np.zeros((num_noise_files, num_snrs, 3, 6))
    for snri in range(num_snrs):
        metsnr[snri, :, :], _, _ = calculate_metrics(cmall[:, :, snri, :, :, :])
        metsnr_avg[snri, :, :] = averages(metsnr[snri, :, :])
        metsnr_avgwo[snri, :, :] = averages(metsnr[snri, 0:-1, :])  # without other class = nclass
        for ni in range(num_noise_files):
            metnsnr[ni, snri, :, :], _, _ = calculate_metrics(cmall[ni, :, snri, :, :, :])
            metnsnr_avg[ni, snri, :, :] = averages(metnsnr[ni, snri, :, :])
            metnsnr_avgwo[ni, snri, :, :] = averages(metnsnr[ni, snri, 0:-1, :])

    # mcm: [TN FP; FN TP]
    # Fields in mstat, TargetSNR, TargetGain: 
    FTSNR = 1
    FTGAIN = 5
    # Fields in metrics: 
    FACC = 0
    FF1 = 6
    FTPR = 1
    FFA = 4
    FHITFA = 5

    # FA per noise-file @ lowest SNR, averages over classes:
    fanf_macwo = metnsnr_avgwo[:, np_snrs, 0, 3]  # macro-average wo other class NNFx1
    fanf_micwo = metnsnr_avgwo[:, np_snrs, 1, 3]  # micro-average wo other class NNFx1
    fanf_mac = metnsnr_avg[:, np_snrs, 0, 3]  # macro-average NNFx1
    fanf_mic = metnsnr_avg[:, np_snrs, 1, 3]  # micro-average NNFx1
    nfafail = [i for i, x in enumerate(fanf_mic) if x > nfacrit]

    # Create summary report
    summary_name = '{}/nn_perfsummary.txt'.format(output_dir)
    with open(file=summary_name, mode='w') as f:
        # RMSEmean = np.squeeze(np.mean(np.reshape(mstat[:, :, :, :, 20], (num_noise_files, num_target_files * num_augmentation_types * num_snrs, 1)), 1))

        if bmode:  # -------------- Binary Classification ------------------
            f.write('\n')
            f.write('--- Aaware Binary NN Performance Analysis: {}\n'.format(outname))
            f.write('Performance over {} mixtures at {} SNR cases created from\n'.format(NMIX, num_snrs))
            f.write(
                '{} target files and {} noise files and {} augmentations.\n'.format(num_target_files, num_noise_files,
                                                                                    num_augmentation_types))
            f.write('Binary classification threshold: {:4.2f}.\n'.format(binary_detection_threshold))
            f.write('\n')
            # FA Summary, note: for binary *_avg are accurate, although no avg needed (but avgwo is not)
            f.write('--- False Alarm Performance over {} noise files  ---\n'.format(num_noise_files))
            f.write('FA over all mixtures:             {:6.5f}%\n'.format(metsa_avg[1, 3] * 100))
            f.write('Max FA over SNRs and Noise files: {:6.5f}%\n'.format(np.max(metnsnr_avg[:, :, 1, 3]) * 100))
            f.write('FA of lowest SNR {:2.0f} dB:          {:6.5f}%\n'.format(FPSNR, metsnr_avg[np_snrs, 1, 3] * 100))
            if len(nfafail) > 0:
                f.write('FAIL: Number of failing noise files with FPR rate > {:3.1f}%: {}\n'
                        .format(nfacrit * 100, len(nfafail)))
            else:
                f.write('PASS: Number of failing noise files with FPR rate > {:3.1f}%: {}\n'
                        .format(nfacrit * 100, len(nfafail)))

            f.write(generate_snr_summary(mstat, metsnr, snrfloat, tasnridx))

            f.write('\n\n')
            # Failing Noise File List
            if len(nfafail) > 0:
                f.write(
                    '--- List of {} failing noise files with FA rate > {:3.1f}%:\n'.format(len(nfafail), nfacrit * 100))
                for jj in range(len(nfafail)):
                    f.write('{:40s}: {:3.1f}%\n'.format(noise_files[nfafail[jj]], 100 * fanf_mic[nfafail[jj]]))

            f.write('\n')

        else:  # ----------------- Multiclass Classification -----------------------------
            f.write('\n')
            f.write('--- Aaware Multiclass NN Performance Analysis: {}\n'.format(outname))
            f.write('Performance over {} mixtures at {} SNR cases created from\n'.format(NMIX, num_snrs))
            f.write(
                '{} target files and {} noise files and {} augmentations.\n'.format(num_target_files, num_noise_files,
                                                                                    num_augmentation_types))
            f.write('Number of classes: {}.\n'.format(NCLASS))
            f.write('Mutex mode (single-label): {}\n'.format(truth_is_mutex))
            f.write('Classification decision threshold: {:4.2f}.\n'.format(binary_detection_threshold))
            f.write('Confusion Matrix over all mixtures:\n')
            f.write(generate_snr_summary(mstat, metsnr, snrfloat, tasnridx))
            f.write('\n')
            # Metrics over all mixtures:
            f.write('Confusion Matrix over all mixtures:\n')
            f.write(format_confusion_matrix(cmsumsa))
            f.write('Metric summary, all mixtures:\n')
            f.write(generate_summary(metsa))
            f.write('\n')
            # Metrics excluding special case SNR
            if FPSNR < -96:
                f.write(
                    'Metrics excluding special case false-positive SNR (FPSNR) at {:2.0f} dB\n'.format(FPSNR))
                f.write('Confusion Matrix for all mixtures except FPSNR:\n')
                f.write(format_confusion_matrix(cmsumsn))

            # FA Summary
            f.write('False alarm over all mixtures, class micro-avg for all, non-other: {:6.5f}%, {:6.5f}%\n'
                    .format(metsa_avg[1, 3] * 100, metsa_avgwo[1, 3] * 100))
            f.write(
                'False alarm summary for lowest SNR at {:2.0f} dB, class micro-avg over all, non-other: {:6.5f}%, {:6.5f}%\n'
                    .format(FPSNR, metsnr_avg[np_snrs, 1, 3] * 100, metsnr_avgwo[np_snrs, 1, 3] * 100))
            if len(nfafail) > 0:
                f.write(
                    'FAIL: Number of failing noise files with FPR rate > {:3.1f}%: {} (see noise-breakdown report)\n'
                        .format(nfacrit * 100, len(nfafail)))
            else:
                f.write('PASS: Number of failing noise files with FPR rate > {:3.1f}%: {}\n'
                        .format(nfacrit * 100, len(nfafail)))
            # Print false alarm summary, use micro-avg which tends more pessimistic excluding other class if in mutex mode

            f.write('\n\n')
            f.write('-------- Per SNR Metrics ------------ \n')
            f.write('\n')
            for snri in range(num_snrs):
                si = tasnridx[snri]  # sorted list
                f.write('\n')
                f.write('--- Confusion Matrix for SNR {:3.1f} dB:\n'.format(float(snrs[si])))
                (met, _, cmsum) = calculate_metrics(cmall[:, :, si, :, :, :])
                f.write(format_confusion_matrix(cmsum))
                f.write('Metric summary:\n')
                f.write(generate_summary(metsnr[si, :, :]))
                f.write('\n\n')

    # --------------- Create noise breakdown report --------------------------------
    noise_breakdown_name = '{}/noise_breakdown.txt'.format(output_dir)
    with open(file=noise_breakdown_name, mode='w') as f:
        # Calc #frames per noise file, all speech,augm cases at lowSNR case
        f.write('\n')
        f.write('--- Aaware sonusai() NN False Alarm Analysis: {}\n'.format(outname))
        f.write('Performance over {} mixtures at {} SNR cases created from\n'.format(NMIX, num_snrs))
        f.write(
            '{} target files, {} noise files and {} augmentations.\n'.format(num_target_files, num_noise_files,
                                                                             num_augmentation_types))
        f.write('Classification decision threshold: {:4.2f}.\n'.format(binary_detection_threshold))
        f.write('Number of classes: {}.\n'.format(NCLASS))
        f.write('Mutex mode (single-label): {}\n'.format(truth_is_mutex))
        f.write('\n')
        f.write('--- NN False Alarm Summary over {} noise files ---\n'.format(num_noise_files))
        # FA Summary
        # Print false alarm summary, use micro-avg which tends more pessimistic excluding other class if in mutex mode
        f.write('False alarm over all mixtures, class micro-avg for all, non-other: {:6.5f}%,{:6.5f}%\n'
                .format(metsa_avg[1, 3] * 100, metsa_avgwo[1, 3] * 100))
        f.write(
            'False alarm summary for lowest SNR at {:2.0f} dB, class micro-avg over all, non-other: {:6.5f}%, {:6.5f}%\n'
                .format(FPSNR, metsnr_avg[np_snrs, 1, 3] * 100, metsnr_avgwo[np_snrs, 1, 3] * 100))

        if len(nfafail) > 0:
            f.write('FAIL: Number of failing noise files with FPR rate > {:3.1f}%: {}\n'
                    .format(nfacrit * 100, len(nfafail)))
        else:
            f.write('PASS: Number of failing noise files with FPR rate > {:3.1f}%: {}\n'
                    .format(nfacrit * 100, len(nfafail)))
        # FA per SNR
        f.write('False alarm per SNR micro-avg (%):\n')
        f.write('{}\n'.format(np.transpose(snrfloat[tasnridx].astype(int))))
        f.write('{}\n'.format(np.round(metsnr_avg[tasnridx, 1, 3] * 100, 2)))
        # FA per SNR and Class:
        # f.write('False alarm per SNR and Class (%):\n {}\n'.format(np.round(metsnr[:,:,FFA]*100,2)))

        f.write('\n')
        NFLOWSNR = (np.sum((metnsnr[:, np_snrs, 0, 8] + metnsnr[:, np_snrs, 0, 9])) / num_noise_files).astype(
            int)  # Nframes = NT + PT
        f.write(
            '--- FA perf. per noise file, over {} mixtures, {} frames per SNR:\n'.format(
                num_target_files * num_augmentation_types,
                int(NFLOWSNR)))

        nfileidx = fnameidx[:, 0, 0, 0, 0]
        for ni in range(num_noise_files):
            # sortni = issnrl[ni]   # TBD figure out how to sort by FA perf
            # FA per SNR
            tmpnfname = splitext(basename(noise_files[nfileidx[ni]]))[0]
            f.write('\n')
            f.write('--- NN Perf. for noise file {} of {}: {} ---\n'.format(ni + 1, num_noise_files, tmpnfname))
            f.write('False alarm per SNR micro-avg (%):\n')
            f.write('{}\n'.format(np.transpose(snrfloat[tasnridx].astype(int))))
            f.write('{}\n'.format(np.round(metnsnr_avg[ni, tasnridx, 1, 3] * 100, 2)))
            f.write('Confusion Matrix:\n')
            (_, _, cmsum) = calculate_metrics(cmall[ni, :, :, :, :, :])
            f.write(format_confusion_matrix(cmsum))
            f.write('Noise file full path: {}\n'.format(noise_files[nfileidx[ni]]))


def main():
    try:
        args = docopt(trim_docstring(__doc__), version=version(), options_first=True)

        feature_name = args['--feature']

        if args['--pred']:
            predict_name = args['--pred']
        else:
            predict_name = ''

        binary_detection_threshold = float(args['--bthr'])

        plot_number = int(args['--plotnum'])

        # create output directory
        now = datetime.now()
        output_dir = 'evaluate-{:%Y%m%d-%H%M%S}'.format(now)
        try:
            mkdir(output_dir)
        except OSError as error:
            logger.error('Could not create directory, {}: {}'.format(output_dir, error))
            exit()

        log_name = output_dir + '/evaluate.log'
        create_file_handler(log_name)

        feature = read_feature_data(feature_name)
        predict = read_predict_data(predict_name, feature['feature'].shape[0])

        evaluate(feature=feature, output_dir=output_dir, predict=predict,
                 binary_detection_threshold=binary_detection_threshold,
                 plot_number=plot_number, verbose=args['--verbose'])

        logger.info('Wrote results to {}'.format(output_dir))

    except KeyboardInterrupt:
        logger.info('Canceled due to keyboard interrupt')
        exit()


if __name__ == '__main__':
    main()
