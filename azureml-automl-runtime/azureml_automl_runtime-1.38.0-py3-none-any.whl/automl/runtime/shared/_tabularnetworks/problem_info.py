# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Dataset info utility for training a TabNet model."""


class ProblemInfo:
    """Container object for metadata about the problem being worked on."""

    def __init__(
        self,
        X=None,
        dataset_samples=0,
        dataset_features=0,
        dataset_classes=0,
        dataset_categoricals=None,
        gpu_training_param_dict=None,
    ):
        """Construct ProblemInfo.

        :param dataset_samples: number of samples in the whole dataset
        :param dataset_features: number of features in the dataset
        :param dataset_classes: number of classes in the targets of the dataset
        :param dataset_categoricals: integer array indicating the categorical features
        :param gpu_training_param_dict: dict representing gpu training related parameters.
        """
        if X is not None:
            self.dataset_samples = X.shape[0]
            self.dataset_features = X.shape[1]
        else:
            self.dataset_samples = dataset_samples
            self.dataset_features = dataset_features
        self.dataset_classes = dataset_classes

        self.dataset_categoricals = dataset_categoricals
        self.gpu_training_param_dict = gpu_training_param_dict
