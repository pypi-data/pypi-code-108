from typing import List

import numpy as np

from sonusai.metrics import averages


def generate_summary(metrics: np.ndarray, target_names: List[str] = None, otheridx: int = -2, digits: int = 2) -> str:
    # Generate multi-class metric summary into string report, where
    # the simplest usage is print(generate_summary(metrics))
    #                 PPV     TPR      f1     FPR     ACC   support
    #     Class 1     0.71    0.80    0.75    0.00    0.99      44
    #     Class 2     0.90    0.76    0.82    0.00    0.99     128
    #     Class 3     0.86    0.82    0.84    0.04    0.93     789
    #     Other       0.94    0.96    0.95    0.18    0.92    2807
    #
    #   micro-avg                     0.92    0.027           3768
    #   macro avg     0.85    0.83    0.84    0.05    0.96    3768
    #   micro-avgwo
    #
    # metrics is num_classesx12 data from confusion_matrix() that calcs stats on raw data.
    # otheridx is used to declare which category is the "other" class for
    # single label multi-class classification, and reports will use this,
    # otheridx == -1 specifies the other class is not present and
    # micro-avgwo and macro-avgwo metrics are not printed.
    # otheridx == -2 is special case declaring other class in last class index = num_classes
    # For binary classification otheridx is ignored.
    num_classes = np.shape(metrics)[0]  # num classes, assumes metrics is from confusion_matrix()
    if num_classes == 1:
        otheridx = -1

    if otheridx == -2:
        otheridx = num_classes - 1

    if target_names is None or len(target_names) != num_classes:
        # target_names = ['%s' % l for l in labels]
        target_names = ([f'Class {i}' for i in range(1, num_classes + 1)])
        if otheridx > -1:
            target_names[otheridx] = 'Other'

    # format from sklearn,  headers = ["precision", "recall", "f1-score", "support"]
    headers = ["PPV", "TPR", "F1", "FPR", "ACC", "Support"]
    p = metrics[:, 2]
    r = metrics[:, 1]
    fpr = metrics[:, 4]
    f1 = metrics[:, 6]
    acc = metrics[:, 0]
    s = metrics[:, 9].astype(int)
    rows = zip(target_names, p, r, f1, fpr, acc, s)

    longest_last_line_heading = 'weighted avg'
    name_width = max(len(cn) for cn in target_names)
    width = max(name_width, len(longest_last_line_heading), digits)
    head_fmt = '{:>{width}s} ' + ' {:>7}' * len(headers)
    report = head_fmt.format('', *headers, width=width)
    report += '\n'
    row_fmt = '{:>{width}s} ' + ' {:>7.{digits}f}' * 5 + ' {:>7}\n'
    for row in rows:
        report += row_fmt.format(*row, width=width, digits=digits)
    report += '\n'

    if num_classes > 1:  # Binary does not require average
        # compute averages, all options are average_options = ('micro', 'macro', 'weighted', 'samples')
        if otheridx > -1:
            average_options = ('micro-avg', 'macro-avg', 'micro-avgwo', 'macro-avgwo')
            tmp = np.delete(metrics, otheridx, 0)
            mavgwo = averages(tmp)  # avg without other class
        else:
            average_options = ('micro-avg', 'macro-avg')

        mavg = averages(metrics)  # [PPV, TPR, F1, FPR, ACC, TPSUM]
        for average in average_options:
            line_heading = average

            # compute averages with specified averaging method
            if average == 'macro-avg':
                idx = 0
                # [np.mean(p), np.mean(r), np.mean(f1), np.mean(fpr), np.mean(acc), np.sum(s)]
                avg = [mavg[idx, 0], mavg[idx, 1], mavg[idx, 2],
                       mavg[idx, 3], mavg[idx, 4], mavg[idx, 5].astype(int)]
            elif average == 'micro-avg':
                # micro-mode : micro-F1 = micro-precision = micro-recall = accuracy
                idx = 1
                avg = [mavg[idx, 0], mavg[idx, 1], mavg[idx, 2],
                       mavg[idx, 3], mavg[idx, 4], mavg[idx, 5].astype(int)]
            elif average == 'macro-avgwo':
                idx = 0
                # [np.mean(p), np.mean(r), np.mean(f1), np.mean(fpr), np.mean(acc), np.sum(s)]
                avg = [mavgwo[idx, 0], mavgwo[idx, 1], mavgwo[idx, 2],
                       mavgwo[idx, 3], mavgwo[idx, 4], mavgwo[idx, 5].astype(int)]
            elif average == 'micro-avgwo':
                # micro-mode : micro-F1 = micro-precision = micro-recall = accuracy
                idx = 1
                avg = [mavgwo[idx, 0], mavgwo[idx, 1], mavgwo[idx, 2],
                       mavgwo[idx, 3], mavgwo[idx, 4], mavgwo[idx, 5].astype(int)]
            elif average == 'weighted':
                avg = mavg[2, :]  # TBD

            if line_heading.startswith('micro'):
                row_fmt_accuracy = '{:>{width}s} ' + ' {:>7.{digits}}' * 4 + ' {:>7.{digits}s}' + ' {:>7}\n'
                report += row_fmt_accuracy.format(line_heading, '', '', *avg[2:4], '', avg[5], width=width,
                                                  digits=digits)
            else:
                report += row_fmt.format(line_heading, *avg,
                                         width=width, digits=digits)

    return report
