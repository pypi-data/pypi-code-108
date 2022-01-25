import logging

import tqdm
import numpy as np
import tensorflow as tf
from decouple import config as env_config
from tensorflow.keras.models import Model
from tensorflow.keras.applications.vgg19 import VGG19, preprocess_input

from stram.utils.json_processing import dict2namespace
from stram.domain.methods.base_method import BaseMethod
from stram.domain.toolsets.gatys_toolset import (
    style_loss,
    content_loss,
    compute_mask_set,
    compute_gram_matrices,
)
from stram.domain.toolsets.general_toolset import (
    clip_0_255,
    validate_masks,
    initialize_mask,
    variation_loss,
    create_optimizer,
    EarlyStopper,
)

logger = logging.getLogger(__name__)
tf.config.optimizer.set_jit(env_config('STRAM_TF_JIT', default=False, cast=bool))


class GatysMethod(BaseMethod):
    """
    Source: https://arxiv.org/abs/1508.06576
    Title: A Neural Algorithm of Artistic Style
    Authors: Leon A. Gatys, Alexander S. Ecker, Matthias Bethge

    The algorithm works by using a well pretrained classification model (VGG19) as a
    feature extractor. Content is kept by directly minimizing the loss between the
    features from the content image and the features from the synthesized image from
    various levels of VGG19. Style is enforced by mathcing statistics between the
    features of the style image and the features of the synthesized image. These
    statistics are obtained by computing the gram matrix on the channel dimension.

    Optionally, one can provide masks that map particular regions from the content
    and style images that will be matched for the style transfer.
    """

    def __str__(self):
        return 'gatys'

    def set_up(
        self, config, content_image, style_image, content_mask=None, style_mask=None
    ):
        content_image_reshaped = tf.expand_dims(content_image, axis=0)
        content_image_casted = tf.cast(content_image_reshaped, tf.float32)
        self.content_image_input = preprocess_input(content_image_casted)

        style_image_reshaped = tf.expand_dims(style_image, axis=0)
        style_image_casted = tf.cast(style_image_reshaped, tf.float32)
        self.style_image_input = preprocess_input(style_image_casted)

        self.content_mask = initialize_mask(content_image, content_mask)
        self.style_mask = initialize_mask(style_image, style_mask)
        validate_masks(self.content_mask, self.style_mask)

        self.content_image_np = content_image
        self.synthesized_image = tf.Variable(content_image_casted, trainable=True)

        if env_config('STRAM_SUMMARY', default=False, cast=bool):
            self.summarize_initial_tensors(
                content_image_reshaped, style_image_reshaped, content_mask, style_mask
            )

    def process(self, config):
        logger.info('<Gatys Method>')
        content_layers_names = list(config.content_layers.keys())
        style_layers_names = list(config.style_layers.keys())
        all_layers = set(content_layers_names + style_layers_names)

        self._step_1_create_feature_extractor(all_layers)
        self._step_2_precompute_features(config)
        self._step_3_run_training_loop(config)

    def get_synthesized_image(self):
        synthesized_image = np.round(self.synthesized_image.numpy()[0]).astype(np.uint8)
        return np.where(self.content_mask > 0, synthesized_image, self.content_image_np)

    def _step_1_create_feature_extractor(self, layers):
        """
        Create an instance of VGG19 that's specialized for returning the
        intermediate representations from the requested layers.

        Args:
            layers (list): name of the VGG19 layers used for feature extraction
        """
        vgg = VGG19(include_top=False, weights='imagenet')
        vgg.trainable = False
        outputs = {layer: vgg.get_layer(layer).output for layer in layers}

        self.feature_extractor = Model([vgg.input], outputs)
        self.feature_extractor.trainable = False

    def _step_2_precompute_features(self, config):
        """
        Extract features from the original content and style images.
        Pre-compute gram matrices from the style image features.

        Args:
            config (Bunch): configurations for the styling process
        """
        assert hasattr(self, 'feature_extractor'), 'Cannot perform step 2 before step 1'

        raw_content_features = self.feature_extractor(self.content_image_input)
        raw_style_features = self.feature_extractor(self.style_image_input)

        self.content_features = {
            layer: raw_content_features[layer] for layer in config.content_layers
        }
        mask_content_features = {
            layer: raw_content_features[layer] for layer in config.style_layers
        }
        style_features = {
            layer: raw_style_features[layer] for layer in config.style_layers
        }

        self.content_mask_set = compute_mask_set(self.content_mask, mask_content_features)
        style_mask_set = compute_mask_set(self.style_mask, style_features)

        self.style_gram_matrices = {}
        for layer, features in style_features.items():
            mask = style_mask_set[layer].numpy()
            self.style_gram_matrices[layer] = compute_gram_matrices(features, mask)

    def _step_3_run_training_loop(self, config):
        """
        Prepare and run the image optimization loop to synthesize the final image.

        Args:
            config (Bunch): configurations for the styling process
        """
        assert hasattr(self, 'content_features'), 'Cannot perform step 3 before step 2'
        assert hasattr(self, 'content_mask_set'), 'Cannot perform step 3 before step 2'
        assert hasattr(self, 'style_gram_matrices'), 'Cannot perform step 3 before step 2'

        optimizer = create_optimizer(
            config.optimizer, config.optimizer_params, config.learning_rate_params
        )
        stopper_config = dict2namespace(config.early_stopping)
        if stopper_config.enabled:
            stopper = EarlyStopper(stopper_config.delta, stopper_config.patience)
        else:
            stopper = None

        if env_config('STRAM_SUMMARY', default=False, cast=bool):
            self._train_with_summaries(config, optimizer, stopper)
        else:
            self._train_without_summaries(config, optimizer, stopper)

    @tf.function(autograph=env_config('STRAM_AUTOGRAPH', default=True, cast=bool))
    def _train_step(self, config, optimizer):
        """
        Perform an iteration of optimization for the synthesized image.

        Args:
            config (Bunch): configurations for the styling process
            optimizer (tf.optimizers.Optimizer): the optimizer object
        Returns:
            content_loss_value (tf.float32): current content loss
            style_loss_value (tf.float32): current style loss
            variation_loss_value (tf.float32): current variation loss
            total_loss (tf.float32): current total loss
        """
        with tf.GradientTape() as tape:
            preprocessed_image = preprocess_input(self.synthesized_image)
            image_features = self.feature_extractor(preprocessed_image)

            image_features_for_content = {
                layer: image_features[layer] for layer in config.content_layers
            }
            image_features_for_style = {
                layer: image_features[layer] for layer in config.style_layers
            }

            content_loss_value = content_loss(
                self.content_features, image_features_for_content, config.content_layers
            )
            style_loss_value = style_loss(
                self.style_gram_matrices,
                image_features_for_style,
                self.content_mask_set,
                config.style_layers,
            )
            variation_loss_value = variation_loss(self.synthesized_image)

            total_loss = (
                config.content_loss_weight * content_loss_value
                + config.style_loss_weight * style_loss_value
                + config.variation_loss_weight * variation_loss_value
            )

        gradients = tape.gradient(total_loss, self.synthesized_image)
        optimizer.apply_gradients([(gradients, self.synthesized_image)])
        self.synthesized_image.assign(clip_0_255(self.synthesized_image))

        return content_loss_value, style_loss_value, variation_loss_value, total_loss

    def _train_without_summaries(self, config, optimizer, stopper):
        """
        Run the image optimization loop without writing summaries.

        Args:
            config (Bunch): configurations for the styling process
            optimizer (tf.optimizers.Optimizer): the optimizer object
            stopper (EarlyStopper): object responsible for tracking loss evolution for
                                    early stopping
        """
        for i in tqdm.trange(
            config.max_iterations,
            desc='Progress',
            disable=logger.getEffectiveLevel() > logging.INFO,
        ):
            total_loss = self._train_step(config, optimizer)[-1]

            if stopper is not None and stopper(total_loss):
                logger.info(f'Stopped early: iteration {i}; {stopper.deltas_info()}')
                break

    def _train_with_summaries(self, config, optimizer, stopper):
        """
        Run the image optimization loop while writing summaries.

        Args:
            config (Bunch): configurations for the styling process
            optimizer (tf.optimizers.Optimizer): the optimizer object
            stopper (EarlyStopper): object responsible for tracking loss evolution for
                                    early stopping
        """
        images_freq = env_config('STRAM_SUMMARY_FREQUENCY_IMAGES', cast=int, default=100)

        with self.summary_writer.as_default():
            for i in tqdm.trange(
                config.max_iterations,
                desc='Progress',
                disable=logger.getEffectiveLevel() > logging.INFO,
            ):
                (
                    content_loss_value,
                    style_loss_value,
                    variation_loss_value,
                    total_loss,
                ) = self._train_step(config, optimizer)

                tf.summary.scalar('content_loss', content_loss_value, step=i)
                tf.summary.scalar('style_loss', style_loss_value, step=i)
                tf.summary.scalar('variation_loss', variation_loss_value, step=i)
                tf.summary.scalar('total_loss', total_loss, step=i)

                if i % images_freq == 0:
                    tb_image = tf.cast(self.synthesized_image, tf.uint8)
                    tf.summary.image('synthesized', tb_image, step=i)

                if stopper is not None:
                    if stopper.actual_delta is not None:
                        tf.summary.scalar('loss_delta', stopper.actual_delta, step=i)
                    if stopper(total_loss):
                        tb_image = tf.cast(self.synthesized_image, tf.uint8)
                        tf.summary.image('synthesized', tb_image, step=i)
                        logger.info(
                            f'Stopped early: iteration {i}; {stopper.deltas_info()}'
                        )
                        break
