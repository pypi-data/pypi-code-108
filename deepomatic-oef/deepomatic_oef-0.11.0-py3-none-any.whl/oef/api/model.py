from abc import ABC, abstractmethod


# -----------------------------------------------------------------------------#

class ModelInterface(ABC):
    """
    This is the base class for any specific model implementation that is part of
    the `model` OneOf field of ../protos/model.proto
    """

    @staticmethod
    @abstractmethod
    def get_output_tensors():
        """
        Return output tensor names.

        Return:
            outputs: A list of string.
        """


# -----------------------------------------------------------------------------#

class TensorflowModelInterface(ModelInterface):

    @abstractmethod
    def get_feature_extractor_scopes(self):
        """
        Return the TF variable scope for the feature extractor on top of the backbone scope,
        without a trailing slash. This is used to decide whether the provided checkpoint file
        is a backbone chekpoint or a full model chekpoint.

        If the model does not have something else than a backbone part, it should return None.

        For example: ['FirstStageFeatureExtractor']

        Return
            scopes: A list of feature extractor scopes (string) or None if there is nothing else than a feature extractor.
        """

    @abstractmethod
    def get_groundtruth(self, mode, annotations):
        """
        Returns groundtruth tensors.

        Args:
            mode (tf.estimator.ModeKeys): tf.estimator.ModeKeys.TRAIN / EVAL / PREDICT
            annotations (dict of tensors): the annotation dict tensor

        Return:
            A groundtruth object that will be passed to `get_prediction_dict`, `get_loss_dict` and `get_eval_metrics`.
        """

    @abstractmethod
    def get_predictions(self, mode, input_data, groundtruth=None):
        """
        Returns raw predictions (typically logits).

        Args:
            mode (tf.estimator.ModeKeys): tf.estimator.ModeKeys.TRAIN / EVAL / PREDICT
            input_data (dict of tensors): the dictionary of input tensors
            groundtruth: the ground truth as returned by get_groundtruth.
                         Some models like Faster-RCNN need ground-truth at training time to
                         properly balance sampled proposals. In prediction mode, this parameter
                         will be None.

        Returns:
            A predictions object that will be passed to `postprocess_predictions` and `get_eval_metrics`
        """

    @abstractmethod
    def get_postprocessed_predictions(self, input_data, predictions):
        """
        Apply a final post-processing step to predictions.

        Args:
            input_data (dict of tensors): the dictionary of input tensors
            predictions (object): the predictions object as returned by `get_predictions`

        Returns:
            A dictionary of tensors with keys being the same as the dict returned by
            `get_export_tensors_fn_dict`
        """

    @abstractmethod
    def get_loss_dict(self, input_data, predictions, groundtruth):
        """
        Returns a dictionary of losses

        Args:
            input_data (dict of tensors): the dictionary of input tensors
            predictions (object): the predictions object as returned by `get_predictions`
            groundtruth (object): the groundtruth object as returned by `get_groundtruth`

        Returns:
            A dictionary of losses.
        """

    @abstractmethod
    def get_regularization_losses(self, model):
        """
        Returns a list of regularization losses
        """

    @abstractmethod
    def get_update_ops(self):
        """
        Returns tensorflow update ops
        """

    @abstractmethod
    def get_eval_metrics(self, model, input_data, postprocessed_predictions, groundtruth):
        """
        Returns a dictionary of metrics

        Args:
            model (object): the model as returned by `model_fn`
            input_data (dict of tensors): the dictionary of input tensors
            postprocessed_predictions (dict of tensors): the post-processed predictions object as returned by `postprocess_predictions`
            groundtruth (object): the groundtruth object as returned by `get_groundtruth`

        Returns:
            A dictionary of metrics.
        """

    @abstractmethod
    def get_export_tensors_fn_dict(self):
        """
        Returns a dictionary of function (the values) to apply of post-processed prediction tensors
        (the keys, which must match keys from `postprocess_predictions` output)
        """

# -----------------------------------------------------------------------------#
