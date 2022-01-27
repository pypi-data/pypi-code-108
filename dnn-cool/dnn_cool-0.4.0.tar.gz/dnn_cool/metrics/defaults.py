from dnn_cool.catalyst_utils.metrics import ClassificationAccuracy, MultiLabelClassificationAccuracy, BinaryAccuracy, \
    JaccardIndex
from dnn_cool.metrics.base import ClassificationF1Score, ClassificationPrecision, ClassificationRecall, BinaryF1Score, \
    BinaryPrecision, BinaryRecall, MeanAbsoluteError


def get_default_classification_metrics():
    return (
        ('accuracy', ClassificationAccuracy()),
        ('f1_score', ClassificationF1Score()),
        ('precision', ClassificationPrecision()),
        ('recall', ClassificationRecall()),
    )


def get_default_multilabel_classification_metrics():
    return (
        ('accuracy', MultiLabelClassificationAccuracy()),
        ('iou_0.5', JaccardIndex()),
    )


def get_default_binary_metrics():
    return (
        ('accuracy', BinaryAccuracy()),
        ('f1_score', BinaryF1Score()),
        ('precision', BinaryPrecision()),
        ('recall', BinaryRecall()),
    )


def get_default_bounded_regression_metrics():
    return (
        ('mean_absolute_error', MeanAbsoluteError()),
    )
