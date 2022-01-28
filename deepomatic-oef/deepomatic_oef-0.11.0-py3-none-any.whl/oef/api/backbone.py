from abc import ABC, abstractmethod


# -----------------------------------------------------------------------------#

class BackboneInterface(ABC):

    def __init__(self, generic_config, config):
        """
        Initialize the backbone.

        Args:
            generic_config: An instance of deepomatic.oef.protos.models.image.backbones_pb2.Backbone.
            config: The specific config of the backbone. Its type depends on the backbone type, it might
                    for exemple be an instance of deepomatic.oef.protos.models.image.backbones_pb2.InceptionBackbone.
        """
        self._generic_config = generic_config
        self._config = config

    @abstractmethod
    def builder(self, inputs, is_training, input_to_output_ratio=None, reuse=None):
        """
        Build the backbone graph given its inputs.

        Args:
            inputs: The preprocessed input tensor
            is_training: Whether training is active or not. Typically used to decide if
                dropout should be active and batch_norm trainable.
            input_to_output_ratio: When using Faster-RCNN, it allows to decide where
                to cut the backbone into two parts: one part goes before the ROI pooling layer,
                the other part goes after.
            reuse (bool): Whether to create new tensors or re-used existing one with the same name.

        Return:
            features: A tensor for the backbone head
            end_point: A dict of tensors indexed by strings
            feature_maps: A dict of tensor names (strings) with keys being each stride level: 2, 4, 8, 16, ...
        """

    @abstractmethod
    def get_aux_logits(self):
        """
        Return the list of auxiliary logits tensor functions.

        Each items of the list is function with the following signature:
        logits_tensor = aux_fn(endpoints) with `endpoints` as returned by the builder.
        """

    @abstractmethod
    def get_scope_name(self):
        """
        Return the scope name of the backbone.

        Used by feature extractors to build feature pyramids.
        """
        return self._scope_name
